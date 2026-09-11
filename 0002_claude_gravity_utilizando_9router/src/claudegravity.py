#!/usr/bin/env python3
"""
==============================================================================
ClaudeGravity (CLI Runner & Gateway Proxy Launcher)
Executa o Claude Code configurado com o gateway 9Router, Google Antigravity
e Combos de Fallback com bypass total de permissões (--dangerously-skip-permissions).
==============================================================================
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

# Valores do .env.example: presentes no arquivo, mas sem chave real configurada.
PLACEHOLDERS = {"coloque_aqui_sua_chave_do_9router", "sk-sua-chave-gerada-localmente", "sk-sua-chave-do-9router", "coloque_aqui_sua_senha", "coloque_aqui_seu_jwt_secret", ""}


def require_api_key(valor):
    """Valida a chave do gateway ou aborta: nunca há chave padrão embutida no código."""
    valor = (valor or "").strip()
    if valor and valor not in PLACEHOLDERS:
        return valor
    print("❌ Erro: ANTHROPIC_API_KEY não configurada.", file=sys.stderr)
    print("   A chave do gateway é gerada localmente, exclusiva desta máquina.", file=sys.stderr)
    print("   Gere-a executando:  python3 src/sync_antigravity_token.py", file=sys.stderr)
    print("   Ou informe a chave com --api-key.", file=sys.stderr)
    sys.exit(1)

AVAILABLE_MODELS = [
    ("ag/gemini-3.8-flash-high", "ClaudeGravity Principal (Gemini 3.8 Flash High - Antigravity Pro)"),
    ("claudegravity-fallback", "ClaudeGravity Resiliente (Fallback Automatico com Modelos Gratuitos)"),
    ("claudegravity-thinking", "ClaudeGravity Thinking (Opus 4.6 Thinking primeiro, nao depende da cota do Gemini)"),
    ("ag/gemini-3.7-flash-high", "Gemini 3.7 Flash High (Hybrid Reasoning)"),
    ("ag/gemini-3.6-flash-high", "Gemini 3.6 Flash High (Alta velocidade)"),
    ("ag/gemini-pro-agent",       "Gemini 3.1 Pro High (raciocinio profundo, mais lento)"),
    ("ag/gemini-3.1-pro-low",     "Gemini 3.1 Pro Low (resposta direta, sem raciocinio estendido)"),
    ("ag/claude-sonnet-4-6",     "Claude Sonnet 4.6 (Roteamento via Antigravity)"),
    ("ag/claude-opus-4-6-thinking", "Claude Opus 4.6 Thinking (Extended Reasoning)"),
    ("ag/gpt-oss-120b-medium",   "GPT-OSS 120B (Open-Weight Sovereign Model)"),
]

DEFAULT_CONTAINER = "claudegravity-router"


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


def ensure_fallback_combo(container_name=DEFAULT_CONTAINER):
    """Garante que as credenciais Antigravity e o combo de fallback estejam registrados no banco SQLite do 9Router."""
    try:
        check = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            capture_output=True, text=True, check=True
        )
        if container_name not in check.stdout:
            return

        # Garantir sincronizacao das credenciais do Antigravity
        try:
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            if curr_dir not in sys.path:
                sys.path.insert(0, curr_dir)
            import sync_antigravity_token
            sync_antigravity_token.sync_to_container(container_name)
        except Exception as e:
            print(f"⚠️  Falha ao sincronizar credenciais do Antigravity: {e}", file=sys.stderr)

        # Dois combos, para que o seletor de modelos nunca ofereca um ponto unico de falha.
        # A cota do Antigravity e contabilizada por familia: um bloqueio do Gemini nao atinge
        # os modelos Claude nem o GPT-OSS servidos pela mesma conta.
        node_script = """
