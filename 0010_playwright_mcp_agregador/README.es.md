# Comprueba el dashboard real del agregador con Playwright MCP

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Node.js 22 con npm, Python 3.10+, Google Chrome y Claude Code para el flujo interactivo. El verificador directo funciona sin una sesión de modelo.

## Inicio rápido

Arranca la aplicación desde la raíz. Abre Claude Code en el laboratorio y usa el escenario. Ejecuta el verificador directo desde la raíz de la serie mientras la aplicación esté activa.

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

Ejecuta `python3 0010_playwright_mcp_agregador/examples/verify_dashboard.py` desde este repositorio con la aplicación activa. La comprobación abre el dashboard, busca, marca, recarga y quita el favorito.

Resultado esperado: filtro aplicado, favorito guardado, persistencia tras recargar y eliminación que conserva el favorito de control.

## Archivos del módulo

- [Artículo completo](article/ARTICLE.es.md)
- [Ejemplo práctico](examples/README.es.md)
- [Artículo para LinkedIn](article/ARTICLE_LINKEDIN.es.md)
- [Publicación para LinkedIn](article/POST_LINKEDIN.es.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
