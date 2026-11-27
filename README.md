# 🚀 Pathbit AI for Devs

Arquiteturas agênticas e engenharia de inteligência artificial para desenvolvedores, publicadas pela **Pathbit**.

---

## 📚 Artigos Disponíveis

### [0001 - Google Antigravity com Acesso Total Irrestrito e sem Interrupções](./0001_antigravity_acesso_total_irrestrito/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Autonomia de Agentes

Elimina as confirmações manuais que interrompem tarefas agênticas longas, configurando acesso irrestrito na **Antigravity IDE**, na **CLI `agy`** e no motor compartilhado **Agent 2.0**. Cobre a precedência `DENY > ASK > ALLOW`, os seis wildcards universais e os caminhos de configuração em macOS, Linux e Windows. Inclui scripts em Python para aplicação idempotente, diagnóstico do ambiente e restauração de backups, com suíte de testes que simula os três sistemas operacionais.

[📖 Ler Artigo](./0001_antigravity_acesso_total_irrestrito/article/ARTICLE.md) | [🔧 Executar Localmente](./0001_antigravity_acesso_total_irrestrito/README.md) | [🧪 Exemplos Práticos](./0001_antigravity_acesso_total_irrestrito/examples/README.md)

---

### [0002 - ClaudeGravity e o Roteamento de Modelos Gemini no Claude Code via 9Router](./0002_claude_gravity_utilizando_9router/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Gateways e Model Routing

Conecta o harness de desenvolvimento do **Claude Code CLI** à infraestrutura de modelos do **Google Antigravity (Google AI Pro)** através do gateway **9Router** em container Docker, sujeito às cotas e condições da conexão utilizada. Aborda a tradução bidirecional de protocolo, a compressão RTK de saídas de ferramentas, a auto-renovação contínua de tokens via container sidecar (`router-sync`, imagem oficial `ghcr.io/pathbit/9rtksync:latest` em Alpine) e o mapeamento de modelos primários, secundários e de subagentes. Inclui análise de risco, arquitetura multi-conta com Round-Robin e scripts de diagnóstico e inferência.

[📖 Ler Artigo](./0002_claude_gravity_utilizando_9router/article/ARTICLE.md) | [🔧 Executar Localmente](./0002_claude_gravity_utilizando_9router/README.md) | [🧪 Exemplos Práticos](./0002_claude_gravity_utilizando_9router/examples/README.md)

---

### [0003 - Fallback no 9Router para o Claude Code](./0003_fallback_modelos_gratuitos_9router/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Alta Disponibilidade

Transforma o 9Router em uma central de alta disponibilidade para o Claude Code, mapeando **9 fontes gratuitas de modelos** e integrando 5 delas em **combos com fallback automático**. Quando um provedor atinge o teto de cota, sai do catálogo ou passa a exigir permissão, o gateway comuta para o próximo nível quando há uma rota compatível disponível. Inclui provisionamento idempotente dos combos, validação nível a nível da cascata e um laboratório que simula rate limit, desautenticação e auto-cura.

[📖 Ler Artigo](./0003_fallback_modelos_gratuitos_9router/article/ARTICLE.md) | [🔧 Executar Localmente](./0003_fallback_modelos_gratuitos_9router/README.md) | [🧪 Exemplos Práticos](./0003_fallback_modelos_gratuitos_9router/examples/README.md)

---

### [0004 - DeepClaude: A Alternativa ao ClaudeGravity com DeepSeek e OrcaRouter no Claude Code](./0004_deepclaude_alternativa_ao_claudegravity/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Provedores Alternativos

Opera o **Claude Code CLI** diretamente com modelos **DeepSeek**, sem gateway local e sem assinatura do Google Antigravity: pela plataforma oficial (**DeepSeek Platform**, com preços mínimos por milhão de tokens) ou pelo **OrcaRouter** (com o `deepseek/deepseek-v4-flash-free` gratuito e 1M de contexto). Detalha os cinco escopos de configuração da CLI e por que a credencial mora em `settings.local.json`, mostra o que o sufixo `[1m]` realmente faz (a CLI o remove; o gateway recusa), e expõe a armadilha do menu `/model` — o Enter grava o modelo no `~/.claude/settings.json` global e faz o DeepSeek virar o padrão até da sua conta Anthropic. Traz 41 capturas de tela cobrindo cadastro, vinculação do GitHub para elegibilidade do tier gratuito, validação no Playground e operação no terminal com ambos os provedores, além de um verificador que prova a integração com inferência real.

