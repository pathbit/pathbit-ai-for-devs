#!/usr/bin/env python3
"""Laboratório de simulação e teste de fallback do 9Router no Claude Code.

Este utilitário testa e comprova de forma profunda e automatizada:
1. Cenário Nominal: inferência direta e via combo no modelo primário.
2. Cenário de Rate Limit / Erro: comutação automática (hop) para o próximo modelo.
3. Cenário de Logout / Token Inválido: comportamento sob desautenticação do Antigravity.
4. Cenário de Auto-Cura: restauração de credenciais e volta ao canal primário.
5. Execução Real no Claude Code CLI: validação no terminal com bypass de permissões.

O código de saída é 0 apenas quando todos os cenários executados passam.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

GATEWAY_URL = "http://localhost:20128"
# Valores do .env.example: presentes no arquivo, mas sem chave real configurada.
PLACEHOLDERS = {"coloque_aqui_sua_chave_do_9router", "sk-sua-chave-gerada-localmente", ""}


def require_api_key():
    """Obtém a chave do gateway ou aborta: nunca há chave padrão embutida no código."""
    valor = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if valor and valor not in PLACEHOLDERS:
        return valor
    print("[!] ANTHROPIC_API_KEY não configurada.", file=sys.stderr)
    print("    A chave do gateway é gerada localmente, exclusiva desta máquina.", file=sys.stderr)
    print("    Gere-a com:  python3 ../0002_claude_gravity_utilizando_9router/src/sync_antigravity_token.py", file=sys.stderr)
    print("    Ou defina o valor manualmente no arquivo .env deste módulo.", file=sys.stderr)
    sys.exit(1)
CONTAINER_NAME = "claudegravity-router"
TEST_COMBO_ID = "sim_combo_test"

PASS = "PASSOU"
FAIL = "FALHOU"
SKIP = "PULADO"


def load_dotenv():
    """Carrega variáveis de ambiente de arquivos .env locais se existirem."""
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.getcwd(), ".env"),
    ]
    for path in search_paths:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip("'\"")
                        if key not in os.environ:
                            os.environ[key] = value
        except Exception:
            pass


load_dotenv()
API_KEY = require_api_key()


def log_header(title):
    print("\n" + "=" * 70)
    print(f"🔬 {title.upper()}")
    print("=" * 70)


def log_step(step, desc):
    print(f"\n[Etapa {step}] {desc}")


def run_node_script(script, *args, check=True):
    """Executa um script Node dentro do container.

    Os valores variáveis trafegam por process.argv, nunca interpolados no código —
    uma chave com aspas ou barra invertida quebraria (ou injetaria código no) script.
    """
    cmd = ["docker", "exec", CONTAINER_NAME, "node", "-e", script, *[str(a) for a in args]]
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def get_docker_logs_tail(lines=12):
    """Obtém as últimas linhas de log do container 9Router."""
    try:
        res = subprocess.run(
            ["docker", "logs", "--tail", str(lines), CONTAINER_NAME],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception as e:
        return f"Erro ao coletar logs: {e}"


def send_chat_request(model_name, prompt="Diga apenas: PONG", max_tokens=100):
    """Envia uma requisição no padrão Anthropic Messages API para o gateway."""
    url = f"{GATEWAY_URL}/v1/messages"
    payload = {
        "model": model_name,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "content-type": "application/json",
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            elapsed = time.time() - t0
            raw_body = resp.read().decode("utf-8")
            status = resp.status

            content = ""
            for line in raw_body.splitlines():
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if data_str and data_str != "[DONE]":
                        try:
                            parsed = json.loads(data_str)
                            if parsed.get("type") == "content_block_delta":
                                content += parsed.get("delta", {}).get("text", "")
                            elif "content" in parsed and isinstance(parsed["content"], list):
                                for block in parsed["content"]:
                                    if block.get("type") == "text":
                                        content += block.get("text", "")
                        except Exception:
                            pass

            # Sem conteúdo estruturado a resposta não é uma inferência válida: devolvemos
            # o corpo bruto apenas como diagnóstico, marcado para não passar nas asserções.
            if not content:
                return False, status, elapsed, "", f"Resposta sem bloco de texto: {raw_body[:200]}"

            return True, status, elapsed, content.strip(), None
    except urllib.error.HTTPError as e:
        elapsed = time.time() - t0
        err_body = e.read().decode("utf-8")
        return False, e.code, elapsed, "", err_body
    except Exception as e:
        elapsed = time.time() - t0
        return False, 500, elapsed, "", str(e)


def backup_antigravity_credentials():
    """Lê as credenciais do Antigravity direto do banco SQLite no container."""
    script = (
        "const db = require('/app/node_modules/better-sqlite3')('/app/data/db/data.sqlite');"
        "const row = db.prepare(\"SELECT data FROM providerConnections WHERE provider = 'antigravity'\").get();"
        "console.log(row ? row.data : '');"
    )
    return run_node_script(script).stdout.strip()


def set_antigravity_credentials(cred_json_str):
    """Atualiza as credenciais do Antigravity no SQLite."""
    script = (
        "const db = require('/app/node_modules/better-sqlite3')('/app/data/db/data.sqlite');"
        "db.prepare(\"UPDATE providerConnections SET data = ? WHERE provider = 'antigravity'\")"
        ".run(process.argv[1]);"
    )
    run_node_script(script, cred_json_str)


def register_test_combo(combo_id, combo_name, models_list):
    """Registra um combo temporário no banco SQLite."""
    script = (
        "const db = require('/app/node_modules/better-sqlite3')('/app/data/db/data.sqlite');"
        "const now = new Date().toISOString();"
        "db.prepare(\"INSERT OR REPLACE INTO combos (id, name, kind, models, createdAt, updatedAt)"
        " VALUES (?, ?, ?, ?, ?, ?)\")"
        ".run(process.argv[1], process.argv[2], 'llm', process.argv[3], now, now);"
    )
    run_node_script(script, combo_id, combo_name, json.dumps(models_list))


def delete_test_combo(combo_id):
    """Remove o combo de teste temporário."""
    script = (
        "const db = require('/app/node_modules/better-sqlite3')('/app/data/db/data.sqlite');"
        "db.prepare(\"DELETE FROM combos WHERE id = ?\").run(process.argv[1]);"
    )
    run_node_script(script, combo_id, check=False)


def clear_model_locks():
    """Remove quaisquer travas temporárias de rate limit ou lock nos modelos."""
    script = (
        "const db = require('/app/node_modules/better-sqlite3')('/app/data/db/data.sqlite');"
        "const row = db.prepare(\"SELECT id, data FROM providerConnections WHERE provider = 'antigravity'\").get();"
        "if (row) {"
        "  const parsed = JSON.parse(row.data);"
        "  delete parsed.rateLimitedUntil;"
        "  parsed.backoffLevel = 0;"
        "  for (const k of Object.keys(parsed)) { if (k.startsWith('modelLock_')) delete parsed[k]; }"
        "  db.prepare('UPDATE providerConnections SET data = ? WHERE id = ?').run(JSON.stringify(parsed), row.id);"
        "}"
    )
    run_node_script(script, check=False)


def run_claude_cli_test(model_name, prompt):
    """Dispara uma consulta real via Claude Code CLI.

    Devolve available=False quando o binário `claude` não está instalado, para que
    o cenário seja registrado como pulado em vez de derrubar a suíte inteira.
    """
    cmd = [
        "claude",
        "-p",
        prompt,
        "--model",
        model_name,
        "--dangerously-skip-permissions",
    ]
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = GATEWAY_URL
    env["ANTHROPIC_API_KEY"] = API_KEY

    examples_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "examples"))
    t0 = time.time()
    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            cwd=examples_dir if os.path.exists(examples_dir) else None,
        )
    except FileNotFoundError:
        return False, False, 0.0, "", "CLI oficial do Claude Code não encontrada no PATH."
    elapsed = time.time() - t0
    return True, res.returncode == 0, elapsed, res.stdout.strip(), res.stderr.strip()


def print_summary(results):
    """Imprime o resumo honesto de cada cenário e devolve o total de falhas."""
    log_header("Resultado Final da Suíte de Resiliência")
    icons = {PASS: "✅", FAIL: "❌", SKIP: "⏭️"}
    for name, status, detail in results:
        line = f"  {icons.get(status, '•')} {status:<7} · {name}"
        if detail:
            line += f" — {detail}"
        print(line)

    failures = sum(1 for _, status, _ in results if status == FAIL)
    skipped = sum(1 for _, status, _ in results if status == SKIP)
    passed = sum(1 for _, status, _ in results if status == PASS)

    print(f"\n  Total: {passed} aprovado(s), {failures} falha(s), {skipped} pulado(s).")
    if failures:
        print("\n[!] A suíte falhou. Corrija os cenários acima antes de publicar resultados.\n")
    else:
        print("\n[*] Todos os cenários executados foram aprovados.\n")
    return failures


def main():
    log_header("Simulador de Fallback e Resiliência Multi-Cenários do 9Router")
    print("Iniciando verificação e testes em tempo real contra o container ativo...\n")

    results = []

    backup = backup_antigravity_credentials()
    if not backup:
        print("[!] Erro fatal: nenhuma credencial encontrada no SQLite do 9Router.")
        print("[!] Execute primeiro: python3 0002_claude_gravity_utilizando_9router/src/sync_antigravity_token.py")
        sys.exit(1)
    print("✅ Credenciais ativas do Antigravity detectadas e salvas em backup de segurança.")

    try:
        clear_model_locks()

        # =====================================================================
        # CENÁRIO 1: Estado Nominal (operação primária com Antigravity)
        # =====================================================================
        log_header("Cenário 1: Estado Nominal (Antigravity Autenticado)")
        log_step("1.1", "Enviando prompt ao combo 'arsenal-supremo'...")
        ok, status, lat, text, err = send_chat_request("arsenal-supremo", "Diga: CENARIO_NOMINAL_OK")
        if ok and "CENARIO_NOMINAL_OK" in text:
            print(f"  ✅ Resposta recebida com sucesso (HTTP {status}) em {lat:.2f}s:")
            print(f"     💬 \"{text}\"")
            results.append(("Cenário 1 · Estado nominal", PASS, f"HTTP {status} em {lat:.2f}s"))
        else:
            print(f"  ❌ Falha no cenário nominal (HTTP {status}): {err}")
            results.append(("Cenário 1 · Estado nominal", FAIL, f"HTTP {status}"))

        print("\n  📋 Evidência do log do 9Router (modelo primário atendendo):")
        for line in get_docker_logs_tail(8).splitlines():
            if "COMBO" in line or "POST" in line or "DONE" in line:
                print(f"     {line}")

        # =====================================================================
        # CENÁRIO 2: Simulação de rate limit e salto automático (hop)
        # =====================================================================
        log_header("Cenário 2: Simulação de Rate Limit no Modelo Primário")
        print("Criando combo com Modelo 1 saturado e Modelo 2 como fallback imediato...")
        test_combo_name = "sim-combo-ratelimit-hop"
        register_test_combo(
            TEST_COMBO_ID,
            test_combo_name,
            ["ag/gemini-9.9-saturado-rate-limit", "ag/gemini-3.8-flash-high"],
        )
        print(f"  [+] Combo temporário registrado: {test_combo_name}")
        print("  [+] Cadeia: 1. ag/gemini-9.9-saturado (erro 404/429) -> 2. ag/gemini-3.8-flash-high")

        log_step("2.1", f"Disparando requisição para o combo '{test_combo_name}'...")
        ok, status, lat, text, err = send_chat_request(test_combo_name, "Diga: SALTO_DE_FALLBACK_CONFIRMADO")
        if ok and "SALTO_DE_FALLBACK_CONFIRMADO" in text:
            print(f"  ✅ Salto executado com sucesso! Resposta obtida em {lat:.2f}s (HTTP {status}):")
            print(f"     💬 \"{text}\"")
            results.append(("Cenário 2 · Salto de fallback", PASS, f"HTTP {status} em {lat:.2f}s"))
        else:
            print(f"  ❌ Falha na simulação de salto: {err}")
            results.append(("Cenário 2 · Salto de fallback", FAIL, f"HTTP {status}"))

        print("\n  📋 Evidência nos logs do 9Router provando o salto de modelo:")
        for line in get_docker_logs_tail(10).splitlines():
            if "COMBO" in line or "AUTH" in line or "POST" in line or "trying next" in line:
                print(f"     {line}")

        delete_test_combo(TEST_COMBO_ID)

        # =====================================================================
        # CENÁRIO 3: Simulação de logout / token inválido no Antigravity
        # =====================================================================
        log_header("Cenário 3: Simulação de Logout e Token Inválido no Antigravity")
        print("Invalidando temporariamente o access token do Antigravity no SQLite...")

        tampered = json.loads(backup)
        tampered["accessToken"] = "INVALID_SIMULATED_TOKEN_EXPIRED_LOGOUT"
        tampered["refreshToken"] = "INVALID_REFRESH_SIMULATED"
        tampered["expiresAt"] = int((time.time() - 3600) * 1000)
        set_antigravity_credentials(json.dumps(tampered))
        print("  [+] Token alterado para credencial expirada.")

        log_step("3.1", "Testando chamada direta ao modelo Antigravity deslogado...")
        ok, status, lat, text, err = send_chat_request("ag/gemini-3.8-flash-high", "Deveria falhar")
        if not ok and status in (401, 503):
            print(f"  ✅ Comportamento esperado confirmado: gateway barrou a chamada com HTTP {status}!")
            print(f"     Motivo retornado: {err[:120]}...")
            results.append(("Cenário 3 · Bloqueio sob token inválido", PASS, f"HTTP {status}"))
        else:
            print(f"  ⚠️ Retorno inesperado na chamada deslogada (HTTP {status})")
            results.append(("Cenário 3 · Bloqueio sob token inválido", FAIL, f"HTTP {status} inesperado"))

        print("\n  📋 Evidência do log do 9Router registrando a desautenticação:")
        for line in get_docker_logs_tail(8).splitlines():
            if "AUTH" in line or "ERROR" in line or "TOKEN" in line or "UNAVAILABLE" in line:
                print(f"     {line}")

        # =====================================================================
        # CENÁRIO 4: Auto-cura e restauração do Antigravity (self-healing)
        # =====================================================================
        log_header("Cenário 4: Auto-Cura e Restauração das Credenciais")
        print("Executando sincronizador oficial 'sync_antigravity_token.py'...")

        sync_script = os.path.join(
            os.path.dirname(__file__), "..", "..", "0002_claude_gravity_utilizando_9router", "src", "sync_antigravity_token.py"
        )
        sync_res = subprocess.run(["python3", sync_script], capture_output=True, text=True)
        print(sync_res.stdout.strip())

        clear_model_locks()

        log_step("4.1", "Testando recuperação imediata do canal primário...")
        ok, status, lat, text, err = send_chat_request("arsenal-supremo", "Diga: AUTO_CURA_CONCLUIDA")
        if ok and "AUTO_CURA_CONCLUIDA" in text:
            print(f"  ✅ Canal primário restabelecido com sucesso (HTTP {status}) em {lat:.2f}s:")
            print(f"     💬 \"{text}\"")
            results.append(("Cenário 4 · Auto-cura", PASS, f"HTTP {status} em {lat:.2f}s"))
        else:
            print(f"  ❌ Falha na restauração: {err}")
            results.append(("Cenário 4 · Auto-cura", FAIL, f"HTTP {status}"))

        # =====================================================================
        # CENÁRIO 5: Validação real no Claude Code CLI
        # =====================================================================
        log_header("Cenário 5: Execução Real no Claude Code CLI")
        log_step("5.1", "Executando Claude Code CLI no terminal apontado para 'arsenal-supremo'...")
        prompt_cli = "Diga apenas: 'Claude Code conectado e operando 100% via Arsenal Supremo'"
        available, ok_cli, lat_cli, out_cli, err_cli = run_claude_cli_test("arsenal-supremo", prompt_cli)

        if not available:
            print(f"  ⏭️ Cenário pulado: {err_cli}")
            print("     Instale com: npm install -g @anthropic-ai/claude-code")
            results.append(("Cenário 5 · Claude Code CLI", SKIP, "binário `claude` ausente"))
        elif ok_cli:
            print(f"  ✅ Claude Code CLI executou em {lat_cli:.2f}s com retorno íntegro:")
            print("  ┌" + "─" * 66 + "┐")
            for line in out_cli.splitlines():
                print(f"  │ {line.ljust(64)} │")
            print("  └" + "─" * 66 + "┘")
            results.append(("Cenário 5 · Claude Code CLI", PASS, f"{lat_cli:.2f}s"))
        else:
            print(f"  ❌ Falha na execução do Claude Code CLI: {err_cli}")
            results.append(("Cenário 5 · Claude Code CLI", FAIL, err_cli[:60]))

    finally:
        # Garantia de restauração: confere se as credenciais originais voltaram ao banco.
        set_antigravity_credentials(backup)
        clear_model_locks()
        delete_test_combo(TEST_COMBO_ID)

        restored = backup_antigravity_credentials()
        if restored == backup:
            print("\n[*] Credenciais originais do Antigravity restauradas e conferidas.")
        else:
            print("\n[!] ATENÇÃO: a restauração das credenciais não pôde ser confirmada.")
            print("[!] Rode: python3 0002_claude_gravity_utilizando_9router/src/sync_antigravity_token.py")
            results.append(("Restauração de credenciais", FAIL, "estado divergente do backup"))

    sys.exit(1 if print_summary(results) else 0)


if __name__ == "__main__":
    main()
