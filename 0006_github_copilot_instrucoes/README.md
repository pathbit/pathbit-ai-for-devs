# Instruções de projeto no GitHub Copilot

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Configure instruções gerais e regras específicas para testes Python. Use um caso de frete grátis para conferir o que entrou no contexto e validar a sugestão.

## Estrutura do módulo

- [Artigo completo](article/ARTICLE.md)
- [Artigo para LinkedIn](article/ARTICLE_LINKEDIN.md)
- [Post para LinkedIn](article/POST_LINKEDIN.md)
- [Exemplo prático e prompt](examples/README.md)

## Pré-requisitos

- [VS Code](https://code.visualstudio.com/download) e [GitHub Copilot configurado](https://code.visualstudio.com/docs/copilot/setup).
- Python 3.10 ou superior. O exemplo usa só a biblioteca padrão.

## Início rápido

Abra a pasta `examples` como raiz de um workspace no VS Code. No terminal desse workspace, confirme a base do laboratório.

```bash
python3 -m unittest discover -s tests -v
```

Anexe `tests/test_pricing.py` no chat e use o [roteiro do exercício](examples/README.md). Confira a proposta antes de aplicá-la e rode os testes de novo.

Developed with ❤️ by [Pathbit](https://pathbit.co/)
