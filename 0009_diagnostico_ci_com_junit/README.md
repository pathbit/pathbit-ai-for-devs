# Diagnóstico de CI com relatórios JUnit

**Português (Brasil)** · [English](README.en.md) · [Español](README.es.md)

Reúna a evidência dos jobs obrigatórios e separe testes aprovados, falhas registradas e resultados inconclusivos. O laboratório resume XMLs locais em JSON sem depender de um servidor de CI.

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

Na raiz do repositório, rode o conjunto em que as duas suítes obrigatórias concluíram com sucesso.

```sh
python3 0009_diagnostico_ci_com_junit/src/diagnose_reports.py --reports 0009_diagnostico_ci_com_junit/examples/passed --jobs api storage
```

A saída traz `status: passed`, dois testes aprovados em `api` e um em `storage`. No exemplo com falha, a CLI retorna 1. Quando a evidência não basta, retorna 2.

## Verificar o laboratório

Rode o grupo de testes deste artigo na raiz do repositório.

```sh
python3 tools/test_engineering_articles.py CiReportsTests -v
```

[Artigo completo](article/ARTICLE.md) · [Exemplo prático](examples/README.md) · [Artigo para LinkedIn](article/ARTICLE_LINKEDIN.md) · [Post de divulgação](article/POST_LINKEDIN.md)

---

Developed with ❤️ by [Pathbit](https://www.pathbit.com.br/)