[📖 Ler Artigo](./0004_deepclaude_alternativa_ao_claudegravity/article/ARTICLE.md) | [🔧 Executar Localmente](./0004_deepclaude_alternativa_ao_claudegravity/README.md) | [🧪 Exemplos Práticos](./0004_deepclaude_alternativa_ao_claudegravity/examples/README.md)

---

### [0005 - Do Vibe Coding à Engenharia Determinística usando Spec-Driven Development (SDD) no Claude Code](./0005_sdd_do_vibe_coding_a_engenharia_deterministica/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Método de Desenvolvimento

Depois de resolver a infraestrutura de modelos nos quatro primeiros módulos, este artigo aborda a camada metodológica central: o que você entrega ao agente para ele construir? Apresenta o **Spec-Driven Development (SDD)**, a disciplina de engenharia que substitui o improviso do *vibe coding* por especificações executáveis e verificáveis, estabelecendo a especificação como a fonte primária da verdade e o código como um subproduto estritamente derivado. Detalha a anatomia de uma especificação precisa, as armadilhas comuns de ambiguidade, o ciclo iterativo em seis fases com loopback consciente, a física cognitiva da janela de contexto do agente e a sinergia com o TDD. Mostra como o ecossistema nativo do Claude Code (como `CLAUDE.md`, plan mode, slash commands e subagentes com contexto isolado) viabiliza o método na prática, acompanhado do estudo de caso completo de uma API de agregador de notícias desenvolvida em seis ciclos incrementais.

[📖 Ler Artigo](./0005_sdd_do_vibe_coding_a_engenharia_deterministica/article/ARTICLE.md) | [🔧 Executar Localmente](./0005_sdd_do_vibe_coding_a_engenharia_deterministica/README.md) | [🧪 Exemplos Práticos](./0005_sdd_do_vibe_coding_a_engenharia_deterministica/examples/README.md)

---

### [0006 - OpenSpec e Claude Code no Agregador](./0006_openspec_claude_code/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Spec-Driven Development

Parte da API do 0005 e acrescenta um download CSV de favoritos com o **OpenSpec** e o **Claude Code**. Mostra a especificação vigente, a change com delta, a implementação isolada, a verificação HTTP de cabeçalhos e conteúdo e o arquivamento que atualiza o requisito do produto.

[📖 Ler Artigo](./0006_openspec_claude_code/article/ARTICLE.md) | [🔧 Executar Localmente](./0006_openspec_claude_code/README.md) | [🧪 Exemplos Práticos](./0006_openspec_claude_code/examples/README.md)

---

### [0007 - Skills de projeto no Claude Code](./0007_skills_claude_code/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Skills e contexto de projeto

Transforma o roteiro de planejamento do Agregador em uma **Skill de projeto do Claude Code**, com mapa de rotas, procedimento e modelo de proposta. Dois pedidos mostram como distinguir uma funcionalidade nova de outra que a aplicação já oferece.

[📖 Ler Artigo](./0007_skills_claude_code/article/ARTICLE.md) | [🔧 Executar Localmente](./0007_skills_claude_code/README.md) | [🧪 Exemplos Práticos](./0007_skills_claude_code/examples/README.md)

---

### [0008 - Claude Code e Git Worktrees](./0008_claude_code_worktrees/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Sessões de desenvolvimento em paralelo

Desenvolve uma rota de saúde e uma mudança no dashboard em **Git Worktrees** distintas. Compara o atalho `claude --worktree` ao fluxo explícito do Git e integra as duas alterações em um checkout que verifica os contratos do Agregador.

[📖 Ler Artigo](./0008_claude_code_worktrees/article/ARTICLE.md) | [🔧 Executar Localmente](./0008_claude_code_worktrees/README.md) | [🧪 Exemplos Práticos](./0008_claude_code_worktrees/examples/README.md)

---

### [0009 - OpenCode com 9Router e Ollama](./0009_opencode_9router_ollama/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Gateways e modelos locais

Configura o **OpenCode** para escolher entre um combo do **9Router** e um modelo local do **Ollama**. Uma sonda reproduzível registra o destino e o identificador enviados em cada sessão antes de ligar provedores reais.

[📖 Ler Artigo](./0009_opencode_9router_ollama/article/ARTICLE.md) | [🔧 Executar Localmente](./0009_opencode_9router_ollama/README.md) | [🧪 Exemplos Práticos](./0009_opencode_9router_ollama/examples/README.md)

---

### [0010 - Playwright MCP no dashboard do Agregador](./0010_playwright_mcp_agregador/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Navegador e Model Context Protocol

Conecta **Playwright MCP** ao **Claude Code** e percorre o dashboard do 0005 em um navegador isolado. Busca, favoritos, persistência após recarregar e remoção são comparados com os registros que o Agregador devolve pela API.

