# pathbit-ai-for-devs

## 0003_fallback_modelos_gratuitos_9router

![Capa - Combos de Fallback e Modelos Gratuitos](assets/00_cover_arsenal_fallback.png)

**Ano:** 2026
**ID do Artigo:** 0003
**Autor:** Eliel Sousa
**Categoria:** Engenharia de IA / Claude Code / Gateways e Model Routing

---

### Resumo

Guia prático e orquestração de infraestrutura para criar um ecossistema de alta disponibilidade para o **Claude Code**, mapeando **9 provedores gratuitos de inteligência artificial** e integrando 5 deles nos **Combos com Fallback Automático do 9Router**.

---

### Destaques da Solução

- **Zero Paradas por Rate Limit (HTTP 429):** Comutação automática para o próximo modelo do combo quando o provedor atual falha por cota, indisponibilidade ou descontinuação  -  sem derrubar a sessão do Claude Code.
- **9 Provedores Gratuitos Mapeados:** Antigravity (Google AI Pro), Kiro AWS Builder, Google AI Studio, Groq Cloud, Cerebras, OpenRouter Free, Cloudflare Workers AI, Mistral e Ollama Local. Os combos de referência integram Antigravity, OpenRouter, Groq, Mistral e Ollama Local; os demais ficam documentados como extensões da mesma cascata.
- **Laboratório de Simulação de Falhas:** Script automatizado (`src/simulate_fallback.py`) para validar cenários de erro 429, desautenticação de token (401) e auto-cura em tempo real.
- **Continuidade Local com Ollama:** o nível final da cascata roda na sua máquina e garante que o gateway sempre devolva resposta, mesmo com todos os provedores em nuvem fora do ar. Testamos o harness do Claude Code com modelos de 0.5B a 7B: todos respondem à API, mas nenhum conduz uma sessão real de trabalho  -  trate o nível local como garantia de continuidade, não como substituto dos níveis em nuvem.
- **Sidecar de Auto-Renovação Contínua:** Container `claudegravity-token-sync` (imagem oficial `python:3.14-alpine` com o daemon `token_daemon.py`), monitorando o SQLite e mantendo a credencial do Antigravity renovada sem quedas na cascata.
- **Autonomia Total sem Fricção:** Configurado com `--dangerously-skip-permissions` e `bypassPermissions` no `.claude/settings.json`.
- **Compatibilidade com 9Router e OmniRoute:** Explicação detalhada da resolução de URLs (`http://localhost:20128` vs `http://localhost:20128/v1`) e regras de nomenclatura de combos.
- **Passo a Passo Visual Completo:** Prints reais de cada portal para obtenção dos tokens gratuitos e da configuração gráfica de provedores e combos no 9Router.
- **Scripts em Python Puro:** Provisionamento e testes 100% em Python, compatíveis com qualquer sistema operacional.

---

### Estrutura de Arquivos do Módulo

