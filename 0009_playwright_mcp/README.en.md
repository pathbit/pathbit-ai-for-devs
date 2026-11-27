# Verify a local form with Playwright MCP in VS Code

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

VS Code with Copilot, Google Chrome, Node.js 20 or newer with npm, and Python 3.10 or newer.

## Quick start

Open `examples` and run `python3 -m http.server 19890 --bind 127.0.0.1 --directory site`. Start the MCP server from VS Code. Ask the assistant to go only to `http://127.0.0.1:19890/`, type `123` into `CEP`, click `Calcular frete`, and report the status. On the same page, replace it with `01001-000`, submit, and report the new value.

The first status is `Informe um CEP com 8 dígitos.`. The second is `Frete simulado: R$ 12,00`. The exercise validates format and uses a fixed shipping amount. If the result misses a step, request the observed status for both submissions. A recurring check can become a Playwright test with assertions for both messages.

- [Read the complete article](article/ARTICLE.en.md)
- [Practical example and prompt (PT-BR)](examples/README.md)
- [LinkedIn article](article/ARTICLE_LINKEDIN.en.md)
- [LinkedIn post](article/POST_LINKEDIN.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
