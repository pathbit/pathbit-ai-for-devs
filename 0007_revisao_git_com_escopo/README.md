# Revisão Git com escopo verificável

**Português (Brasil)** · [English](README.en.md) · [Español](README.es.md)

Use uma lista versionada de caminhos para revisar alterações feitas por agentes de código. O laboratório lê o índice, a árvore de trabalho e os arquivos novos do Git e mostra quais mudanças exigem revisão humana.

## Pré-requisitos

- [Python 3.10 ou posterior](https://www.python.org/downloads/). A versão recomendada para o laboratório é o [Python 3.14.7](https://www.python.org/downloads/release/python-3147/), com instaladores para cada sistema.
- [Git 2.28 ou posterior](https://git-scm.com/downloads) disponível no terminal. Confira com `git --version`.

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

Na raiz do repositório, rode o laboratório. Ele cria uma cópia temporária independente, prepara uma mudança permitida e acrescenta um arquivo protegido.

```sh
python3 0007_revisao_git_com_escopo/examples/run_sandbox.py
```

A saída contém `allowed.ok: true` para a mudança em `src/app.py`. A segunda rodada contém `blocked.ok: false` e a violação `protected` em `.github/workflows/check.yml`. O laboratório retorna 0 quando comprova os dois resultados; cada chamada ao verificador usa 0 para escopo aprovado, 1 para violação e 2 para erro de execução.

## Verificar o laboratório

Rode o grupo de testes deste artigo na raiz do repositório.

```sh
python3 tools/test_engineering_articles.py GitScopeTests -v
```

[Artigo completo](article/ARTICLE.md) · [Exemplo prático](examples/README.md) · [Artigo para LinkedIn](article/ARTICLE_LINKEDIN.md) · [Post de divulgação](article/POST_LINKEDIN.md)

---

Developed with ❤️ by [Pathbit](https://www.pathbit.com.br/)
