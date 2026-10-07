# Brief de imagem: 01_diagrama_chute_vs_spec.png

- **Arquivo alvo:** `assets/01_diagrama_chute_vs_spec.png`
- **Dimensões:** 1200×600
- **Uso:** Figura 1 no ARTICLE.md
- **Status:** gerado. Renderizado a partir do fonte HTML em `diagrams/` (Chrome headless, 2x, corte na área do diagrama).

## Conteúdo

Diagrama "Do freestyle probabilístico à especificação determinística", com cabeçalho editorial (kicker mono "SDD · SPEC DRIVEN DEVELOPMENT · ARTIGO 0005", título em serifa "Do freestyle probabilístico à especificação determinística" e linha divisória) e duas pistas horizontais empilhadas:

- Pista superior rotulada `FREESTYLE VIBE CODING: FLUXO DE INCERTEZA`: três caixas conectadas por setas: `prompt solto` → `código gerado` → `premissas implícitas`, com uma seta tracejada laranja de retorno (`loop de retrabalho ↻`) voltando do fim para o começo; ao lado, a nota "dívida técnica oculta, resultado imprevisível".
- Pista inferior rotulada `SPEC-DRIVEN DEVELOPMENT: ENGENHARIA DETERMINÍSTICA`: quatro caixas conectadas por setas: `especificação (.md)` → `plan mode` → `código derivado` → `✓ critérios de aceite`, sendo a última destacada com acento laranja.
- Rodapé com linha divisória, nota editorial e kicker "PATHBIT AI FOR DEVS · ARTIGO 0005".

## Estilo

Paleta e tipografia do repo: fundo `#f5f5f5`, tinta `#2d3142`, secundário `#4f5d75`, acento `#eb6c36`; Instrument Serif para títulos, Geist para texto, Geist Mono para rótulos; linguagem editorial sóbria, sem cliparts.

## Como gerar

Fonte primária: `diagrams/01_diagrama_chute_vs_spec.html` (abrir no navegador e exportar/capturar como PNG em 2x). Alternativa: regenerar com modelo de imagem usando o Conteúdo e Estilo acima.