[📖 Ler Artigo](./0010_playwright_mcp_agregador/article/ARTICLE.md) | [🔧 Executar Localmente](./0010_playwright_mcp_agregador/README.md) | [🧪 Exemplos Práticos](./0010_playwright_mcp_agregador/examples/README.md)

---

## 📖 Documentação

Índice geral em **[docs/_DOCS.md](./docs/_DOCS.md)**.

### 📘 Guias Operacionais

- **[Ciclo de Vida dos Ambientes](./docs/GUIA_CICLO_DE_VIDA_AMBIENTES.md)** - Provisionamento, inspeção, pausa e destruição completa dos ambientes locais (`start`, `status`, `stop`, `destroy`)
- **[Integração com Claude Code CLI](./docs/GUIA_INTEGRACAO_CLAUDE_CODE.md)** - Conexão da CLI oficial aos gateways de inferência, resolução da URL base e streaming SSE
- **[Permissões e Autonomia no Antigravity](./docs/GUIA_PERMISSOES_ANTIGRAVITY.md)** - Sistema unificado de permissões do Agent 2.0 e configuração do acesso total irrestrito

### 📐 Padrões e Organização

- **[Padrões de Engenharia de IA](./docs/PADROES_ENGENHARIA_IA.md)** - Diretrizes de scripts em Python puro, isolamento de segredos e regras editoriais
- **[Resumo da Organização](./docs/RESUMO_ORGANIZACAO.md)** - Topologia de diretórios, anatomia dos módulos e checklist de publicação
- **[Checklist dos settings do Claude Code](./docs/CHECKLIST_SETTINGS_CLAUDE_CODE.md)** - Regras verificadas para os `settings.local.json` dos exemplos, estado global da CLI e verificador de consistência

### 🔧 Soluções para Problemas Comuns

- **[Problemas Comuns](./docs/SOLUCAO_PROBLEMAS_COMUNS.md)** - Portas ocupadas, modelo local ausente, lock no SQLite e variáveis de ambiente faltando
- **[Token Expirado no Antigravity](./docs/SOLUCAO_TOKEN_EXPIRADO_ANTIGRAVITY.md)** - Diagnóstico e auto-cura de falhas de autenticação `HTTP 401` no gateway

### 📁 Estrutura do Projeto

```text
pathbit-ai-for-devs/
├── README.md                                # Este arquivo
├── AGENTS.md                                # Regras para qualquer agente de código
├── CLAUDE.md                                # Mesmas regras, no arquivo que o Claude Code carrega
├── .githooks/
│   └── commit-msg                           # Remove assinatura de coautoria de IA
├── tmp/                                     # Relatórios e evidências locais
│   ├── RELATORIO_VALIDACAO.md
│   ├── RELATORIO_REVISAO_2026-10-07.md
│   └── prova_no_fio/
├── docs/                                    # Documentação técnica
│   ├── _DOCS.md
│   ├── CHECKLIST_SETTINGS_CLAUDE_CODE.md
│   ├── GUIA_CICLO_DE_VIDA_AMBIENTES.md
│   ├── GUIA_INTEGRACAO_CLAUDE_CODE.md
│   ├── GUIA_PERMISSOES_ANTIGRAVITY.md
│   ├── PADROES_ENGENHARIA_IA.md
│   ├── RESUMO_ORGANIZACAO.md
│   ├── SOLUCAO_PROBLEMAS_COMUNS.md
│   └── SOLUCAO_TOKEN_EXPIRADO_ANTIGRAVITY.md
├── 0001_antigravity_acesso_total_irrestrito/  # Artigo 0001
│   ├── README.md
│   ├── requirements.txt
│   ├── .env.example
│   ├── article/
│   ├── assets/
│   ├── examples/
│   └── src/
├── 0002_claude_gravity_utilizando_9router/    # Artigo 0002
│   ├── README.md
│   ├── requirements.txt
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── article/
│   ├── assets/
│   ├── examples/
│   └── src/
├── 0003_fallback_modelos_gratuitos_9router/   # Artigo 0003
│   ├── README.md
│   ├── requirements.txt
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── article/
│   ├── assets/
│   ├── examples/
│   └── src/
├── 0004_deepclaude_alternativa_ao_claudegravity/  # Artigo 0004
│   ├── README.md
│   ├── requirements.txt
│   ├── article/
│   ├── assets/
│   │   └── diagrams/
│   ├── examples/
│   └── src/
├── 0005_sdd_do_vibe_coding_a_engenharia_deterministica/      # Artigo 0005
│   ├── README.md
│   ├── article/
│   ├── assets/
│   │   └── diagrams/
│   ├── src/
│   ├── tests/
│   └── examples/
│       ├── specs/
│       └── .claude/
├── 0006_openspec_claude_code/  # Artigo 0006
├── 0007_skills_claude_code/  # Artigo 0007
├── 0008_claude_code_worktrees/  # Artigo 0008
├── 0009_opencode_9router_ollama/  # Artigo 0009
└── 0010_playwright_mcp_agregador/  # Artigo 0010
```

