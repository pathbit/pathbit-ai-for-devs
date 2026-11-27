# Plan a compatible change with Claude Code Plan Mode

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

An authenticated Claude Code CLI, Git, and Python 3.10 or newer.

## Quick start

In `examples`, run `python3 -m unittest discover -s tests -v` before planning. Ask for `weekly_filename(day)` with an ISO week year. Use `date(2021, 1, 1)` as the acceptance case. The expected file name is `orders-2020-W53.csv`, because that date belongs to the last ISO week of 2020.

Check that the plan calls `date.isocalendar()` for both the year and the week. After reviewing and implementing it, inspect `git diff -- src tests` and rerun the test suite. The new assertion should cover the year boundary alongside the unchanged daily and hourly cases.

- [Read the complete article](article/ARTICLE.en.md)
- [Practical example and prompt (PT-BR)](examples/README.md)
- [LinkedIn article](article/ARTICLE_LINKEDIN.en.md)
- [LinkedIn post](article/POST_LINKEDIN.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
