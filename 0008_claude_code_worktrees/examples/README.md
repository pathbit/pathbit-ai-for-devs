# Duas branches do Agregador e um checkout de integração

Siga o [início rápido](../README.md) até criar o commit de base da aplicação. Execute em Bash ou zsh no checkout de base da cópia. `$repo` aponta para o repositório da série e `$base` para o commit inicial do laboratório.

## Crie as duas worktrees

```bash
git worktree add -b lab/api-health ../api-health "$base"
git worktree add -b lab/dashboard-title ../dashboard-title "$base"
git worktree list
```

Em cada diretório, abra o Claude Code com o [pedido correspondente](prompts.md), ou aplique o patch de referência. Revise o arquivo alterado antes de registrar o commit. Use seu nome e e-mail de Git habituais.

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

## Confira o conjunto em uma terceira worktree

```bash
git worktree add -b lab/integracao ../integracao "$base"
git -C ../integracao cherry-pick lab/api-health lab/dashboard-title
cd ../integracao
npm ci
npm test
HOST=127.0.0.1 PORT=19808 DATABASE_PATH="$PWD/data/lab.sqlite" npm start
```

Em outro terminal, `curl -fsS http://127.0.0.1:19808/health` deve retornar `{"status":"ok"}`. Confira que `curl -fsS http://127.0.0.1:19808/` contém `Meu Agregador de Notícias`. Os resultados das duas branches aparecem no mesmo processo.
