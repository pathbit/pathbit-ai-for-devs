# CI diagnostics with JUnit reports

[Português (Brasil)](README.md) · **English** · [Español](README.es.md)

Gather evidence from required jobs and distinguish passed tests, recorded failures and inconclusive results. The lab summarizes local XML as JSON without depending on a CI server.

## Requirements

- [Python 3.10 or later](https://www.python.org/downloads/). The lab recommends [Python 3.14.7](https://www.python.org/downloads/release/python-3147/), with installers for each system.

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

At the repository root, run the scenario where both required suites completed successfully.

```sh
python3 0009_diagnostico_ci_com_junit/src/diagnose_reports.py --reports 0009_diagnostico_ci_com_junit/examples/passed --jobs api storage
```

The output shows `status: passed`, two passed tests in `api` and one in `storage`. The failing example exits 1. When evidence is incomplete, the CLI exits 2.

## Verify the lab

Run this article's test group at the repository root.

```sh
python3 tools/test_engineering_articles.py CiReportsTests -v
```

[Full article](article/ARTICLE.en.md) · [Practical example](examples/README.en.md) · [LinkedIn article](article/ARTICLE_LINKEDIN.en.md) · [Announcement post](article/POST_LINKEDIN.en.md)

---

Developed with ❤️ by [Pathbit](https://www.pathbit.com.br/)
