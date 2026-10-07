# Brief de imagem: 05_diagrama_ciclo_sdd.png

- **Arquivo alvo:** `assets/05_diagrama_ciclo_sdd.png`
- **Dimensões:** 1200×600
- **Uso:** Figura 5 no ARTICLE.md
- **Status:** gerado. Renderizado a partir do fonte HTML em `diagrams/` (Chrome headless, 2x, corte na área do diagrama).

## Conteúdo

Diagrama "Seis fases, um loop", com cabeçalho editorial (kicker mono "SDD · SPEC DRIVEN DEVELOPMENT · ARTIGO 0005", título em serifa "Seis fases, um loop" e linha divisória) e o ciclo iterativo:

- Fluxo horizontal de seis nós conectados por setas: `princípios` → `especificar` → `planejar` → `tarefas` → `implementar` → `verificar`.
- Seta tracejada laranja de retorno de `verificar` para `especificar`, rotulada `desviou? volta pra spec`.
- Etiquetas sob os quatro primeiros nós ("PENSAR") e sob os dois últimos ("FAZER"), em faixas sutis.
- Nota em destaque: "o ciclo é iterativo: voltar é o processo funcionando".
- Rodapé com linha divisória, nota editorial e kicker "PATHBIT AI FOR DEVS · ARTIGO 0005".

## Estilo

Paleta e tipografia do repo: fundo `#f5f5f5`, tinta `#2d3142`, secundário `#4f5d75`, acento `#eb6c36`; Instrument Serif para títulos, Geist para texto, Geist Mono para rótulos; linguagem editorial sóbria, sem cliparts.

## Como gerar

Fonte primária: `diagrams/05_diagrama_ciclo_sdd.html` (abrir no navegador e exportar/capturar como PNG em 2x). Alternativa: regenerar com modelo de imagem usando o Conteúdo e Estilo acima.
