# Spec 01: Ler um feed RSS e listar artigos

> Convenções permanentes do projeto: ver `../CLAUDE.md.example`. Esta spec contém apenas o que é deste incremento.

## Objetivo

Trazer notícias de uma fonte RSS para dentro do app e listá-las, estabelecendo a base persistente do agregador.

## Contexto

Ciclo 1: o projeto parte do zero. Ainda não há nenhuma feature implementada.

## Requisitos funcionais

1. Dada a URL de um feed RSS, buscar os artigos e guardá-los no banco, com: `titulo`, `link`, `data_publicacao`, `fonte` (origem do feed) e `conteudo` (resumo/descrição do item RSS, quando houver).
2. Listar os artigos guardados, mais recentes primeiro.
3. Reprocessar o mesmo feed não deve duplicar artigos já existentes (deduplicar por `link`).

## Requisitos não-funcionais

- Persistência: os artigos importados sobrevivem a um reinício do servidor (banco em arquivo local, criado na inicialização se não existir).
- Respostas em JSON; datas no formato ISO `YYYY-MM-DD`.
- Erros de validação retornam HTTP 422 com corpo `{ "erro": "<mensagem clara>" }`; recurso inexistente retorna 404.

## Modelo de dados

Tabela `artigo`:

- `id` (inteiro, automático)
- `titulo` (texto)
- `link` (texto, único)
- `data_publicacao` (texto ISO)
- `fonte` (texto)
- `conteudo` (texto, pode ser vazio)

## Contrato de API

- `POST /feeds/importar`: recebe `{ url }`; busca o feed via rss-parser, salva os artigos novos e retorna `{ importados: <n> }`.
- `GET /artigos`: retorna a lista de artigos ordenada por `data_publicacao` decrescente.

## Critérios de aceite

- Importar um feed válido salva os artigos e `GET /artigos` os lista, mais recentes primeiro.
- Importar o mesmo feed de novo não duplica artigos (`importados` reflete só os novos).
- Os artigos persistem após reiniciar o servidor.

## Escopo / Fora de escopo

**Escopo deste incremento:**

- Importar um feed RSS a partir de uma URL.
- Listar os artigos persistidos, mais recentes primeiro.
- Deduplicar por `link` ao reprocessar o mesmo feed.

**Fora de escopo:**

- Gerenciar múltiplas fontes, resumo por IA, categorias, filtros, autenticação.

## Restrições técnicas

- Usar rss-parser para ler o feed.
- SQLite via better-sqlite3.
- Deduplicação por `link` (índice único).
