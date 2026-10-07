# Brief de imagem: 08_diagrama_ferramentas_fases.png

- **Arquivo alvo:** `assets/08_diagrama_ferramentas_fases.png`
- **Dimensões:** 1200×700
- **Uso:** Figura 8 no ARTICLE.md
- **Status:** gerado. Renderizado a partir do fonte HTML em `diagrams/` (Chrome headless, 2x, corte na área do diagrama).

## Conteúdo

Diagrama "Cada ferramenta atende uma fase do ciclo", com cabeçalho editorial (kicker mono "SDD · SPEC DRIVEN DEVELOPMENT · ARTIGO 0005", título em serifa "Cada ferramenta atende uma fase do ciclo" e linha divisória) e as seis fases do ciclo, cada uma conectada à ferramenta do Claude Code correspondente:

- `0. Princípios Globais` → `CLAUDE.md + AGENTS.md (Constituição Viva)`
- `1. Especificar` → `Comando /spec (Caça ambiguidades)`
- `2. Planejar` → `Plan Mode (Modo Somente Leitura)`
- `3. Tarefas` → `Checklist Atômico (DB, API, SPA, Docker)`
- `4. Implementar` → `/implementar-spec + Disciplina dos 2 Commits`
- `5. Verificar` → `Subagente Revisor + Suíte de Testes`

- Colunas rotuladas "FASE DO CICLO SDD" e "HARNESS CLAUDE CODE & GOVERNANÇA PATHBIT", com caixas de ferramenta em borda de acento laranja.
- Legenda: "No SDD, o ferramental do Claude Code automatiza os rituais para que o engenheiro foque em formular e auditar".
- Rodapé com linha divisória e kicker "PATHBIT AI FOR DEVS · ARTIGO 0005".

## Estilo

Paleta e tipografia do repo: fundo `#f5f5f5`, tinta `#2d3142`, secundário `#4f5d75`, acento `#eb6c36`; Instrument Serif para títulos, Geist para texto, Geist Mono para rótulos; linguagem editorial sóbria, sem cliparts.

## Como gerar

Fonte primária: `diagrams/08_diagrama_ferramentas_fases.html` (abrir no navegador e exportar/capturar como PNG em 2x). Alternativa: regenerar com modelo de imagem usando o Conteúdo e Estilo acima.
