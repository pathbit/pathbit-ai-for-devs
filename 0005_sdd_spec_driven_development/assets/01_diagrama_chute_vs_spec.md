# Brief de imagem: 01_diagrama_chute_vs_spec.png

- **Arquivo alvo:** `assets/01_diagrama_chute_vs_spec.png`
- **Dimensões:** 1200×600
- **Uso:** Figura 1 no ARTICLE.md
- **Status:** gerado. Renderizado a partir do fonte HTML em `diagrams/` (Chrome headless, 2x, corte na área do diagrama).

## Conteúdo

Diagrama "O mesmo trabalho, dois caminhos", com cabeçalho editorial (kicker mono "SDD · SPEC DRIVEN DEVELOPMENT · ARTIGO 0005", título em serifa "Do codar no chute à especificação como alvo" e linha divisória) e duas pistas horizontais empilhadas:

- Pista superior rotulada `SEM SPEC: CODAR NO CHUTE`: três caixas brancas conectadas por setas: `pedido vago` → `código` → `"não era isso"`, com uma seta tracejada laranja de retorno (`retrabalho`) voltando do fim para o começo; ao lado, a nota "horas gastas, resultado incerto".
- Pista inferior rotulada `COM SPEC: SPEC DRIVEN DEVELOPMENT`: quatro caixas conectadas por setas: `spec` → `plano` → `código` → `✓ critério de aceite`, sendo a última com borda de acento laranja.
- Rodapé com linha divisória, nota editorial e kicker "PATHBIT AI FOR DEVS · ARTIGO 0005".

## Estilo

Paleta e tipografia do repo: fundo `#f5f5f5`, tinta `#2d3142`, secundário `#4f5d75`, acento `#eb6c36`; Instrument Serif para títulos, Geist para texto, Geist Mono para rótulos; linguagem editorial sóbria, sem cliparts.

## Como gerar

Fonte primária: `diagrams/01_diagrama_chute_vs_spec.html` (abrir no navegador e exportar/capturar como PNG em 2x). Alternativa: regenerar com modelo de imagem usando o Conteúdo e Estilo acima.
