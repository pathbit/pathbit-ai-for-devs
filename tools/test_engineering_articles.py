#!/usr/bin/env python3
"""Exercise the documented offline CLIs for articles 0007 to 0009."""

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parent.parent
SCOPE = ROOT / "0007_revisao_git_com_escopo"
FIXTURES = ROOT / "0008_fixtures_reproduziveis"
CI = ROOT / "0009_diagnostico_ci_com_junit"


def run_python(script, *arguments, env=None):
    return subprocess.run(
        [sys.executable, script, *arguments], capture_output=True, check=False, env=env,
    )


class LabTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory(prefix="pathbit-lab-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    def write(self, name, text):
        destination = self.directory / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        return destination

    def assert_report(self, result, status):
        self.assertEqual(result.returncode, status, result.stderr.decode("utf-8"))
        return json.loads(result.stdout)


class GitScopeTests(LabTests):
    def setUp(self):
        super().setUp()
        self.environment = {name: value for name, value in os.environ.items() if not name.upper().startswith("GIT_")}
        self.environment["GIT_CONFIG_GLOBAL"] = os.devnull
        self.environment["GIT_CONFIG_NOSYSTEM"] = "1"
        self.git("init", "--quiet", "--template=")
        self.git("config", "core.excludesFile", str(self.write(".git/empty-excludes", "")))

    def git(self, *arguments):
        return subprocess.run(
            ["git", "-C", self.directory, "-c", "user.name=Offline Test", "-c",
             "user.email=offline@example.invalid", "-c", "commit.gpgsign=false", *arguments],
            capture_output=True, check=True, env=self.environment,
        ).stdout

    def check_scope(self, *arguments, env=None, policy=None):
        return run_python(
            SCOPE / "src/check_scope.py", "--repo", self.directory,
            "--policy", policy or SCOPE / "examples/scope.json.example", *arguments, env=env,
        )

    def test_sandbox_reaches_both_documented_outcomes(self):
        report = self.assert_report(run_python(SCOPE / "examples/run_sandbox.py"), 0)
        self.assertTrue(report["allowed"]["ok"])
        self.assertFalse(report["blocked"]["ok"])
        self.assertEqual(report["blocked"]["changes"][-1]["violations"], [
            {"path": ".github/workflows/check.yml", "reason": "protected"},
        ])

    def test_worktree_and_index_are_read_separately_and_remain_intact(self):
        path = "src/ação com espaço.py"
        self.write(path, "version = 1\n")
        self.git("add", "--", path)
        self.write(path, "version = 2\n")
        index = (self.directory / ".git/index").read_bytes()
        report = self.assert_report(self.check_scope(), 0)
        self.assertEqual([(item["stage"], item["paths"]) for item in report["changes"]],
                         [("index", [path]), ("worktree", [path])])
        self.assertEqual((self.directory / path).read_text(encoding="utf-8"), "version = 2\n")
        self.assertEqual((self.directory / ".git/index").read_bytes(), index)

    def test_directory_prefix_and_protected_paths_are_distinct(self):
        self.write("src-other/app.py", "pass\n")
        self.write("src/generated/prices.py", "pass\n")
        self.write(".git/info/exclude", "scratch/\n")
        self.write("scratch/note.txt", "ignored by fixture\n")
        report = self.assert_report(self.check_scope(), 1)
        self.assertEqual([violation for change in report["changes"] for violation in change["violations"]], [
            {"path": "src-other/app.py", "reason": "outside-scope"},
            {"path": "src/generated/prices.py", "reason": "protected"},
        ])

    def test_staged_rename_checks_origin_and_destination(self):
        self.write("settings.yml", "mode: demo\n")
        self.write("src/.keep", "")
        self.git("add", "--", "settings.yml", "src/.keep")
        self.git("commit", "--quiet", "-m", "Add a fixture")
        self.git("mv", "settings.yml", "src/settings.yml")
        report = self.assert_report(self.check_scope(), 1)
        change, = report["changes"]
        self.assertTrue(change["status"].startswith("R"))
        self.assertEqual(change["paths"], ["settings.yml", "src/settings.yml"])
        self.assertEqual(change["violations"], [{"path": "settings.yml", "reason": "outside-scope"}])

    def test_invalid_policy_is_a_tool_error(self):
        invalid = self.write("bad-policy.json", '{"allow":["../src/"],"protect":[]}')
        result = self.check_scope(policy=invalid)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"Invalid policy path", result.stderr)

    def test_environment_does_not_redirect_git_index(self):
        self.write("README.md", "in this repository\n")
        self.git("add", "--", "README.md")
        environment = dict(self.environment, GIT_INDEX_FILE=str(self.directory / "other-index"))
        report = self.assert_report(self.check_scope(env=environment), 0)
        self.assertEqual([item["stage"] for item in report["changes"]], ["index"])
        self.assertFalse((self.directory / "other-index").exists())


