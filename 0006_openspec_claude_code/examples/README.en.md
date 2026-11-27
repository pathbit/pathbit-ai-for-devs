# Practical example — Evolve the news aggregator with OpenSpec and Claude Code

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

[Quick start](../README.en.md)

Follow the quick start first. Run the commands in the same lab terminals and use only the disposable data for this exercise.

```bash
curl -is http://127.0.0.1:19806/favoritos
curl -is http://127.0.0.1:19806/favoritos/export.csv
```

Once the app is running, execute `python3 0006_openspec_claude_code/examples/verify_export.py` from this repository. Mark tasks after testing and archive the change from the lab application.

- [proposal](openspec/changes/export-favorites-csv/proposal.md)
- [delta](openspec/changes/export-favorites-csv/specs/favorites/spec.md)
- [HTTP verifier](verify_export.py)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
