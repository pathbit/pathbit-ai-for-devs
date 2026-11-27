# Playwright MCP para verificar uma página local

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Conecte o Playwright ao VS Code e peça ao assistente para observar duas interações de um formulário de frete servido no seu computador.

## Estrutura do módulo

- [Artigo completo](article/ARTICLE.md)
- [Artigo para LinkedIn](article/ARTICLE_LINKEDIN.md)
- [Post para LinkedIn](article/POST_LINKEDIN.md)
- [Exemplo prático e prompt](examples/README.md)

## Pré-requisitos

- [VS Code com GitHub Copilot configurado](https://code.visualstudio.com/docs/copilot/setup).
- Google Chrome, Node.js 20 ou superior com npm e Python 3.10 ou superior.

## Início rápido

Abra a pasta `examples` como raiz do workspace. Use o terminal dessa pasta para servir o exemplo.

```bash
python3 -m http.server 19890 --bind 127.0.0.1 --directory site
```

Abra a configuração `.vscode/mcp.json` e inicie o servidor `playwright` pelo controle do VS Code. Use o [prompt do exercício](examples/README.md) no chat com as ferramentas do MCP ativas. Encerre o servidor HTTP com `Ctrl+C` ao terminar.

Developed with ❤️ by [Pathbit](https://pathbit.co/)
