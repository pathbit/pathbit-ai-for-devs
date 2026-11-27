# Verify the real aggregator dashboard with Playwright MCP

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Node.js 22 with npm, Python 3.10+, Google Chrome, and Claude Code for the interactive path. The direct verifier can run without a model session.

## Quick start

Start the app from the repository root. In the laboratory directory, open Claude Code and use the scenario. Run the direct verifier from the series repository while the app is running.

```bash
repo="$PWD"
lab=$(mktemp -d)
python3 tools/prepare_aggregator_lab.py "$lab/app"
cd "$lab/app"
npm ci
cp "$repo/0010_playwright_mcp_agregador/examples/.mcp.json" .mcp.json
export HOST=127.0.0.1 PORT=19810 DATABASE_PATH="$PWD/data/lab.sqlite"
node "$repo/tools/seed_aggregator_lab.mjs"
npm start
```

Run `python3 0010_playwright_mcp_agregador/examples/verify_dashboard.py` from this repository while the app is running. The direct check opens the dashboard, searches, favorites, reloads, and removes the target.

Expected outcome: search narrowed the grid, favoriting changed the server list, a reload preserved the target, and removal kept the control favorite.

## Module files

- [Full article](article/ARTICLE.en.md)
- [Practical example](examples/README.en.md)
- [LinkedIn article](article/ARTICLE_LINKEDIN.en.md)
- [LinkedIn post](article/POST_LINKEDIN.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
