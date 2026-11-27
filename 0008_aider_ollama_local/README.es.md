# Edita un proyecto Python pequeño con Aider y Ollama

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Ollama, Aider, Git, Python 3.10 o posterior y espacio para el modelo.

## Inicio rápido

Copia `examples` a un repositorio Git descartable y crea un commit de base con `src` y `tests`. Inicia Ollama y ejecuta `ollama pull qwen2.5-coder:7b`. Ejecuta `aider --model ollama_chat/qwen2.5-coder:7b --no-auto-commits --no-dirty-commits --no-analytics --no-check-update src/durations.py tests/test_durations.py` con la variable de loopback configurada.

Pide `ValueError` para horas negativas o minutos fuera de `0` a `59`. Cubre `59` y `60` y conserva la conversión existente. Revisa `git diff` y vuelve a ejecutar `python3 -m unittest discover -s tests -v`. En un equipo con menos memoria, usa la etiqueta `3b` en los dos comandos y mantén la tarea acotada.

- [Lee el artículo completo](article/ARTICLE.es.md)
- [Ejemplo práctico y mensaje (PT-BR)](examples/README.md)
- [Artículo para LinkedIn](article/ARTICLE_LINKEDIN.es.md)
- [Publicación para LinkedIn](article/POST_LINKEDIN.es.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