```text
0003_fallback_modelos_gratuitos_9router/
├── README.md                              # Este arquivo com resumo executivo e instruções
├── requirements.txt                       # Dependências Python mínimas (requests)
├── docker-compose.yml                     # Orquestração do gateway 9Router em container
├── .env.example                           # Modelo de variáveis de ambiente e chaves gratuitas
├── article/
│   └── ARTICLE.md                         # Artigo técnico completo, ilustrado e aprofundado
├── assets/                                # Capturas reais de tela e capas (sequenciados 00 a 22)
│   ├── diagrams/                          # Fontes vetoriais semânticas em HTML (diagram-design)
│   ├── cover_linkedin.png              # Capa para compartilhamento no LinkedIn
│   ├── 00_cover_arsenal_fallback.png      # Capa do artigo
│   ├── 01_diagrama_malha_multiprovedor.png# Diagrama da malha multi-provedor
│   ├── 02_openrouter_dashboard_keys.png   # Painel de chaves no OpenRouter
│   ├── 03_openrouter_obter_api_key.png    # Captura da chave no OpenRouter
│   ├── 04_groq_dashboard_keys.png         # Painel de chaves na Groq
│   ├── 05_groq_obter_api_key.png          # Captura da chave na Groq Cloud
│   ├── 06_google_aistudio_dashboard.png   # Painel de chaves no Google AI Studio
│   ├── 07_google_aistudio_obter_api_key.png# Captura da chave no AI Studio
│   ├── 08_ollama_setup_local.png          # Download e execução do Ollama via Docker
│   ├── 09_ollama_dashboard_keys.png       # Painel de chaves no portal Ollama
│   ├── 10_ollama_obter_api_key.png        # Captura da chave no Ollama
│   ├── 11_9router_provider_openrouter.png # Gestão de conexão OpenRouter no 9Router
│   ├── 12_9router_add_connection_modal.png# Modal de cadastro de API key no 9Router
│   ├── 13_9router_provider_groq.png       # Gestão de conexão Groq no 9Router
│   ├── 14_9router_provider_ollama.png     # Gestão de conexão Ollama no 9Router
│   ├── 15_9router_create_combo_modal.png  # Modal de criação de combo no 9Router
│   ├── 16_9router_edit_combo_cascade.png  # Ordem hierárquica da cascata de fallback
│   ├── 17_diagrama_cascata_fallback.png   # Diagrama da cascata de fallback
│   ├── 18_9router_combos.png              # Grade de combos ativos no 9Router
│   ├── 19_9router_dashboard_endpoint.png  # Configuração do endpoint e chave
│   ├── 20_docker_container.png            # Execução dos containers Docker
│   ├── 21_simulacao_fallback_laboratorio.png # Terminal com simulação de fallback
│   └── 22_claude_arsenal_terminal.png     # Execução do Claude Code com o combo ativo
├── examples/                              # Espaço isolado de execução e testes práticos do Claude Code
│   ├── README.md                          # Instruções de execução do Claude Code
│   ├── sample_task.py                     # Código de exemplo para testes práticos
│   └── .claude/
│       ├── settings.json.example          # Configurações compartilhadas apontando para o combo
│       └── settings.local.json.example    # Configurações locais com menu /model customizado
└── src/
    ├── arsenal_launcher.py                # Launcher CLI para iniciar o Claude Code conectado ao combo
    ├── manage_env.py                      # Gerenciador do ciclo de vida do ambiente (start, stop, destroy, status)
    ├── setup_combos.py                    # Provisionamento idempotente de combos no SQLite do 9Router
    ├── simulate_fallback.py               # Laboratório de simulação de falhas, rate limits e auto-cura
    ├── token_daemon.py                    # Daemon continuo do container sidecar para auto-renovacao eterna de tokens
    └── test_arsenal.py                    # Script de teste de inferência e validação de latência
```

---

### Roteiro Prático de Reprodução

Para reproduzir esta configuração em qualquer máquina:

> ⚠️ **Modelos gratuitos são voláteis.** Identificadores com sufixo `:free` podem ser descontinuados, migrados para a versão paga, saturados (`429`) ou passar a exigir permissão (`403`) a qualquer momento. A cascata existe justamente para absorver isso: revalide com `python3 src/test_arsenal.py`, que testa cada nível isoladamente.

### 📋 Pré-requisitos do Ambiente e Plataformas

Antes de iniciar a configuração da cascata e dos combos de fallback, garanta os seguintes componentes instalados e configurados na sua máquina:

