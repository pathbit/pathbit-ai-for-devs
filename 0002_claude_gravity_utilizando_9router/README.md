# pathbit-ai-for-devs

## 0002_claude_gravity_utilizando_9router

![Capa - ClaudeGravity](assets/00_cover_claudegravity.png)

**Ano:** 2026
**ID do Artigo:** 0002
**Autor:** Eliel Sousa
**Categoria:** Engenharia de IA / Claude Code / Gateways e Model Routing

---

### Resumo

Este módulo apresenta o **ClaudeGravity**, arquitetura que conecta o harness de desenvolvimento do **Claude Code** aos modelos de alta capacidade do **Google Antigravity (Google AI Pro)** utilizando o gateway inteligente **9Router**.

Enquanto o mercado popularizou o conceito de *DeepClaude* (DeepSeek como cérebro de raciocínio dentro do harness do Claude Code), o **ClaudeGravity** desbloqueia o ecossistema Gemini (3.8, 3.7, 3.6 e Gemini Pro) com contexto de 1 milhão de tokens, aproveitando sua assinatura AI Pro sem cobrança de tokens na API do Google AI Studio.

- Base fundamentada no [Artigo 0001 - Google Antigravity com Acesso Total Irrestrito e sem Interrupções](../0001_antigravity_acesso_total_irrestrito/) para destravar o motor Agent 2.0.
- Execução isolada via **Docker Compose** (método recomendado para produção).
- Alternativa de instalação **Nativa (CLI)**.
- Roteamento nativo para **Gemini 3.8 Flash**, **Gemini 3.7 Flash**, **Gemini 3.6 Flash**, **Gemini 3.1 Pro**, **Claude Sonnet 4.6 (Thinking)** e **GPT-OSS 120B**.
- Configuração de zero-interrupção com `--dangerously-skip-permissions` no Claude Code e AGY.
- Ativação de recursos avançados: loops, advisors, goal mode e integração irrestrita com MCPs e terminal.
- Economia de 20% a 40% de tokens via compressão automática de payloads de ferramentas com **RTK Token Saver**.

---

### Tecnologias e Modelos Utilizados

- **Harness & Agent CLI:** `Claude Code CLI v2.1+`
- **Gateway & Proxy Inteligente:** `9Router v0.5.69+` (Container Docker / Node.js)
- **Modelos Gemini Suportados:**
  - `ag/gemini-3.8-flash-high` (Gemini 3.8 Flash High Thinking e Raciocínio Profundo)
  - `ag/gemini-3.8-flash-medium` e `ag/gemini-3.8-flash-low`
  - `ag/gemini-3.7-flash-high` (Gemini 3.7 Flash Fast e Accurate)
  - `ag/gemini-3.6-flash-high` (Gemini 3.6 Flash Low Latency)
  - `ag/gemini-pro-agent` (Gemini 3.1 Pro para Arquitetura e Agentes Complexos)
- **Outros Modelos via Antigravity:**
  - `ag/claude-sonnet-4-6` e `ag/claude-opus-4-6-thinking`
  - `ag/gpt-oss-120b-medium`
- **Ambiente:** Docker 29+, Node.js 22+, Python 3.14+

---

### Estrutura de Arquivos

```text
0002_claude_gravity_utilizando_9router/
├── README.md                      # Este arquivo
├── requirements.txt               # Dependências Python para scripts de diagnóstico
├── docker-compose.yml             # Orquestração do gateway 9Router em container
├── .env.example                   # Modelo de variáveis de ambiente do gateway e Claude
├── article/
│   └── ARTICLE.md                 # Artigo técnico completo e aprofundado
├── assets/                        # Imagens, telas e diagramas do artigo (sequenciados 00 a 12)
│   ├── diagrams/                  # Fontes vetoriais semânticas em HTML e SVG (diagram-design)
│   ├── 00_cover_claudegravity.png
│   ├── 01_diagrama_arquitetura_claudegravity.png
│   ├── 02_docker_container_running.png
│   ├── 03_9router_login.png
│   ├── 04_9router_dashboard.png
│   ├── 05_9router_providers.png
│   ├── 06_9router_antigravity_connected.png
│   ├── 07_9router_antigravity_provider.png
│   ├── 08_9router_cli_tools.png
│   ├── 09_9router_claude_code_config.png
│   ├── 10_9router_combos.png
│   ├── 11_claude_gravity_terminal.png
│   └── 12_diagrama_arquitetura_equipes.png
├── examples/                      # Espaço isolado de execução e testes práticos do Claude Code
│   ├── README.md                  # Instruções de execução do Claude Code
│   ├── sample_task.py             # Código de exemplo para testes práticos
│   └── .claude/
│       ├── settings.json.example  # Modelo de configurações compartilhadas do Claude Code
│       └── settings.local.json.example # Modelo de menu interativo /model e permissões
└── src/
    ├── claudegravity.py           # Launcher CLI do Claude Code pré-configurado (Python)
    ├── manage_env.py              # Gerenciador do ciclo de vida do ambiente (start, stop, destroy, status)
    ├── sync_antigravity_token.py  # Sincronizador de tokens OAuth Google Antigravity para o 9Router (Python)
    ├── test_gateway.py            # Script de validação dos endpoints e modelos do gateway (Python)
    └── verify_setup.py            # Diagnóstico automatizado do ambiente (Python)
```