class FixtureTests(LabTests):
    source = FIXTURES / "examples/orders.json.example"
    expected = FIXTURES / "examples/orders.expected.json"

    def fixture(self, source, *arguments):
        return run_python(FIXTURES / "src/build_fixture.py", source, *arguments)

    def test_golden_matches_exact_bytes(self):
        self.assertEqual(self.fixture(self.source, "--check", self.expected).returncode, 0)
        result = self.fixture(self.source)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, self.expected.read_bytes())
        orders = json.loads(result.stdout)["orders"]
        self.assertEqual([item["customer_id"] for item in orders], ["ana", "bruno", "sofia"])
        self.assertEqual(orders[0]["customer_name"], "Ana Araújo")

    def test_reordering_input_keeps_bytes(self):
        spec = json.loads(self.source.read_bytes())
        spec["customers"].reverse()
        reordered = self.write("reordered.json", json.dumps(spec))
        self.assertEqual(self.fixture(reordered, "--check", self.expected).returncode, 0)

    def test_inserting_customer_keeps_existing_orders(self):
        spec = json.loads(self.source.read_bytes())
        spec["customers"].insert(0, {"id": "a-new", "name": "New customer"})
        inserted = self.write("inserted.json", json.dumps(spec))
        result = self.assert_report(self.fixture(inserted), 0)
        previous = json.loads(self.expected.read_bytes())["orders"]
        self.assertEqual(result["orders"][1:], previous)

    def test_drift_is_nonzero_and_does_not_rewrite_golden(self):
        spec = json.loads(self.source.read_bytes())
        spec["seed"] = "another-seed"
        changed = self.write("changed.json", json.dumps(spec))
        before = self.expected.read_bytes()
        result = self.fixture(changed, "--check", self.expected)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"Fixture differs", result.stderr)
        self.assertEqual(self.expected.read_bytes(), before)

    def test_invalid_date_and_duplicate_id_have_no_fixture(self):
        original = json.loads(self.source.read_bytes())
        for label, specification in [
            ("date", dict(original, created_at="2026-02-30T00:00:00Z")),
            ("duplicate", dict(original, customers=original["customers"] * 2)),
        ]:
            with self.subTest(label=label):
                result = self.fixture(self.write("invalid.json", json.dumps(specification)))
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")


class CiReportsTests(LabTests):
    def report(self, directory, *jobs):
        return run_python(CI / "src/diagnose_reports.py", "--reports", directory, "--jobs", *jobs)

    def test_report_passes_only_with_both_jobs(self):
        result = self.assert_report(self.report(CI / "examples/passed", "api", "storage"), 0)
        self.assertEqual(result["status"], "passed")
        self.assertEqual([job["counts"]["passed"] for job in result["reports"]], [2, 1])

    def test_failure_keeps_priority_and_missing_report_is_visible(self):
        result = self.assert_report(self.report(CI / "examples/failed", "api", "storage"), 1)
        self.assertEqual(result["status"], "failed")
        self.assertEqual([job["reason"] for job in result["reports"]], ["test-failures", "missing-report"])

    def test_skipped_and_missing_reports_are_inconclusive(self):
        result = self.assert_report(self.report(CI / "examples/incomplete", "api", "storage"), 2)
        self.assertEqual(result["status"], "inconclusive")
        self.assertEqual([job["reason"] for job in result["reports"]], ["missing-report", "skipped-tests"])

    def test_inconsistent_totals_empty_and_malformed_xml(self):
        self.write("inconsistent.xml", '<testsuite tests="7"><testcase name="one"/></testsuite>')
        self.write("empty.xml", '<testsuite tests="0"/>')
        self.write("malformed.xml", '<testsuite><testcase/>')
        result = self.assert_report(self.report(self.directory, "inconsistent", "empty", "malformed"), 2)
        self.assertEqual([job["reason"] for job in result["reports"]], [
            "invalid-report", "empty-report", "invalid-report",
        ])

    def test_runner_error_is_counted_and_private_message_is_omitted(self):
        self.write("api.xml", '<testsuite errors="1"><testcase><error message="sample private note"/></testcase></testsuite>')
        result = self.report(self.directory, "api")
        self.assertNotIn(b"sample private note", result.stdout)
        report = self.assert_report(result, 1)
        self.assertEqual(report["reports"][0]["counts"]["errors"], 1)

    def test_dtd_and_large_reports_are_inconclusive(self):
        self.write("doctype.xml", '<!DOCTYPE testsuite><testsuite/>')
        self.write("large.xml", " " * (1024 * 1024 + 1))
        result = self.assert_report(self.report(self.directory, "doctype", "large"), 2)
        self.assertEqual([job["reason"] for job in result["reports"]], ["invalid-report", "invalid-report"])

    def test_unrecognized_test_outcome_cannot_approve_report(self):
        self.write("api.xml", '<testsuite tests="1"><testcase><flakyFailure/></testcase></testsuite>')
        report = self.assert_report(self.report(self.directory, "api"), 2)
        self.assertEqual(report["reports"][0]["reason"], "invalid-report")


if __name__ == "__main__":
    unittest.main()
