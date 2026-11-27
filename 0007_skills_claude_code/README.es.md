# Crea Skills de proyecto en Claude Code para una aplicación existente

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Claude Code, identidad Git para el commit del laboratorio y Python 3.10+. Usa Node.js 22 si ejecutas el agregador.

## Inicio rápido

Ejecuta desde la raíz para copiar el proyecto e instalar la Skill en el laboratorio. Usa los dos mensajes del ejemplo.

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

Ejecuta `/planejar-mudanca` con una pregunta sobre el contador de la categoría y luego sobre los avisos de favoritos. Contrasta la respuesta con el código y revisa el estado de Git.

Resultado esperado: una propuesta con rutas y criterios para la funcionalidad nueva, y el reconocimiento de los avisos de favoritos existentes.

## Archivos del módulo

- [Artículo completo](article/ARTICLE.es.md)
- [Ejemplo práctico](examples/README.es.md)
- [Artículo para LinkedIn](article/ARTICLE_LINKEDIN.es.md)
- [Publicación para LinkedIn](article/POST_LINKEDIN.es.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
