# Ambiente Prático de Execução e Testes - DeepSeek como Alternativa ao ClaudeGravity

Este diretório é o espaço de testes do **Claude Code** para o Artigo 0004. A pasta `.claude/` fica isolada aqui dentro, sem interferir no restante do repositório.

---

## Como Executar os Testes neste Diretório

### 1. Inicializar a Configuração

Há um modelo por provedor. Copie o que você vai usar:

```bash
# DeepSeek Platform (pago por uso)
cp .claude/settings.json.deepseek.example .claude/settings.json

# ou OrcaRouter (DeepSeek Flash gratuito na data da escrita)
cp .claude/settings.json.orcarouter.example .claude/settings.json
```

Troque o valor de `ANTHROPIC_AUTH_TOKEN` pela sua chave. Valide o JSON antes de seguir:

```bash
python3 -c "import json; json.load(open('.claude/settings.json'))"
```

### 2. Primeira Execução

```bash
claude --settings .claude/settings.json
```

A flag aplica o arquivo antes do assistente de primeiro uso, que de outro modo pediria login na Anthropic. Nas sessões seguintes basta `claude`.

### 3. Teste Rápido

```bash
claude -p "Responda somente OK" --max-turns 1
```

---

## Arquivos Disponíveis

* **`.claude/settings.json.deepseek.example`:** papéis de modelo, permissões e `env` para a API oficial da DeepSeek.
* **`.claude/settings.json.orcarouter.example`:** o mesmo para o OrcaRouter.

Se o Claude Code pedir login, siga a ordem de diagnóstico em [docs/SOLUCAO_PROBLEMAS_COMUNS.md](../../docs/SOLUCAO_PROBLEMAS_COMUNS.md), Problema 8.
