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
   - Conecta-se ao container `claudegravity-router` e atualiza a tabela `connections` do banco SQLite `/app/data/db/data.sqlite`.
   - Limpa bloqueios de rate limit anteriores.

Saída esperada:

```text
[*] Credencial detectada em: ~/.gemini/jetski-standalone-oauth-token
[+] Access token renovado com sucesso (validade: 3599s)
[+] Credenciais Antigravity injetadas no container claudegravity-router com sucesso!
```

---

## 🧪 Validação da Recuperação

Após a sincronização, confirme que o modelo primário voltou a responder imediatamente:

```bash
python3 0002_claude_gravity_utilizando_9router/src/test_gateway.py
```

Se o teste indicar `Status HTTP 200 recebido`, o canal primário está restabelecido e você pode continuar desenvolvendo normalmente sem interrupções.
