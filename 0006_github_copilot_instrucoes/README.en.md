# Teach GitHub Copilot the conventions of your project

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

VS Code with GitHub Copilot configured and Python 3.10 or newer.

## Quick start

Open `examples` as the workspace root and attach `tests/test_pricing.py` to a fresh Copilot chat. Ask for the tests at and immediately below the free-shipping threshold. The patch should keep `src/pricing.py` intact. Run `python3 -m unittest discover -s tests -v` and check `10_000 → 0`, `9_999 → 750`, and the existing case at `5_000`.

Look for the instruction references or the customization diagnostics in your VS Code version. If the scoped file is missing, confirm the workspace and file context, then attach it manually to isolate a discovery problem. Keep the instructions short enough to review. The executed test provides evidence that the proposed change meets the contract.

- [Read the complete article](article/ARTICLE.en.md)
- [Practical example and prompt (PT-BR)](examples/README.md)
- [LinkedIn article](article/ARTICLE_LINKEDIN.en.md)
- [LinkedIn post](article/POST_LINKEDIN.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
