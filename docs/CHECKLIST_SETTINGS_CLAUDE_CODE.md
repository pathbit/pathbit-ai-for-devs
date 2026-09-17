# ⚙️ Checklist dos `settings.local.json` do Claude Code nos Artigos

Este documento consolida as regras para os arquivos `examples/.claude/settings.local.json*` de todos os artigos e o que foi **verificado** para chegar a elas. Cada regra nasceu de um problema real; a coluna "por quê" aponta a evidência. Versão da CLI usada na verificação: **Claude Code 2.1.268** (2026-09-17).

---

## 1. Um arquivo por cenário, sem `settings.local.json`

| Regra | Por quê |
| :--- | :--- |
| Cada artigo versiona apenas `examples/.claude/settings.local.json.example` (o 0004 tem um `.example` por provedor). A cópia ativa `settings.local.json` fica no `.gitignore`. | O `settings.local.json` existia como cópia idêntica do `settings.local.json`; eram dois lugares para manter a mesma coisa. |
| Não crie `settings.local.json.example`. | A função do arquivo local é guardar o que é específico da máquina e não pode ir para o git. Nos artigos não há nada nessa categoria. |
| O bloco `modelPicker` pode ficar no arquivo, mas **só é honrado** em `~/.claude/settings.json`, em settings gerenciadas ou via `claude --settings <arquivo>`. Em checkout de projeto (`.claude/settings.local.json` ou `.claude/settings.local.json`) é ignorado. | Descrição do próprio esquema de settings dentro do binário; confirmado nos testes. |

---

## 2. Credencial em `ANTHROPIC_AUTH_TOKEN`, não em `ANTHROPIC_API_KEY`

| Regra | Por quê |
| :--- | :--- |
| No `env` dos settings use `"ANTHROPIC_AUTH_TOKEN": "<chave do gateway>"`. | `ANTHROPIC_API_KEY` vinda do `env` exige a aprovação interativa *"Do you want to use this API key?"*, guardada em `~/.claude.json` e apagada pelo `/logout`. `ANTHROPIC_AUTH_TOKEN` vai direto para `Authorization: Bearer`, sem aprovação nem estado global. |
| No `.env` e nos scripts Python o nome continua `ANTHROPIC_API_KEY`. Os launchers (`claudegravity.py`, `arsenal_launcher.py`, `simulate_fallback.py`) repassam o valor à CLI como `ANTHROPIC_AUTH_TOKEN` e removem `ANTHROPIC_API_KEY` do ambiente do subprocesso. | Com as duas variáveis presentes, a CLI ainda pergunta pela aprovação da `ANTHROPIC_API_KEY`. |
| Gateways confirmados lendo `Authorization: Bearer`: DeepSeek (`api.deepseek.com/anthropic`, testado), OrcaRouter (testado; lê os dois cabeçalhos), 9Router (middleware lê `Authorization` antes de `x-api-key`, verificado no código da imagem `decolua/9router`). | Evita trocar para um cabeçalho que o gateway não aceita. |

---

## 3. Advisor desligado com o kill switch

| Regra | Por quê |
| :--- | :--- |
| No `env`: `"CLAUDE_CODE_DISABLE_ADVISOR_TOOL": "1"`. | Remove o comando `/advisor` e impede que a CLI anexe a ferramenta. É a chave de desligamento documentada. |
| Não use `"CLAUDE_CODE_ENABLE_EXPERIMENTAL_ADVISOR_TOOL": "0"`. | A CLI lê a variável como booleano: `"0"` equivale a não definir. Com `"1"` ela **libera** o modo experimental. |
| Não use `"advisorModel": ""`. | Com o recurso desligado a chave é ignorada. |
| O advisor **não funciona** com nenhum gateway ou provedor fora da API da Anthropic, por nenhuma configuração. | Ele é uma *server tool*: a CLI anexa `{"type": "advisor_20260301", "name": "advisor", "model": "..."}` ao array `tools`, e quem executa é o servidor da Anthropic. O DeepSeek responde `400 unknown variant advisor_20260301` e a requisição inteira falha. Não tem relação com `WebSearch`. |
| O menu `/advisor` lista só os aliases `fable`, `opus` e `sonnet`, nomeados pelo modelo em que resolvem. Dois papéis ou duas chaves de `modelOverrides` no mesmo modelo produzem linhas duplicadas ("Fable" duas vezes, nenhum "Opus"). | Sintoma da mesma limitação; some com o kill switch. |

---

## 4. O que é global e não se controla pelo projeto

Fica em `~/.claude.json` e **nenhuma chave de `settings.local.json` altera**, por desenho:

| Estado | O que zera |
| :--- | :--- |
| Assistente de primeiro uso concluído (tema, notas de segurança) | `/logout`, instalação nova |
| Login na conta Anthropic | `/logout` |
| Aprovação de `ANTHROPIC_API_KEY` vinda do `env` | `/logout` |
| Confiança na pasta (por caminho absoluto) | Renomear ou mover a pasta |

Fatos verificados com `CLAUDE_CONFIG_DIR` apontando para um diretório vazio:

