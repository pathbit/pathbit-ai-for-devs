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

Conecta o harness de desenvolvimento do **Claude Code CLI** à infraestrutura de modelos do **Google Antigravity (Google AI Pro)** através do gateway **9Router** em container Docker, sem custo adicional de tokens de API. Aborda a tradução bidirecional de protocolo, a compressão RTK de saídas de ferramentas, a renovação automática de credenciais OAuth e o mapeamento de modelos primários, secundários e de subagentes. Inclui análise de risco, arquitetura multi-conta com Round-Robin e scripts de diagnóstico e inferência.

[📖 Ler Artigo](./0002_claude_gravity_utilizando_9router/article/ARTICLE.md) | [🔧 Executar Localmente](./0002_claude_gravity_utilizando_9router/README.md) | [🧪 Exemplos Práticos](./0002_claude_gravity_utilizando_9router/examples/README.md)

---

### [0003 - Claude Code sem Limites com Arsenal de Modelos Gratuitos e Fallback no 9Router](./0003_fallback_modelos_gratuitos_9router/)

**Ano:** 2026 | **Categoria:** Engenharia de IA / Alta Disponibilidade

Transforma o 9Router em uma central de alta disponibilidade para o Claude Code, mapeando **9 fontes gratuitas de modelos** e integrando 5 delas em **combos com fallback automático**. Quando um provedor atinge o teto de cota, sai do catálogo ou passa a exigir permissão, o gateway comuta para o próximo nível sem derrubar a sessão. Inclui provisionamento idempotente dos combos, validação nível a nível da cascata e um laboratório que simula rate limit, desautenticação e auto-cura.

[📖 Ler Artigo](./0003_fallback_modelos_gratuitos_9router/article/ARTICLE.md) | [🔧 Executar Localmente](./0003_fallback_modelos_gratuitos_9router/README.md) | [🧪 Exemplos Práticos](./0003_fallback_modelos_gratuitos_9router/examples/README.md)

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
- **[Relatório de Validação](./docs/RELATORIO_VALIDACAO.md)** - Evidências de execução end-to-end dos três artigos a partir de um ambiente zerado

### 🔧 Soluções para Problemas Comuns

- **[Problemas Comuns](./docs/SOLUCAO_PROBLEMAS_COMUNS.md)** - Portas ocupadas, modelo local ausente, lock no SQLite e variáveis de ambiente faltando
- **[Token Expirado no Antigravity](./docs/SOLUCAO_TOKEN_EXPIRADO_ANTIGRAVITY.md)** - Diagnóstico e auto-cura de falhas de autenticação `HTTP 401` no gateway

### 📁 Estrutura do Projeto

```text
pathbit-ai-for-devs/
├── README.md                                # Este arquivo
├── docs/                                    # Documentação técnica
│   ├── _DOCS.md
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
└── 0003_fallback_modelos_gratuitos_9router/   # Artigo 0003
    ├── README.md
    ├── requirements.txt
    ├── docker-compose.yml
    ├── .env.example
    ├── article/
    ├── assets/
    ├── examples/
    └── src/
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
│       ├── settings.json.example        # Políticas de permissão compartilhadas
│       └── settings.local.json.example  # Preferências locais e menu de modelos
└── src/                                 # Scripts executáveis em Python
```

Os artigos exibem apenas os **PNG**. Cada diagrama guarda seu fonte em `assets/diagrams/`, um HTML
autocontido com SVG embutido, para que a figura possa ser reeditada e reexportada sem refazê-la do
zero. As capturas de tela não têm fonte: são registros de execução real.

---

**Desenvolvido com ❤️ pela [Pathbit](https://pathbit.com)**
