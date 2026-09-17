# Ambiente Prático de Execução e Testes - Arsenal de Fallback

Este diretório funciona como o espaço de testes e execução prática do **Claude Code** para o Artigo 0003.

A pasta de configuração do Claude Code (`.claude/`) fica isolada aqui dentro, mantendo a raiz do módulo e do repositório completamente limpas.

---

## Como Executar os Testes neste Diretório

### 1. Inicializar as Configurações

Gere os arquivos ativos a partir dos modelos `.example`:

```bash
cp .claude/settings.json.example .claude/settings.json
```

> Em seguida substitua `sk-sua-chave-do-9router` no arquivo pela chave que o
> `sync_antigravity_token.py` grava no `.env` do módulo. O placeholder é recusado pelo gateway.

### 2. Iniciar o Claude Code Conectado ao Combo (Recomendado: Sempre com `--settings`)

Com o ambiente iniciado por `python3 ../src/manage_env.py start`, que sobe os serviços **e provisiona os combos**:

```bash
claude --settings .claude/settings.json --model arsenal-supremo
```

> **Por que usar `--settings` sempre?** No binário da CLI do Claude Code (v2.1.x), o bloco `modelPicker` é ignorado em checkouts locais quando chamado apenas como `claude`. Ao invocar com `--settings .claude/settings.json`, a CLI honra o menu customizado com `replaceBuiltInOptions: true` (ocultando os modelos Anthropic) e evita que configurações residuais de `~/.claude/settings.json` interfiram na sessão.

Ou execute um prompt de teste diretamente:

```bash
claude --settings .claude/settings.json -p "Explique a lógica do script sample_task.py" --model arsenal-supremo
```

---

## Arquivos Disponíveis

* **`.claude/`:** Modelos do Antigravity como padrão nos quatro papéis, combos `arsenal-*` disponíveis por `/model`, permissões totais e advisor desligado. O bloco `modelPicker` só vale com `claude --settings .claude/settings.json` ou em `~/.claude/settings.json`.
* **`sample_task.py`:** Código Python de exemplo para testar inferência resiliente e fallback automático.
