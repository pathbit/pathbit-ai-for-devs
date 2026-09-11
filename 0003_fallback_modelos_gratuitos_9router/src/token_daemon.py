#!/usr/bin/env python3
"""
==============================================================================
Token Daemon - Renovacao Continua de Credenciais Google Antigravity
Mantem a conexao do Google Antigravity eternamente ativa no 9Router.
Executa em background como container sidecar ou servico do host.
==============================================================================

Funcionalidades:
1. Monitora o banco SQLite do 9Router a cada ciclo (padrao: 5 minutos).
2. Detecta se o token esta ausente, expirado, com validade menor que 15 min
   ou se o campo expiresAt foi corrompido em string ISO pelo gateway.
3. Renova o access_token preventivamente via Google OAuth API oficial.
4. Grava a credencial atualizada no SQLite com expiresAt numerico.
5. Garante a presenca das chaves de API e dos combos de fallback.
"""

import argparse
import datetime
import json
import os
import re
import secrets
import signal
import sqlite3
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import uuid

# Constantes e configuracoes padrao
DEFAULT_DB_CONTAINER = "/app/data/db/data.sqlite"
DEFAULT_MARGIN_SECONDS = 900       # 15 minutos de antecedencia
DEFAULT_CHECK_INTERVAL = 300       # conferir a cada 5 minutos
DEFAULT_GATEWAY_URL = "http://claudegravity-router:20128/dashboard"
RUNNING = True


def signal_handler(signum, frame):
    global RUNNING
    print(f"\n[!] Sinal {signum} recebido. Encerrando daemon graciosamente...", flush=True)
    RUNNING = False


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def log(msg):
    """Emite log formatado com data e timestamp UTC-3 / local."""
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{agora}] {msg}", flush=True)


def locate_token_file(custom_path=None):
    """Procura o arquivo de credenciais do Antigravity no host ou container."""
    if custom_path and os.path.exists(custom_path):
        return custom_path

    candidates = [
        # Caminho montado dentro do container
        "/root/.gemini/jetski-standalone-oauth-token",
        "/root/.gemini/oauth_creds.json",
        # Caminho no host (se rodando fora do container)
        os.path.expanduser("~/.gemini/jetski-standalone-oauth-token"),
        os.path.expanduser("~/.gemini/oauth_creds.json"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def read_host_credentials(token_path):
    """Extrai refresh_token e access_token do arquivo de credenciais."""
    if not token_path or not os.path.exists(token_path):
        return None, None
    try:
        with open(token_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "token" in data and isinstance(data["token"], dict):
            tok = data["token"]
            return tok.get("refresh_token"), tok.get("access_token")
        if "refresh_token" in data:
            return data.get("refresh_token"), data.get("access_token")
    except Exception as e:
        log(f"[!] Erro ao ler credenciais em {token_path}: {e}")
    return None, None


def get_oauth_credentials():
    """Obtem client_id e client_secret dinamicamente do container, volume ou ambiente."""
    cid = os.environ.get("ANTIGRAVITY_CLIENT_ID")
    csec = os.environ.get("ANTIGRAVITY_CLIENT_SECRET")
    if cid and csec:
        return cid, csec

    # 1. Leitura direta do arquivo compartilhado pelo container do 9Router no volume
    caminhos_shared = [
        "/app/data/shared.js",
        os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "shared.js")),
        os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "shared.js")),
    ]
    for p in caminhos_shared:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    content = f.read()
                id_match = re.search(r'clientId:\s*[\'"]([^\'"]+)[\'"]', content)
                sec_match = re.search(r'clientSecret:\s*[\'"]([^\'"]+)[\'"]', content)
                if id_match and sec_match:
                    return id_match.group(1), sec_match.group(1)
            except Exception:
                pass

    # 2. Se executando no host com Docker CLI disponivel
    try:
        node_cmd = (
            "const fs = require('fs');"
            "const code = fs.readFileSync('/app/open-sse/providers/shared.js', 'utf-8');"
            "const idMatch = code.match(/clientId:\\s*['\\\"]([^'\\\"]+)['\\\"]/);"
            "const secMatch = code.match(/clientSecret:\\s*['\\\"]([^'\\\"]+)['\\\"]/);"
            "console.log(JSON.stringify({clientId: idMatch ? idMatch[1] : null, clientSecret: secMatch ? secMatch[1] : null}));"
        )
        res = subprocess.run(
            ["docker", "exec", "claudegravity-router", "node", "-e", node_cmd],
            capture_output=True, text=True, check=True, timeout=5
        )
        data = json.loads(res.stdout.strip())
        if data.get("clientId") and data.get("clientSecret"):
            return data["clientId"], data["clientSecret"]
    except Exception:
        pass

    return None, None