---

### Como Executar

#### 1. Pré-requisitos do Ambiente

Antes de iniciar o gateway e executar o Claude Code, certifique-se de que as ferramentas e credenciais abaixo estejam instaladas e prontas:

1. **Python 3.10 ou Superior:**
   - Verifique com `python3 --version`. Se necessário, instale:
     - macOS: `brew install python` ou via pyenv `pyenv install 3.12`
     - Linux (Ubuntu/Debian): `sudo apt update && sudo apt install -y python3 python3-venv python3-pip`
     - Windows: `winget install Python.Python.3.12`

2. **Ambiente Virtual Dedicado (venv):**
   - Crie e ative o ambiente virtual para isolar as dependências e ferramentas do módulo:
   ```bash
   python3 -m venv .venv

   # Ativar no macOS e Linux
   source .venv/bin/activate

   # Ativar no Windows (PowerShell)
   .venv\Scripts\Activate.ps1

   # Instalar dependências
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Docker e Docker Compose:**
   - O 9Router é executado em container Docker. Caso ainda não tenha o Docker instalado:
     - **macOS:** Instale o Docker Desktop com `brew install --cask docker` ou pelo instalador DMG em [docker.com](https://www.docker.com/).
     - **Linux:** Instale via script oficial com `curl -fsSL https://get.docker.com | sh` e adicione seu usuário com `sudo usermod -aG docker $USER`.
     - **Windows:** Instale o Docker Desktop com `winget install Docker.DockerDesktop` habilitando o backend WSL2.
   - Valide que o serviço está ativo com `docker --version` e `docker compose version`.

4. **Node.js e Claude Code CLI:**
   - O Claude Code requer Node.js 18 ou superior. Se necessário, instale:
     - **macOS:** `brew install node`
     - **Linux:** `sudo apt install -y nodejs npm`
     - **Windows:** `winget install OpenJS.NodeJS`
   - Instale o Claude Code globalmente:
     ```bash
     npm install -g @anthropic-ai/claude-code
     ```
   - Verifique com `claude --version`.

5. **Conta Google com Antigravity (Google AI Pro) e Navegador Logado:**
   - Possuir uma conta Google ativa com o plano Google AI Pro, Google One AI Premium ou Workspace com Gemini.
   - Faça login prévio no **Google Antigravity IDE** ou na CLI `agy` na sua máquina (`agy --version`). Esse passo gera as credenciais OAuth locais em `~/.gemini/` que o script `src/sync_antigravity_token.py` consome e renova automaticamente para o gateway.
   - **Mandatório para o 9Router:** O dashboard (`http://localhost:20128/dashboard`) deve ser aberto no mesmo perfil de navegador em que essa conta com a licença está autenticada.

#### 2. Preparar Arquivos de Configuração

Na pasta deste módulo, inicialize as configurações a partir dos modelos `.example`:

```bash
cd 0002_claude_gravity_utilizando_9router
cp .env.example .env
cp examples/.claude/settings.json.example examples/.claude/settings.json
cp examples/.claude/settings.local.json.example examples/.claude/settings.local.json
```

#### 3. Gerenciamento do Ciclo de Vida do Ambiente (Criar e Destruir)

##### Opção A (Via Utilitário Python de Ciclo de Vida)

```bash
# Iniciar o ambiente, sincronizar credenciais e validar integridade
python3 src/manage_env.py start

# Consultar a saúde do container e do gateway HTTP
python3 src/manage_env.py status

# Pausar containers (preservando configurações e dados)
python3 src/manage_env.py stop

# DESTRUIR TUDO (remove containers, redes e volumes Docker completamente)
python3 src/manage_env.py destroy
```

##### Opção B (Via Docker Compose Nativo)

```bash
# Iniciar o gateway em segundo plano
docker compose up -d

# Verificar se o container está saudável
docker ps --filter "name=claudegravity-router"

# Pausar o gateway
docker compose stop

# DESTRUIR TUDO (remover container e volume persistente)
docker compose down -v --remove-orphans
```

