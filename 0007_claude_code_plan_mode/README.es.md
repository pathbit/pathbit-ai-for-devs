# Planifica un cambio compatible con Plan Mode de Claude Code

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

CLI de Claude Code con sesión iniciada, Git y Python 3.10 o posterior.

## Inicio rápido

Desde `examples`, ejecuta `python3 -m unittest discover -s tests -v` antes de planificar. Pide `weekly_filename(day)` con año y semana ISO. El caso de aceptación es `date(2021, 1, 1)`. Debe producir `orders-2020-W53.csv`, porque esa fecha pertenece a la última semana ISO de 2020.

Comprueba que el plan obtiene tanto el año como la semana con `date.isocalendar()`. Tras revisar e implementar, inspecciona `git diff -- src tests` y vuelve a ejecutar las pruebas. El caso nuevo de cambio de año debe coexistir con los formatos diario y horario.

- [Lee el artículo completo](article/ARTICLE.es.md)
- [Ejemplo práctico y mensaje (PT-BR)](examples/README.md)
- [Artículo para LinkedIn](article/ARTICLE_LINKEDIN.es.md)
- [Publicación para LinkedIn](article/POST_LINKEDIN.es.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
