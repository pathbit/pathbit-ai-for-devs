# Brief de imagem: 03_diagrama_custo_do_erro.png

- **Arquivo alvo:** `assets/03_diagrama_custo_do_erro.png`
- **Dimensões:** 1200×640
- **Uso:** Figura 3 no ARTICLE.md
- **Status:** gerado. Renderizado a partir do fonte HTML em `diagrams/` (Chrome headless, 2x, corte na área do diagrama).

## Conteúdo

Diagrama "Corrigir cedo é barato; tarde, é sprint", com cabeçalho editorial (kicker mono "SDD · SPEC DRIVEN DEVELOPMENT · ARTIGO 0005", título em serifa "Corrigir cedo é barato; tarde, é sprint" e linha divisória) e um gráfico de colunas crescentes:

- Eixo x rotulado "quando o erro é descoberto", com quatro colunas: `na spec` (coluna mínima), `no plano`, `na revisão do código` e `em produção` (coluna máxima, em acento laranja).
- Marcador de destaque tracejado laranja sobre a primeira coluna, com o rótulo "SDD decide aqui".
- Legenda abaixo do gráfico: "Mudar uma frase da spec custa segundos. A mesma decisão em produção custa uma sprint."
- Rodapé com kicker "PATHBIT AI FOR DEVS · ARTIGO 0005".

## Estilo

Paleta e tipografia do repo: fundo `#f5f5f5`, tinta `#2d3142`, secundário `#4f5d75`, acento `#eb6c36`; Instrument Serif para títulos, Geist para texto, Geist Mono para rótulos; linguagem editorial sóbria, sem cliparts.

## Como gerar

Fonte primária: `diagrams/03_diagrama_custo_do_erro.html` (abrir no navegador e exportar/capturar como PNG em 2x). Alternativa: regenerar com modelo de imagem usando o Conteúdo e Estilo acima.
