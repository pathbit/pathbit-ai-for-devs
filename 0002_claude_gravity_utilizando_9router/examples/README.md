# Ambiente Prático de Execução e Testes - ClaudeGravity

Este diretório funciona como o espaço de testes e execução prática do **Claude Code** para o Artigo 0002.

A pasta de configuração do Claude Code (`.claude/`) fica isolada aqui dentro, garantindo que a raiz do artigo e do projeto permaneçam limpas e organizadas.

---

## Como Executar os Testes neste Diretório

### 1. Copie o Template ANTES de Começar os Testes

O repositório versiona apenas o arquivo terminado em `.example`. O arquivo ativo — o que carrega a sua credencial — você gera com um `cp`, e ele fica fora do Git pelo `.gitignore`:

```bash
cp .claude/settings.local.json.example .claude/settings.local.json
```

Faça essa cópia **antes** de qualquer outro passo: sem o arquivo ativo, o `--settings` do passo 3 falha com `Settings file not found`.

### 2. Provisionar credenciais e combos

O arquivo copiado acima usa `ag/gemini-3.8-flash-high` como modelo padrão e aponta os quatro
papéis para modelos individuais do Antigravity. Os dois combos ficam a um `/model claudegravity-fallback`
de distância, como rede de segurança para quando a cota de uma família estourar  -  e precisam existir
no gateway antes da primeira sessão:

```bash
cd ..
python3 src/sync_antigravity_token.py   # credenciais e a chave do gateway no .env
python3 src/claudegravity.py            # provisiona os dois combos e abre a sessao
cd examples
```

> Sem este passo o gateway não conhece nenhum identificador `ag/*`, e a primeira mensagem falha.
> O `claudegravity.py` resolve credencial e combos de uma vez, por isso é o caminho recomendado.

### 3. Iniciar o Claude Code (Recomendado: Sempre com `--settings`)

Com o container do 9Router em execução na porta `20128` e os combos provisionados, inicie o Claude Code aplicando explicitamente o arquivo de configuração:

```bash
claude --settings .claude/settings.local.json
```

> **Por que usar `--settings` sempre?** O bloco `modelPicker` — o que substitui os modelos Anthropic pelos seus rótulos no menu `/model` — **não é lido de um checkout de projeto**. A descrição da chave no binário da CLI é taxativa: ele é honrado apenas a partir de *managed settings*, do arquivo global do usuário ou de um arquivo passado com `--settings`. Sem a flag, o menu customizado é ignorado, não importa se o arquivo se chama `settings.json` ou `settings.local.json`.
>
> A flag **não isola** a sessão do arquivo global: ela apenas coloca o seu arquivo acima dele na ordem de precedência. Rode `/status` e veja a linha `Setting sources` — ela lista `User settings` junto com `Command line arguments`.

Ou execute uma instrução direta no terminal:

```bash
claude --settings .claude/settings.local.json -p "Analise o arquivo sample_task.py e sugira melhorias de desempenho"
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

* **`.claude/`:** Contém o arquivo de configuração: modelo padrão, quatro papéis, permissões totais e advisor desligado. O bloco `modelPicker` só vale com `--settings` ou em `~/.claude/settings.json`.
* **`sample_task.py`:** Código Python de exemplo para testar refatoração e planejamento agêntico com o modelo padrão do `settings.local.json`.
