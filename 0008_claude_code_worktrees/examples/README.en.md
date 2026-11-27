# Practical example — Use Claude Code and Git Worktrees for parallel changes

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

[Quick start](../README.en.md)

Follow the quick start first. Run the commands in the same lab terminals and use only the disposable data for this exercise.

```bash
git worktree add -b lab/api-health ../api-health "$base"
git worktree add -b lab/dashboard-title ../dashboard-title "$base"
git worktree list
```

```bash
git -C ../api-health apply "$repo/0008_claude_code_worktrees/examples/health.patch"
git -C ../dashboard-title apply "$repo/0008_claude_code_worktrees/examples/dashboard.patch"
git -C ../api-health diff --stat
git -C ../dashboard-title diff --stat
git -C ../api-health add src/server.js tests/artigos.test.js
git -C ../api-health commit -m 'Add process health endpoint'
git -C ../dashboard-title add src/public/index.html
git -C ../dashboard-title commit -m 'Update the dashboard title'
```

```bash
git worktree add -b lab/integracao ../integracao "$base"
git -C ../integracao cherry-pick lab/api-health lab/dashboard-title
cd ../integracao
npm ci
npm test
HOST=127.0.0.1 PORT=19808 DATABASE_PATH="$PWD/data/lab.sqlite" npm start
```

The example takes you from the baseline into two worktrees and a third integration checkout. `GET /health` returns the expected JSON and `/` serves the updated heading.

- [Health patch](health.patch)
- [Dashboard patch](dashboard.patch)
- [Prompts (PT-BR)](prompts.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
