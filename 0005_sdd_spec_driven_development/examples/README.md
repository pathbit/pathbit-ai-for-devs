# Kit de Exemplos: Spec Driven Development

Este diretório é o ponto de partida prático do [artigo completo](../article/ARTICLE.md): um estudo de caso de SDD com Claude Code, a API "Agregador de Notícias com resumo por IA", construída em seis incrementos, cada um guiado por uma spec.

## O que tem aqui

- `specs/` tem as seis specs, uma por incremento (Ciclos 1 a 6).
- `CLAUDE.md.example` é a memória permanente do projeto; copie para `CLAUDE.md` na raiz do seu projeto.
- `.claude/commands/` traz os slash commands `/spec` e `/implementar-spec`.
- `.claude/agents/` traz o subagente `revisor-de-spec`.
- `PROMPTS.md` é o roteiro de prompts por ciclo.

## Como usar

1. Inicie um projeto Node.js 20+ (Express, better-sqlite3, rss-parser, @anthropic-ai/sdk, Vitest + supertest).
2. Copie `CLAUDE.md.example` para `CLAUDE.md` na raiz do projeto.
3. Copie a pasta `.claude/` para o projeto.
4. Siga os ciclos usando as specs de `specs/`, na ordem: `01-feed-artigos.md` → `02-fontes-atualizar.md` → `03-resumo-ia.md` → `04-categorias-filtros.md` → `05-digest-testes.md` → `06-favoritos-dashboard-deploy.md`.

## Árvore de arquivos

```
examples/
├── CLAUDE.md.example
├── PROMPTS.md
├── README.md
├── specs/
│   ├── 01-feed-artigos.md
│   ├── 02-fontes-atualizar.md
│   ├── 03-resumo-ia.md
│   ├── 04-categorias-filtros.md
│   ├── 05-digest-testes.md
│   └── 06-favoritos-dashboard-deploy.md
└── .claude/
    ├── agents/
    │   └── revisor-de-spec.md
    └── commands/
        ├── implementar-spec.md
        └── spec.md
```

Leia o [artigo completo](../article/ARTICLE.md) para o contexto e a motivação de cada decisão.
