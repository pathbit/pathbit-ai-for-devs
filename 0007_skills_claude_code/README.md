# Skills de projeto no Claude Code

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Versione um fluxo de descoberta de rotas, proposta e critérios de aceite. Rode a mesma Skill para uma função nova e para outra que o dashboard já oferece.

## Início rápido

### Pré-requisitos

- Claude Code autenticado, Git e Python 3.10+.
- Node.js 22 para executar a suíte do Agregador quando quiser verificar uma implementação.

### Instale a Skill na cópia do projeto

Execute a partir da raiz deste repositório.

```bash
repo="$PWD"
lab=$(mktemp -d)
python3 tools/prepare_aggregator_lab.py "$lab/app"
cd "$lab/app"
mkdir -p .claude/skills
cp -R "$repo/0007_skills_claude_code/examples/.claude/skills/planejar-mudanca" .claude/skills/
git init -b main
git add .
git commit -m 'Record aggregator and planning skill baseline'
git status --short
claude --permission-mode plan
```

Use o [roteiro com dois pedidos](examples/prompts.md). Confira a rota, os arquivos citados e os critérios de aceite. Compare com o código e confirme que `git status --short` permanece limpo depois de sair. Para realizar a mudança, coloque a proposta aprovada no fluxo de especificação adotado pelo projeto.

## Material do módulo

- [Artigo completo](article/ARTICLE.md)
- [Arquivos e roteiro do exercício](examples/README.md)
- [Artigo para LinkedIn](article/ARTICLE_LINKEDIN.md)
- [Post para LinkedIn](article/POST_LINKEDIN.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
