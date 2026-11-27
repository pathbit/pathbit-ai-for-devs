# Plan Mode no Claude Code

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Planeje uma mudança em nomes de arquivos de exportação. O exercício usa um caso de virada de ano para distinguir ano civil de ano da semana ISO.

## Estrutura do módulo

- [Artigo completo](article/ARTICLE.md)
- [Artigo para LinkedIn](article/ARTICLE_LINKEDIN.md)
- [Post para LinkedIn](article/POST_LINKEDIN.md)
- [Exemplo prático e prompt](examples/README.md)

## Pré-requisitos

- [Claude Code com sessão autenticada](https://code.claude.com/docs/en/quickstart).
- Git e Python 3.10 ou superior.

## Início rápido

Entre em `examples`. Use uma cópia do exemplo em um repositório descartável se quiser examinar o diff sem alterar o clone deste catálogo.

```bash
python3 -m unittest discover -s tests -v
claude --permission-mode plan
```

Use o [pedido do laboratório](examples/README.md), confira o plano e só então escolha como implementar. Rode novamente a suíte após revisar o diff.

Developed with ❤️ by [Pathbit](https://pathbit.co/)
