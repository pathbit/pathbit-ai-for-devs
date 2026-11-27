# Roteiro observável de busca e favoritos

Suba o dashboard pelo [guia](../README.md). Copie [`.mcp.json`](.mcp.json) na raiz da aplicação descartável para o cliente Claude Code. O mesmo arquivo alimenta o [verificador direto](verify_dashboard.py).

## Execute o fluxo

Use o [roteiro do agente](scenario.md). Valide a lista de cartões em `#articlesGrid`, separada do digest. O digest pode continuar exibindo títulos que deixaram a grade depois de uma busca. Registre o filtro antes e depois de recarregar.

O script pode ser executado a partir da raiz deste repositório enquanto o Agregador está ouvindo na porta de demonstração.

```bash
python3 0010_playwright_mcp_agregador/examples/verify_dashboard.py
```

A saída esperada confirma, em ordem, o filtro de busca, a gravação de favoritos, a persistência após recarregar e a remoção. Se uma execução parou após marcar o favorito, use uma nova cópia e semeie uma base nova para repetir o roteiro completo.
