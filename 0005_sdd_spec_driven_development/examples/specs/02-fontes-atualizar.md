# Spec 02: Gerenciar fontes e atualizar

> Convenções permanentes do projeto: ver `../CLAUDE.md.example`. Esta spec contém apenas o que é deste incremento.

## Objetivo

Permitir cadastrar várias fontes de notícias e atualizar todas de uma vez, com validação.

## Contexto

Ciclo 2: parte do estado deixado pelo Ciclo 1. Já existe importação de um feed e listagem de artigos; este incremento introduz o conceito de fonte persistente e a atualização em lote.

## Requisitos funcionais

1. Gerenciar fontes: adicionar, listar e remover feeds cadastrados.
2. Validar ao adicionar: URL bem formada e que responde como RSS válido; URL duplicada é rejeitada.
3. Atualizar: buscar artigos novos de todas as fontes cadastradas de uma vez.

## Requisitos não-funcionais

- Validação: URL inválida ou que não responde como RSS retorna HTTP 422 com mensagem clara; fonte inexistente retorna 404.
- Resiliência: uma fonte fora do ar não derruba a atualização das demais.
- Respostas em JSON; datas no formato ISO `YYYY-MM-DD`.

## Modelo de dados

Tabela `fonte`:

- `id` (inteiro, automático)
- `nome` (texto, pode vir do título do feed)
- `url` (texto, único)

Alteração em `artigo`: associar `fonte_id` ao artigo importado.

## Contrato de API

- `POST /fontes`: recebe `{ url }`; valida, resolve o nome pelo feed e salva; retorna 201 com a fonte.
- `GET /fontes`: lista as fontes.
- `DELETE /fontes/:id`: remove a fonte; 404 se não existir.
- `POST /atualizar`: percorre todas as fontes, importa artigos novos e retorna `{ importados: <n> }`.

## Critérios de aceite

- `POST /fontes` com URL válida cria a fonte; URL inválida ou que não é RSS retorna 422 com mensagem clara; URL duplicada retorna 422.
- `DELETE /fontes/:id` remove; id inexistente retorna 404.
- `POST /atualizar` traz apenas artigos novos de todas as fontes, sem duplicar.

## Escopo / Fora de escopo

**Escopo deste incremento:**

- CRUD de fontes (adicionar, listar, remover).
- Validação de URL como RSS antes de salvar.
- Atualização em lote de todas as fontes.

**Fora de escopo:**

- Resumo por IA, categorias, filtros.

## Restrições técnicas

- Validar o feed tentando parseá-lo antes de salvar.
- Tratar fonte fora do ar sem derrubar a atualização das demais.
