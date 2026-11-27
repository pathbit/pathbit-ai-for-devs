# Edit a small Python project with Aider and Ollama

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Ollama, Aider, Git, Python 3.10 or newer, and space for the model.

## Quick start

Copy `examples` to a disposable Git repository and commit `src` and `tests` as a baseline. Start Ollama and run `ollama pull qwen2.5-coder:7b`. Run `aider --model ollama_chat/qwen2.5-coder:7b --no-auto-commits --no-dirty-commits --no-analytics --no-check-update src/durations.py tests/test_durations.py` with the loopback variable set.

Ask for `ValueError` for negative hours or minutes outside `0` to `59`. Cover `59` and `60`, and preserve the existing conversion. Review `git diff` and rerun `python3 -m unittest discover -s tests -v`. On a machine with less memory, use the `3b` tag in both commands and keep the task small.

- [Read the complete article](article/ARTICLE.en.md)
- [Practical example and prompt (PT-BR)](examples/README.md)
- [LinkedIn article](article/ARTICLE_LINKEDIN.en.md)
- [LinkedIn post](article/POST_LINKEDIN.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
