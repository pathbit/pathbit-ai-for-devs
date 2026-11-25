#!/usr/bin/env python3
"""Summarize the JUnit reports required for a CI job group."""

import argparse
import json
from pathlib import Path
import re
import stat
import sys
import xml.etree.ElementTree as ET


MAX_REPORT_BYTES = 1024 * 1024
OUTCOMES = {"failure": "failures", "error": "errors", "skipped": "skipped"}
DETAIL_ELEMENTS = {"properties", "system-out", "system-err"}


def check_child_tags(element, allowed):
    if any(child.tag not in allowed and child.tag not in DETAIL_ELEMENTS for child in element):
        raise ValueError(f"Unsupported child of {element.tag}.")


def suite_counts(suite):
    check_child_tags(suite, {"testcase"})
    counts = dict.fromkeys(("tests", "passed", *OUTCOMES.values()), 0)
    for case in suite.findall("testcase"):
        check_child_tags(case, OUTCOMES)
        outcomes = {element.tag for element in case if element.tag in OUTCOMES}
        if len(outcomes) > 1:
            raise ValueError("A testcase has conflicting outcomes.")
        outcome = OUTCOMES[next(iter(outcomes))] if outcomes else "passed"
        counts["tests"] += 1
        counts[outcome] += 1
    check_declared_counts(suite, counts)
    return counts


def check_declared_counts(element, counts):
    for field in ("tests", *OUTCOMES.values()):
        value = element.get(field)
        if value is not None and (not re.fullmatch(r"[0-9]+", value) or int(value) != counts[field]):
            raise ValueError(f"Declared {field} differs from testcase records.")


def read_report(path):
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("Reports must be regular files.")
    with path.open("rb") as report:
        raw = report.read(MAX_REPORT_BYTES + 1)
    if len(raw) > MAX_REPORT_BYTES:
        raise ValueError("Report exceeds 1 MiB.")
    content = raw.decode("utf-8-sig")
    if any(declaration in content for declaration in ("<!DOCTYPE", "<!ENTITY")):
        raise ValueError("DTD and entity declarations are unsupported.")
    root = ET.fromstring(content)
    if root.tag == "testsuite":
        return suite_counts(root)
    if root.tag != "testsuites":
        raise ValueError("Expected testsuite or testsuites containing testsuite records.")
    check_child_tags(root, {"testsuite"})
    counts = dict.fromkeys(("tests", "passed", *OUTCOMES.values()), 0)
    for suite in root.findall("testsuite"):
        for field, count in suite_counts(suite).items():
            counts[field] += count
    check_declared_counts(root, counts)
    return counts


def diagnose(directory, jobs):
    reports = []
    for job in jobs:
        entry = {"job": job}
        try:
            counts = read_report(directory / f"{job}.xml")
        except FileNotFoundError:
            entry.update(status="inconclusive", reason="missing-report")
        except (OSError, ET.ParseError, ValueError):
            entry.update(status="inconclusive", reason="invalid-report")
        else:
            if counts["failures"] or counts["errors"]:
                entry.update(status="failed", reason="test-failures")
            elif not counts["tests"]:
                entry.update(status="inconclusive", reason="empty-report")
            elif counts["skipped"]:
                entry.update(status="inconclusive", reason="skipped-tests")
            else:
                entry.update(status="passed")
            entry["counts"] = counts
        reports.append(entry)
    statuses = {entry["status"] for entry in reports}
    overall = next(status for status in ("failed", "inconclusive", "passed") if status in statuses)
    return {"status": overall, "reports": reports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", required=True, type=Path)
    parser.add_argument("--jobs", required=True, nargs="+")
    args = parser.parse_args()
    if len(set(args.jobs)) != len(args.jobs) or any(
        not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", job) for job in args.jobs
    ):
        parser.error("Job IDs must be unique lowercase ASCII slugs.")
    result = diagnose(args.reports, args.jobs)
    print(json.dumps(result, indent=2))
    return {"passed": 0, "failed": 1, "inconclusive": 2}[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
