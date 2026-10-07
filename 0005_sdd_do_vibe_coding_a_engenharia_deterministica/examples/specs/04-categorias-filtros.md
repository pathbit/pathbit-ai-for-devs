# Spec 04: Categorização por tema e filtros

> Convenções permanentes do projeto: ver `../CLAUDE.md.example`. Esta spec contém apenas o que é deste incremento.

## Objetivo

Organizar os artigos por tema e permitir encontrar o que interessa.

## Contexto

Ciclo 4: parte do estado deixado pelo Ciclo 3. Os artigos já têm resumo por IA; ainda não há categorização nem filtros.

## Requisitos funcionais

1. Classificar cada artigo por tema (ex.: tecnologia, economia, esportes), via IA ou por palavras-chave (decidir e registrar no `CLAUDE.md`).
2. Filtrar artigos combinando: `tema`, `fonte` e período (`data_inicio`, `data_fim`). Todos opcionais e combináveis.

## Requisitos não-funcionais

- Queries sempre com parâmetros vinculados, nunca concatenação de SQL.
- Tempo de resposta: a listagem com todos os filtros combinados responde em menos de 500 ms para uma base de até 10.000 artigos.
- Parâmetros inválidos (ex.: período invertido) retornam HTTP 422 com mensagem clara.

## Modelo de dados

Alteração em `artigo`: adicionar `tema` (texto, pode ser nulo até classificar).

## Contrato de API

- `POST /classificar`: classifica os artigos ainda sem tema; retorna `{ classificados: <n> }`.
- `GET /artigos` passa a aceitar os parâmetros opcionais `tema`, `fonte`, `data_inicio`, `data_fim`, combinados por E lógico.

## Critérios de aceite

- Após `POST /classificar`, os artigos têm `tema` preenchido.
- `GET /artigos?tema=tecnologia&fonte=<x>` combina os filtros corretamente.
- Período por `data_inicio`/`data_fim` funciona isolado e junto dos demais filtros.
- Parâmetros inválidos (ex.: período invertido) retornam 422.

## Escopo / Fora de escopo

**Escopo deste incremento:**

- Classificação de artigos por tema.
- Filtros combináveis em `GET /artigos`.

**Fora de escopo:**

- Digest, favoritos, dashboard.

## Restrições técnicas

- Montar a query de filtros dinamicamente com parâmetros vinculados (sem concatenar SQL).
- Se a classificação for por IA, reaproveitar o cliente e o cuidado de custo do Ciclo 3.
