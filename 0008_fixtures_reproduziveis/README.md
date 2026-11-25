# Fixtures reproduzíveis para testes de integração

**Português (Brasil)** · [English](README.en.md) · [Español](README.es.md)

Gere uma amostra estável de pedidos a partir de dados sintéticos. O laboratório fixa o horário, calcula valores por ID e compara a saída com um arquivo esperado versionado.

## Pré-requisitos

- [Python 3.10 ou posterior](https://www.python.org/downloads/). A versão recomendada para o laboratório é o [Python 3.14.7](https://www.python.org/downloads/release/python-3147/), com instaladores para cada sistema.

Os scripts usam apenas a biblioteca padrão do Python. Se preferir um ambiente isolado, crie-o na raiz do repositório.

```sh
python3 -m venv .venv
. .venv/bin/activate
```

No Windows, use PowerShell. Depois de ativar o ambiente, use `python` no lugar de `python3` nos comandos abaixo.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Começo rápido

Na raiz do repositório, execute o modo de comparação. Ele lê o arquivo de entrada e o esperado sem gravar em nenhum deles.

```sh
python3 0008_fixtures_reproduziveis/src/build_fixture.py 0008_fixtures_reproduziveis/examples/orders.json.example --check 0008_fixtures_reproduziveis/examples/orders.expected.json
```

A mensagem `Fixture matches` indica que a saída bate byte a byte com o esperado. A CLI retorna 0 na comparação aprovada, 1 quando a saída difere e 2 quando não consegue gerar ou ler os arquivos.

## Verificar o laboratório

Rode o grupo de testes deste artigo na raiz do repositório.

```sh
python3 tools/test_engineering_articles.py FixtureTests -v
```

[Artigo completo](article/ARTICLE.md) · [Exemplo prático](examples/README.md) · [Artigo para LinkedIn](article/ARTICLE_LINKEDIN.md) · [Post de divulgação](article/POST_LINKEDIN.md)

---

Developed with ❤️ by [Pathbit](https://www.pathbit.com.br/)
