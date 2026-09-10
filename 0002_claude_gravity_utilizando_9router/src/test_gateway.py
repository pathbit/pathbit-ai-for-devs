#!/usr/bin/env python3
"""
==============================================================================
ClaudeGravity (Gateway Health Check & Models Test)
Validacao dos endpoints HTTP do 9Router, catalogo de modelos Antigravity,
inferência direta com Gemini 3.8 e teste de resiliência do combo de fallback.
==============================================================================
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

# Valores do .env.example: presentes no arquivo, mas sem chave real configurada.
PLACEHOLDERS = {"coloque_aqui_sua_chave_do_9router", "sk-sua-chave-gerada-localmente", ""}


def require_api_key():
    """Obtém a chave do gateway ou aborta: nunca há chave padrão embutida no código."""
    valor = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if valor and valor not in PLACEHOLDERS:
        return valor
    print("[!] ANTHROPIC_API_KEY não configurada.", file=sys.stderr)
    print("    A chave do gateway é gerada localmente, exclusiva desta máquina.", file=sys.stderr)
    print("    Gere-a executando:  python3 src/sync_antigravity_token.py", file=sys.stderr)
    print("    Ou defina o valor manualmente no arquivo .env deste módulo.", file=sys.stderr)
    sys.exit(1)


def load_dotenv():
    """Carrega variáveis do arquivo .env do artigo sem sobrescrever o ambiente atual."""
    env_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip().strip("'\""))
    except OSError as e:
        print(f"⚠️  Não foi possível ler {env_path}: {e}", file=sys.stderr)


load_dotenv()

ENDPOINT = os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:20128")
API_KEY = require_api_key()


def test_endpoint():
    print(f"🔍 [1/4] Verificando disponibilidade do gateway 9Router em {ENDPOINT}...")
    try:
        req = urllib.request.Request(f"{ENDPOINT}/dashboard")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status in (200, 301, 302):
                print(f"✅ Gateway 9Router está online e respondendo (HTTP {response.status})!")
                return True
    except Exception as e:
        print(f"❌ Erro ao conectar ao 9Router em {ENDPOINT}: {e}")
        return False


def test_models():
    print(f"\n🔍 [2/4] Listando modelos Antigravity registrados...")
    try:
        req = urllib.request.Request(
            f"{ENDPOINT}/v1/models",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            models = [m.get("id") for m in data.get("data", []) if m.get("id", "").startswith("ag/")]
            print(f"✅ Total de modelos Antigravity identificados: {len(models)}")
            print("Modelos em destaque:")
            for m in models[:6]:
                print(f"   • {m}")
            return len(models) > 0
    except Exception as e:
        print(f"❌ Erro ao listar modelos: {e}")
        return False


def test_inference(model: str = "ag/gemini-3.8-flash-high", step_name: str = "[3/4] Testando chamada direta ao Gemini 3.8"):
    print(f"\n🔍 {step_name} ({model})...")
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "user", "content": "Responda apenas: PONG - ClaudeGravity Operacional"}
        ],
        "max_tokens": 50
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{ENDPOINT}/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": API_KEY
            }
        )
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=30) as response:
            elapsed = time.time() - t0
            raw_body = response.read().decode("utf-8")
            print(f"✅ Status HTTP {response.status} recebido em {elapsed:.2f}s!")

            extracted = []
            for line in raw_body.split("\n"):
                if line.startswith("data: ") and not line.endswith("[DONE]"):
                    try:
                        chunk = json.loads(line[6:])
                        delta = chunk.get("delta", {})
                        if "text" in delta:
                            extracted.append(delta["text"])
                    except Exception:
                        pass

            content = "".join(extracted).strip() or raw_body[:100]
            print(f"💬 Resposta do modelo: {content}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ Erro HTTP {e.code}: {e.read().decode('utf-8')[:200]}")
        return False
    except Exception as e:
        print(f"❌ Erro na requisicao: {e}")
        return False


def main():
    print("=" * 70)
    print("🧪 TESTE DE INTEGRACAO CLAUDEGRAVITY & GATEWAY 9ROUTER")
    print("=" * 70)

    t1 = test_endpoint()
    t2 = test_models()
    t3 = test_inference("ag/gemini-3.8-flash-high", "[3/4] Testando ClaudeGravity Principal (ag/gemini-3.8-flash-high direto via Antigravity Pro)")
    t4 = test_inference("claudegravity-fallback", "[4/4] Testando ClaudeGravity Resiliente com Fallback Free (claudegravity-fallback)")

    print("\n" + "=" * 70)
    if all([t1, t2, t3, t4]):
        print("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("O ClaudeGravity está 100% operacional no modelo Principal e no Fallback.")
        sys.exit(0)
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs e a conexão do 9Router.")
        sys.exit(1)


if __name__ == "__main__":
    main()
