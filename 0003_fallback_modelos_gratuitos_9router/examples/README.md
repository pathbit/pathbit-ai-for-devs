# Ambiente Prático de Execução e Testes - Arsenal de Fallback

Este diretório funciona como o espaço de testes e execução prática do **Claude Code** para o Artigo 0003.

A pasta de configuração do Claude Code (`.claude/`) fica isolada aqui dentro, mantendo a raiz do módulo e do repositório completamente limpas.

---

## Como Executar os Testes neste Diretório

### 1. Copie o Template ANTES de Começar os Testes

O repositório versiona apenas o arquivo terminado em `.example`. O arquivo ativo — o que carrega a sua credencial — você gera com um `cp`, e ele fica fora do Git pelo `.gitignore`:

```bash
cp .claude/settings.local.json.example .claude/settings.local.json
```

Faça essa cópia **antes** de qualquer outro passo: sem o arquivo ativo, o `--settings` do passo 2 falha com `Settings file not found`.

> Em seguida substitua `sk-sua-chave-do-9router` no arquivo pela chave que o
> `sync_antigravity_token.py` grava no `.env` do módulo. O placeholder é recusado pelo gateway.

### 2. Iniciar o Claude Code Conectado ao Combo (Recomendado: Sempre com `--settings`)

Com o ambiente iniciado por `python3 ../src/manage_env.py start`, que sobe os serviços **e provisiona os combos**:

```bash
claude --settings .claude/settings.local.json --model arsenal-supremo
```

> **Por que usar `--settings` sempre?** O bloco `modelPicker` — o que substitui os modelos Anthropic pelos seus rótulos no menu `/model` — **não é lido de um checkout de projeto**. A descrição da chave no binário da CLI é taxativa: ele é honrado apenas a partir de *managed settings*, do arquivo global do usuário ou de um arquivo passado com `--settings`. Sem a flag, o menu customizado é ignorado, não importa se o arquivo se chama `settings.json` ou `settings.local.json`.
>
> A flag **não isola** a sessão do arquivo global: ela apenas coloca o seu arquivo acima dele na ordem de precedência. Rode `/status` e veja a linha `Setting sources` — ela lista `User settings` junto com `Command line arguments`.

Ou execute um prompt de teste diretamente:

```bash
claude --settings .claude/settings.local.json -p "Explique a lógica do script sample_task.py" --model arsenal-supremo
```

---

## ⚠️ No Menu `/model`, Use `s` — Nunca Enter

O rodapé do seletor de modelos diz: `Enter to set as default · s to use this session only`.

O **Enter** significa *"salvar como meu padrão para novas sessões"*, e o destino dessa gravação é fixo: a chave `"model"` do seu **`~/.claude/settings.json` global**. Isso acontece mesmo com a sessão iniciada via `--settings`, porque um arquivo passado por flag é uma fonte somente leitura para a CLI.

O efeito colateral é silencioso e incômodo: toda nova sessão do Claude Code — em qualquer pasta, inclusive com a sua conta Anthropic — passa a abrir com o modelo do gateway. Use **`s`** (só esta sessão) ou `Esc`.

Para checar e limpar o vazamento:

```bash
python3 ../../0004_deep_claude_alternativa_claudegravity/src/verify_deepclaude.py --fix-global
```

---

## Arquivos Disponíveis

* **`.claude/`:** Modelos do Antigravity como padrão nos quatro papéis, combos `arsenal-*` disponíveis por `/model`, permissões totais e advisor desligado. O bloco `modelPicker` só vale com `claude --settings .claude/settings.local.json` ou em `~/.claude/settings.json`.
* **`sample_task.py`:** Código Python de exemplo para testar inferência resiliente e fallback automático.
