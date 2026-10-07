# Roteiro de Prompts: Agregador de Notícias com resumo por IA

Prompts sugeridos para o Claude Code, ciclo a ciclo, seguindo o fluxo completo de SDD:

> **Plano → (revisar) → Escopo → Implementação → Verificação → Commit**

Copie e cole, ajustando os caminhos das specs ao seu repositório. Os prompts são propositalmente **magros**: o peso mora nas specs e no `CLAUDE.md`. Se precisar explicar muita coisa no chat, atualize a spec. Os comandos `/spec` e `/implementar-spec` já estão em `.claude/commands/`.

## Ciclo 1. Feed de artigos

**Passo 1. Criar o esqueleto e o CLAUDE.md (antes de qualquer feature):**
```
Vamos iniciar um projeto de API "Agregador de Notícias com resumo por IA".
Stack: Node.js 20+, Express, SQLite (better-sqlite3), rss-parser e o SDK do Claude
para JS (@anthropic-ai/sdk).

Antes de implementar qualquer coisa, crie o esqueleto do projeto e um arquivo CLAUDE.md
com: descrição do projeto, stack, como rodar, estrutura de pastas, e estas convenções:
datas em ISO YYYY-MM-DD; erros de validação em HTTP 422 no formato { "erro": "<mensagem>" };
recurso inexistente em 404; a chave da API SEMPRE via variável de ambiente ANTHROPIC_API_KEY,
nunca hardcoded; banco SQLite em arquivo local criado na inicialização.
Entre em plan mode primeiro e me mostre o plano antes de criar os arquivos.
```

**Passo 2. Implementar a primeira spec:**
```
/implementar-spec specs/01-feed-artigos.md
```
(ou o equivalente sem slash command: "Leia a spec em specs/01-feed-artigos.md, entre em plan mode, mostre o plano, implemente só esta spec respeitando o CLAUDE.md e verifique os critérios de aceite.")

**Passo 3. Fechar o ciclo:**
```
Suba o servidor e me mostre como testar POST /feeds/importar (com uma URL de feed
real) e GET /artigos. Confirme que reimportar não duplica. Depois faça o commit inicial.
```

## Ciclo 2. Gerenciar fontes e atualizar

**Plano + implementação:**
```
/implementar-spec specs/02-fontes-atualizar.md
```

**Reforço em plan mode (casos de erro):**
```
No plano, garanta que POST /fontes valide a URL parseando o feed antes de salvar
(URL inválida ou não-RSS → 422; duplicada → 422), e que POST /atualizar continue
funcionando mesmo se uma das fontes estiver fora do ar. Ajuste antes de implementar.
```

**Verificação + memória + commit:**
```
Teste cada critério de aceite (fonte válida, inválida, duplicada, DELETE inexistente,
atualizar sem duplicar). Registre no CLAUDE.md decisões novas (ex.: como o nome da fonte
é resolvido). Faça o commit.
```

## Ciclo 3. Resumo por IA (introduz a chamada externa)

**Decisão + cuidado antes de codar:**
```
Antes de implementar, revise comigo a estratégia da chamada de IA (Claude): resumo sob
demanda, escolha de um modelo econômico (ex.: Claude Haiku), cache do resultado no próprio
artigo, tratamento de falha (sem gravar resumo inválido) e limite de tamanho do conteúdo
enviado para controlar custo. Registre essas decisões no CLAUDE.md.
```

**Plano + implementação:**
```
/implementar-spec specs/03-resumo-ia.md
```

**Verificação + commit:**
```
Verifique: primeira chamada gera e persiste o resumo; segunda chamada NÃO chama a API
de novo (usa cache); artigo inexistente → 404; falha simulada da API é tratada.
Confirme que a chave vem de ANTHROPIC_API_KEY. Atualize o CLAUDE.md e faça o commit.
```

## Ciclo 4. Categorização por tema e filtros

**Decisão de spec:**
```
Antes de implementar, me ajude a decidir e registrar no CLAUDE.md: a classificação por
tema será via IA ou por palavras-chave? Recomende uma opção considerando custo e
previsibilidade, e explique o porquê.
```

**Plano + implementação:**
```
/implementar-spec specs/04-categorias-filtros.md
```

**Verificação + commit:**
```
Teste POST /classificar e os filtros combinados de GET /artigos (tema + fonte + período),
cada um isolado e todos juntos, além de período invertido (deve dar 422). Confirme que a
query usa parâmetros vinculados, não concatenação de SQL. Atualize o CLAUDE.md e commite.
```

## Ciclo 5. Digest diário e testes automatizados

**Plano + implementação:**
```
/implementar-spec specs/05-digest-testes.md
```

**Verificação com subagente:**
```
Rode a suíte de testes (Vitest) e me mostre o resultado. Confirme que a IA está mockada
e que nenhum teste chama a API real. Em seguida, use o subagente revisor-de-spec para
revisar o código desta feature contra a spec e apontar casos não cobertos ou erros de
correção. Itere no que ele encontrar.
```

**Commit:**
```
Com os testes passando, registre no CLAUDE.md o comando de testes e a estratégia de mock,
e faça o commit.
```

## Ciclo 6. Favoritos, dashboard e deploy

**Plano + implementação:**
```
/implementar-spec specs/06-favoritos-dashboard-deploy.md
```