1. **Durante o assistente, o `settings.local.json` do projeto ainda não foi carregado.** Mesmo com a pasta já confiável e o arquivo completo, o assistente mostra *"Select login method"*. O arquivo do projeto só entra depois do assistente e da confirmação de confiança.
2. **`claude --settings .claude/settings.local.json` aplica o arquivo antes do assistente.** Sequência observada: tema, notas de segurança, confiança na pasta, prompt. Nenhuma tela de login. A flag também faz a CLI honrar o `modelPicker`.
3. **Depois da primeira execução, `claude` puro na pasta confiável carrega o `settings.local.json` do projeto** e não pede login (com `ANTHROPIC_AUTH_TOKEN`).
4. Com `ANTHROPIC_API_KEY` não aprovada, pasta confiável e assistente concluído, a pergunta *"Do you want to use this API key?"* reaparece.

---

## 5. Higiene do arquivo

| Regra | Por quê |
| :--- | :--- |
| Valide o JSON antes de usar: `python3 -c "import json; json.load(open('.claude/settings.local.json'))"`. | Uma vírgula sobrando depois da última chave faz a CLI **descartar o arquivo inteiro em silêncio**. Sem ele, some o `ANTHROPIC_BASE_URL` e a CLI cai no fluxo de login da Anthropic. Aconteceu duas vezes durante a revisão. |
| Não copie o bloco `env` de um artigo para outro sem revisar os modelos. | Um `CLAUDE_CODE_SUBAGENT_MODEL: "deepseek-flash"` colado no exemplo do 9Router aponta para um modelo que aquele gateway não serve. |
| O bloco JSON dentro do `ARTICLE.md` deve ser **idêntico** ao arquivo `.example`. | O leitor copia de um dos dois; divergência vira bug de reprodução. Há um verificador simples na seção 7. |
| `modelOverrides` com uma entrada por família (`claude-fable-5-1`, `claude-opus-5`, `claude-sonnet-5`), sem duplicar com o sufixo `[1m]`. | A CLI normaliza o identificador antes de consultar o mapa. |

---

## 6. Diagnóstico rápido quando o Claude Code pede login na pasta do exemplo

Nesta ordem:

1. **O JSON é válido?** Rode o comando da seção 5. Se falhar, é o arquivo.
2. **O assistente de primeiro uso está aparecendo** (tela "Choose the text style")? Saia dele com `claude --settings .claude/settings.local.json`. Depois disso o `claude` puro volta a funcionar.
3. **A pasta foi renomeada ou movida?** A confiança é por caminho absoluto; aceite de novo.
4. **Só então** é credencial: confira `ANTHROPIC_BASE_URL` e `ANTHROPIC_AUTH_TOKEN` no `env`.

---

## 7. Verificador de consistência (rode antes de commitar)

```bash
# Na raiz do repositório
python3 - <<'PY'
import json, re, glob
ok = True
for f in glob.glob('0*/examples/.claude/settings*'):
    try:
        d = json.load(open(f))
    except Exception as e:
        ok = False; print('JSON INVÁLIDO:', f, e); continue
    env = d.get('env', {})
    if 'ANTHROPIC_API_KEY' in env: ok = False; print('use ANTHROPIC_AUTH_TOKEN:', f)
    if env.get('CLAUDE_CODE_DISABLE_ADVISOR_TOOL') != '1' and 'ANTHROPIC_BASE_URL' in env:
        ok = False; print('falta CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1:', f)
    if 'advisorModel' in d or 'CLAUDE_CODE_ENABLE_EXPERIMENTAL_ADVISOR_TOOL' in env:
        ok = False; print('chave obsoleta do advisor:', f)
for art in glob.glob('0*/article/ARTICLE.md'):
    t = open(art, encoding='utf-8').read()
    for m in re.finditer(r'```json[^\n]*\n(.*?)```', t, re.S):
        b = m.group(1)
        if b.lstrip().startswith('{') and b.rstrip().endswith('}'):
            try: json.loads(b)
            except Exception as e: ok = False; print('bloco JSON inválido em', art, 'linha', t[:m.start()].count('\n') + 1, e)
print('OK' if ok else 'PROBLEMAS ENCONTRADOS')
PY
```

---

## 8. Onde cada regra está explicada nos artigos

| Tema | Artigo 0002 | Artigo 0003 | Artigo 0004 |
| :--- | :--- | :--- | :--- |
| Arquivo único, sem `.local` | "O arquivo de configuração do Claude Code" | "O arquivo de configuração do Claude Code" | (padrão desde a criação) |
| Estado global e `--settings` | "O que fica no estado global do Claude Code" | idem | idem |
| Advisor | aviso `[!IMPORTANT]` junto ao settings e seção "O Advisor e Ferramentas Experimentais" | aviso `[!IMPORTANT]` e `[!CAUTION]` em "Três blocos que merecem explicação" | aviso `[!IMPORTANT]` junto aos settings e `[!CAUTION]` no item "Advisor e Provedores Alternativos" |
