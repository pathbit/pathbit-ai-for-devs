# 📋 Padrões de Engenharia de Software e IA

Este guia define os padrões técnicos, arquiteturais e de qualidade adotados no projeto **Pathbit AI for Devs**. Todos os scripts, módulos, documentações e integrações agênticas devem seguir rigorosamente estas diretrizes.

---

## 🎯 Princípios Fundamentais

1. **Simplicidade e Acessibilidade:** O código e os textos devem ser diretos, fáceis de ler e livres de complexidade desnecessária ou vocabulário rebuscado.
2. **Autonomia com Segurança:** Ferramentas devem rodar de forma automatizada e desimpedida, mas sempre criando backups automáticos antes de modificar qualquer configuração do sistema.
3. **Multiplataforma por Padrão:** Todo script deve funcionar igualmente no macOS, Linux e Windows WSL2.
4. **Resiliência e Continuidade:** Ambientes de IA para desenvolvedores não podem parar por indisponibilidade de um único provedor. O design deve contemplar múltiplos provedores e contingência local offline.

---

## 🐍 Padrões de Desenvolvimento em Python

### 1. Uso Exclusivo da Biblioteca Padrão

Para evitar problemas de compatibilidade e instalação de dependências pesadas, todos os scripts utilitários em `src/` devem utilizar preferencialmente a biblioteca padrão do Python 3 (`urllib.request`, `subprocess`, `json`, `os`, `sys`, `time`, `platform`, `argparse`, `shutil`).

```python
# Exemplo limpo e multiplataforma sem dependencias externas
import urllib.request
import json

def fetch_status(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Pathbit/1.0"})
    with urllib.request.urlopen(req, timeout=5) as res:
        return res.status
```

### 2. Idempotência e Backups com Timestamp

Qualquer script que altere configurações de sistema ou arquivos do usuário (como `setup_permissions.py`) deve:
- Ser **idempotente** (executar múltiplas vezes produz o mesmo resultado sem duplicar chaves).
- Gerar um backup automático com timestamp no padrão `backup-permissoes-YYYYMMDD_HHMM` antes de aplicar modificações.
- Oferecer um utilitário de reversão imediata (`restore_permissions.py`).

### 3. Dupla Abordagem de Gerenciamento (CLI Python vs Docker Compose)

Cada módulo que contenha containers Docker deve disponibilizar duas formas de controle:
- **Abordagem A (Python CLI):** `python3 src/manage_env.py [start|status|stop|destroy]`, que cuida de checagens prévias, inicialização, provisionamento e testes automáticos de integridade.
- **Abordagem B (Docker Compose Nativo):** `docker compose up -d` e `docker compose down -v --remove-orphans` para desenvolvedores que preferem a interface padrão do Docker.

---

## 🔒 Higiene de Segredos e Isolamento de Diretórios

### 1. Regra de Ouro do `.claude`

A pasta `.claude/` **NUNCA** deve existir na raiz do repositório nem na raiz de cada artigo.
A localização permitida para `.claude/` é exclusivamente dentro da subpasta de sandbox `examples/`:

```text
0002_claude_gravity_utilizando_9router/
├── examples/
│   ├── .claude/
│   │   ├── settings.json.example        # Versionado no Git
│   │   ├── settings.local.json.example  # Versionado no Git
│   │   ├── settings.json                # Ignorado no Git (.gitignore)
│   │   └── settings.local.json          # Ignorado no Git (.gitignore)
```

### 2. Gestão de Chaves de API e `.env`

- Arquivos `.env` contendo chaves reais são de uso estritamente local, devem estar sempre no `.gitignore` e **NUNCA** devem existir na raiz do repositório (apenas dentro da pasta de cada artigo).
- Arquivos `.env.example` devem ser versionados e documentar cada variável de ambiente com exemplos descritivos ou chaves de demonstração públicas sem limite financeiro (como chaves gratuitas do OpenRouter limitadas a $0.00).

---

## 🐳 Padrões de Nomenclatura Docker

Para manter a consistência e evitar colisões entre projetos na máquina do desenvolvedor:

1. **Nome do Projeto Compose:** Definido como `name: claudegravity`.
2. **Container do Gateway:** Sempre explicitado como `container_name: claudegravity-router`.
3. **Container do LLM Local:** Sempre explicitado como `container_name: claudegravity-ollama`.
4. **Container Sidecar de Tokens:** Sempre explicitado como `container_name: claudegravity-token-sync` (usando a imagem oficial `python:3.14-alpine` para executar o daemon contínuo `token_daemon.py` sem poluir o host).
5. **Volumes de Dados:** Persistidos como volumes nomeados (`9router_data`, `ollama_data`).
6. **Rede do Host:** Utilizar a diretiva `extra_hosts: ["host.docker.internal:host-gateway"]` para assegurar paridade de roteamento local entre macOS, Linux e Windows WSL2.

