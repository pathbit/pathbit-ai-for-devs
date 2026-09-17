# Ambiente Prático de Execução e Testes - DeepClaude

Este diretório é o laboratório do **Claude Code** para o Artigo 0004. A pasta `.claude/` fica isolada aqui dentro, sem interferir no restante do repositório.

---

## Como Executar os Testes neste Diretório

### 1. Copie o Template ANTES de Abrir o Claude Code

O repositório versiona apenas os arquivos terminados em `.example`. O arquivo ativo — o que carrega o seu token real — você gera com um `cp`, e ele nunca entra no Git:

```bash
# DeepSeek Platform (pago por uso)
cp .claude/settings.local.json.deepseek.example .claude/settings.local.json

# ou OrcaRouter (DeepSeek V4 Flash gratuito na data da escrita)
cp .claude/settings.local.json.orcarouter.example .claude/settings.local.json
```

Abra o arquivo gerado e troque `ANTHROPIC_AUTH_TOKEN` pela sua chave (`sk-...`). Confira também a `ANTHROPIC_BASE_URL`, que já vem correta para cada provedor:

| Provedor | `ANTHROPIC_BASE_URL` | Modelos |
| :--- | :--- | :--- |
| DeepSeek Platform | `https://api.deepseek.com/anthropic` | `deepseek-v4-pro`, `deepseek-flash` |
| OrcaRouter | `https://api.orcarouter.ai` | `deepseek/deepseek-v4-flash-free` |

> A URL base vai **sem** `/v1`. O Claude Code anexa `/v1/messages` por conta própria; incluir o sufixo gera `/v1/v1/messages` e a chamada falha.

Valide o JSON antes de seguir:

```bash
python3 -c "import json; json.load(open('.claude/settings.local.json'))"
```

### 2. Execute Sempre com `--settings`

```bash
claude --settings .claude/settings.local.json
```

> **Por que a flag é obrigatória?** O bloco `modelPicker` — o que substitui os modelos Anthropic pelos rótulos do DeepSeek no menu `/model` — **não é lido de um checkout de projeto**. A documentação embutida no binário da CLI é explícita: ele é honrado apenas a partir de *managed settings*, do arquivo global do usuário ou de um arquivo passado com `--settings`. Sem a flag, o menu customizado é ignorado, não importa se o arquivo se chama `settings.json` ou `settings.local.json`.

### 3. Teste Rápido

```bash
claude --settings .claude/settings.local.json -p "Responda somente OK" --max-turns 1
```

### 4. Verificação Automatizada

```bash
python3 ../src/verify_deepclaude.py --online
```

---

## ⚠️ Duas Armadilhas que Valem uma Leitura

**1. No menu `/model`, nunca aperte Enter.** O rodapé do seletor diz `Enter to set as default · s to use this session only`. O Enter grava a escolha como `"model"` no seu **`~/.claude/settings.json` global** — e a partir daí toda nova sessão do Claude Code, em qualquer pasta e com a sua conta Anthropic, tenta abrir com o modelo DeepSeek. Use `s` ou `Esc`. Se já aconteceu: `python3 ../src/verify_deepclaude.py --fix-global`.

**2. O arquivo ativo vale para qualquer sessão aberta nesta pasta.** Enquanto existir um `.claude/settings.local.json` aqui, qualquer `claude` iniciado neste diretório usará o DeepSeek — inclusive sem a flag `--settings`. É o comportamento desejado no laboratório. Para voltar à sua conta Anthropic, abra o Claude Code fora de `examples/` ou remova o arquivo ativo (`rm .claude/settings.local.json`); os templates continuam aqui para recriá-lo.

---

## Arquivos Disponíveis

| Arquivo | Conteúdo |
| :--- | :--- |
| `.claude/settings.local.json.deepseek.example` | Papéis de modelo, permissões e `env` para a API oficial da DeepSeek |
| `.claude/settings.local.json.orcarouter.example` | O mesmo para o OrcaRouter, com o modelo gratuito |
| `.claude/settings.local.json` | Sua cópia ativa com o token real — **gerada por você, ignorada pelo Git** |

Se o Claude Code pedir login, siga a ordem de diagnóstico em [docs/SOLUCAO_PROBLEMAS_COMUNS.md](../../docs/SOLUCAO_PROBLEMAS_COMUNS.md), Problema 8.
