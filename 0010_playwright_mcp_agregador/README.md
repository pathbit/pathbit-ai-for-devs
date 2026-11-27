# Playwright MCP no dashboard do Agregador

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Conecte o servidor MCP ao Claude Code e reproduza busca, favoritos, persistência após recarregar e remoção na interface do artigo 0005.

## Início rápido

### Pré-requisitos

- Node.js 22 com npm, Python 3.10+ e Google Chrome.
- Claude Code autenticado para conduzir o roteiro pelo chat. O verificador direto usa o mesmo servidor MCP sem sessão de modelo.

### Suba o Agregador original com uma base de laboratório

Na raiz do repositório, execute:

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

Em outro terminal, abra `claude` na pasta `$lab/app` indicada no primeiro terminal. Revise e aprove a integração MCP do projeto. Use o [roteiro](examples/scenario.md) para interagir com `http://127.0.0.1:19810/`. Para repetir o percurso com o cliente direto, rode `python3 0010_playwright_mcp_agregador/examples/verify_dashboard.py` na raiz deste repositório enquanto o servidor está rodando. O resultado esperado é o artigo favoritado, persistido após recarregar e removido, mantendo o favorito de controle.

## Material do módulo

- [Artigo completo](article/ARTICLE.md)
- [Arquivos e roteiro do exercício](examples/README.md)
- [Artigo para LinkedIn](article/ARTICLE_LINKEDIN.md)
- [Post para LinkedIn](article/POST_LINKEDIN.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
