# 🔧 Soluções para Problemas Comuns

Este documento reúne soluções práticas para os erros e incidentes operacionais mais frequentes encontrados ao executar os ambientes do **Pathbit AI for Devs**.

> **Onde executar os comandos.** Os caminhos `src/...`, `.env` e `docker-compose.yml` citados aqui são relativos à **pasta do módulo** (`0001_antigravity_acesso_total_irrestrito`, `0002_claude_gravity_utilizando_9router`, `0003_fallback_modelos_gratuitos_9router` ou `0004_deep_claude_alternativa_claudegravity`), não à raiz do repositório. Entre na pasta correspondente antes de rodar.

---

## ❌ Problema 1 - Porta 20128 ou 11434 Já em Uso

### Sintoma
Ao tentar subir os containers com `docker compose up -d` ou `manage_env.py start`, ocorre o erro:

```text
Error response from daemon: Ports are not available: exposing port TCP 0.0.0.0:20128 -> 0.0.0.0:0: bind: address already in use
```

### Causa
Existe outro container, serviço nativo do Ollama ou instância anterior do 9Router rodando na mesma porta do host.

### Solução

1. Identifique o processo que está retendo a porta no macOS ou Linux:
   ```bash
   lsof -i :20128
   lsof -i :11434
   ```
2. Se for um container Docker antigo com outro nome:
   ```bash
   docker ps
   docker stop <container_id_antigo>
   ```
3. Se for o serviço nativo do Ollama instalado diretamente no sistema operacional:
   - No macOS: Encerre o aplicativo Ollama na barra de menus antes de subir o container Docker.
   - No Linux: Execute `sudo systemctl stop ollama`.
4. Em seguida, reinicie o ambiente:
   ```bash
   python3 src/manage_env.py start
   ```

---

## ❌ Problema 2 - Modelo do Ollama Local Não Encontrado (Erro 404)

### Sintoma
Ao testar o combo `arsenal-offline`, o gateway retorna:

```text
HTTP Error 404: model 'qwen2.5-coder:latest' not found
```

### Causa
O container `claudegravity-ollama` foi iniciado, mas o download do modelo especialista de 0.5B ainda não foi realizado para o volume persistente.

### Solução

Execute o download e a cópia da tag padrão no container:

```bash
# 1. Baixar o modelo especialista leve (397 MB)
docker exec -it claudegravity-ollama ollama pull qwen2.5-coder:0.5b

# 2. Criar a tag 'latest' para o modelo
docker exec claudegravity-ollama ollama cp qwen2.5-coder:0.5b qwen2.5-coder:latest

# 3. Confirmar que o modelo esta listado
docker exec claudegravity-ollama ollama list
```

---

## ❌ Problema 3 - Erro de Permissão ou Lock no Banco SQLite

### Sintoma
Mensagens de `SQLITE_BUSY: database is locked` ou erro ao executar `setup_combos.py`.

### Causa
Múltiplos comandos tentando escrever no banco SQLite do container `claudegravity-router` ao mesmo tempo.

### Solução

1. Aguarde alguns segundos para operações em segundo plano terminarem.
2. Se o bloqueio persistir, pause e inicie novamente o container do 9Router:
   ```bash
   docker restart claudegravity-router
   ```
3. Execute novamente o script de provisionamento:
   ```bash
   python3 src/setup_combos.py
   ```

---

## ❌ Problema 4 - O Agente Pede Confirmação a Cada Edição de Arquivo

### Sintoma
No Google Antigravity, cada comando ou edição de arquivo abre uma janela solicitando clique manual de confirmação do usuário.

### Causa
As configurações de `autoExecutionPolicy` ou `agentMode` não foram propagadas para as pastas de projetos locais ou a IDE não foi reiniciada.

### Solução

1. Execute o configurador de acesso irrestrito:
   ```bash
   cd 0001_antigravity_acesso_total_irrestrito
   python3 src/setup_permissions.py
   ```
2. Valide o estado das 5 camadas com o diagnóstico:
   ```bash
   python3 src/verify_permissions.py
   ```
3. **Passo essencial:** Feche completamente o Antigravity IDE e reabra a aplicação para que o VSCode Core recarregue as novas configurações de usuário.

---

## ❌ Problema 5 - Chave de API do OpenRouter Rejeitada

