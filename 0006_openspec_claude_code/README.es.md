# Evoluciona el agregador con OpenSpec y Claude Code

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Node.js 22.20+, npm, Git y Python 3.10+. Usa Claude Code autenticado para implementar con el agente o los archivos de referencia para el laboratorio local.

## Inicio rápido

Ejecuta el primer bloque desde la raíz hasta validar OpenSpec.

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

Usa la referencia o implementa con Claude Code. Si usas el agente, omite las dos líneas que copian archivos de referencia.

```bash
cp "$repo/0006_openspec_claude_code/examples/reference/favoritesCsv.js" src/services/
cp "$repo/0006_openspec_claude_code/examples/reference/favoritos.js" src/routes/
export HOST=127.0.0.1 PORT=19806 DATABASE_PATH="$PWD/data/lab.sqlite"
node "$repo/tools/seed_aggregator_lab.mjs"
npm start
```

Con la aplicación activa, ejecuta `python3 0006_openspec_claude_code/examples/verify_export.py` desde este repositorio. Marca las tareas tras probar y archiva el cambio desde la copia del laboratorio.

Resultado esperado: validación estructural, contrato CSV comprobado por HTTP y requisito incorporado a la especificación vigente.

## Archivos del módulo

- [Artículo completo](article/ARTICLE.es.md)
- [Ejemplo práctico](examples/README.es.md)
- [Artículo para LinkedIn](article/ARTICLE_LINKEDIN.es.md)
- [Publicación para LinkedIn](article/POST_LINKEDIN.es.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
