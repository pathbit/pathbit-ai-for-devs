# Cómo enseñar a GitHub Copilot las convenciones de tu proyecto

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

VS Code con GitHub Copilot configurado y Python 3.10 o posterior.

## Inicio rápido

Abre `examples` como raíz del espacio de trabajo y adjunta `tests/test_pricing.py` a un chat nuevo de Copilot. Pide pruebas para el umbral de envío gratuito y el valor inmediatamente anterior. El cambio debe conservar `src/pricing.py`. Ejecuta `python3 -m unittest discover -s tests -v` y comprueba `10_000 → 0`, `9_999 → 750` y el caso existente de `5_000`.

Busca las referencias de instrucciones o los diagnósticos de personalización de tu versión de VS Code. Si falta el archivo específico, comprueba la raíz y los archivos en contexto y luego adjúntalo manualmente. Mantén instrucciones fáciles de revisar y usa las pruebas para comprobar la propuesta.

- [Lee el artículo completo](article/ARTICLE.es.md)
- [Ejemplo práctico y mensaje (PT-BR)](examples/README.md)
- [Artículo para LinkedIn](article/ARTICLE_LINKEDIN.es.md)
- [Publicación para LinkedIn](article/POST_LINKEDIN.es.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
