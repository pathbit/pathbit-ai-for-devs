# Reproducible fixtures for integration tests

[Português (Brasil)](README.md) · **English** · [Español](README.es.md)

Generate a stable set of orders from synthetic inputs. The lab fixes the timestamp, derives values per ID and compares the output with a versioned golden file.

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

At the repository root, run comparison mode. It reads the input and expected files without writing either one.

```sh
python3 0008_fixtures_reproduziveis/src/build_fixture.py 0008_fixtures_reproduziveis/examples/orders.json.example --check 0008_fixtures_reproduziveis/examples/orders.expected.json
```

The `Fixture matches` message means the output matches byte for byte. The CLI exits 0 for a match, 1 for drift and 2 when it cannot generate or read a file.

## Verify the lab

Run this article's test group at the repository root.

```sh
python3 tools/test_engineering_articles.py FixtureTests -v
```

[Full article](article/ARTICLE.en.md) · [Practical example](examples/README.en.md) · [LinkedIn article](article/ARTICLE_LINKEDIN.en.md) · [Announcement post](article/POST_LINKEDIN.en.md)

---

Developed with ❤️ by [Pathbit](https://www.pathbit.com.br/)
