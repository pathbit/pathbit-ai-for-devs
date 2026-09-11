# 🔧 Soluções para Problemas Comuns

Este documento reúne soluções práticas para os erros e incidentes operacionais mais frequentes encontrados ao executar os ambientes do **Pathbit AI for Devs**.

> **Onde executar os comandos.** Os caminhos `src/...`, `.env` e `docker-compose.yml` citados aqui são relativos à **pasta do módulo** (`0001_antigravity_acesso_total_irrestrito`, `0002_claude_gravity_utilizando_9router` ou `0003_fallback_modelos_gratuitos_9router`), não à raiz do repositório. Entre na pasta correspondente antes de rodar.

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

1. **Correção Automática via Sidecar:** Os manifestos `docker-compose.yml` dos artigos 0002 e 0003 já incluem o container `claudegravity-token-sync` (imagem oficial `python:3.14-alpine`). Ele roda continuamente e renova o token preventivamente 15 minutos antes da expiração. Inspecione os logs com:

   ```bash
   docker logs -f claudegravity-token-sync
   ```

2. **Correção Manual Imediata:** Se precisar forçar a renovação imediata sem reiniciar containers:

   ```bash
   python3 0002_claude_gravity_utilizando_9router/src/sync_antigravity_token.py
   ```

3. Para entender todos os detalhes da análise forense e da auto-cura, consulte o guia dedicado [SOLUCAO_TOKEN_EXPIRADO_ANTIGRAVITY.md](./SOLUCAO_TOKEN_EXPIRADO_ANTIGRAVITY.md).
