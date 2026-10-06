# Spec 03: Resumo de artigos por IA

> Convenções permanentes do projeto: ver `../CLAUDE.md.example`. Esta spec contém apenas o que é deste incremento.

## Objetivo

Gerar um resumo curto de cada artigo usando IA, o valor central do produto.

## Contexto

Ciclo 3: parte do estado deixado pelo Ciclo 2. O app já tem fontes e artigos; ainda não há nenhuma chamada de IA.

## Requisitos funcionais

1. Gerar, sob demanda, um resumo em português de um artigo, a partir do seu `titulo` + `conteudo`, chamando a API do Claude.
2. Cachear o resumo: uma vez gerado, é persistido e reutilizado nas próximas chamadas (não chama a API de novo).
3. Tratar falha da API (timeout/erro) sem derrubar a requisição; retorna erro claro e não gravar resumo inválido.

## Requisitos não-funcionais

- Chave da API sempre via `process.env.ANTHROPIC_API_KEY`, nunca hardcoded.
- Limite de tamanho do conteúdo enviado à API, para controlar custo e latência.
- Cache: a segunda chamada ao mesmo artigo não faz nova chamada à API.
- Falha da API retorna 502 (ou similar) com corpo `{ "erro": ... }`, sem derrubar a requisição.

## Modelo de dados

Alteração em `artigo`: adicionar `resumo` (texto, nulo até ser gerado).

## Contrato de API

- `GET /artigos/:id/resumo`: se já houver resumo, retorna o cacheado; senão, gera via IA, salva e retorna. 404 se o artigo não existir; 502 (ou similar) com `{ "erro": ... }` se a IA falhar.

## Critérios de aceite

- Primeira chamada a `GET /artigos/:id/resumo` gera o resumo e o persiste; a segunda retorna o mesmo resumo sem nova chamada à API.
- Artigo inexistente retorna 404.
- Falha simulada da API é tratada: a requisição não quebra e nenhum resumo inválido é salvo.

## Escopo / Fora de escopo

**Escopo deste incremento:**

- Resumo sob demanda por artigo, com cache persistido.
- Tratamento de falha da API.

**Fora de escopo:**

- Categorização, digest, filtros.

## Restrições técnicas

- Usar o SDK `@anthropic-ai/sdk` (Messages API).
- Chave por `ANTHROPIC_API_KEY`.
- Escolher um modelo econômico (ex.: Claude Haiku) e registrar no `CLAUDE.md`.
- Prompt de resumo curto e objetivo.
- Limitar tamanho do conteúdo enviado para controlar custo/latência.