O dashboard estará disponível em:
👉 **http://localhost:20128** (ou `http://localhost:20128/dashboard`)

#### 4. Conectar a Conta Antigravity no Dashboard (Atenção ao Perfil Correto)

> **Pré-requisito Vital:** Abra o navegador na janela ou perfil onde você está logado na **conta Google titular da assinatura Antigravity / AI Pro**. Se o 9Router for vinculado a uma conta gratuita pessoal por engano, os modelos recusarão requisições com erro `HTTP 403 Forbidden`.

1. Abra `http://localhost:20128/dashboard/providers` no seu navegador.
2. Localize o card **Antigravity** na seção *OAuth Providers* e clique nele.
3. Clique no botão **+ Add Connection**.
4. Uma janela segura de autenticação Google será aberta. Selecione expressamente sua conta Google que possui o plano **AI Pro / Antigravity**.
5. O 9Router validará a assinatura, salvará o token OAuth seguro e exibirá o status **`active • OAuth #1`**.
6. Valide a conexão no terminal executando:
   ```bash
   python3 src/test_gateway.py
   ```

#### 5. Alternativa de Instalação Nativa (Sem Docker)

Se preferir rodar direto na máquina host via Node.js/npm:

```bash
npm install -g 9router
9router
```

O serviço abrirá a mesma porta `20128` localmente.

---

### Configuração do Claude Code (Zero Interrupção)

Para evitar prompts repetitivos de autorização para cada comando bash ou edição de arquivo, utilize o modo **`bypassPermissions`**:

#### Opção A (Execução via script Python fornecido)

```bash
# Modo 1 - ClaudeGravity Principal (Gemini 3.8 Flash High - Antigravity Pro)
python3 src/claudegravity.py

# Modo 2 - ClaudeGravity Resiliente (Fallback Automático com Modelos Gratuitos)
python3 src/claudegravity.py --model claudegravity-fallback

# Outros modelos específicos
python3 src/claudegravity.py --model ag/gemini-3.7-flash-high
```

Para listar todos os modelos disponíveis:

```bash
python3 src/claudegravity.py --list-models
```

#### Opção B (Execução manual via Terminal)

> A chave é gerada localmente na primeira execução de `src/sync_antigravity_token.py` e gravada no `.env` do módulo (não versionado). Substitua o placeholder abaixo pelo valor que o script imprimir.

```bash
# macOS e Linux (bash / zsh)
export ANTHROPIC_BASE_URL="http://localhost:20128"
export ANTHROPIC_API_KEY="sk-sua-chave-do-9router"

# Windows (PowerShell)
$env:ANTHROPIC_BASE_URL="http://localhost:20128"
$env:ANTHROPIC_API_KEY="sk-sua-chave-do-9router"

# Teste 1 - ClaudeGravity Principal
claude --dangerously-skip-permissions --model ag/gemini-3.8-flash-high

# Teste 2 - ClaudeGravity com Fallback Gratuito
claude --dangerously-skip-permissions --model claudegravity-fallback
```

> **Dica para o Antigravity CLI** O mesmo padrão de flag aplica-se ao CLI do Google.

```bash
agy --dangerously-skip-permissions
```

---

### Diagnóstico e Testes

Para validar a integridade de todos os serviços:

```bash
# Diagnóstico completo com Python
python3 src/verify_setup.py

# Teste de endpoints, listagem de modelos e inferência
python3 src/test_gateway.py
```

---

### O que você vai aprender

1. Como desacoplar o harness de execução (Claude Code) do provedor de inferência proprietário.
2. Como configurar gateways de tradução de protocolo (OpenAI ↔ Claude ↔ Google Cloud Code).
3. Como economizar tokens com o pipeline RTK embutido no 9Router.
4. Como utilizar recursos experimentais, loops contínuos e permissões bypass sem atritos no Claude Code.
5. Como alternar dinamicamente entre Gemini 3.8 Flash, 3.7 Flash, 3.6 Flash e Gemini 3.1 Pro.
6. Gestão de segurança, mitigação de riscos, desmistificação do `RISK_NOTICE` e boas práticas com contas dedicadas.
7. Arquitetura para equipes: Connection Pooling Multi-Contas (Round-Robin) e isolamento estrito de sessões.

---

### Links úteis

- Artigo completo: [ARTICLE.md](./article/ARTICLE.md)
- Artigo 0003 (Claude Code sem Limites com Arsenal de Modelos Gratuitos e Fallback no 9Router): [0003_fallback_modelos_gratuitos_9router](../0003_fallback_modelos_gratuitos_9router/README.md)
- Repositório: [pathbit-ai-for-devs](https://github.com/pathbit/pathbit-ai-for-devs)
