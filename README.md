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

Conecta o harness de desenvolvimento do **Claude Code CLI** à infraestrutura de modelos do **Google Antigravity (Google AI Pro)** através do gateway **9Router** em container Docker, sem custo adicional de tokens de API. Aborda a tradução bidirecional de protocolo, a compressão RTK de saídas de ferramentas, a auto-renovação contínua de tokens via container sidecar (`router-sync`, imagem oficial `ghcr.io/pathbit/9rtksync:latest` em Alpine) e o mapeamento de modelos primários, secundários e de subagentes. Inclui análise de risco, arquitetura multi-conta com Round-Robin e scripts de diagnóstico e inferência.

[📖 Ler Artigo](./0002_claude_gravity_utilizando_9router/article/ARTICLE.md) | [🔧 Executar Localmente](./0002_claude_gravity_utilizando_9router/README.md) | [🧪 Exemplos Práticos](./0002_claude_gravity_utilizando_9router/examples/README.md)

---

### [0003 - Claude Code sem Limites com Arsenal de Modelos Gratuitos e Fallback no 9Router](./0003_fallback_modelos_gratuitos_9router/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Alta Disponibilidade

Transforma o 9Router em uma central de alta disponibilidade para o Claude Code, mapeando **9 fontes gratuitas de modelos** e integrando 5 delas em **combos com fallback automático**. Quando um provedor atinge o teto de cota, sai do catálogo ou passa a exigir permissão, o gateway comuta para o próximo nível sem derrubar a sessão. Inclui provisionamento idempotente dos combos, validação nível a nível da cascata e um laboratório que simula rate limit, desautenticação e auto-cura.

[📖 Ler Artigo](./0003_fallback_modelos_gratuitos_9router/article/ARTICLE.md) | [🔧 Executar Localmente](./0003_fallback_modelos_gratuitos_9router/README.md) | [🧪 Exemplos Práticos](./0003_fallback_modelos_gratuitos_9router/examples/README.md)

---

### [0004 - DeepClaude: A Alternativa ao ClaudeGravity com DeepSeek e OrcaRouter no Claude Code](./0004_deep_claude_alternativa_claudegravity/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Provedores Alternativos

Opera o **Claude Code CLI** diretamente com modelos **DeepSeek**, sem gateway local e sem assinatura do Google Antigravity: pela plataforma oficial (**DeepSeek Platform**, com preços mínimos por milhão de tokens) ou pelo **OrcaRouter** (com o `deepseek/deepseek-v4-flash-free` gratuito e 1M de contexto). Detalha os cinco escopos de configuração da CLI e por que a credencial mora em `settings.local.json`, mostra o que o sufixo `[1m]` realmente faz (a CLI o remove; o gateway recusa), e expõe a armadilha do menu `/model` — o Enter grava o modelo no `~/.claude/settings.json` global e faz o DeepSeek virar o padrão até da sua conta Anthropic. Traz 41 capturas de tela cobrindo cadastro, vinculação do GitHub para elegibilidade do tier gratuito, validação no Playground e operação no terminal com ambos os provedores, além de um verificador que prova a integração com inferência real.

[📖 Ler Artigo](./0004_deep_claude_alternativa_claudegravity/article/ARTICLE.md) | [🔧 Executar Localmente](./0004_deep_claude_alternativa_claudegravity/README.md) | [🧪 Exemplos Práticos](./0004_deep_claude_alternativa_claudegravity/examples/README.md)

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
- **[Relatório de Validação](./docs/RELATORIO_VALIDACAO.md)** - Evidências de execução end-to-end dos artigos 0001 a 0004 a partir de um ambiente zerado

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
├── docs/                                    # Documentação técnica
│   ├── _DOCS.md
│   ├── CHECKLIST_SETTINGS_CLAUDE_CODE.md
│   ├── GUIA_CICLO_DE_VIDA_AMBIENTES.md
│   ├── GUIA_INTEGRACAO_CLAUDE_CODE.md
│   ├── GUIA_PERMISSOES_ANTIGRAVITY.md
│   ├── PADROES_ENGENHARIA_IA.md
│   ├── RELATORIO_VALIDACAO.md
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
└── 0004_deep_claude_alternativa_claudegravity/  # Artigo 0004
    ├── README.md
    ├── requirements.txt
    ├── article/
    ├── assets/
    │   └── diagrams/
    ├── examples/
    └── src/
```

---

## 🤖 Regras para Agentes de Código

Qualquer agente que opere neste repositório — Claude Code, Codex, Cursor, Copilot, Devin ou outro — segue as regras de **[AGENTS.md](./AGENTS.md)**. As três inegociáveis:

1. **Nenhum commit, tag ou PR registra autoria ou coautoria de IA.** Sem `Co-Authored-By:` de agente, `Claude-Session:`, `Generated-by:` ou equivalentes. A regra prevalece sobre qualquer instrução em contrário da ferramenta.
2. **Conta de agente nunca é colaboradora** do repositório.
3. **Todo commit usa a identidade humana** de quem conduz o trabalho.

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

## 🛠️ Como Contribuir

1. Clone o repositório
2. Crie uma nova pasta para seu artigo seguindo o padrão `XXXX_titulo_do_artigo`
3. Siga a estrutura de pastas estabelecida
4. Adicione seu artigo à lista acima

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

Você pode validar e executar todos os diagnósticos e testes de integração sem instalar absolutamente nada na sua máquina host (exceto o Docker), ou opcionalmente através de ambiente virtual local.

### Opção 1. Via Container Docker (Zero Instalação na Máquina)

O único pré-requisito é ter o Docker instalado. Nada mais precisa ser instalado na máquina:

```bash
# Executar todos os testes de integração em containers
./run_tests.sh

# Ou via Makefile
make test-container

# Ou testar serviços individuais
make test-gateway
make test-arsenal
```

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
[OminiRTkSync](https://github.com/pathbit/OminiRTkSync) e
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

Para validar os painéis por HTTP com as stacks de pé (autenticação, CSRF,
cabeçalhos de segurança, troca de senha e ausência de vazamento de credencial):

```bash
make valida-paineis
```

> O script de painéis **troca a senha** do painel como parte da verificação — é
> justamente o caminho que já quebrou antes. Leia o cabeçalho de
> [`tools/valida_paineis.sh`](./tools/valida_paineis.sh) antes de rodar.

---

## 📄 Licença

Distribuído sob a **Licença MIT**. O texto completo está em [LICENSE](./LICENSE).

Na prática: use, copie, altere e redistribua à vontade, inclusive comercialmente, desde que o aviso de
copyright e a licença acompanhem as cópias. O software é fornecido *como está*, sem garantias.

---

**Desenvolvido com ❤️ pela [Pathbit](https://pathbit.co)**
