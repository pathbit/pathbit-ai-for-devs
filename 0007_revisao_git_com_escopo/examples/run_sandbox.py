"""Run the approved and blocked cases in a temporary Git repository."""

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


def validate(repository, expected_status):
    example = Path(__file__).resolve().parent
    check = subprocess.run(
        [sys.executable, example.parent / "src/check_scope.py", "--repo", repository,
         "--policy", example / "scope.json.example"],
        capture_output=True,
        text=True,
        check=False,
    )
    if check.returncode != expected_status:
        raise RuntimeError(f"Expected exit {expected_status}, got {check.returncode}: {check.stderr}")
    return json.loads(check.stdout)


def main():
    environment = {name: value for name, value in os.environ.items() if not name.upper().startswith("GIT_")}
    with TemporaryDirectory(prefix="scope-lab-") as temporary:
        repository = Path(temporary)
        subprocess.run(["git", "init", "--quiet", "--template=", repository], check=True, env=environment)
        empty_excludes = repository / ".git" / "empty-excludes"
        empty_excludes.touch()
        subprocess.run(
            ["git", "-C", repository, "config", "core.excludesFile", empty_excludes],
            check=True, env=environment,
        )
        (repository / "src").mkdir()
        (repository / "src" / "app.py").write_text("print('checkout')\n", encoding="utf-8")
        subprocess.run(["git", "-C", repository, "add", "--", "src/app.py"], check=True, env=environment)
        allowed = validate(repository, 0)
        workflows = repository / ".github" / "workflows"
        workflows.mkdir(parents=True)
        (workflows / "check.yml").write_text("name: Example check\n", encoding="utf-8")
        blocked = validate(repository, 1)
    print(json.dumps({"allowed": allowed, "blocked": blocked}, indent=2))


if __name__ == "__main__":
    main()
