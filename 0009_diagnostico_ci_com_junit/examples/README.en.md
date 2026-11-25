# Exercise in an isolated environment

[Português (Brasil)](README.md) · **English** · [Español](README.es.md)

Use the [module guide](../README.en.md#requirements) to prepare the environment. Run the commands at the repository root.

```sh
python3 0009_diagnostico_ci_com_junit/src/diagnose_reports.py --reports 0009_diagnostico_ci_com_junit/examples/passed --jobs api storage
python3 0009_diagnostico_ci_com_junit/src/diagnose_reports.py --reports 0009_diagnostico_ci_com_junit/examples/failed --jobs api storage
python3 0009_diagnostico_ci_com_junit/src/diagnose_reports.py --reports 0009_diagnostico_ci_com_junit/examples/incomplete --jobs api storage
```

Each directory contains reports from one fictional run. The first command exits 0. The second exits 1 and records both `test-failures` in `api` and `missing-report` in `storage`. The third exits 2 with `missing-report` in `api` and `skipped-tests` in `storage`.

Inspect [the failed assertion](failed/api.xml) and [the skipped test](incomplete/storage.xml). Run one case at a time if your shell stops on errors, because the last two commands should return nonzero status.

To try this with your project's CI, use XML from a single run, one `<job>.xml` file per expected job, and adapt the IDs in `--jobs`. The [article](../article/ARTICLE.en.md) describes the supported format and exit status.
