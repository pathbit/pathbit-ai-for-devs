#!/usr/bin/env python3
"""
Sincronizador automático de credenciais OAuth do Google Antigravity para o 9Router.
Extrai os tokens do Antigravity IDE (~/.gemini/jetski-standalone-oauth-token)
ou (~/.gemini/oauth_creds.json), renova o access token via Google OAuth e
atualiza o banco SQLite do container 9Router.
"""

import json
import os
import re
import secrets
import subprocess
import sys
import time
import urllib.parse
import urllib.request

DEFAULT_CONTAINER = "claudegravity-router"
ENV_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Valores do .env.example: presentes no arquivo, mas sem chave real configurada.
PLACEHOLDERS = {
    "coloque_aqui_sua_chave_do_9router",
    "sk-sua-chave-gerada-localmente",
    "",
}


def load_dotenv():
    """Carrega variáveis do .env do artigo sem sobrescrever o ambiente atual."""
    if not os.path.exists(ENV_PATH):
        return
    try:
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    value = value.split("#", 1)[0].strip().strip("'\"")
                    os.environ.setdefault(key.strip(), value)
    except OSError as e:
        print(f"[!] Não foi possível ler {ENV_PATH}: {e}", file=sys.stderr)


def persist_api_key(api_key):
    """Grava a chave gerada no .env local, criando ou substituindo a linha."""
    linha = f"ANTHROPIC_API_KEY={api_key}"
    try:
        if os.path.exists(ENV_PATH):
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                conteudo = f.read()
            if re.search(r"^ANTHROPIC_API_KEY=.*$", conteudo, re.MULTILINE):
                conteudo = re.sub(r"^ANTHROPIC_API_KEY=.*$", linha, conteudo, count=1, flags=re.MULTILINE)
            else:
                conteudo = conteudo.rstrip("\n") + f"\n{linha}\n"
        else:
            conteudo = f"{linha}\n"
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(conteudo)
        return True
    except OSError as e:
        print(f"[!] Não foi possível gravar a chave em {ENV_PATH}: {e}", file=sys.stderr)
        return False


def resolve_api_key():
    """Devolve a chave do gateway, gerando uma exclusiva desta instalação se necessário.

    A chave nunca é fixa no código: cada máquina que segue o artigo recebe um valor
    aleatório próprio, gravado no .env local, que não é versionado.
    """
    atual = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if atual and atual not in PLACEHOLDERS:
        return atual, False

    nova = "sk-" + secrets.token_hex(24)
    os.environ["ANTHROPIC_API_KEY"] = nova
    persist_api_key(nova)
    return nova, True


def get_oauth_client_creds(container_name=DEFAULT_CONTAINER):
    """Obtem o client ID e secret do Antigravity dinamicamente do container ou ambiente."""
    client_id = os.environ.get("ANTIGRAVITY_CLIENT_ID")
    client_secret = os.environ.get("ANTIGRAVITY_CLIENT_SECRET")
    if client_id and client_secret:
        return client_id, client_secret

    try:
        node_cmd = (
            "const fs = require('fs');"
            "const code = fs.readFileSync('/app/open-sse/providers/shared.js', 'utf-8');"
            "const idMatch = code.match(/clientId:\\s*['\\\"]([^'\\\"]+)['\\\"]/);"
            "const secMatch = code.match(/clientSecret:\\s*['\\\"]([^'\\\"]+)['\\\"]/);"
            "console.log(JSON.stringify({clientId: idMatch ? idMatch[1] : null, clientSecret: secMatch ? secMatch[1] : null}));"
        )
        res = subprocess.run(
            ["docker", "exec", container_name, "node", "-e", node_cmd],
            capture_output=True, text=True, check=True
        )
        data = json.loads(res.stdout.strip())
        return data.get("clientId"), data.get("clientSecret")
    except Exception:
        return None, None