def refresh_google_token(refresh_token):
    """Aciona a API oficial do Google OAuth para obter novo access token."""
    client_id, client_secret = get_oauth_credentials()
    payload = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["access_token"], int(res.get("expires_in", 3600))


def resolve_api_key(env_path):
    """Localiza ou gera uma chave de API para o 9Router."""
    chave_env = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    placeholders = {"coloque_aqui_sua_chave_do_9router", "sk-sua-chave-gerada-localmente", "sk-sua-chave-do-9router", ""}
    if chave_env and chave_env not in placeholders:
        return chave_env

    if env_path and os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("ANTHROPIC_API_KEY="):
                        val = line.strip().split("=", 1)[1].split("#", 1)[0].strip().strip("'\"")
                        if val and val not in placeholders:
                            return val
        except Exception:
            pass

    nova = "sk-" + secrets.token_hex(24)
    return nova


def get_db_path(custom_path=None):
    """Identifica o caminho do banco SQLite."""
    if custom_path and os.path.exists(custom_path):
        return custom_path
    if os.environ.get("DB_PATH") and os.path.exists(os.environ["DB_PATH"]):
        return os.environ["DB_PATH"]
    if os.path.exists(DEFAULT_DB_CONTAINER):
        return DEFAULT_DB_CONTAINER
    return None


def read_db_connection(db_path):
    """Consulta os dados atuais da conexao Antigravity no SQLite."""
    if not db_path or not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM providerConnections WHERE provider = 'antigravity'")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return json.loads(row[0])
    except Exception as e:
        log(f"[!] Falha ao ler banco SQLite {db_path}: {e}")
    return None


def diagnose_token(data):
    """Classifica o estado da credencial: (status, segundos_restantes)."""
    if not data:
        return "ausente", 0
    expires_at = data.get("expiresAt")
    if isinstance(expires_at, str):
        # Caso critico: gateway gravou como texto ISO
        return "corrompido", 0
    if not isinstance(expires_at, (int, float)):
        return "corrompido", 0

    restante = int((expires_at - time.time() * 1000) / 1000)
    if restante <= 0:
        return "expirado", restante
    return "valido", restante