1. **Python 3.14.7 (Recomendado) ou Superior (mínimo 3.10):**
   - Recomendamos a versão oficial: [Python 3.14.7](https://www.python.org/ftp/python/3.14.7/python-3.14.7-macos11.pkg) (pacote instalador macOS).
   - Verifique a versão com `python3 --version`.
   - Se ainda não tiver o Python instalado:
     - **macOS:** Baixe o pacote oficial [Python 3.14.7](https://www.python.org/ftp/python/3.14.7/python-3.14.7-macos11.pkg) ou instale via Homebrew com `brew install python`
     - **Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install -y python3 python3-venv python3-pip`
     - **Windows:** `winget install Python.Python.3.14`
   - Crie e ative um ambiente virtual dedicado para o módulo:
     ```bash
     # macOS e Linux
     python3 -m venv .venv
     source .venv/bin/activate

     # Windows (PowerShell)
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - Atualize o gerenciador de pacotes e instale as dependências:
     ```bash
     pip install --upgrade pip
     pip install -r requirements.txt
     ```

2. **Docker e Docker Compose:**
   - O gateway 9Router e o Ollama rodam em containers isolados. Se necessário, instale:
     - **macOS:** `brew install --cask docker` ou instalador DMG oficial.
     - **Linux:** `curl -fsSL https://get.docker.com | sh` e adicione seu usuário com `sudo usermod -aG docker $USER`.
     - **Windows:** `winget install Docker.DockerDesktop` com suporte a WSL2.
   - Valide que o daemon está no ar com `docker info` e confirme o plugin com `docker compose version`.

3. **Node.js 18+ e Claude Code CLI:**
   - O Claude Code requer Node.js 18+. Instale via `brew install node` (macOS), `sudo apt install -y nodejs npm` (Linux) ou `winget install OpenJS.NodeJS` (Windows).
   - Instale a ferramenta oficial da Anthropic globalmente:
     ```bash
     npm install -g @anthropic-ai/claude-code
     ```
   - Verifique a instalação com `claude --version`.

4. **Contas e Tokens nas Plataformas Gratuitas:**
   - **OpenRouter (Custo Zero Travado):** Crie conta em [openrouter.ai](https://openrouter.ai/settings/keys). Gere uma API Key e defina o limite de gastos para `$0.00`. Isso garante que apenas modelos gratuitos com sufixo `:free` sejam consumidos sem qualquer cobrança.
   - **Groq Cloud (Inferência Ultrarrápida em LPU):** Crie conta gratuita em [console.groq.com/keys](https://console.groq.com/keys) e gere uma chave com prefixo `gsk_...`.
   - **Google AI Studio (famílias Gemini Flash e Pro vigentes):** Acesse [aistudio.google.com/apikey](https://aistudio.google.com/apikey) com sua conta Google e gere uma chave `AIza...`.
   - **Mistral AI (Codestral e Mistral Small):** Crie conta em [console.mistral.ai/api-keys](https://console.mistral.ai/api-keys) e gere uma chave de API para o modelo Codestral.
   - **Ollama Local (Continuidade Offline):** Não requer conta ou token externo. O serviço sobe diretamente no container Docker e garante resposta mesmo se toda a conexão cair.

### 1. Obter as Chaves Gratuitas nas Plataformas
1. **OpenRouter:** Acesse `https://openrouter.ai/settings/keys`, crie uma chave com limite `$0.00` para usufruir dos modelos com sufixo `:free`. Até a data de escrita deste arquivo, respondiam corretamente: `cohere/north-mini-code:free` (código), `nvidia/nemotron-3.5-lightning:free` (contexto de 1M) e `nex-agi/nex-n2.5-mini:free` (o mais rápido).
2. **Groq Cloud:** Acesse `https://console.groq.com/keys`, gere sua chave gratuita `gsk_...` para inferência ultra rápida com chips LPU (validamos o `openai/gpt-oss-120b`).
3. **Google AI Studio:** Acesse `https://aistudio.google.com/apikey`, gere sua chave no projeto associado; os limites do tier gratuito variam por modelo, consulte a [tabela oficial](https://ai.google.dev/gemini-api/docs/rate-limits).
4. **Mistral:** Acesse `https://console.mistral.ai/`, crie uma chave de API e registre-a como `MISTRAL_API_KEY` no `.env`. Foi o provedor em nuvem mais rápido que medimos (0,35s a 1,23s entre os dez modelos testados).
5. **Ollama Local via Docker:** O serviço já vem configurado no `docker-compose.yml`. Ao subir a stack, baixe o modelo leve e marque a tag que a cascata usa:

   ```bash
   docker exec -it claudegravity-ollama ollama pull qwen2.5-coder:0.5b
   docker exec claudegravity-ollama ollama cp qwen2.5-coder:0.5b qwen2.5-coder:latest
   ```

   São 397 MB. O segundo comando não é opcional: a cascata referencia `qwen2.5-coder:latest`, e sem ele o provisionamento acusa modelo ausente. Repita após cada destruição do ambiente, porque o modelo vive no volume do container.

### 2. Preparar Arquivos de Configuração

Na pasta deste módulo, inicialize as configurações e chaves a partir dos arquivos `.example`:

```bash
cd 0003_fallback_modelos_gratuitos_9router
cp .env.example .env
cp examples/.claude/settings.json.example examples/.claude/settings.json
cp examples/.claude/settings.local.json.example examples/.claude/settings.local.json
```

Edite o arquivo `.env` para inserir suas chaves caso deseje personalizá-las.

### 3. Gerenciamento do Ciclo de Vida do Ambiente (Criar e Destruir)

#### Opção A (Via Utilitário Python de Ciclo de Vida)

```bash
# Iniciar o 9Router e Ollama, provisionar combos e validar inferência
python3 src/manage_env.py start

# Consultar a saúde dos containers e portas 20128 e 11434
python3 src/manage_env.py status

# Pausar containers (preservando configurações e dados)
python3 src/manage_env.py stop

# DESTRUIR TUDO (remove containers, redes e volumes Docker completamente)
python3 src/manage_env.py destroy
```

#### Opção B (Via Docker Compose Nativo)

```bash
# Iniciar 9Router, Ollama e o container sidecar de renovacao continua em segundo plano
docker compose up -d

# Verificar se os containers estao saudaveis e ativos
docker ps --filter "name=claudegravity"

# Inspecionar os logs da renovacao automatica de tokens
docker logs -f claudegravity-token-sync

# Pausar os serviços
docker compose stop

# DESTRUIR TUDO (remover containers e volumes)
docker compose down -v --remove-orphans
```

O dashboard estará acessível em:
👉 **http://localhost:20128/dashboard**

### 4. Cadastrar os Provedores e o Combo de Fallback

Você pode configurar visualmente pelo painel web (`http://localhost:20128/dashboard/combos`) ou executar o script automático em Python:

```bash
python3 src/setup_combos.py
```

Combos criados e organizados por prioridade:
- **`claudegravity-fallback`:** Gemini 3.8 -> Gemini 3.7 -> Gemini 3.6 -> Claude Sonnet 4.6 -> GPT-OSS 120B (todos via Antigravity)
- **`arsenal-supremo`:** Gemini 3.8 -> Gemini 3.7 -> Gemini 3.6 -> Cohere North Mini Code (OpenRouter) -> GPT-OSS 120B (Groq) -> Codestral (Mistral) -> Ollama Qwen 2.5 Coder
- **`arsenal-rapido`:** GPT-OSS 120B (Groq) -> Codestral (Mistral) -> Gemini Flash 3.7 -> Gemini Flash 3.6
- **`arsenal-offline`:** Ollama Qwen 2.5 Coder (local e privado; continuidade, não sessão de trabalho)

### 5. Validar a Inferência dos Combos

```bash
python3 src/test_arsenal.py
```

### 6. Simular Cenários de Fallback, Rate Limit e Desautenticação

Execute o laboratório completo para testar e comprovar a comutação de modelos em tempo real:

```bash
python3 src/simulate_fallback.py
```

O script testa 5 cenários:
1. Estado Nominal com Antigravity ativo (Gemini 3.8 Flash High)
2. Simulação de Rate Limit e salto automático de modelo
3. Simulação de Logout / Token expirado do Antigravity
4. Auto-Cura e restauração de credenciais
5. Execução real no Claude Code CLI

### 7. Iniciar o Claude Code Conectado ao Combo

```bash
python3 src/arsenal_launcher.py
```

Ou diretamente pelo comando shell:

> A chave é gerada localmente na primeira execução de `sync_antigravity_token.py` (artigo 0002) e gravada no `.env` do módulo (não versionado). Substitua o placeholder abaixo pelo valor que o script imprimir.

```bash
# macOS e Linux (bash / zsh)
export ANTHROPIC_BASE_URL="http://localhost:20128"
export ANTHROPIC_API_KEY="sk-sua-chave-do-9router"
claude --dangerously-skip-permissions --model arsenal-supremo

# Windows (PowerShell)
$env:ANTHROPIC_BASE_URL="http://localhost:20128"
$env:ANTHROPIC_API_KEY="sk-sua-chave-do-9router"
claude --dangerously-skip-permissions --model arsenal-supremo
```

---

### Artigos Relacionados

- [Artigo 0001 - Google Antigravity com Acesso Total Irrestrito e sem Interrupções](../0001_antigravity_acesso_total_irrestrito/article/ARTICLE.md)
- [Artigo 0002 - ClaudeGravity e o Roteamento de Modelos Gemini no Claude Code via 9Router](../0002_claude_gravity_utilizando_9router/article/ARTICLE.md)
