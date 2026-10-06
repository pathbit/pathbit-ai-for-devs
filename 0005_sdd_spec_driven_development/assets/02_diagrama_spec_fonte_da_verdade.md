# Brief de imagem: 02_diagrama_spec_fonte_da_verdade.png

- **Arquivo alvo:** `assets/02_diagrama_spec_fonte_da_verdade.png`
- **Dimensões:** 1200×700
- **Uso:** Figura 2 no ARTICLE.md
- **Status:** gerado. Renderizado a partir do fonte HTML em `diagrams/` (Chrome headless, 2x, corte na área do diagrama).

## Conteúdo

Diagrama "A especificação como fonte da verdade", com cabeçalho editorial (kicker mono "SDD · SPEC DRIVEN DEVELOPMENT · ARTIGO 0005", título em serifa "A especificação como fonte da verdade" e linha divisória) e dois painéis lado a lado:

- Painel esquerdo `MODELO ANTIGO`: fluxo `código → (talvez) doc` e quatro bullets — "o código é a única verdade", "a doc é escrita depois, se sobrar tempo", "divergiu? a doc está errada", "a intenção fica na cabeça de quem escreveu".
- Painel direito `MODELO SDD` (borda de acento laranja): fluxo `spec → plano → código` e quatro bullets — "a spec é a única verdade", "o código é um artefato derivado dela", "divergiu? ou o código está errado, ou a spec mudou — é decidido, não descoberto", "a intenção fica registrada e revisável".
- Rodapé com linha divisória, nota editorial e kicker "PATHBIT AI FOR DEVS · ARTIGO 0005".

## Estilo

Paleta e tipografia do repo: fundo `#f5f5f5`, tinta `#2d3142`, secundário `#4f5d75`, acento `#eb6c36`; Instrument Serif para títulos, Geist para texto, Geist Mono para rótulos; linguagem editorial sóbria, sem cliparts.

## Como gerar

Fonte primária: `diagrams/02_diagrama_spec_fonte_da_verdade.html` — abrir no navegador e exportar/capturar como PNG em 2x. Alternativa: regenerar com modelo de imagem usando o Conteúdo e Estilo acima.
