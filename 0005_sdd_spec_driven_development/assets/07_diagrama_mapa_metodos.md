# Brief de imagem: 07_diagrama_mapa_metodos.png

- **Arquivo alvo:** `assets/07_diagrama_mapa_metodos.png`
- **Dimensões:** 1200×660
- **Uso:** Figura 7 no ARTICLE.md
- **Status:** gerado. Renderizado a partir do fonte HTML em `diagrams/` (Chrome headless, 2x, corte na área do diagrama).

## Conteúdo

Diagrama "Nenhum método vence sempre — o que muda é a região do mapa", com cabeçalho editorial (kicker mono "SDD · SPEC DRIVEN DEVELOPMENT · ARTIGO 0005", título em serifa "Nenhum método vence sempre — o que muda é a região do mapa" e linha divisória) e o mapa de métodos:

- Plano cartesiano com eixo x `ambiguidade da tarefa →` e eixo y `custo do erro →`.
- Quadrante inferior-esquerdo: `vibe coding` — script descartável, protótipo, correção trivial, exploração.
- Quadrante superior-direito: `SDD` (região em acento laranja) — feature nova, requisito ambíguo, trabalho em time, código que fica.
- Quadrante inferior-direito: `tarefa clara, mas crítica:` — spec curta + testes fortes.
- Quadrante superior-esquerdo: `ambíguo mas barato:` — explore antes, especifique depois.
- Faixa no rodapé do gráfico: "waterfall: especifica tudo, uma vez só, e não volta".
- Rodapé com kicker "PATHBIT AI FOR DEVS · ARTIGO 0005".

## Estilo

Paleta e tipografia do repo: fundo `#f5f5f5`, tinta `#2d3142`, secundário `#4f5d75`, acento `#eb6c36`; Instrument Serif para títulos, Geist para texto, Geist Mono para rótulos; linguagem editorial sóbria, sem cliparts.

## Como gerar

Fonte primária: `diagrams/07_diagrama_mapa_metodos.html` — abrir no navegador e exportar/capturar como PNG em 2x. Alternativa: regenerar com modelo de imagem usando o Conteúdo e Estilo acima.
