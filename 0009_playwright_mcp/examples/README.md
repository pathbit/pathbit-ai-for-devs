# Exercício de playwright MCP para verificar uma página local

Inicie o [laboratório](../README.md) e confirme que o VS Code encontra [mcp.json](.vscode/mcp.json). A aplicação é uma [página local](site/index.html) com dados fictícios.

## Prompt para o chat

```text
Use apenas o Playwright MCP e esta página: http://127.0.0.1:19890/
Identifique o campo CEP e o botão Calcular frete pelo nome acessível.

Digite 123, envie o formulário e registre a mensagem observada.

Na mesma página, substitua por 01001-000, envie novamente e registre
o novo texto. Informe o resultado de cada etapa sem editar arquivos.

```

A primeira mensagem é `Informe um CEP com 8 dígitos.`. A segunda é `Frete simulado: R$ 12,00`. Se só houver relato da última etapa, peça evidência da primeira ou reproduza as duas interações no navegador.
