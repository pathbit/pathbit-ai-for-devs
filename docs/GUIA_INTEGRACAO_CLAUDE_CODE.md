# 🚀 Guia de Integração com Claude Code CLI

Este guia aborda os aspectos técnicos e práticos para plugar a CLI oficial do **Claude Code** aos gateways de inferência do projeto **Pathbit AI for Devs**.

---

## 🏗️ Como Funciona o Roteamento

O Claude Code foi desenvolvido nativamente para se comunicar com a API da Anthropic via endpoint `/v1/messages` com streaming de Server-Sent Events (SSE). 

O container `claudegravity-router` atua como uma ponte transparente:
1. Recebe as chamadas do Claude Code na porta local `20128`.
2. Converte a estrutura de mensagens do formato Claude para o formato do provedor de destino (Google Antigravity, OpenRouter, Groq ou Ollama).
3. Transmite as respostas token por token via SSE de volta para o terminal do Claude Code.

---

## 💻 Formas de Executar o Claude Code

### 1. Via Launcher Python Automatizado (`claudegravity.py`)

No diretório `0002_claude_gravity_utilizando_9router`, disponibilizamos um launcher Python que inicializa o ambiente com as variáveis de ambiente necessárias e oferece um menu interativo de seleção de modelos:

```bash
python3 src/claudegravity.py
```

Você também pode passar o modelo diretamente via argumento:

```bash
# Conectar ao combo de fallback automatico com modelos gratuitos
python3 src/claudegravity.py --model claudegravity-fallback

# Conectar diretamente ao modelo primario Gemini 3.7 Flash High
python3 src/claudegravity.py --model ag/gemini-3.7-flash-high

# Listar todos os modelos registrados no gateway
python3 src/claudegravity.py --list-models
```

### 2. Via Linha de Comando Nativa

Se preferir exportar as variáveis no seu terminal antes de executar o comando `claude`:

> A chave do gateway é gerada localmente na primeira execução de `sync_antigravity_token.py` e gravada no `.env` do módulo, que não é versionado. Substitua o placeholder pelo valor que o script imprimir.

```bash
export ANTHROPIC_BASE_URL="http://localhost:20128"
export ANTHROPIC_API_KEY="sk-sua-chave-do-9router"

# Executar com selecao do combo de fallback
claude --model claudegravity-fallback
```

### 3. Modo Desimpedido e Autônomo para Agentes

Para automações contínuas onde o Claude Code deve aplicar alterações de código e executar testes sem pedir confirmações manuais no terminal:

```bash
claude --dangerously-skip-permissions --model claudegravity-fallback
```

---

## 📊 Principais Modelos e Combos Disponíveis

| Identificador do Modelo | Descrição |
| :--- | :--- |
| `claudegravity-fallback` | Combo com salto automático entre Gemini 3.8, Gemini 3.7, Sonnet 4.6 e GPT-OSS |
| `arsenal-supremo` | Combo com 7 níveis de contingência incluindo OpenRouter, Groq, Mistral e Ollama local |
| `arsenal-rapido` | Focado em velocidade extrema com chips LPU da Groq Cloud |
| `arsenal-offline` | Atendido pelo modelo local `qwen2.5-coder`, sem depender de internet. Mantém a cascata respondendo, mas **não conduz uma sessão de trabalho no harness**, portanto não o use em `ANTHROPIC_DEFAULT_*_MODEL` |
| `ag/gemini-3.8-flash-high` | Roteamento direto ao Gemini 3.8 Flash com raciocínio profundo no Antigravity Pro |
| `ag/gemini-3.7-flash-high` | Roteamento direto ao Gemini 3.7 Flash híbrido no Antigravity Pro |

---

## 🔍 Como Testar a Conexão antes de Programar

Antes de iniciar uma sessão de desenvolvimento, você pode validar a integridade da ponte com um teste simples em Python:

```bash
python3 src/test_gateway.py
```

Se todos os 4 testes apresentarem status `HTTP 200 OK`, seu ambiente está 100% pronto para codificar.

> **Importante:** Certifique-se de que o dashboard do 9Router (`http://localhost:20128/dashboard`) esteja acessível no navegador e com a conta Google titular da licença Antigravity (Google AI Pro) conectada em **Providers → Antigravity**. Se os testes acusarem erro `HTTP 403 Forbidden`, verifique se o navegador não vinculou inadvertidamente uma conta pessoal secundária sem assinatura.
