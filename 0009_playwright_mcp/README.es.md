# Comprueba un formulario local con Playwright MCP en VS Code

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

VS Code con Copilot, Google Chrome, Node.js 20 o posterior con npm y Python 3.10 o posterior.

## Inicio rápido

Abre `examples` y ejecuta `python3 -m http.server 19890 --bind 127.0.0.1 --directory site`. Inicia el servidor MCP en VS Code. Pide al asistente que visite solo `http://127.0.0.1:19890/`, escriba `123` en `CEP`, pulse `Calcular frete` y registre el estado. En la misma página, cambia el valor a `01001-000`, envía de nuevo y registra el nuevo texto.

El primer estado es `Informe um CEP com 8 dígitos.`. El segundo es `Frete simulado: R$ 12,00`. El ejercicio valida el formato y usa un importe fijo. Si falta un paso, solicita el estado observado en los dos envíos. Una comprobación habitual puede convertirse en una prueba Playwright con aserciones para ambos mensajes.

- [Lee el artículo completo](article/ARTICLE.es.md)
- [Ejemplo práctico y mensaje (PT-BR)](examples/README.md)
- [Artículo para LinkedIn](article/ARTICLE_LINKEDIN.es.md)
- [Publicación para LinkedIn](article/POST_LINKEDIN.es.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