---

## 🚫 Proibição Absoluta de Coautoria com IA em Commits e Repositórios

Nos projetos da Pathbit, todo commit deve refletir exclusivamente a autoria humana do desenvolvedor responsável. É terminantemente proibida a inclusão de assinaturas sintéticas de coautoria de inteligência artificial (como `Co-Authored-By: Claude...`, `Co-Authored-By: Antigravity...`, `Co-Authored-By: Gemini...`, `Claude-Session:...` ou referências de agentes).

### 1. Desativação Nativa no Claude Code

O Claude Code insere por padrão o trailer `Co-Authored-By` nos commits quando executado. Para desativar esse comportamento permanentemente, definimos `"includeCoAuthoredBy": false` em todos os níveis de configuração:
- Global do usuário: `~/.claude/settings.json` e `~/.claude/settings.local.json`.
- Sandboxes e exemplos: `examples/.claude/settings.json.example` e `examples/.claude/settings.local.json.example`.

```json
{
  "includeCoAuthoredBy": false
}
```

### 2. Desativação Nativa no Google Antigravity e VSCode

Na IDE do Google Antigravity e na CLI `agy`, as seguintes diretivas garantem que ferramentas integradas de git e assistentes não incluam coautoria de IA nos commits:
- `User/settings.json`: `"claudeCode.includeCoAuthoredBy": false`, `"git.includeCoAuthoredBy": false` e `"git.authorCommit": true`.
- `antigravity-cli/settings.json`: `"includeCoAuthoredBy": false`.
- `config/config.json`: `"includeCoAuthoredBy": false` em `userSettings`.

### 3. Sanitização Global Ativa via Git Hook (commit-msg)

Como camada de proteção definitiva e independente de qualquer editor ou CLI, instalamos um hook de commit global em `~/.git-hooks/commit-msg` e ativamos via `git config --global core.hooksPath ~/.git-hooks`.
Esse hook intercepta todas as mensagens de commit antes de serem gravadas e remove automaticamente qualquer linha com padrões proibidos de coautoria sintética, preservando o assunto e o corpo legítimos do commit.

---

## 📝 Regras Editoriais para Markdown

Todos os arquivos `.md` (artigos, readmes e documentações) devem respeitar as regras da Pathbit Academy:

1. **Zero dois-pontos em títulos:**
   - ❌ `# 1. Introdução: O que é o Antigravity`
   - ✅ `# 1. Introdução ao Google Antigravity`
2. **Zero travessões (em-dash):**
   - Evite o uso de caracteres de travessão longo. Prefira hifens normais (` - `), vírgulas ou parênteses.
3. **Vocabulário simples e direto:**
   - Evite termos excessivamente cultos ou eruditos.
   - Prefira vocabulário acessível e objetivo como "rápida", "principal" e "além disso".
4. **Seção Obrigatória `## Show-Me-The-Code`:**
   - Todo artigo deve apresentar a seção prática `## Show-Me-The-Code` dividida em Opção 1 (Execução Local via README) e Opção 2 (Ambiente Isolado via `examples/`).
5. **Imagens Numeradas em Sequência:**
   - As imagens devem seguir numeração sequencial (`00_cover_...`, `01_diagrama_...`, `02_evidencia_...`) correspondendo à ordem exata de aparição no texto.
6. **Seção Obrigatória de Pré-requisitos do Ambiente:**
   - Todo artigo e README de módulo deve apresentar detalhadamente a seção de pré-requisitos antes dos passos de execução.
   - Deve cobrir:
     - Versão do Python: mínimo 3.10+ com recomendação oficial explícita do [Python 3.14.7](https://www.python.org/ftp/python/3.14.7/python-3.14.7-macos11.pkg) e comandos exatos de criação e ativação do ambiente virtual (`python3 -m venv .venv`, ativação para macOS/Linux e Windows).
     - Instalação de dependências (`pip install -r requirements.txt`).
     - Ferramentas de infraestrutura quando aplicável (Docker e Docker Compose, Node.js / Claude Code CLI).
     - Passo a passo explícito para criar contas e obter tokens/chaves de API nas plataformas correspondentes (OpenRouter com limite de $0.00, Groq Cloud, Google AI Studio, Mistral, Ollama), garantindo total autonomia e clareza ao leitor.

