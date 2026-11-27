# Trabaja en paralelo con Claude Code y Git Worktrees

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Git 2.28+, Python 3.10+, Node.js 22 y Claude Code autenticado para el camino interactivo.

## Inicio rápido

Crea la copia base y usa los comandos y parches de referencia del ejemplo práctico.

```bash
repo="$PWD"
lab=$(mktemp -d)
python3 tools/prepare_aggregator_lab.py "$lab/app"
cd "$lab/app"
git init -b main
git add .
git commit -m 'Record aggregator baseline'
base=$(git rev-parse HEAD)
git worktree list
```

El ejemplo parte del commit base, crea dos worktrees y un directorio de integración. `GET /health` devuelve el JSON esperado y `/` sirve el nuevo título.

Resultado esperado: dos ramas independientes, las pruebas integradas, una respuesta de `/health` y el nuevo título desde el mismo servidor.

## Archivos del módulo

- [Artículo completo](article/ARTICLE.es.md)
- [Ejemplo práctico](examples/README.es.md)
- [Artículo para LinkedIn](article/ARTICLE_LINKEDIN.es.md)
- [Publicación para LinkedIn](article/POST_LINKEDIN.es.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
