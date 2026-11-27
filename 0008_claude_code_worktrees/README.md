# Claude Code e Git Worktrees

Isole duas alterações do Agregador em branches e pastas diferentes. Integre os resultados no mesmo checkout e exercite os contratos reais da aplicação.

## Início rápido

### Pré-requisitos

- Git 2.28+, Python 3.10+ e Node.js 22 com npm.
- Claude Code autenticado para trabalhar nas sessões. O modo com patches reproduz o exercício localmente.

### Crie o repositório de demonstração

Na raiz deste repositório, execute:

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

Abra dois terminais na raiz dessa cópia. Use `claude --worktree api-health` no primeiro e `claude --worktree dashboard-title` no segundo, com os [dois pedidos](examples/prompts.md). Se quiser escolher os nomes de branch e aplicar os patches prontos, siga o [exercício com Git](examples/README.md).

Depois de rever e registrar cada mudança, crie uma terceira worktree a partir de `$base`. Aplique os dois commits nela e rode `npm ci` e `npm test`. Use `HOST=127.0.0.1 PORT=19808 DATABASE_PATH="$PWD/data/lab.sqlite" npm start` para conferir `/health` e `/`.

## Material do módulo

- [Artigo completo](article/ARTICLE.md)
- [Arquivos e roteiro do exercício](examples/README.md)
- [Artigo para LinkedIn](article/ARTICLE_LINKEDIN.md)
- [Post para LinkedIn](article/POST_LINKEDIN.md)
- [Figuras e roteiro do exercício](assets/figuras.md)

Developed with ❤️ by [Pathbit](https://www.pathbit.com.br/)
