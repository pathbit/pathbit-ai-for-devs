#!/usr/bin/env python3
"""
ClaudeGravity (Diagnostics & Setup Verification Script)
Verifica a integridade do Docker, porta 20128, configurações do Claude Code,
conexão Antigravity e combos de fallback.
"""
import json
import os
import shutil
import subprocess
import sys
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
                    value = value.split("#", 1)[0].strip().strip("'\"")
                    os.environ.setdefault(key.strip(), value)
    except OSError as e:
        print(f"⚠️  Não foi possível ler {env_path}: {e}", file=sys.stderr)


load_dotenv()

# Sem sys.exit aqui: o diagnóstico precisa rodar mesmo sem chave, para dizer
# o que está de pé. A ausência reprova apenas o check que depende dela.
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
if API_KEY in PLACEHOLDERS:
    API_KEY = ""


def check_docker():
    print("[1/5] Verificando Docker e container 9Router...")
    try:
        res = subprocess.run(
            ["docker", "ps", "--filter", "name=claudegravity-router", "--format", "{{.Names}} - {{.Status}}"],
            capture_output=True, text=True, check=True
        )
        output = res.stdout.strip()
        if output:
            print(f"  ✅ Container ativo: {output}")
            res_sync = subprocess.run(
                ["docker", "ps", "--filter", "name=claudegravity-token-sync", "--format", "{{.Names}} - {{.Status}}"],
                capture_output=True, text=True
            )
            out_sync = res_sync.stdout.strip()
            if out_sync:
                print(f"  ✅ Sidecar de auto-renovação: {out_sync}")
            return True
        else:
            print("  ⚠️  Container claudegravity-router não encontrado em execução.")
            return False
    except Exception as e:
        print(f"  ❌ Erro ao consultar Docker: {e}")
        return False


def check_endpoint():
    print("[2/5] Verificando endpoint HTTP do 9Router (http://localhost:20128)...")
    try:
        req = urllib.request.Request("http://localhost:20128/api/auth/status")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"  ✅ 9Router API online. requireLogin={data.get('requireLogin')}")
            return True
    except Exception as e:
        print(f"  ❌ Falha de conexão: {e}")
        return False


def check_models():
    print("[3/5] Verificando modelos Gemini e Antigravity disponíveis...")
    try:
        req = urllib.request.Request(
            "http://localhost:20128/v1/models",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("id") for m in data.get("data", []) if m.get("id", "").startswith("ag/")]
            if not models:
                print("  ⚠️  Nenhum modelo Antigravity (ag/*) catalogado no 9Router.")
                print("  💡 Abra http://localhost:20128/dashboard no navegador com sua conta Google AI Pro / Antigravity logada")
                print("     e conecte em Providers -> Antigravity (+ Add Connection).")
                return False
            print(f"  ✅ {len(models)} modelos Antigravity catalogados:")
            for m in models[:6]:
                print(f"     • {m}")
            return True
    except Exception as e:
        print(f"  ❌ Falha ao listar modelos: {e}")
        print("  💡 Dica: Verifique se o container está ativo e se o dashboard http://localhost:20128/dashboard")
        print("     foi configurado com a conta Google detentora da licença Antigravity.")
        return False


def check_combos():
    print("[4/5] Verificando combos de fallback e resiliência...")
    try:
        cmd = ["docker", "exec", "claudegravity-router", "node", "-e", "const db = require('/app/node_modules/better-sqlite3')('/app/data/db/data.sqlite'); console.log(JSON.stringify(db.prepare('SELECT name, models FROM combos').all()));"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        combos = json.loads(res.stdout.strip())
        print(f"  ✅ {len(combos)} combos cadastrados no 9Router:")
        for c in combos:
            models = json.loads(c.get("models", "[]"))
            print(f"     • {c.get('name')} ({len(models)} modelos)")
        ESPERADOS = {"claudegravity-fallback", "claudegravity-thinking"}
        nomes = {c.get("name") for c in combos} if combos else set()
        faltando = ESPERADOS - nomes
        if faltando:
            print(f"  ❌ Combos obrigatórios ausentes: {', '.join(sorted(faltando))}")
            print("     Rode: python3 src/claudegravity.py")
            return False
        return True
    except Exception as e:
        print(f"  ⚠️  Não foi possível inspecionar combos: {e}")
        return False


def check_claude_cli():
    print("[5/5] Verificando instalação da CLI do Claude Code...")
    claude_bin = shutil.which("claude")
    if claude_bin:
        try:
            res = subprocess.run(["claude", "--version"], capture_output=True, text=True)
            print(f"  ✅ Claude Code detectado no PATH: {res.stdout.strip() or claude_bin}")
            return True
        except Exception:
            print(f"  ✅ Claude Code detectado no PATH: {claude_bin}")
            return True
    else:
        print("  ❌ Executável 'claude' não encontrado no PATH.")
        print("     Instale com: npm install -g @anthropic-ai/claude-code")
        return False


def main():
    print("=" * 60)
    print("🔍 DIAGNÓSTICO CLAUDEGRAVITY - AMBIENTE DE EXECUÇÃO")
    print("=" * 60)

    results = [
        check_docker(),
        check_endpoint(),
        check_models(),
        check_combos(),
        check_claude_cli(),
    ]

    print("-" * 60)
    if all(results):
        print("🚀 AMBIENTE 100% OPERACIONAL E RESILIENTE!")
        print("Inicie com: python3 src/claudegravity.py")
        sys.exit(0)
    else:
        print("⚠️  Alguns componentes precisam de atenção. Veja os logs acima.")
        sys.exit(1)


if __name__ == "__main__":
    main()
