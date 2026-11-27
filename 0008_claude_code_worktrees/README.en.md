# Use Claude Code and Git Worktrees for parallel changes

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Git 2.28+, Python 3.10+, Node.js 22, and an authenticated Claude Code session for the interactive path.

## Quick start

Create the base checkout, then use the commands and reference patches in the practical example.

```bash
repo="$PWD"
lab=$(mktemp -d)
python3 tools/prepare_aggregator_lab.py "$lab/app"
cd "$lab/app"
git init -b main
git add .
git commit -m 'Record aggregator baseline'
base=$(git rev-parse HEAD)
git worktree list
```

The example takes you from the baseline into two worktrees and a third integration checkout. `GET /health` returns the expected JSON and `/` serves the updated heading.

Expected outcome: two independent branches, the full integrated suite, a successful `/health` response, and the new heading from the same server.

## Module files

- [Full article](article/ARTICLE.en.md)
- [Practical example](examples/README.en.md)
- [LinkedIn article](article/ARTICLE_LINKEDIN.en.md)
- [LinkedIn post](article/POST_LINKEDIN.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
