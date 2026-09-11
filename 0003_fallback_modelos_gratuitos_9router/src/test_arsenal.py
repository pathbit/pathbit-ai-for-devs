"""Validador de inferência dos combos do Arsenal no 9Router.

Testa cada nível da cascata isoladamente antes de testar o combo. Sem isso, um
combo cujo primeiro nível responde é aprovado mesmo com os níveis seguintes
mortos, e a rede de segurança só é descoberta quebrada quando já é tarde.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

# Valores do .env.example: presentes no arquivo, mas sem chave real configurada.
PLACEHOLDERS = {"coloque_aqui_sua_chave_do_9router", "sk-sua-chave-gerada-localmente", "sk-sua-chave-do-9router", "coloque_aqui_sua_senha", "coloque_aqui_seu_jwt_secret", ""}


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

# As cascatas vêm de setup_combos.py, que é a única fonte da verdade. Duplicar as
# listas aqui já causou divergência silenciosa: o validador aprovava uma cascata
# diferente da que estava provisionada no gateway.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setup_combos import COMBOS as PROVISIONED_COMBOS  # noqa: E402

# O claudegravity-fallback pertence ao artigo 0002; aqui validamos os do Arsenal.
COMBOS = {
    combo["name"]: combo["models"]
    for combo in PROVISIONED_COMBOS
    if combo["name"].startswith("arsenal-")
}


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
        except OSError:
            pass


load_dotenv()
BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:20128")
API_KEY = require_api_key()


def extract_response(raw):
    """Extrai (texto, caracteres_de_raciocínio, erro) de resposta JSON ou SSE.

    O gateway responde em text/event-stream. Modelos com raciocínio podem gastar
    todo o orçamento pensando e não emitir texto, o que ainda é uma resposta
    válida, não uma falha.
    """
    raw = raw.strip()
    try:
        data = json.loads(raw)
        if data.get("type") == "error":
            return "", 0, json.dumps(data.get("error", {}))[:120]
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        thinking = sum(len(b.get("thinking", "")) for b in data.get("content", []) if b.get("type") == "thinking")
        return text, thinking, None
    except json.JSONDecodeError:
        pass

    chunks, thinking, error = [], 0, None
    for line in raw.splitlines():
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            continue
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        if kind == "content_block_delta":
            delta = event.get("delta", {})
            chunks.append(delta.get("text", ""))
            thinking += len(delta.get("thinking", ""))
        elif kind == "content_block_start":
            block = event.get("content_block", {})
            chunks.append(block.get("text", ""))
            thinking += len(block.get("thinking", ""))
        elif kind == "error":
            error = json.dumps(event.get("error", {}))[:120]
    return "".join(chunks), thinking, error


def probe(model, prompt="Responda estritamente PONG", max_tokens=400, timeout=35):
    """Dispara uma inferência e devolve (sucesso, latência, detalhe)."""
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE_URL}/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01"
        },
    )
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            text, thinking, error = extract_response(resp.read().decode("utf-8"))
            elapsed = time.time() - started
            if error:
                return False, elapsed, f"evento de erro: {error}"
            if text.strip():
                return True, elapsed, repr(text.strip()[:40])
            if thinking:
                return True, elapsed, f"somente raciocínio ({thinking} caracteres)"
            return False, elapsed, "resposta vazia"
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8")
        try:
            detail = json.loads(detail)["error"]["message"]
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        return False, time.time() - started, f"HTTP {e.code}: {detail[:110]}"
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        return False, time.time() - started, f"{type(e).__name__}: {str(e)[:80]}"


def test_cascade(combo_name, models):
    """Testa cada nível da cascata isoladamente. Devolve a lista de níveis quebrados."""
    print(f"[*] Cascata de '{combo_name}' - {len(models)} nível(is):", flush=True)
    broken = []
    for position, model in enumerate(models, start=1):
        ok, elapsed, detail = probe(model)
        status = "OK   " if ok else "FALHA"
        print(f"  [{status}] {position}º {model} - {elapsed:.2f}s · {detail}", flush=True)
        if not ok:
            broken.append((position, model, detail))
    return broken


def test_combo(combo_name):
    """Testa o combo como um todo, do jeito que o Claude Code o consome."""
    ok, elapsed, detail = probe(combo_name)
    status = "OK   " if ok else "FALHA"
    print(f"  [{status}] combo '{combo_name}' - {elapsed:.2f}s · {detail}", flush=True)
    return ok


def main():
    print("=== Validador do Arsenal de Fallback do 9Router ===")
    print(f"    Gateway: {BASE_URL}\n")

    broken_by_combo = {}
    failed_combos = []

    for combo_name, models in COMBOS.items():
        broken = test_cascade(combo_name, models)
        if broken:
            broken_by_combo[combo_name] = broken
        if not test_combo(combo_name):
            failed_combos.append(combo_name)
        print()

    print("=" * 70)
    print("RESUMO")
    print("=" * 70)

    total_levels = sum(len(m) for m in COMBOS.values())
    total_broken = sum(len(b) for b in broken_by_combo.values())
    print(f"  Níveis testados: {total_levels} · quebrados: {total_broken}")
    print(f"  Combos testados: {len(COMBOS)} · com falha: {len(failed_combos)}")

    for combo_name, broken in broken_by_combo.items():
        for position, model, detail in broken:
            print(f"  [!] {combo_name} nível {position}: {model} - {detail}")
    for combo_name in failed_combos:
        print(f"  [!] combo '{combo_name}' não respondeu")

    if broken_by_combo or failed_combos:
        print("\n[!] Arsenal degradado: corrija os níveis acima antes de confiar na cascata.")
        sys.exit(1)

    print("\n[*] Todos os níveis e todos os combos responderam corretamente.")
    sys.exit(0)


if __name__ == "__main__":
    main()
