# Git review with verifiable scope

[Português (Brasil)](README.md) · **English** · [Español](README.es.md)

Use a versioned list of paths to review changes made by coding agents. The lab reads the Git index, working tree and untracked files and shows which changes need human review.

## Requirements

- [Python 3.10 or later](https://www.python.org/downloads/). The lab recommends [Python 3.14.7](https://www.python.org/downloads/release/python-3147/), with installers for each system.
- [Git 2.28 or later](https://git-scm.com/downloads) available in your terminal. Check with `git --version`.

The scripts use only the Python standard library. To use an isolated environment, create it at the repository root.

```sh
python3 -m venv .venv
. .venv/bin/activate
```

Use PowerShell on Windows. After activating the environment, use `python` in place of `python3` in the commands below.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Quick start

Run the lab at the repository root. It creates a separate temporary checkout, stages an allowed change and adds a protected file.

```sh
python3 0007_revisao_git_com_escopo/examples/run_sandbox.py
```

The output contains `allowed.ok: true` for the change to `src/app.py`. The second round contains `blocked.ok: false` and a `protected` violation for `.github/workflows/check.yml`. The lab exits 0 when it verifies both results. Each checker invocation uses 0 for scope approval, 1 for a violation and 2 for a tool error.

## Verify the lab

Run this article's test group at the repository root.

```sh
python3 tools/test_engineering_articles.py GitScopeTests -v
```

[Full article](article/ARTICLE.en.md) · [Practical example](examples/README.en.md) · [LinkedIn article](article/ARTICLE_LINKEDIN.en.md) · [Announcement post](article/POST_LINKEDIN.en.md)

---

Developed with ❤️ by [Pathbit](https://www.pathbit.com.br/)
