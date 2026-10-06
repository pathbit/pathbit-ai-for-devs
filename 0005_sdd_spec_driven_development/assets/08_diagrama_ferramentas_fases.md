# Brief de imagem: 08_diagrama_ferramentas_fases.png

- **Arquivo alvo:** `assets/08_diagrama_ferramentas_fases.png`
- **Dimensões:** 1200×700
- **Uso:** Figura 8 no ARTICLE.md
- **Status:** gerado. Renderizado a partir do fonte HTML em `diagrams/` (Chrome headless, 2x, corte na área do diagrama).

## Conteúdo

Diagrama "Cada ferramenta atende uma fase do ciclo", com cabeçalho editorial (kicker mono "SDD · SPEC DRIVEN DEVELOPMENT · ARTIGO 0005", título em serifa "Cada ferramenta atende uma fase do ciclo" e linha divisória) e as seis fases do ciclo, cada uma conectada à ferramenta do Claude Code correspondente:

- `princípios` → `CLAUDE.md`
- `especificar` → `comando /spec`
- `planejar` → `plan mode`
- `tarefas` → `plano aprovado em etapas`
- `implementar` → `edição + Git`
- `verificar` → `subagente revisor`

- Colunas rotuladas "FASE DO CICLO" e "FERRAMENTA CLAUDE CODE", com caixas de ferramenta em borda de acento laranja.
- Legenda: "as ferramentas não são o método — elas removem o atrito de praticá-lo".
- Rodapé com linha divisória e kicker "PATHBIT AI FOR DEVS · ARTIGO 0005".

## Estilo

Paleta e tipografia do repo: fundo `#f5f5f5`, tinta `#2d3142`, secundário `#4f5d75`, acento `#eb6c36`; Instrument Serif para títulos, Geist para texto, Geist Mono para rótulos; linguagem editorial sóbria, sem cliparts.

## Como gerar

Fonte primária: `diagrams/08_diagrama_ferramentas_fases.html` — abrir no navegador e exportar/capturar como PNG em 2x. Alternativa: regenerar com modelo de imagem usando o Conteúdo e Estilo acima.
