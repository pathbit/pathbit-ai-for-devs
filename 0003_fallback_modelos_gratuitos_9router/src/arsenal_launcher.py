"""Launcher CLI para iniciar o Claude Code conectado aos Combos do 9Router.

Injeta as variáveis de ambiente necessárias e inicia a sessão com
--dangerously-skip-permissions e modo bypass ativo.
"""

import argparse
import os
import shutil
import subprocess
import sys

DEFAULT_COMBO = "arsenal-supremo"

# Valores do .env.example: presentes no arquivo, mas sem chave real configurada.
PLACEHOLDERS = {"coloque_aqui_sua_chave_do_9router", "sk-sua-chave-gerada-localmente", "sk-sua-chave-do-9router", "coloque_aqui_sua_senha", "coloque_aqui_seu_jwt_secret", ""}


def require_api_key(valor):
    """Valida a chave do gateway ou aborta: nunca há chave padrão embutida no código."""
    valor = (valor or "").strip()
    if valor and valor not in PLACEHOLDERS:
        return valor
    print("[!] Erro: ANTHROPIC_API_KEY não configurada.", file=sys.stderr)
    print("    A chave do gateway é gerada localmente, exclusiva desta máquina.", file=sys.stderr)
    print("    Gere-a com:  python3 ../0002_claude_gravity_utilizando_9router/src/sync_antigravity_token.py", file=sys.stderr)
    print("    Ou informe a chave com --api-key.", file=sys.stderr)
    sys.exit(1)


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
DEFAULT_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:20128")
DEFAULT_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


def check_claude_cli():
    """Verifica se a CLI do Claude Code está instalada no sistema."""
    return shutil.which("claude") is not None


def run_claude(model, base_url, api_key, extra_args):
    """Executa a CLI do Claude Code com o ambiente e o combo configurados."""
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = base_url
    env["ANTHROPIC_API_KEY"] = api_key
    env["ANTHROPIC_MODEL"] = model
    # Os quatro papéis respeitam o que o .env do módulo definir, e só caem para o
    # combo de --model quando a variável não existe. Sobrescrever sempre apagaria a
    # separação entre papel pesado e papel de alta frequência declarada no .env.
    for papel in ("FABLE", "OPUS", "SONNET", "HAIKU"):
        chave = f"ANTHROPIC_DEFAULT_{papel}_MODEL"
        env[chave] = os.environ.get(chave) or model

    # Flags avancadas
    env["CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT"] = "1"

    cmd = [
        "claude",
        "--dangerously-skip-permissions",
        "--model",
        model,
    ] + extra_args

    examples_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "examples"))
    print(f"[*] Iniciando Claude Code conectado ao combo {model} via {base_url}...")
    try:
        subprocess.run(cmd, env=env, cwd=examples_dir if os.path.exists(examples_dir) else None)
    except KeyboardInterrupt:
        print("\n[*] Sessão finalizada pelo desenvolvedor.")


def main():
    parser = argparse.ArgumentParser(
        description="Arsenal Launcher - Claude Code com Combos de Fallback no 9Router"
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_COMBO,
        help=f"Nome do combo ou modelo no 9Router (padrão: {DEFAULT_COMBO})",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"URL base do 9Router (padrão: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--api-key",
        default=DEFAULT_API_KEY,
        help="Chave de API do 9Router",
    )

    args, unknown = parser.parse_known_args()

    args.api_key = require_api_key(args.api_key)

    if not check_claude_cli():
        print("[!] Erro: CLI oficial do Claude Code não encontrada no PATH.")
        print("[!] Instale com: npm install -g @anthropic-ai/claude-code")
        sys.exit(1)

    run_claude(args.model, args.base_url, args.api_key, unknown)


if __name__ == "__main__":
    main()
