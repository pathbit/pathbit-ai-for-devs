# Ejemplo práctico — Trabaja en paralelo con Claude Code y Git Worktrees

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

[Inicio rápido](../README.es.md)

Sigue primero el inicio rápido. Ejecuta los comandos en las terminales del laboratorio y usa solo los datos descartables del ejercicio.

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

El ejemplo parte del commit base, crea dos worktrees y un directorio de integración. `GET /health` devuelve el JSON esperado y `/` sirve el nuevo título.

- [Health patch](health.patch)
- [Dashboard patch](dashboard.patch)
- [Prompts (PT-BR)](prompts.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
