# Spec 06: Favoritos, dashboard e deploy

> Convenções permanentes do projeto: ver `../CLAUDE.md.example`. Esta spec contém apenas o que é deste incremento.

## Objetivo

Dar ao usuário uma interface para ler e guardar notícias, e publicar o app.

## Contexto

Ciclo 6: parte do estado deixado pelo Ciclo 5. O app está completo e testado; falta favoritar, visualizar e publicar.

## Requisitos funcionais

1. Favoritar e desfavoritar artigos; listar favoritos.
2. Servir um mini-dashboard HTML que mostra o digest do dia, os resumos (sob demanda) e os favoritos.
3. Preparar o app para deploy: porta e `ANTHROPIC_API_KEY` por variável de ambiente.

## Requisitos não-funcionais

- Nenhuma credencial hardcoded: a chave da API vem de `process.env.ANTHROPIC_API_KEY`.
- Porta do servidor via variável de ambiente (com padrão local).
- Dashboard servido como HTML simples pelo Express, sem build de front-end.

## Modelo de dados

Alteração em `artigo`: adicionar `favorito` (booleano, padrão falso).

## Contrato de API

- `POST /artigos/:id/favoritar` e `DELETE /artigos/:id/favoritar`: marca/desmarca; 404 se não existir.
- `GET /favoritos`: lista os artigos favoritados.
- `GET /` (ou `/dashboard`): serve a página HTML do dashboard.

## Critérios de aceite

- Favoritar/desfavoritar reflete em `GET /favoritos`.
- O dashboard exibe o digest do dia, permite abrir o resumo de um artigo e mostra os favoritos, consumindo os endpoints existentes.
- O app roda fora da máquina local (deploy), com porta e chave da API vindas de variáveis de ambiente.

## Escopo / Fora de escopo

**Escopo deste incremento:**

- Favoritar/desfavoritar e listagem de favoritos.
- Mini-dashboard HTML consumindo os endpoints existentes.
- Preparação para deploy via variáveis de ambiente.

**Fora de escopo:**

- Autenticação, multiusuário, banco externo (extensões avançadas).

## Restrições técnicas

- Dashboard como HTML simples servido pelo Express, com JS de front leve (fetch nos endpoints; gráfico opcional via Chart.js por CDN).
- Nenhuma credencial hardcoded.