---

## 🤖 Regras para Agentes de Código

Qualquer agente que opere neste repositório — Claude Code, Codex, Cursor, Copilot, Devin ou outro — segue as regras de **[AGENTS.md](./AGENTS.md)**. As três inegociáveis:

1. **Agentes de código jamais assinam commits.** Use a identidade humana e mantenha mensagens de commit, tags e pull requests livres de trailers de agente, como `Co-Authored-By`, `Claude-Session` e `Generated-by`.
2. **Conta de agente nunca é colaboradora** do repositório.
3. **O mantenedor humano realiza a assinatura criptográfica**, quando a branch exigir.

O motivo é concreto: o GitHub monta a lista de *Contributors* da página pública a partir dos trailers `Co-authored-by`. Um único trailer coloca a conta do agente como contribuidora do projeto.

Ao clonar, ative o hook que higieniza as mensagens (o Git não versiona `.git/hooks`):

```bash
make setup
```

(equivale a `git config core.hooksPath .githooks`)

E confira antes de publicar:

```bash
make valida-consistencia
```

---

## 📋 Estrutura Padrão dos Artigos

```text
XXXX_titulo_do_artigo/
├── README.md                            # Instruções de execução e resumo
├── requirements.txt                     # Dependências Python
├── docker-compose.yml                   # Orquestração de containers (quando aplicável)
├── .env.example                         # Modelo de variáveis de ambiente
├── article/
│   └── ARTICLE.md                       # Conteúdo do artigo
├── assets/                              # Capturas de tela e diagramas (PNG)
│   └── diagrams/                        # Fonte HTML de cada diagrama, para regeração
├── examples/                            # Ambiente isolado de execução e testes
│   ├── README.md                        # Instruções de execução do Claude Code
│   ├── sample_task.py                   # Código de exemplo para o agente
│   └── .claude/
│       └── settings.local.json.example  # Template do settings pessoal (a cópia ativa é ignorada pelo Git)
└── src/                                 # Scripts executáveis em Python
```

Os artigos exibem apenas os **PNG**. Cada diagrama guarda seu fonte em `assets/diagrams/`, um HTML
autocontido com SVG embutido, para que a figura possa ser reeditada e reexportada sem refazê-la do
zero. As capturas de tela não têm fonte: são registros de execução real.

---

## 🧪 Execução de Testes

A suíte local reúne consistência editorial, os exemplos Python e os testes do Agregador. A integração dos artigos 0002 e 0003 usa uma stack com os provedores já provisionados.

### Exemplos dos artigos sobre ferramentas