### Sintoma
O OpenRouter retorna erro de saldo insuficiente ou chave inválida.

### Causa
A chave foi criada com limite maior que `$0.00` em uma conta sem saldo ou o modelo solicitado não pertence ao catálogo gratuito com sufixo `:free`.

### Solução

1. Acesse [OpenRouter Keys](https://openrouter.ai/settings/keys).
2. Crie uma nova chave definindo rigorosamente o campo **Credit Limit (USD)** como `0.00`.
3. Certifique-se de que o modelo configurado no combo possui o sufixo `:free` e **ainda está ativo no catálogo**. Identificadores gratuitos são descontinuados sem aviso, e tutoriais antigos costumam citar modelos que já saíram do catálogo. Liste os gratuitos vigentes com:

   ```bash
   curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models \
     | python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin)['data'] if float(m['pricing']['prompt'])==0]"
   ```

4. Atualize o arquivo `.env` e execute `python3 src/setup_combos.py`.
5. Valide a cascata inteira com `python3 src/test_arsenal.py`, que testa cada nível isoladamente e acusa qualquer identificador quebrado.

---

## ❌ Problema 6 - O `docker compose` Falha Reclamando de Variável Ausente

### Sintoma

```text
error while interpolating services.9router.environment.[]: required variable INITIAL_PASSWORD
is missing a value: defina INITIAL_PASSWORD no arquivo .env
```

### Causa

Os manifestos não guardam segredos em texto: `INITIAL_PASSWORD` e `JWT_SECRET` são lidos do arquivo `.env` com a sintaxe `${VARIAVEL:?mensagem}`, que faz o Compose falhar de propósito quando a variável não existe. É uma proteção contra subir o gateway com credencial versionada no repositório.

### Solução

Crie o `.env` a partir do modelo antes de subir o ambiente:

```bash
cp .env.example .env
docker compose up -d
```

Se preferir definir os valores só naquela execução, exporte-os no shell:

```bash
INITIAL_PASSWORD='sua-senha' JWT_SECRET='seu-segredo' docker compose up -d
```

Confirme que a interpolação resolve antes de subir, sem criar nada:

```bash
docker compose config >/dev/null && echo "manifesto válido"
```

---

## ❌ Problema 7 - Sessão Interrompida por Token Expirado ou Erro 503 no Antigravity

### Sintoma

Ao chamar modelos do Antigravity (como `ag/gemini-3.8-flash-high` ou combos), o terminal exibe:

```text
HTTP Error 503: Service Unavailable
{"error":{"message":"[antigravity/gemini-3.8-flash-high] [401]: HTTP 401 (reset after 2m)"}}
```

### Causa

O token OAuth do Antigravity expira a cada 60 minutos. Além disso, o 9Router possui um bug interno de serialização em que grava `expiresAt` como texto ISO (`"2026-09-11T02:05:25.091Z"`) em vez de timestamp numérico em milissegundos. Como `Number("string")` resulta em `NaN`, o gateway considera o token vencido mesmo quando ainda está ativo.

### Solução

1. **Correção Automática via Sidecar:** Os manifestos `docker-compose.yml` dos artigos 0002 e 0003 já incluem o container `router-sync` (imagem oficial `ghcr.io/pathbit/9rtksync:latest`). Ele roda continuamente e renova o token preventivamente 15 minutos antes da expiração. Inspecione os logs com:

   ```bash
   docker logs -f router-sync
   ```

2. **Correção Manual Imediata:** Se precisar forçar a renovação imediata sem reiniciar containers:

   ```bash
   python3 0002_claude_gravity_utilizando_9router/src/sync_antigravity_token.py
   ```

3. Para entender todos os detalhes da análise forense e da auto-cura, consulte o guia dedicado [SOLUCAO_TOKEN_EXPIRADO_ANTIGRAVITY.md](./SOLUCAO_TOKEN_EXPIRADO_ANTIGRAVITY.md).

---

## ❌ Problema 8 - O Claude Code Pede Login ao Abrir a Pasta de Exemplos

### Sintoma

Ao rodar `claude` dentro de `examples/`, aparece o assistente de primeiro uso ("Choose the text style") seguido de "Select login method", mesmo com o `.claude/settings.local.json` apontando para o gateway.

### Causa

Três causas, em ordem de frequência:

1. **JSON inválido** no `settings.local.json` (uma vírgula sobrando depois da última chave). A CLI descarta o arquivo em silêncio e, sem `ANTHROPIC_BASE_URL`, cai no login da Anthropic.
2. **O assistente de primeiro uso foi reiniciado** (um `/logout` faz isso). Enquanto ele roda, o `settings.local.json` do projeto ainda não foi carregado, então ele não enxerga a credencial do gateway.
3. **A pasta foi renomeada ou movida.** A confiança é guardada por caminho absoluto em `~/.claude.json`.

### Solução

```bash
# 1. Validar o JSON
python3 -c "import json; json.load(open('.claude/settings.local.json'))"

# 2. Passar pelo assistente com o arquivo do projeto aplicado antes dele
claude --settings .claude/settings.local.json

# 3. Aceitar a confiança da pasta quando perguntado; depois disso `claude` puro funciona
```

Use `ANTHROPIC_AUTH_TOKEN` (não `ANTHROPIC_API_KEY`) no `env` para não depender da aprovação de chave guardada fora do projeto. Detalhes em [CHECKLIST_SETTINGS_CLAUDE_CODE.md](./CHECKLIST_SETTINGS_CLAUDE_CODE.md).

---

## ❌ Problema 9 - `/advisor` Mostra "Fable" Duas Vezes ou a Sessão Falha com o Advisor Ligado

### Sintoma

O menu `/advisor` lista o mesmo nome duas vezes e nenhum "Opus"; ao ligar o advisor, toda requisição ao gateway falha (no DeepSeek: `400 unknown variant advisor_20260301`).

### Causa

O advisor é uma *server tool* executada pela API da Anthropic; gateways e provedores alternativos não a implementam e rejeitam a requisição inteira. As linhas duplicadas aparecem porque o menu nomeia os aliases `fable`/`opus`/`sonnet` pelo modelo em que resolvem, e dois papéis apontam para o mesmo modelo do provedor.

### Solução

No `env` do `settings.local.json`:

```json
"CLAUDE_CODE_DISABLE_ADVISOR_TOOL": "1"
```

Não use `CLAUDE_CODE_ENABLE_EXPERIMENTAL_ADVISOR_TOOL: "0"` (a CLI lê como booleano e `"0"` equivale a não definir) nem `"advisorModel": ""` (ignorada com o recurso desligado).

---

## ❌ Problema 10 - O Menu `/model` Ignora o `modelPicker` do Projeto

### Sintoma

O bloco `modelPicker` está no `.claude/settings.local.json` do projeto, mas o menu `/model` mostra a lista nativa da Anthropic.

### Causa

A CLI só honra `modelPicker` em `~/.claude/settings.json`, em settings gerenciadas ou via `--settings`. Em checkout de projeto o bloco é ignorado.

### Solução

Inicie com `claude --settings .claude/settings.local.json`, ou copie o bloco `modelPicker` para `~/.claude/settings.json`. Os quatro papéis (`ANTHROPIC_DEFAULT_*_MODEL`) continuam valendo no projeto e são o que roteia de fato.


---

## ❌ Problema 11 - O Modelo do Gateway Virou o Padrão da Conta Anthropic

### Sintoma

Você fez login com a sua conta Anthropic, abriu o Claude Code em uma pasta qualquer — sem nenhum arquivo de configuração de projeto — e o modelo padrão da sessão é o do gateway (`deepseek/...`, `ag/...`). O sintoma persiste entre reinícios e acompanha você em todos os diretórios.

### Causa

O Enter no menu `/model`. O rodapé do seletor oferece duas saídas:

```text
Enter to set as default  ·  s to use this session only  ·  Esc to cancel
```

O Enter significa *"salvar como padrão para novas sessões"*, e o destino dessa gravação é fixo: a chave `"model"` do **`~/.claude/settings.json` global**. A função de persistência no binário da CLI v2.1.274 chama `en("userSettings", { model: ... })`, sem alternativa de escopo.

Isso acontece **mesmo com a sessão iniciada por `--settings`**: um arquivo passado por flag é uma fonte somente leitura para a CLI, então ela grava no escopo gravável de sempre. Não é causado pelo arquivo do projeto, e renomear `settings.json` para `settings.local.json` não altera esse comportamento.

### Solução

Remova a chave `model` do arquivo global:

```bash
python3 0004_deep_claude_alternativa_claudegravity/src/verify_deepclaude.py --fix-global
```

Ou manualmente:

```bash
python3 - <<'PY'
import json, pathlib
p = pathlib.Path.home() / ".claude" / "settings.json"
d = json.loads(p.read_text())
print("Removido:", d.pop("model", None) or "(nada a limpar)")
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
PY
```

### Prevenção

No menu `/model`, use **`s`** (apenas esta sessão) ou `Esc`. Nunca Enter. Nos artigos deste repositório o seletor serve para inspeção visual: o roteamento de fato vem dos quatro papéis (`ANTHROPIC_DEFAULT_*_MODEL`) declarados no `settings.local.json`.

---

## ❌ Problema 12 - `Settings file not found` ao Iniciar com `--settings`

### Sintoma

```text
Error: Settings file not found: .claude/settings.local.json
```

### Causa

Só os templates `.example` são versionados. O arquivo ativo é gerado por você e fica fora do Git pelo `.gitignore` — em um clone novo, ele simplesmente não existe ainda.

### Solução

Faça a cópia **antes** de iniciar qualquer teste, no diretório `examples/` do artigo:

```bash
cp .claude/settings.local.json.example .claude/settings.local.json          # artigos 0002 e 0003
cp .claude/settings.local.json.orcarouter.example .claude/settings.local.json  # artigo 0004
```

Depois troque o `ANTHROPIC_AUTH_TOKEN` pela sua chave real e valide o JSON:

```bash
python3 -c "import json; json.load(open('.claude/settings.local.json'))"
```

---

## ❌ Problema 13 - `CERTIFICATE_VERIFY_FAILED` nos Scripts Python (mas o `curl` funciona)

### Sintoma

Os scripts de verificação falham com `[SSL: CERTIFICATE_VERIFY_FAILED] self-signed certificate in certificate chain`, enquanto o mesmo endpoint responde normalmente via `curl`.

### Causa

Não é erro de configuração do artigo. É uma rede com proxy TLS (inspeção de tráfego corporativa): o `curl` valida contra o keychain do sistema, que confia na CA do proxy; o Python valida contra o próprio bundle de CAs, que não a conhece.

### Solução

Aponte o Python para a CA da sua rede:

```bash
export SSL_CERT_FILE=/caminho/para/ca-corporativa.pem
```

Ou, para uma execução pontual de diagnóstico:

```bash
python3 0004_deep_claude_alternativa_claudegravity/src/verify_deepclaude.py --online --insecure
```

---

## ❌ Problema 14 - `[claude-code:unrecognized_model]` na Abertura da Sessão

### Sintoma

Logo ao abrir o Claude Code apontado para um gateway, aparece:

```text
[claude-code:unrecognized_model] {"model":"arsenal-supremo","query_source":"generate_session_title"}
```

E, em muitos casos, junto com:

```text
⚠ claude.ai connectors are disabled because ANTHROPIC_API_KEY or another auth source is set
```

### Causa

Nenhum dos dois é falha.

O `unrecognized_model` vem da CLI tentando executar uma tarefa auxiliar — reparar em `query_source: generate_session_title` — com um identificador que não pertence ao catálogo nativo dela. Combos virtuais do 9Router (`arsenal-supremo`, `claudegravity-fallback`) e modelos de terceiros só existem do lado do gateway; a CLI registra que não conhece o nome e prossegue. A inferência do trabalho principal acontece normalmente.

O aviso dos conectores é o comportamento esperado ao usar credencial de gateway: a sessão não está autenticada na sua conta claude.ai, então os conectores dela não são carregados.

### Solução

Nenhuma ação é necessária para o funcionamento. Para reduzir o ruído, declare o papel auxiliar apontando para um identificador que o gateway sirva:

```json
"ANTHROPIC_DEFAULT_HAIKU_MODEL": "ag/gemini-3.8-flash"
```

As tarefas auxiliares (título de sessão, resumos curtos) usam o papel Haiku. Com ele mapeado para um modelo real do gateway, o aviso desaparece sem afetar o roteamento do trabalho principal.
