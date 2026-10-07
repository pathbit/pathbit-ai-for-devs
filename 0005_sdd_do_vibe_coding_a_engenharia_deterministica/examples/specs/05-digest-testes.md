# Spec 05: Digest diário e testes automatizados

> Convenções permanentes do projeto: ver `../CLAUDE.md.example`. Esta spec contém apenas o que é deste incremento.

## Objetivo

Entregar um resumo consolidado do dia e blindar o comportamento com testes.

## Contexto

Ciclo 5: parte do estado deixado pelo Ciclo 4. O app já tem artigos, resumos e categorização; ainda não há digest nem testes.

## Requisitos funcionais

1. Gerar um digest diário: os artigos de uma data (opcionalmente de um tema), cada um com seu resumo, numa saída única.
2. Cobrir os fluxos principais com testes automatizados (importar, listar, filtrar, resumo, digest, casos de erro), com a chamada de IA mockada.

## Requisitos não-funcionais

- Testes sem chamada real à API: a IA é sempre mockada, e a suíte passa integralmente sem gastar tokens.
- Banco de teste isolado do banco de desenvolvimento.
- Respostas em JSON; datas no formato ISO `YYYY-MM-DD`.

## Contrato de API

- `GET /digest?data=YYYY-MM-DD`: retorna `{ data, artigos: [{ titulo, fonte, tema, resumo, link }] }` do dia; aceita `&tema=` opcional.

## Critérios de aceite

- `GET /digest?data=2026-08-19` retorna os artigos daquele dia com seus resumos.
- Filtrar o digest por tema funciona.
- Dia sem artigos retorna lista vazia, sem erro.
- A suíte de testes (Vitest) cobre os fluxos principais, com a IA mockada, e passa integralmente sem chamar a API real.

## Escopo / Fora de escopo

**Escopo deste incremento:**

- Digest diário com filtro opcional por tema.
- Suíte de testes automatizados dos fluxos principais.

**Fora de escopo:**

- Favoritos, dashboard, deploy.

## Restrições técnicas

- Testes com Vitest e supertest (ou o cliente HTTP do runner) sobre um banco de teste isolado.
- Mock do SDK do Claude para não gastar tokens nos testes.