Com [Python 3.10 ou posterior](https://www.python.org/downloads/), Git e Make, a suíte verifica a preparação das cópias do Agregador, os patches do laboratório de worktrees e a configuração do OpenCode. Cada guia traz o comando para repetir sua verificação específica.

```bash
make test-articles
```

### Suíte local do repositório

Para executar também os testes do Agregador, use o [Node.js com npm](https://nodejs.org/en/download). A suíte foi verificada com Node.js 22. Use a mesma versão do Node na instalação e nos testes do módulo nativo de SQLite.

```bash
npm ci --prefix 0005_sdd_do_vibe_coding_a_engenharia_deterministica
make test-unit test-app
```

### Opção 1. Diagnóstico e integração em contêiner

O executor conecta os testes Python à rede do gateway. Suba e configure o artigo correspondente antes de usá-lo. Os testes de inferência usam a chave local do 9Router, lida de `ANTHROPIC_API_KEY` ou de um `.env` reconhecido pelo script do artigo.

```bash
./tools/run_tests.sh 0002 --somente-saude
./tools/run_tests.sh 0003 --combo arsenal-offline

# Testes completos contra uma stack com provedores e combos dos dois artigos
make test-container
```

Para uma rede ou URL diferente, defina `ROUTER_NETWORK` e `ROUTER_URL`.

### Opção 2. Via Virtual Environment Local (Pré-requisitos Opcionais)

Se desejar executar diretamente no host com Python 3.14+:

```bash
source .venv/bin/activate
make test-local
```

### Opção 3. Consistência entre os Artigos e o Repositório

Um artigo é publicado uma vez e lido por muito tempo. Quando um arquivo é renomeado ou um print
substituído, o texto continua afirmando o que era verdade antes — e o leitor segue instruções que já
não funcionam, sem ter como saber que o errado é o texto.

```bash
make valida-consistencia
```

Confere que todo bloco `json` de configuração citado num artigo é idêntico ao `.example` versionado,
que toda imagem referenciada existe (e que todo asset é citado), que os links relativos apontam para
arquivos reais, que nenhum comando instrui o uso do nome antigo `.claude/settings.json` e que nenhum
exemplo carrega o sufixo `[1m]`. Não precisa de rede nem de container.

Para validar a configuração do artigo 0004, incluindo uma inferência real contra o provedor ativo:

```bash
make valida-deepclaude              # offline
make valida-deepclaude ONLINE=1     # com chamada real à API
```

### Opção 4. Prova no Fio (o que a CLI realmente envia)

Os artigos prometem que nenhum modelo da Anthropic é usado, que o sufixo `[1m]` não viaja, que o
advisor não é anexado e que a credencial vai por `Authorization: Bearer`. Nada disso se comprova
lendo o arquivo de configuração — só olhando a requisição HTTP.

```bash
make prova-no-fio              # todos os artigos
make prova-no-fio ARTIGO=0004  # só um
```

Sobe uma sonda local que finge ser a API da Anthropic, roda o Claude Code de verdade com o settings
de cada artigo e dispara três sessões por cenário, duas delas pedindo um modelo da Anthropic de
propósito (`--model claude-opus-5`) para verificar que o `modelOverrides` intercepta. Não precisa de
gateway de pé, credencial real nem rede externa.

### Opção 5. Validação Cruzada com os Projetos RTK

Os artigos mandam o leitor copiar um `docker-compose.yml` que sobe imagens dos
projetos [9RTKSync](https://github.com/pathbit/9RTKSync),
[OmniRTKSync](https://github.com/pathbit/OmniRTKSync) e
[LiteLlmRTKSync](https://github.com/pathbit/LiteLlmRTKSync). Quando um desses
projetos muda e o artigo não, o leitor segue instruções que não funcionam mais —
e não tem como saber que o errado é o texto.

```bash
make valida-docs
```

Confere, para cada compose de artigo que usa uma imagem RTKSync: se a porta
interna publicada é a que o serviço realmente escuta, e se toda variável de
ambiente passada ao container é lida pelo projeto. Não precisa de nenhum
container de pé — basta ter os projetos RTK clonados ao lado deste repositório.
Sai com código diferente de zero quando encontra divergência.

Com o 9RTKSync e o OmniRTKSync em ambiente de teste, execute a verificação HTTP dos painéis. Ela cobre autenticação, CSRF, cabeçalhos de segurança, troca de senha e ausência de credenciais nas respostas.

Exporte `NOVE_USER`, `NOVE_PASS` e `NOVE_NOVA` para o 9RTKSync e `OMNI_USER`, `OMNI_PASS` e `OMNI_NOVA` para o OmniRTKSync. Os sufixos `PASS` e `NOVA` identificam a senha atual e a nova senha de teste. As URLs padrão são `http://127.0.0.1:9091` e `http://127.0.0.1:9092`. Ajuste `NOVE_URL` e `OMNI_URL` se a bancada usar outras portas.

```bash
make valida-paineis
```

A senha de teste muda quando o painel permite editá-la pela interface. Se a senha vier de `DASHBOARD_PASSWORD`, o script verifica a recusa da alteração. [Script de validação dos painéis](./tools/valida_paineis.sh)

---

## Contributing and Branch Protection

1. Crie um fork e clone-o.
2. Crie uma pasta `XXXX_titulo_do_artigo` seguindo a estrutura de artigos.
3. Adicione o artigo à lista deste README, execute `make valida-consistencia` e rode as verificações aplicáveis ao laboratório antes de solicitar revisão.
4. Abra um pull request do seu fork para `master` e aguarde a revisão.

Para informar um erro ou sugerir um artigo, [abra uma issue](https://github.com/pathbit/pathbit-ai-for-devs/issues).

---

## 📄 License

Distribuído sob a **Licença MIT**. O texto completo está em [LICENSE](./LICENSE).

Na prática: use, copie, altere e redistribua à vontade, inclusive comercialmente, desde que o aviso de
copyright e a licença acompanhem as cópias. O software é fornecido *como está*, sem garantias.

---

Developed with ❤️ by [Pathbit](https://www.pathbit.com.br/)
