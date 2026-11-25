# Como conferir o escopo de um patch feito por agente

**Português (Brasil)** · [English](ARTICLE_LINKEDIN.en.md) · [Español](ARTICLE_LINKEDIN.es.md)

![Índice, pasta de trabalho e arquivos novos convergem para uma decisão pela política de caminhos](../assets/00_cover_revisao_git.png)

O agente corrigiu a busca e os testes passaram. O patch também mexeu em um arquivo que a tarefa pedia preservar?

## Pré-requisitos

Python e, no artigo 0007, Git. Consulte os [pré-requisitos e downloads](../README.md#pré-requisitos).

Uma política de caminhos torna essa pergunta verificável. No laboratório, a tarefa autoriza mudanças em `src/`, `tests/` e `README.md`, com exceções explícitas para código gerado e workflows. O script consulta o índice, as mudanças locais e os arquivos novos. Uma renomeação é lida como dois caminhos, origem e destino.

## O que o laboratório mostra

O caso permitido cria `src/app.py`. Em seguida o laboratório acrescenta um arquivo fictício sob `.github/workflows/` e observa uma violação `protected`. O script exibe as duas decisões em JSON sem alterar o checkout que contém os artigos.

Mantenha a política aprovada fora do alcance de edição da tarefa. Use o resultado para orientar a revisão de diff e rode os testes de comportamento antes de promover o patch.

## Show-Me-The-Code

### Opção 1. Confira o guia de execução

[Guia de execução](../README.md)

### Opção 2. Reproduza no cenário isolado

[Exemplo prático](../examples/README.md)

[Artigo completo](ARTICLE.md)
