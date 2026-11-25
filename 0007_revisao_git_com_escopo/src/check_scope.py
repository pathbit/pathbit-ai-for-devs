#!/usr/bin/env python3
"""Report Git changes outside the allowed scope of a task."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def git(repository, *arguments):
    environment = {name: value for name, value in os.environ.items() if not name.upper().startswith("GIT_")}
    result = subprocess.run(
        ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", repository, *arguments],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
    )
    if result.returncode:
        raise ValueError(os.fsdecode(result.stderr).strip() or "Git command failed.")
    return result.stdout


def nul_fields(raw):
    if raw and not raw.endswith(b"\0"):
        raise ValueError("Expected NUL-terminated output from Git.")
    return [os.fsdecode(field) for field in raw.split(b"\0")[:-1]]


def diff_entries(raw, stage):
    fields = iter(nul_fields(raw))
    entries = []
    try:
        for status in fields:
            paths = [next(fields)]
            if status.startswith(("R", "C")):
                paths.append(next(fields))
            entries.append({"stage": stage, "status": status, "paths": paths})
    except StopIteration as error:
        raise ValueError("Git returned an incomplete change record.") from error
    return entries


def policy_paths(value):
    if not isinstance(value, list):
        raise ValueError("Every policy field must be a list of repository-relative paths.")
    for path in value:
        if (
            not isinstance(path, str)
            or any(char in path for char in ("\\", ":", "\0"))
            or any(part in ("", ".", "..", ".git") for part in path.removesuffix("/").split("/"))
        ):
            raise ValueError("Invalid policy path. Use a relative path or directory prefix.")
    return value


def matches(path, rules):
    return any(path.startswith(rule) if rule.endswith("/") else path == rule for rule in rules)


def check_scope(repository, policy):
    if not isinstance(policy, dict) or set(policy) != {"allow", "protect"}:
        raise ValueError("Policy needs exactly the allow and protect fields.")
    allow, protect = (policy_paths(policy[key]) for key in ("allow", "protect"))
    if git(repository, "rev-parse", "--show-prefix").strip():
        raise ValueError("Run the scope check from the repository root.")
    diff_options = [
        "diff", "--name-status", "-z", "--find-renames", "--ignore-submodules=none",
        "--no-ext-diff", "--no-textconv",
    ]
    changes = diff_entries(git(repository, *diff_options, "--cached", "--"), "index")
    changes += diff_entries(git(repository, *diff_options, "--"), "worktree")
    changes += [
        {"stage": "untracked", "status": "?", "paths": [path]}
        for path in nul_fields(git(repository, "ls-files", "--others", "--exclude-standard", "-z"))
    ]
    for entry in changes:
        entry["violations"] = [
            {"path": path, "reason": "protected" if matches(path, protect) else "outside-scope"}
            for path in entry["paths"]
            if matches(path, protect) or not matches(path, allow)
        ]
    return {"ok": not any(entry["violations"] for entry in changes), "changes": changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--policy", type=Path, required=True)
    args = parser.parse_args()
    try:
        policy = json.loads(args.policy.read_text(encoding="utf-8"))
        report = check_scope(args.repo, policy)
    except (OSError, ValueError) as error:
        print(f"Scope check could not run: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
