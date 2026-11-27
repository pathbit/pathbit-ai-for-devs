# OpenSpec e Claude Code no Agregador

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Acrescente a exportação CSV ao aplicativo do artigo 0005. Separe a especificação vigente da mudança, implemente em uma cópia e arquive o requisito depois de conferir a resposta HTTP.

## Início rápido

### Pré-requisitos

- Node.js 22.20+ com npm, Python 3.10+ e Git.
- Claude Code autenticado para conduzir a mudança com o agente. Os arquivos de referência permitem executar e verificar a API sem essa sessão.

### Prepare a aplicação e a change

Na raiz deste repositório, execute em Bash ou zsh. Use o mesmo terminal até iniciar o servidor. As pastas de aplicação e banco ficam fora do clone.

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

### Aplique e verifique

Revise `openspec/changes/export-favorites-csv/`. Para implementar com o agente, abra `claude` nessa pasta e use `/openspec-apply-change export-favorites-csv`. Para reproduzir com a solução de referência, execute as duas linhas de cópia.

```bash
cp "$repo/0006_openspec_claude_code/examples/reference/favoritesCsv.js" src/services/
cp "$repo/0006_openspec_claude_code/examples/reference/favoritos.js" src/routes/
export HOST=127.0.0.1 PORT=19806 DATABASE_PATH="$PWD/data/lab.sqlite"
node "$repo/tools/seed_aggregator_lab.mjs"
npm start
```

Se implementou com o agente, prossiga a partir de `export` e mantenha o seu patch. Em outro terminal na raiz do repositório, execute `python3 0006_openspec_claude_code/examples/verify_export.py`. O script verifica o download, as aspas, o filtro e a lista vazia. Ele desfaz a remoção do favorito no banco descartável. Depois de conferir a aplicação, execute `npm test` na cópia. Marque as tarefas concluídas em `tasks.md` e rode `npx -y @fission-ai/openspec@2.2.0 archive export-favorites-csv` para incorporar o requisito à spec vigente.

## Material do módulo

- [Artigo completo](article/ARTICLE.md)
- [Arquivos e roteiro do exercício](examples/README.md)
- [Artigo para LinkedIn](article/ARTICLE_LINKEDIN.md)
- [Post para LinkedIn](article/POST_LINKEDIN.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