def update_db(db_path, access_token, refresh_token, expires_in, api_key, module="0002"):
    """Escreve no SQLite a credencial atualizada, chave de API e combos."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    expires_at_ms = int((time.time() + expires_in) * 1000)

    conn_data = {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "expiresAt": expires_at_ms,
        "scope": "https://www.googleapis.com/auth/cloud-platform https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid",
        "projectId": "aicode-consumers",
        "testStatus": "ok",
        "lastTested": now_iso,
        "backoffLevel": 0
    }

    conn = sqlite3.connect(db_path, timeout=30.0)
    try:
        cursor = conn.cursor()
        # 1. Settings
        cursor.execute("INSERT OR REPLACE INTO settings (id, data) VALUES (1, ?)",
                       (json.dumps({"requireLogin": False}),))

        # 2. Chave de API
        cursor.execute("SELECT id FROM apiKeys WHERE key = ?", (api_key,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT OR REPLACE INTO apiKeys (id, key, name, machineId, isActive, createdAt) VALUES (?, ?, ?, ?, ?, ?)",
                ("key_claudegravity_default", api_key, "ClaudeGravity Default Key", "local", 1, now_iso)
            )

        # 3. Provedor Antigravity
        cursor.execute("SELECT id FROM providerConnections WHERE provider = 'antigravity'")
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE providerConnections SET data = ?, isActive = 1, updatedAt = ? WHERE provider = 'antigravity'",
                (json.dumps(conn_data), now_iso)
            )
        else:
            conn_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO providerConnections (id, provider, authType, name, priority, isActive, data, createdAt, updatedAt) VALUES (?, 'antigravity', 'oauth', 'Google Antigravity Pro', 20, 1, ?, ?, ?)",
                (conn_id, json.dumps(conn_data), now_iso, now_iso)
            )

        # 4. Combos Padrao
        combos_padrao = [
            (
                "claudegravity-fallback",
                "llm",
                json.dumps([
                    "ag/gemini-3.8-flash-high",
                    "ag/gemini-3.7-flash-high",
                    "ag/gemini-3.6-flash-high",
                    "ag/claude-sonnet-4-6",
                    "groq/openai/gpt-oss-120b"
                ])
            ),
            (
                "claudegravity-thinking",
                "llm",
                json.dumps([
                    "ag/claude-opus-4-6-thinking",
                    "ag/claude-sonnet-4-6",
                    "ag/gemini-3.8-flash-high",
                    "groq/openai/gpt-oss-120b"
                ])
            ),
        ]

        if module == "0003":
            combos_padrao.extend([
                (
                    "arsenal-supremo",
                    "llm",
                    json.dumps([
                        "ag/gemini-3.8-flash-high",
                        "ag/gemini-3.7-flash-high",
                        "ag/gemini-3.6-flash-high",
                        "openrouter/cohere/north-mini-code:free",
                        "groq/openai/gpt-oss-120b",
                        "mistral/codestral-latest",
                        "openai-compatible-chat-ollama-local/qwen2.5-coder:latest"
                    ])
                ),
                (
                    "arsenal-rapido",
                    "llm",
                    json.dumps([
                        "groq/openai/gpt-oss-120b",
                        "mistral/codestral-latest",
                        "ag/gemini-3.7-flash-high",
                        "ag/gemini-3.6-flash-high"
                    ])
                ),
                (
                    "arsenal-offline",
                    "llm",
                    json.dumps([
                        "openai-compatible-chat-ollama-local/qwen2.5-coder:latest"
                    ])
                ),
            ])

        for c_id, c_kind, c_models in combos_padrao:
            cursor.execute("SELECT id FROM combos WHERE name = ? OR id = ?", (c_id, c_id))
            row = cursor.fetchone()
            if row:
                existing_id = row[0]
                cursor.execute(
                    "UPDATE combos SET models = ?, kind = ?, updatedAt = ? WHERE id = ?",
                    (c_models, c_kind, now_iso, existing_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO combos (id, name, kind, models, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, ?)",
                    (c_id, c_id, c_kind, c_models, now_iso, now_iso)
                )

        conn.commit()
        return True
    except Exception as e:
        log(f"[!] Erro ao atualizar banco SQLite: {e}")
        return False
    finally:
        conn.close()


def run_cycle(db_path, token_file, env_path, margin, module):
    """Executa um ciclo unico de inspecao e sincronizacao."""
    token_data = read_db_connection(db_path)
    status, restante = diagnose_token(token_data)

    precisa_renovar = (status in ("ausente", "corrompido", "expirado")) or (restante <= margin)

    if not precisa_renovar:
        minutos = restante // 60
        log(f"[OK] Token Antigravity valido no 9Router por mais {minutos} min. Nada a fazer.")
        return True

    motivos = {
        "ausente": "Nenhuma credencial cadastrada no gateway",
        "corrompido": "Campo expiresAt gravado como texto ISO pelo 9Router",
        "expirado": "Access token expirado no banco",
    }
    motivo = motivos.get(status, f"Token proximo do fim ({restante // 60} min restantes, limite {margin // 60} min)")
    log(f"[*] Renovacao necessaria: {motivo}.")

    refresh_token, fallback_access = read_host_credentials(token_file)
    if not refresh_token and token_data and isinstance(token_data.get("refreshToken"), str):
        refresh_token = token_data.get("refreshToken")

    if not refresh_token:
        log(f"[!] Nao foi possivel encontrar um refresh_token valido em {token_file}.")
        log("    Aguardando login no Antigravity IDE ou CLI ('agy login')...")
        return False

    api_key = resolve_api_key(env_path)

    try:
        novo_access, expires_in = refresh_google_token(refresh_token)
        log(f"[+] Access token renovado via Google OAuth (validade: {expires_in}s).")
    except Exception as e:
        log(f"[!] Falha na comunicacao com Google OAuth: {e}")
        if fallback_access:
            log("    Utilizando token local como contingencia provisoria.")
            novo_access = fallback_access
            expires_in = 180
        else:
            return False

    sucesso = update_db(db_path, novo_access, refresh_token, expires_in, api_key, module)
    if sucesso:
        log(f"[+] Credenciais e combos atualizados com sucesso no SQLite! Proxima expiracao em {expires_in // 60} min.")
        return True
    else:
        log("[!] Falha ao gravar credenciais atualizadas no banco.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Daemon de Renovacao Continua de Tokens do Antigravity")
    parser.add_argument("--db-path", default=None, help="Caminho para o data.sqlite")
    parser.add_argument("--token-file", default=None, help="Caminho para o token OAuth do Antigravity")
    parser.add_argument("--env-path", default=None, help="Caminho para o arquivo .env")
    parser.add_argument("--interval", type=int, default=int(os.environ.get("SYNC_INTERVAL", DEFAULT_CHECK_INTERVAL)),
                        help="Intervalo de checagem em segundos (padrao: 300)")
    parser.add_argument("--margin", type=int, default=int(os.environ.get("REFRESH_MARGIN", DEFAULT_MARGIN_SECONDS)),
                        help="Margem de antecedencia para renovacao em segundos (padrao: 900)")
    parser.add_argument("--module", default=os.environ.get("MODULE", "0002"),
                        choices=["0002", "0003"], help="Modulo de operacao (0002 ou 0003)")
    parser.add_argument("--once", action="store_true", help="Executa apenas uma vez e sai")
    args = parser.parse_args()

    log("=" * 70)
    log(f"🚀 INICIANDO CLAUDEGRAVITY TOKEN DAEMON (MODULO {args.module})")
    log("=" * 70)

    # Aguardar banco SQLite ficar disponivel (caso o container do 9router esteja inicializando)
    db_path = None
    tentativas = 0
    while RUNNING and not db_path:
        db_path = get_db_path(args.db_path)
        if not db_path or not os.path.exists(db_path):
            tentativas += 1
            if tentativas % 6 == 1:
                log("[*] Aguardando inicializacao do banco de dados SQLite do 9Router...")
            time.sleep(5)
        else:
            break

    if not RUNNING:
        return

    log(f"[+] Banco SQLite localizado: {db_path}")

    # Localizar arquivo de token
    token_file = locate_token_file(args.token_file)
    if token_file:
        log(f"[+] Arquivo de credencial Antigravity detectado: {token_file}")
    else:
        log("[!] Aviso: Arquivo de credenciais nao detectado no momento. Monitorando...")

    env_path = args.env_path or os.environ.get("ENV_PATH") or os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", ".env")
    )

    if args.once:
        run_cycle(db_path, token_file, env_path, args.margin, args.module)
        return

    log(f"[*] Modo continuo ativo: checagem a cada {args.interval}s (margem de renovacao: {args.margin}s).")

    while RUNNING:
        try:
            # Re-procura o token caso nao tenha sido encontrado na inicializacao
            if not token_file or not os.path.exists(token_file):
                token_file = locate_token_file(args.token_file)

            run_cycle(db_path, token_file, env_path, args.margin, args.module)
        except Exception as e:
            log(f"[!] Erro imprevisto no ciclo do daemon: {e}")

        # Dorme em fatias curtas para responder prontamente ao SIGTERM/SIGINT
        fim = time.time() + args.interval
        while RUNNING and time.time() < fim:
            time.sleep(1)

    log("[*] Daemon encerrado com sucesso.")


if __name__ == "__main__":
    main()
