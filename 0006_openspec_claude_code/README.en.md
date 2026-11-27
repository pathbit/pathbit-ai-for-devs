# Evolve the news aggregator with OpenSpec and Claude Code

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Node.js 22.20+, npm, Git, and Python 3.10+. Use an authenticated Claude Code session for the agent path or the supplied implementation for the local lab.

## Quick start

Run the first block from the repository root through OpenSpec validation.

```bash
repo="$PWD"
lab=$(mktemp -d)
python3 tools/prepare_aggregator_lab.py "$lab/app"
cd "$lab/app"
npm ci
npm test
export OPENSPEC_TELEMETRY=0
npx -y @fission-ai/openspec@2.2.0 init --tools claude --scope project .
cp -R "$repo/0006_openspec_claude_code/examples/openspec/." openspec/
npx -y @fission-ai/openspec@2.2.0 validate export-favorites-csv --strict
```

Choose the reference path or implement with Claude Code. If you use the agent, skip the two reference-file copy lines.

```bash
cp "$repo/0006_openspec_claude_code/examples/reference/favoritesCsv.js" src/services/
cp "$repo/0006_openspec_claude_code/examples/reference/favoritos.js" src/routes/
export HOST=127.0.0.1 PORT=19806 DATABASE_PATH="$PWD/data/lab.sqlite"
node "$repo/tools/seed_aggregator_lab.mjs"
npm start
```

Once the app is running, execute `python3 0006_openspec_claude_code/examples/verify_export.py` from this repository. Mark tasks after testing and archive the change from the lab application.

Expected outcome: structural validation passes, the CSV contract holds over HTTP, and the archived change updates the current favorites specification.

## Module files

- [Full article](article/ARTICLE.en.md)
- [Practical example](examples/README.en.md)
- [LinkedIn article](article/ARTICLE_LINKEDIN.en.md)
- [LinkedIn post](article/POST_LINKEDIN.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
