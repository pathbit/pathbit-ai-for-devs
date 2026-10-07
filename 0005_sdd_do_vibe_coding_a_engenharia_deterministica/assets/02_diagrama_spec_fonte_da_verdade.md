# Brief de imagem: 02_diagrama_spec_fonte_da_verdade.png

- **Arquivo alvo:** `assets/02_diagrama_spec_fonte_da_verdade.png`
- **Dimensões:** 1200×700
- **Uso:** Figura 2 no ARTICLE.md
- **Status:** gerado. Renderizado a partir do fonte HTML em `diagrams/` (Chrome headless, 2x, corte na área do diagrama).

## Conteúdo

Diagrama "A especificação como fonte da verdade", com cabeçalho editorial (kicker mono "SDD · SPEC DRIVEN DEVELOPMENT · ARTIGO 0005", título em serifa "A especificação como fonte da verdade" e linha divisória) e dois painéis lado a lado:

- Painel esquerdo `PARADIGMA TRADICIONAL (DOCUMENTAÇÃO PASSIVA)`: fluxo `código monolítico → documentação tardia` e quatro bullets: "o código é tratado como a única verdade real", "documentação técnica é reativa e desatualiza rapidamente", "divergências são resolvidas por suposições silenciosas", "a intenção de produto e arquitetura fica inacessível no repo".
- Painel direito `PARADIGMA SDD (ESPECIFICAÇÃO COMO FONTE DA VERDADE)` (borda de acento laranja): fluxo `especificação (.md) → plano técnico → código & testes` e quatro bullets: "a especificação versionada no Git é o contrato soberano", "código, esquemas e testes são artefatos secundários derivados", "divergiu? ou o código corrige o desvio, ou a spec evolui no Git: alinhamento transparente e auditável em equipe", "a intenção fica registrada, versionada e revisável por todos".
- Rodapé com linha divisória, nota editorial e kicker "PATHBIT AI FOR DEVS · ARTIGO 0005".

## Estilo

Paleta e tipografia do repo: fundo `#f5f5f5`, tinta `#2d3142`, secundário `#4f5d75`, acento `#eb6c36`; Instrument Serif para títulos, Geist para texto, Geist Mono para rótulos; linguagem editorial sóbria, sem cliparts.

## Como gerar

Fonte primária: `diagrams/02_diagrama_spec_fonte_da_verdade.html` (abrir no navegador e exportar/capturar como PNG em 2x). Alternativa: regenerar com modelo de imagem usando o Conteúdo e Estilo acima.
