# Enruta OpenCode por 9Router y un modelo local en Ollama

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

OpenCode 2.4.x y Python 3.10+. Usa tu instancia de 9Router y un modelo local en Ollama para la etapa opcional con servicios reales.

## Inicio rápido

Inicia la sonda desde la raíz y deja el proceso activo.

```bash
python3 0009_opencode_9router_ollama/examples/probe_server.py --port 19809
```

Abre otra terminal en la raíz y ejecuta los comandos del cliente.

```bash
lab=$(mktemp -d)
cp 0009_opencode_9router_ollama/examples/opencode.json.example "$lab/opencode.json"
cd "$lab"
export PATHBIT_ROUTER_BASE=http://127.0.0.1:19809/router/v1
export PATHBIT_ROUTER_KEY=lab-only
export PATHBIT_OLLAMA_BASE=http://127.0.0.1:19809/local/v1
opencode --standalone run --model router/pathbit-code 'Return only a route receipt.'
opencode --standalone run --model local/qwen2.5-coder:7b 'Return only a route receipt.'
```

La sonda usa una clave ficticia. Configura tu clave autorizada solo al cambiar a tu 9Router. Comprueba el modelo y usa la misma etiqueta de Ollama en el archivo y el comando.

Resultado esperado: los dos recibos y dos rutas OpenAI-compatibles distintas en la salida de la sonda.

## Archivos del módulo

- [Artículo completo](article/ARTICLE.es.md)
- [Ejemplo práctico](examples/README.es.md)
- [Artículo para LinkedIn](article/ARTICLE_LINKEDIN.es.md)
- [Publicación para LinkedIn](article/POST_LINKEDIN.es.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
