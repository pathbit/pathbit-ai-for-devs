# 🔧 Solução para Token Expirado e Erro 401 no Antigravity

Este guia explica como diagnosticar e resolver automaticamente falhas de autenticação com o Google Antigravity no gateway 9Router sem precisar reiniciar containers ou recriar configurações.

---

## ❌ Sintomas Identificados

Ao tentar utilizar modelos como `ag/gemini-3.8-flash-high` ou combos que dependem do Antigravity, o terminal ou log exibe:

```text
HTTP Error 503: Service Unavailable
{"error":{"message":"[antigravity/gemini-3.8-flash-high] [401]: HTTP 401 (reset after 2m)"}}
```

Nos logs do container `claudegravity-router` (`docker logs claudegravity-router`):

```text
[18:12:19] ✗ ERROR 401 · antigravity/gemini-3.8-flash-high · 3513ms
```

---

## 🔍 Causa Raiz

O Google Antigravity utiliza tokens OAuth baseados em Bearer JWTs com validade de 1 hora (3600 segundos). Se o gateway permanecer ligado por várias horas sem renovação automática ou se você tiver feito novo login na IDE/CLI, o token registrado na base SQLite do 9Router fica desatualizado.

---

## ✅ Procedimento de Auto-Cura

Para renovar o token e atualizar o container automaticamente, criamos o utilitário `sync_antigravity_token.py`.

### Passo a Passo da Correção

1. No seu terminal, acesse a pasta do Artigo 0002 ou execute diretamente o script:
   ```bash
   python3 0002_claude_gravity_utilizando_9router/src/sync_antigravity_token.py
   ```

2. O script realiza os seguintes passos em frações de segundo:
   - Localiza o arquivo de credenciais mais recente em `~/.gemini/jetski-standalone-oauth-token` ou `~/.config/antigravity/`.
   - Lê o `refresh_token` e solicita um novo `access_token` aos servidores do Google OAuth.
   - Conecta-se ao container `claudegravity-router` e atualiza a tabela `providerConnections` do banco SQLite `/app/data/db/data.sqlite`.
   - Limpa bloqueios de rate limit anteriores.

Saída esperada:

```text
[*] Credencial detectada em: ~/.gemini/jetski-standalone-oauth-token
[+] Access token renovado com sucesso (validade: 3599s)
[+] Credenciais Antigravity injetadas no container claudegravity-router com sucesso!
```

---

## 🛡️ Prevenção e Renovação Antes de Quebrar

Todo o procedimento acima é **reativo**: você descobre o problema quando a sessão morre. Há uma causa
recorrente que dá para eliminar antes disso.

O token OAuth dura cerca de uma hora. Quando se aproxima do fim, o próprio 9Router renova  -  e, ao
gravar o resultado, escreve o campo `expiresAt` como **string ISO** em vez de epoch em milissegundos:

```text
expiresAt valor : "2026-09-11T02:05:25.091Z"
expiresAt tipo  : string
comparacao > now: false
```

`Number("2026-09-11T02:05:25.091Z")` é `NaN`, e `NaN > Date.now()` é sempre falso. A partir dali a
credencial passa a ser tratada como vencida mesmo estando ativa, com `isActive: 1`,
`testStatus: active` e `backoffLevel: 0` no banco. Nada no painel indica problema, e o sintoma chega
ao terminal como `HTTP 503`.

A prevenção é renovar antes do gateway precisar, gravando o campo como número:

```bash
# Confere e corrige, se necessario
python3 0002_claude_gravity_utilizando_9router/src/keep_connected.py

# Mantem valida enquanto voce trabalha, conferindo a cada 5 minutos
python3 0002_claude_gravity_utilizando_9router/src/keep_connected.py --daemon
```

O script só age quando precisa: com o token novo, sai sem gastar chamada. Ele sai com código `1`
quando a renovação era necessária e não teve efeito, o que permite usá-lo em automação.

### Solução Definitiva com Container Sidecar (`claudegravity-token-sync`)

Para não precisar rodar scripts manuais nem manter um terminal aberto, os arquivos `docker-compose.yml` dos módulos 0002 e 0003 incluem um container sidecar oficial (`token-sync`).

O sidecar roda continuamente com baixíssimo consumo (~14 MB de RAM e 0% de CPU), monta o banco SQLite compartilhado e a pasta `~/.gemini` em modo somente-leitura. A cada 5 minutos ele valida a integridade do token e renova preventivamente quando restam 15 minutos ou menos:

```bash
# Acompanhar a auto-renovacao em tempo real
docker logs -f claudegravity-token-sync
```

Com o sidecar ativo, a sessão nunca mais expira e o bug do `expiresAt` em string ISO é corrigido no momento em que ocorrer, sem intervenção humana.

> **Não confunda com bloqueio de cota.** Se o erro citar um modelo específico e o log do gateway
> trouxer `[AG_QUOTA] CACHE_BLOCK` ou `all 1 accounts locked for <modelo>`, a credencial está boa e o
> que acabou foi a cota daquela família. Nesse caso o `keep_connected.py` não ajuda: use um combo, que
> salta para o próximo nível.

---

## 🧪 Validação da Recuperação

Após a sincronização, confirme que o modelo primário voltou a responder imediatamente:

```bash
python3 0002_claude_gravity_utilizando_9router/src/test_gateway.py
```

Se o teste indicar `Status HTTP 200 recebido`, o canal primário está restabelecido e você pode continuar desenvolvendo normalmente sem interrupções.

---

## 🚫 Erro HTTP 403 Forbidden e a Armadilha da Conta Google sem Licença

Outro erro frequente ocorre quando o 9Router é autenticado no navegador com uma conta Google pessoal comum (gratuita), em vez da conta titular da assinatura Google AI Pro / Antigravity.

### Sintomas
- O 9Router exibe `active • OAuth #1`, mas o Claude Code ou o script `test_gateway.py` devolve:
  ```text
  HTTP Error 403: Forbidden - PERMISSION_DENIED
  ```
- Ou erro de modelo não encontrado (`404 Not Found`).

### Causa Raiz
O navegador utilizou a conta Google padrão (perfil sem plano Pro) durante o consentimento OAuth. O Google emite o token, mas recusa o acesso aos modelos restritos do Antigravity.

### Resolução Passo a Passo
1. Abra o dashboard do 9Router em `http://localhost:20128/dashboard/providers`.
2. Clique no card **Antigravity**.
3. Exclua a conexão incorreta clicando no ícone de lixeira (**Delete Connection**).
4. Em outra aba do mesmo navegador, acesse `myaccount.google.com` e verifique se o perfil ativo é a sua conta Google com a licença do Gemini Pro / Antigravity.
5. Retorne ao 9Router, clique em **+ Add Connection** e autorize com a conta licenciada.
6. Revalide no terminal com `python3 0002_claude_gravity_utilizando_9router/src/test_gateway.py`.