const db = require('/app/node_modules/better-sqlite3')('/app/data/db/data.sqlite');
const now = new Date().toISOString();
const combos = [
  ['claudegravity-fallback', [
    "ag/gemini-3.8-flash-high",
    "ag/gemini-3.7-flash-high",
    "ag/gemini-3.6-flash-high",
    "ag/claude-sonnet-4-6",
    "ag/gpt-oss-120b-medium"
  ]],
  ['claudegravity-thinking', [
    "ag/claude-opus-4-6-thinking",
    "ag/claude-sonnet-4-6",
    "ag/gemini-3.8-flash-high",
    "ag/gpt-oss-120b-medium"
  ]]
];
const stmt = db.prepare('INSERT OR REPLACE INTO combos (id, name, kind, models, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, ?)');
for (const [nome, models] of combos) {
  stmt.run(nome, nome, 'llm', JSON.stringify(models), now, now);
}
"""
        r = subprocess.run(["docker", "exec", container_name, "node", "-e", node_script],
                           capture_output=True, text=True)
        if r.returncode != 0:
            # Sem esta checagem o provisionamento falharia em silêncio e o leitor
            # só descobriria ao ver a sessão morrer por combo inexistente.
            detalhe = (r.stderr or r.stdout or "").strip().splitlines()[-1:] or [""]
            print(f"⚠️  Não foi possível provisionar os combos: {detalhe[0]}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Falha ao provisionar o combo claudegravity-fallback: {e}", file=sys.stderr)


def print_banner(router_url: str, model: str):
    print("=" * 72)
    print("⚡ ClaudeGravity (Claude Code CLI com Google Antigravity & Fallback 9Router)")
    print("=" * 72)
    print(f"• Endpoint Gateway:  {router_url}")
    print(f"• Modelo Ativo:      {model}")
    print("• Modo Autônomo:     --dangerously-skip-permissions (ATIVADO)")
    print("-" * 72)
    print("Modelos e Combos de Resiliência Disponíveis:")
    for m_id, m_desc in AVAILABLE_MODELS:
        prefix = " 👉 " if m_id == model else "    "
        print(f"{prefix}{m_id:<28} : {m_desc}")
    print("=" * 72)
    print("")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="ClaudeGravity: Inicia o Claude Code integrado ao Google Antigravity e combos de fallback via 9Router.",
        add_help=False
    )
    parser.add_argument(
        "--model", "-m",
        dest="model",
        default=os.environ.get("CLAUDE_MODEL", "ag/gemini-3.8-flash-high"),
        help="Modelo ou combo a ser utilizado (padrão: ag/gemini-3.8-flash-high)"
    )
    parser.add_argument(
        "--base-url",
        dest="base_url",
        default=os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:20128"),
        help="URL base da API OpenAI/Anthropic compatível (padrão: http://localhost:20128)"
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        default=os.environ.get("ANTHROPIC_API_KEY", ""),
        help="Chave de API do 9Router (padrão: ANTHROPIC_API_KEY do ambiente ou .env)"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Lista os modelos e combos suportados e encerra"
    )

    args, extra_args = parser.parse_known_args()

    if args.list_models:
        print("Modelos e Combos ClaudeGravity catalogados:")
        for m_id, m_desc in AVAILABLE_MODELS:
            print(f"  • {m_id:<28} - {m_desc}")
        sys.exit(0)

    # A partir daqui a chave é obrigatória: sem ela o gateway rejeita as chamadas.
    args.api_key = require_api_key(args.api_key)

    # Garantir que o combo de fallback esteja ativo no 9Router
    ensure_fallback_combo()

    # Verificar se o executável do Claude Code está presente no PATH
    claude_path = shutil.which("claude")
    if not claude_path:
        print("❌ Erro: O executável 'claude' (Claude Code CLI) não foi encontrado no PATH.")
        print("Instale com: npm install -g @anthropic-ai/claude-code")
        sys.exit(1)

    # Configurar variáveis de ambiente requeridas
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = args.base_url
    env["ANTHROPIC_API_KEY"] = args.api_key
    env["ANTHROPIC_MODEL"] = args.model
    # Os quatro papéis espelham o bloco env de examples/.claude/settings.json.example,
    # que é a fonte da verdade. Cada papel usa um modelo ag/* individual, o que torna
    # o consumo previsível: você sabe exatamente qual modelo atende cada situação.
    # Os combos ficam disponíveis no modelPicker e via --model, para quando a cota de
    # uma família estourar. Uma variável já definida no ambiente tem precedência.
    for papel, padrao in (("FABLE", "ag/gemini-pro-agent"),
                          ("OPUS", "ag/gemini-3.8-flash-high"),
                          ("SONNET", "ag/gemini-3.7-flash-high"),
                          ("HAIKU", "ag/gemini-3.6-flash-high")):
        chave = f"ANTHROPIC_DEFAULT_{papel}_MODEL"
        env[chave] = os.environ.get(chave) or padrao
    env["CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT"] = "1"

    print_banner(args.base_url, args.model)

    # Montar comando do Claude Code
    cmd = [claude_path, "--dangerously-skip-permissions", "--model", args.model] + extra_args

    examples_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "examples"))
    if os.path.exists(examples_dir):
        os.chdir(examples_dir)

    # Substituir o processo atual pelo Claude Code
    os.execvpe(claude_path, cmd, env)


if __name__ == "__main__":
    main()