**Cuidados no plano:**
```
No plano, garanta: dashboard como HTML simples servido pelo Express, consumindo os
endpoints existentes via fetch (gráfico opcional via Chart.js por CDN); porta e
ANTHROPIC_API_KEY vindas de variáveis de ambiente; nenhuma credencial hardcoded.
```

**Verificação + entrega:**
```
Teste favoritar/desfavoritar e GET /favoritos; abra o dashboard e confira o digest do dia,
a abertura de resumo e a lista de favoritos. Depois me guie no deploy usando variáveis de
ambiente. Atualize o CLAUDE.md com as instruções de deploy e faça o commit final.
```

---

## Lembretes para conduzir os ciclos

- **Sempre revise o plano** antes de deixar implementar. É o ponto mais barato para corrigir rumo.
- **Escopo travado:** se o Claude começar a adiantar features de ciclos futuros, corte e reaponte para a spec do ciclo.
- **Chat magro, spec gorda:** precisou explicar muito no chat? Leve isso para a spec ou para o CLAUDE.md.
- **Cuidado com custo de IA:** resumo e classificação chamam a API, então reforce cache e limite de conteúdo; nos testes, a IA é sempre mockada.
- **CLAUDE.md ao fim de cada ciclo:** toda decisão nova vira uma linha lá. É o que faz o ciclo seguinte "já saber".
- **Commit por ciclo:** cada incremento fechado é um commit; a spec correspondente entra versionada junto.

---

## Arsenal de Prompts de Alta Certeza e Validação Cruzada

Estes prompts colocam qualquer agente de IA (Claude Code, Antigravity, Cline, Cursor) em um funil de conformidade estrita, eliminando viés cognitivo e alucinações de frontend:

### 1. Prova com Evidências Visuais em Navegador Real (Auditoria de Wireframes)
```text
PROVE COM EVIDENCIAS VISUAIS EM NAVEGADOR REAL VALIDANDO DE FORMA RESTRITA TODO VISUAL DO
  WIREFRAME QUE ESTA NA PASTAS ./docs/design/wireframes/v1/* E SALVE AS EVIDENCIAS EM ./tmp/evidencias/specs/<spec>
```
*O que faz:* Força o agente a abrir uma sessão real no navegador (`http://localhost:3005`), capturar telas inteiras e componentes, comparar visualmente pixel a pixel contra os wireframes canônicos e salvar os relatórios exclusivamente em `./tmp/evidencias/specs/<spec>/`.

### 2. Validação Cruzada de Critérios de Aceite Binários (Subagente Auditor / QA)
```text
INICIE UMA SESSÃO ISOLADA DE AUDITORIA (SEM VIÉS COGNITIVO DA SESSÃO PRINCIPAL). LEIA ESTRITAMENTE A SPEC EM specs/NN-nome.md E AUDITE O GIT DIFF ATUAL. PARA CADA UM DOS CRITÉRIOS DE ACEITE BINÁRIOS, RESPONDA EXCLUSIVAMENTE COM:
1. [ATENDIDO / NÃO ATENDIDO / DUVIDOSO], INDICANDO A LINHA EXATA DO CÓDIGO E O TESTE AUTOMATIZADO CORRESPONDENTE.
2. IDENTIFIQUE QUALQUER CÓDIGO OU DEPENDÊNCIA ADICIONADA QUE NÃO ESTAVA DECLARADA NA SPEC (ANTI-ESCOPO).
3. REGISTRE O RELATÓRIO DE AUDITORIA EM ./tmp/evidencias/specs/<spec>/auditoria_cruzada.md
```

### 3. Auditoria Cruzada Multidisciplinar das 6 Camadas
```text
EXECUTE UMA AUDITORIA CRUZADA MULTIDISCIPLINAR NAS 6 DISCIPLINAS DO SDD:
- [DB]: Confirme persistência atômica, modo WAL no SQLite e constraints UNIQUE contra duplicação de dados.
- [API]: Valide envelopes de erro HTTP 422 descritivos em entradas inválidas e contratos de resposta JSON.
- [DESIGN SYSTEM]: Audite se todas as cores, espaçamentos e fontes consom os tokens oficiais (zero cores hex hardcoded).
- [FRONTEND]: Inspecione reatividade da busca, feedback visual de carregamento (spinner) e tratamento de listas vazias.
- [DEVOPS]: Audite o Dockerfile garantindo imagem Alpine, usuário não-root (USER node) e healthcheck configurado.
- [QA]: Execute a suíte automatizada (npm test) e comprove que 100% dos testes passam de forma idempotente.
SALVE O LAUDO DE CONFORMIDADE EM ./tmp/evidencias/specs/<spec>/relatorio_multidisciplinar.md
```

### 4. Blindagem de Governança e Autoria Humana no Git
```text
INSPECIONE O HISTÓRICO DO GIT (git log -n 5) E AUDITE SE TODOS OS COMMITS POSSUEM AUTORIA EXCLUSIVAMENTE HUMANA, SEM QUALQUER TRAILER SINTÉTICO ('Co-Authored-By: Claude', 'Signed-off-by: AI'). CONFIRME SE O .gitignore BLINDA O REPOSITÓRIO CONTRA METADADOS (.DS_Store), ARQUIVOS DE BANCO LOCAIS (.sqlite, .db) E CREDENCIAIS (.env).
```