def find_token():
    candidates = [
        os.path.expanduser("~/.gemini/jetski-standalone-oauth-token"),
        os.path.expanduser("~/.gemini/oauth_creds.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "token" in data and isinstance(data["token"], dict):
                    tok = data["token"]
                    return tok.get("refresh_token"), tok.get("access_token"), path
                if "refresh_token" in data:
                    return data.get("refresh_token"), data.get("access_token"), path
            except Exception:
                continue
    return None, None, None


def refresh_access_token(refresh_token, container_name=DEFAULT_CONTAINER):
    client_id, client_secret = get_oauth_client_creds(container_name)
    if not client_id or not client_secret:
        raise RuntimeError("Não foi possível obter credenciais OAuth do container ou ambiente.")

    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["access_token"], res.get("expires_in", 3600)


def wait_for_gateway(url="http://localhost:20128/api/auth/status", timeout=15):
    """Aguarda o endpoint HTTP do 9Router inicializar antes de acessar o SQLite."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status in (200, 301, 302):
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def sync_to_container(container_name=DEFAULT_CONTAINER):
    wait_for_gateway()
    load_dotenv()
    api_key, gerada = resolve_api_key()
    refresh_token, access_token, token_file = find_token()
    if not refresh_token:
        print("[!] Nenhuma credencial Google Antigravity encontrada em ~/.gemini/")
        return False

    print(f"[*] Credencial detectada em: {token_file}")
    refresh_failed = False
    try:
        new_access_token, expires_in = refresh_access_token(refresh_token, container_name)
        print(f"[+] Access token renovado com sucesso (validade: {expires_in}s)")
    except Exception as e:
        # A renovação falhou: o token local provavelmente já expirou, e injetá-lo
        # no gateway só adia a descoberta do problema para o primeiro HTTP 401.
        refresh_failed = True
        new_access_token = access_token
        expires_in = 3600
        print("")
        print("=" * 70)
        print("[!] ATENCAO: a renovacao do token via Google OAuth FALHOU.")
        print(f"    Motivo: {e}")
        print("")
        print("    O token local será injetado como último recurso, mas se ele já")
        print("    estiver expirado o gateway responderá HTTP 401 na primeira chamada.")
        print("")
        print("    Como recuperar:")
        print("      1. Refaca o login na CLI oficial:  agy login")
        print("      2. Ou reautentique o provedor Antigravity no dashboard:")
        print("         http://localhost:20128/dashboard/providers")
        print("      3. Depois execute novamente este script.")
        print("=" * 70)
        print("")

    if not new_access_token:
        print("[!] Nenhum access token disponível para injetar. Abortando.")
        return False

    expires_at_ms = int((time.time() + expires_in) * 1000)

    node_script = f"""
const db = require('/app/node_modules/better-sqlite3')('/app/data/db/data.sqlite');
const now = new Date().toISOString();

// 1. Settings (disable login requirement)
try {{
  db.prepare("INSERT OR REPLACE INTO settings (id, data) VALUES (1, ?)").run(JSON.stringify({{ requireLogin: false }}));
}} catch (e) {{}}

// 2. Chave de API desta instalacao (recebida por argumento, nunca fixa no codigo)
const apiKey = process.argv[1];
try {{
  const keyExists = db.prepare("SELECT id FROM apiKeys WHERE key = ?").get(apiKey);
  if (!keyExists) {{
    db.prepare("INSERT OR REPLACE INTO apiKeys (id, key, name, machineId, isActive, createdAt) VALUES (?, ?, ?, ?, ?, ?)")
      .run('key_claudegravity_default', apiKey, 'ClaudeGravity Default Key', 'local', 1, now);
  }}
}} catch (e) {{}}

// 3. Provider Connection for Antigravity
const connData = {{
  accessToken: "{new_access_token}",
  refreshToken: "{refresh_token}",
  expiresAt: {expires_at_ms},
  scope: "https://www.googleapis.com/auth/cloud-platform https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid",
  projectId: "aicode-consumers",
  testStatus: "ok",
  lastTested: now,
  backoffLevel: 0
}};

const existing = db.prepare("SELECT id FROM providerConnections WHERE provider = 'antigravity'").get();
if (existing) {{
  db.prepare("UPDATE providerConnections SET data = ?, isActive = 1, updatedAt = ? WHERE provider = 'antigravity'")
    .run(JSON.stringify(connData), now);
}} else {{
  const id = require('crypto').randomUUID();
  db.prepare("INSERT INTO providerConnections (id, provider, authType, name, priority, isActive, data, createdAt, updatedAt) VALUES (?, 'antigravity', 'oauth', 'Google Antigravity Pro', 20, 1, ?, ?, ?)")
    .run(id, JSON.stringify(connData), now, now);
}}

// 4. Default claudegravity-fallback combo
try {{
  const models = JSON.stringify([
    "ag/gemini-3.8-flash-high",
    "ag/gemini-3.7-flash-high",
    "ag/gemini-3.6-flash-high",
    "ag/claude-sonnet-4-6",
    "ag/gpt-oss-120b-medium"
  ]);
  db.prepare("INSERT OR REPLACE INTO combos (id, name, kind, models, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, ?)")
    .run('claudegravity-fallback', 'claudegravity-fallback', 'llm', models, now, now);
}} catch (e) {{}}

console.log('OK_SYNCED');
"""

    try:
        res = subprocess.run(
            ["docker", "exec", container_name, "node", "-e", node_script, api_key],
            capture_output=True, text=True, check=True
        )
        if "OK_SYNCED" in res.stdout:
            if gerada:
                print("")
                print("=" * 70)
                print("[+] Chave de API exclusiva desta instalacao gerada e registrada:")
                print(f"      {api_key}")
                print("")
                print(f"    Ela foi gravada em {ENV_PATH} (arquivo nao versionado).")
                print("    Use esta chave em ANTHROPIC_API_KEY ao rodar o Claude Code.")
                print("=" * 70)
                print("")
            if refresh_failed:
                # A injeção funcionou, mas o token pode estar expirado: sinaliza
                # falha para que o chamador não trate isso como ambiente saudável.
                print(f"[!] Credenciais injetadas em {container_name}, porem SEM renovacao valida.")
                print("[!] Reautentique antes de usar (veja as instruções acima).")
                return False
            print(f"[+] Credenciais Antigravity injetadas no container {container_name} com sucesso!")
            return True
        else:
            print(f"[!] Resposta inesperada do container: {res.stdout}")
            return False
    except Exception as e:
        print(f"[!] Erro ao sincronizar com o SQLite do container: {e}")
        return False


if __name__ == "__main__":
    success = sync_to_container()
    sys.exit(0 if success else 1)
