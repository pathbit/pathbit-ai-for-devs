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
│   │   ├── settings.local.json.example        # Versionado no Git
│   │   └── settings.local.json                # Ignorado no Git (.gitignore)
```

### 2. Gestão de Chaves de API e `.env`

- Arquivos `.env` contendo chaves reais são de uso estritamente local, devem estar sempre no `.gitignore` e **NUNCA** devem existir na raiz do repositório (apenas dentro da pasta de cada artigo).
- Arquivos `.env.example` devem ser versionados e documentar cada variável de ambiente com exemplos descritivos ou chaves de demonstração públicas sem limite financeiro (como chaves gratuitas do OpenRouter limitadas a $0.00).

### 3. Regras para os `settings.local.json` do Claude Code nos Exemplos

Cada artigo versiona apenas templates `examples/.claude/settings.local.json*.example` (o 0004 tem um por provedor). A cópia ativa `settings.local.json` — a que carrega a credencial real — fica no `.gitignore`.

O nome é `settings.local.json`, e não `settings.json`, por escopo: o `.claude/settings.json` é a configuração **compartilhada do time**, feita para ser comitada; a nossa carrega credencial e redireciona o harness para outro provedor, então pertence ao escopo **pessoal da máquina**.

Regras obrigatórias: `ANTHROPIC_AUTH_TOKEN` como credencial (nunca `ANTHROPIC_API_KEY`), `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` no `env`, `ANTHROPIC_BASE_URL` sem sufixo `/v1`, nenhum identificador com `[1m]` e JSON validado antes do commit. O bloco JSON dentro do `ARTICLE.md` deve ser **idêntico** ao arquivo `.example` — `make valida-consistencia` verifica isso. As regras completas e o porquê de cada uma estão em [CHECKLIST_SETTINGS_CLAUDE_CODE.md](./CHECKLIST_SETTINGS_CLAUDE_CODE.md).

---

## 🐳 Padrões de Nomenclatura Docker

Para manter a consistência e evitar colisões entre projetos na máquina do desenvolvedor:

1. **Nome do Projeto Compose:** Definido como `name: claudegravity`.
2. **Container do Gateway:** Sempre explicitado como `container_name: claudegravity-router`.
3. **Container do LLM Local:** Sempre explicitado como `container_name: claudegravity-ollama`.
4. **Container Guardião de Conexões e Tokens:** Sempre explicitado como `container_name: router-sync` (usando a imagem oficial `ghcr.io/pathbit/9rtksync:latest` do projeto [9RTKSync](https://github.com/pathbit/9RTKSync) · *9Router Universal Token & Connection Synchronizer*, executando com virtual environment dedicado em `/opt/venv`). Para o gateway [OmniRoute](https://github.com/diegosouzapw/OmniRoute), o guardião oficial correspondente é o [OminiRTKSync](https://github.com/pathbit/OminiRTkSync) (*OminiRoute Universal Token & Connection Synchronizer*).
5. **Volumes de Dados:** Persistidos como volumes nomeados (`9router_data`, `ollama_data`).
6. **Rede do Host:** Utilizar a diretiva `extra_hosts: ["host.docker.internal:host-gateway"]` para assegurar paridade de roteamento local entre macOS, Linux e Windows WSL2.

---

## 🚫 Proibição Absoluta de Coautoria com IA em Commits e Repositórios

Nos projetos da Pathbit, todo commit deve refletir exclusivamente a autoria humana do desenvolvedor responsável. É terminantemente proibida a inclusão de assinaturas sintéticas de coautoria de inteligência artificial (como `Co-Authored-By: Claude...`, `Co-Authored-By: Antigravity...`, `Co-Authored-By: Gemini...`, `Claude-Session:...` ou referências de agentes).

### 1. Desativação Nativa no Claude Code

Para impedir que a CLI do Claude Code insira automaticamente metadados de coautoria nos commits gerados:

```bash
# Desativa a coautoria automática do Claude Code
claude config set -g includeCoAuthor false
```

Essa configuração grava `"includeCoAuthor": false` em `~/.claude.json`, garantindo que nenhum commit gerado por ferramentas locais receba trailers indesejados.

### 1.1. O Hook Não é Versionado — Verifique o Histórico Também

O hook `commit-msg` instalado pelo `setup_permissions.py` do artigo 0001 higieniza a mensagem no momento do commit, mas ele vive em `.git/hooks` (ou no `core.hooksPath` global). Nada disso é versionado: **um clone novo, ou uma máquina onde o hook não foi instalado, aceita o trailer sem reclamar**.

Foi exatamente o que aconteceu neste repositório em 17/09/2026: quatro commits entraram com `Co-Authored-By:` e `Claude-Session:` porque o clone não tinha `core.hooksPath` configurado. As mensagens foram reescritas e o histórico republicado.

Para que a regra valha em qualquer clone e em CI, a verificação também roda a partir do repositório:

```bash
make valida-consistencia
```

A seção **Autoria dos commits** percorre todas as mensagens do histórico e falha se encontrar qualquer assinatura sintética. Para instalar o hook neste clone:

```bash
python3 0001_antigravity_acesso_total_irrestrito/src/setup_permissions.py
```

### 1.2. Como Limpar um Histórico que Já Recebeu Trailers

Reescrever mensagens muda os SHAs e exige `push --force`. Faça backup antes:

```bash
git bundle create ../backup.bundle --all          # backup completo
git branch backup-antes-limpeza                   # rede de segurança local

git filter-branch -f --msg-filter '
  sed -E "/^Co-Authored-By:.*(claude|anthropic|devin|copilot|bot|noreply)/Id;
          /^Claude-Session:/Id;
          /Generated with \[?Claude Code/Id;
          /^https:\/\/claude\.ai\/code\/session/Id;
          /🤖/d"
' <commit-base>..HEAD

git push --force-with-lease origin master
```

Confira que a árvore não mudou antes de publicar — só as mensagens deveriam ter sido tocadas:

```bash
git diff backup-antes-limpeza master     # precisa sair vazio
```

### 2. Configuração de Autoria do Git

Certifique-se de que seu ambiente Git esteja sempre configurado com seu nome e e-mail oficiais:

```bash
git config --global user.name "Eliel Sousa"
git config --global user.email "eliel@pathbit.co"
```

### 3. Sanitização Preventiva

Antes de qualquer `git push`, inspecione as mensagens dos últimos commits:

```bash
git log -n 5 --format="%h - %an <%ae> : %s"
```

Caso identifique qualquer menção ou linha de coautoria, reescreva a mensagem com `git commit --amend` antes de enviar ao repositório remoto.

---

## 📝 Regras Editoriais para Markdown

Todos os arquivos `.md` (artigos, readmes e documentações) devem respeitar as regras da Pathbit Academy:

1. **Zero dois-pontos em títulos de cabeçalho Markdown:**
   - Em títulos (`#`, `##`, `###`), nunca utilize dois-pontos (`:`).
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

---

## 📄 Licença

Distribuído sob a Licença MIT. O texto completo está em [LICENSE](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/LICENSE).

Na prática: use, copie, altere e redistribua à vontade, inclusive comercialmente, desde que o aviso de copyright e a licença acompanhem as cópias. O software é fornecido como está, sem garantias.

---

Desenvolvido com ❤️ pela [Pathbit](https://pathbit.co/)
