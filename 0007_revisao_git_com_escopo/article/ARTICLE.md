# Revisão Git com escopo verificável

**Português (Brasil)** · [English](ARTICLE.en.md) · [Español](ARTICLE.es.md)

![Índice, pasta de trabalho e arquivos novos convergem para uma decisão pela política de caminhos](../assets/00_cover_revisao_git.png)

O [gate de aceite do artigo 0006](../../0006_gate_de_release_de_contratos/article/ARTICLE.md) mede o comportamento que a aplicação entrega. Antes de executá-lo em um patch feito por um agente, eu quero responder outra pergunta. Os arquivos alterados correspondem ao combinado? Um pequeno ajuste na busca pode ter testes verdes e ainda incluir alterações em um workflow de publicação ou em código gerado.

## Pré-requisitos

- [Python 3.10 ou posterior](https://www.python.org/downloads/). A versão recomendada para o laboratório é o [Python 3.14.7](https://www.python.org/downloads/release/python-3147/), com instaladores para cada sistema.
- [Git 2.28 ou posterior](https://git-scm.com/downloads) disponível no terminal. Confira com `git --version`.
- Ambiente virtual opcional. Veja [como preparar](../README.md#pré-requisitos).

## Transforme o escopo em uma regra revisável

No pedido ao agente, descreva o resultado e a fronteira da tarefa. Para uma correção de checkout, comece por `src/`, `tests/` e o `README.md`. A exceção `src/generated/` continua protegida, mesmo dentro de uma pasta permitida. A pessoa que aprova o escopo mantém a política fora do checkout editável. O [arquivo de exemplo](../examples/scope.json.example) mostra os dois campos usados pelo verificador.

Um item com barra final é prefixo de diretório. Assim, `src/` entra em `src/cart.py`, enquanto `src-other/cart.py` exige revisão. Um caminho sem barra final, como `README.md`, exige igualdade completa. As regras respeitam a grafia e as maiúsculas do caminho como aparece no Git. A lista `protect` tem precedência sobre `allow`.

## Consulte as três fontes do Git

| Fonte | O que pode aparecer |
| --- | --- |
| `git diff --cached --name-status -z` | O conteúdo preparado no índice desde o commit atual. |
| `git diff --name-status -z` | O conteúdo modificado na árvore de trabalho desde o índice. |
| `git ls-files --others --exclude-standard -z` | Arquivos novos que o Git mostra segundo suas regras de ignore. |

Ler índice e árvore de trabalho separadamente mantém visível um arquivo que foi preparado e depois editado novamente. O separador NUL permite ler nomes com acentos, espaços ou quebras de linha. Em um renomeio, o verificador avalia a origem e o destino. Assim, mover `settings.yml` para `src/settings.yml` continua sinalizando a origem fora da área combinada. [Opções de git diff](https://git-scm.com/docs/git-diff) · [Opções de git ls-files](https://git-scm.com/docs/git-ls-files).

## Decida com base no relatório

O código 0 indica que os caminhos observados passam pela política. O código 1 indica pelo menos uma violação e o JSON aponta o caminho, a fonte e o motivo. O código 2 indica que a verificação não conseguiu rodar, por exemplo por um JSON inválido ou por ausência do Git. Faça a automação bloquear 1 e 2 e use o motivo para encaminhar a revisão.

Execute no checkout dedicado à tarefa. Arquivos ignorados ficam fora da lista de novos e submódulos aparecem como entradas do repositório pai. Para revisar commits já produzidos ou conteúdo de submódulos, confira também o intervalo e o repositório correspondentes. O resultado de escopo complementa a leitura do diff, os testes e o gate de aceite.

## Show-Me-The-Code

### Opção 1. Rode no checkout da tarefa

O [guia do módulo](../README.md) apresenta o comando e os testes. Revise a política e execute a CLI usando a raiz do checkout que contém o trabalho.

### Opção 2. Rode o cenário isolado

O [laboratório](../examples/README.md) monta uma árvore temporária e mostra a diferença entre uma alteração aprovada e uma em arquivo protegido.

## Acompanhe o próximo passo

Depois de conferir os caminhos, estabilize os dados usados para provar o comportamento. Continue com [fixtures reproduzíveis](../../0008_fixtures_reproduziveis/article/ARTICLE.md).
