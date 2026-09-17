# ⚙️ Checklist dos `settings.local.json` do Claude Code nos Artigos

Este documento consolida as regras para os arquivos `examples/.claude/settings.local.json*` de todos os artigos e o que foi **verificado** para chegar a elas. Cada regra nasceu de um problema real; a coluna "por quê" aponta a evidência. Versões da CLI usadas na verificação: **Claude Code 2.1.268 e 2.1.274** (2026-09-17).

---

## 1. Um arquivo ativo por cenário, chamado `settings.local.json`

| Regra | Por quê |
| :--- | :--- |
| Cada artigo versiona apenas `examples/.claude/settings.local.json.example` (o 0004 tem um `.example` por provedor). A cópia ativa `settings.local.json` fica no `.gitignore`. | Só o template entra no Git; o arquivo com a credencial real nunca. |
| Use `settings.local.json`, **não** `settings.json`. | O `.claude/settings.json` é o escopo de configuração **compartilhada do time**, feito para ser comitado. Nossa configuração carrega credencial e redireciona o harness para outro provedor: comitá-la imporia isso a quem clonasse o repositório. O `settings.local.json` é o escopo pessoal/da máquina — exatamente o caso aqui. |
| Faça o `cp` do `.example` **antes** de qualquer teste. | Sem o arquivo ativo, `claude --settings .claude/settings.local.json` aborta com `Settings file not found`. |
| O bloco `modelPicker` pode ficar no arquivo, mas **só é honrado** em `~/.claude/settings.json`, em settings gerenciadas ou via `claude --settings <arquivo>`. Em qualquer checkout de projeto — `settings.json` **ou** `settings.local.json` — é ignorado. | Está na descrição da chave dentro do binário: *"Honored from managed, --settings/SDK, and user settings only (not from a project checkout)"*. Confirmado nos testes. |
| A flag `--settings` **não isola** a sessão do arquivo global: ela se sobrepõe a ele. | O `/status` da sessão lista `Setting sources: User settings, Shared project settings, Command line arguments` — as três simultaneamente. |

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
5. **A flag `--settings`, sozinha, não escreve no arquivo global.** Hash SHA-256 de `~/.claude/settings.json` medido antes e depois de uma sessão completa com inferência real: idêntico.

### 4.1. O Enter no menu `/model` grava no `~/.claude/settings.json`

Este é o único caminho pelo qual a configuração do laboratório escapa para a conta pessoal, e não tem relação com o arquivo do projeto.

| Fato | Evidência |
| :--- | :--- |
| O rodapé do seletor oferece `Enter to set as default · s to use this session only · Esc to cancel`. | Visível no menu `/model` da CLI 2.1.274. |
| O Enter grava a escolha como `"model"` no escopo `userSettings`, isto é, `~/.claude/settings.json`. | A função de persistência no binário chama `en("userSettings", { model: ... })` — literal, sem alternativa de escopo. |
| Isso ocorre **mesmo** com a sessão iniciada por `--settings`. | Um arquivo passado por flag é fonte somente leitura para a CLI (*"This rule comes from a read-only source (the --settings flag) and cannot be modified here"*), então ela persiste no escopo gravável. |
| Efeito: toda nova sessão, em qualquer pasta e com a conta Anthropic, abre com o modelo de terceiros. | Sintoma relatado e reproduzido. |

**Regra:** no `/model`, use `s` ou `Esc`. Nunca Enter.
**Limpeza:** `python3 0004_deep_claude_alternativa_claudegravity/src/verify_deepclaude.py --fix-global`.

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

## 7. Verificadores (rode antes de commitar)

Os dois verificadores do repositório substituem a inspeção manual:

```bash
# Na raiz: JSON transcrito nos artigos x arquivos .example, imagens citadas x
# assets em disco, links relativos e convenção de nomes dos settings.
make valida-consistencia

# Configuração do 0004: sintaxe, ANTHROPIC_AUTH_TOKEN, sufixo [1m], URL com /v1,
# credencial vazada em template e contaminação do settings global.
python3 0004_deep_claude_alternativa_claudegravity/src/verify_deepclaude.py

# Com inferência real contra o provedor configurado:
python3 0004_deep_claude_alternativa_claudegravity/src/verify_deepclaude.py --online
```

Em redes com proxy TLS corporativo, o Python falha a validação de certificado enquanto o `curl` passa (ele valida contra o próprio bundle de CAs, não contra o keychain do sistema). Use `export SSL_CERT_FILE=/caminho/ca.pem` ou a flag `--insecure`.

---

## 8. Onde cada regra está explicada nos artigos

| Tema | Artigo 0002 | Artigo 0003 | Artigo 0004 |
| :--- | :--- | :--- | :--- |
| `settings.local.json` vs `settings.json` | "O arquivo de configuração do Claude Code" | "O arquivo de configuração do Claude Code" | "A Arquitetura de Configurações do Claude Code" |
| Estado global e `--settings` | "O que fica no estado global do Claude Code" | idem | "Blindagem Contra o Estado Global da CLI" |
| Vazamento do `/model` | `[!CAUTION]` "A Terceira Fonte de Estado Global" | idem | "A Armadilha do `/model`" |
| Sufixo `[1m]` | tabela de chaves | tabela de chaves | "O Sufixo `[1m]`: Por Que Ele Não Pertence a um Modelo de Terceiros" |
| Advisor | aviso `[!IMPORTANT]` junto ao settings e seção "O Advisor e Ferramentas Experimentais" | aviso `[!IMPORTANT]` e `[!CAUTION]` em "Três blocos que merecem explicação" | aviso `[!IMPORTANT]` junto aos settings e `[!CAUTION]` no item "Advisor e Provedores Alternativos" |
