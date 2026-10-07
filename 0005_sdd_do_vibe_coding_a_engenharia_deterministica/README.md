# 0005 - Do Vibe Coding à Engenharia Determinística usando Spec-Driven Development (SDD) no Claude Code

Nos módulos anteriores desta série, resolvemos toda a infraestrutura operacional: acesso irrestrito ao Antigravity, roteamento de modelos no Claude Code, malha de fallback e alternativas de baixo custo. Com o ambiente de alta performance estabelecido, a pergunta central muda de figura: o que você entrega ao agente para ele construir?

Este módulo apresenta o **Spec Driven Development (SDD)**, a disciplina de escrever a especificação antes do código e tratá-la como a fonte primária da verdade do projeto. O código passa a ser um artefato estritamente derivado dela, e o agente deixa de adivinhar o que você queria dizer por telepatia.

## O que este módulo cobre

1. Por que pedir código no improviso transfere decisões críticas de produto para o agente em silêncio
2. As seis seções fundamentais de uma especificação executável, com critérios de aceite binários no centro
3. O ciclo iterativo em seis fases: princípios, especificar, planejar, tarefas, implementar e verificar
4. Como um agente interpreta uma especificação: janela de contexto, preenchimento de lacunas e curadoria enxuta
5. Onde o SDD brilha, onde é exagero, e como ele se combina com o TDD sem qualquer competição
6. As ferramentas nativas do Claude Code encaixadas em cada fase: `CLAUDE.md`, plan mode, slash commands e subagentes isolados
7. Um estudo de caso completo: a API de Agregador de Notícias com resumo por inteligência artificial, construída em seis ciclos de SDD em Node.js

## Estrutura do módulo

| Diretório | Conteúdo |
| :--- | :--- |
| `src/` | Aplicação executável: API Express, banco SQLite, serviço de resumo com IA, rotas e dashboard web |
| `article/` | O artigo completo para o repositório, a versão editorial para LinkedIn e o post de divulgação |
| `examples/` | Kit pronto para uso: as seis specs do estudo de caso, o `CLAUDE.md.example`, os slash commands `/spec` e `/implementar-spec`, o subagente revisor e o roteiro de prompts |
| `assets/` | Diagramas conceituais em PNG de alta resolução acompanhados de seus respectivos briefs em Markdown e fontes HTML |
| `tests/` | Suíte de testes automatizados cobrindo os critérios de aceite das specs 01 a 06 |

## Como rodar o produto (Agregador de Notícias)

1. Instale as dependências:
   ```bash
   npm install
   ```
2. Execute a suíte de testes automatizados:
   ```bash
   npm test
   ```
3. Inicie o servidor da aplicação:
   ```bash
   npm start
   ```
4. Acesse o dashboard interativo no navegador:
   - **URL:** [http://localhost:3005](http://localhost:3005)
   - **API de Artigos:** [http://localhost:3005/artigos](http://localhost:3005/artigos)
   - **Digest Diário:** [http://localhost:3005/digest/hoje](http://localhost:3005/digest/hoje)

> Sobre as imagens: os diagramas em `assets/` seguem rigorosamente a paleta de cores e o padrão editorial sóbrio dos módulos anteriores. Cada imagem conta com um brief descritivo em arquivo `.md` contendo seu conteúdo semântico, dimensões e instruções de geração.

## Leitura recomendada

1. [Artigo completo](./article/ARTICLE.md)
2. [Artigo para LinkedIn](./article/ARTICLE_LINKEDIN.md)
3. [Kit de exemplos práticos](./examples/README.md)
4. [Roteiro de prompts por ciclo](./examples/PROMPTS.md)
