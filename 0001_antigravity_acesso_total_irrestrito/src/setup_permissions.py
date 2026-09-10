#!/usr/bin/env python3
"""
setup_permissions.py
Configurador idempotente e multiplataforma de permissões irrestritas para o Google Antigravity.
Aplica permissões completas no motor Agent 2.0, IDE e CLI (agy) no macOS, Linux e Windows.
"""

import os
import json
import glob
import ntpath
import re
import shutil
import platform
import argparse
import stat
import subprocess
from datetime import datetime

WILDCARDS = [
    "read_file(/)",
    "write_file(/)",
    "command(*)",
    "read_url(*)",
    "execute_url(*)",
    "mcp(*)"
]

IDE_KEYS = {
    "antigravity.agent.terminal.autoExecutionPolicy": "always",
    "antigravity.agent.terminal.confirmCommands": False,
    "antigravity.agent.terminal.allowedCommands": ["*"],
    "antigravity.terminal.autoRun": True,
    "cortex.agent.autoRun": True,
    "geminicodeassist.agentYoloMode": True,
    "security.workspace.trust.enabled": False,
    "claudeCode.includeCoAuthoredBy": False,
    "git.includeCoAuthoredBy": False,
    "github.copilot.git.includeCoAuthoredBy": False,
    "cursor.composer.includeCoAuthoredBy": False,
    "cursor.git.includeCoAuthoredBy": False,
    "git.authorCommit": True
}

UNIVERSAL_NO_AI_COAUTHORS = {
    "claudeCode.includeCoAuthoredBy": False,
    "git.includeCoAuthoredBy": False,
    "github.copilot.git.includeCoAuthoredBy": False,
    "cursor.composer.includeCoAuthoredBy": False,
    "cursor.git.includeCoAuthoredBy": False,
    "git.authorCommit": True
}

GIT_HOOK_CONTENT = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
commit-msg hook
Higieniza mensagens de commit para impedir qualquer assinatura de coautoria
com IA (Claude, Antigravity, Gemini, Anthropic, Google, OpenAI, Cursor, Copilot,
Windsurf, Devin, Kimi, Kiro, Aider, Cline, Roo, Continue, Kilo, etc.).
\"\"\"
import sys
import re

if len(sys.argv) < 2:
    sys.exit(0)

msg_file = sys.argv[1]

try:
    with open(msg_file, "r", encoding="utf-8") as f:
        content = f.read()
except Exception:
    try:
        with open(msg_file, "r", encoding="latin-1") as f:
            content = f.read()
    except Exception:
        sys.exit(0)

AI_AGENTS_REGEX = (
    r"(claude|antigravity|gemini|anthropic|google|openai|chatgpt|gpt|cursor|copilot|"
    r"windsurf|codeium|devin|cognition|kimi|moonshot|kiro|minimax|mavis|grok|xai|"
    r"aider|cline|roo|continue|kilo|qwen|mistral|codestral|deepseek|meta-ai|llama|"
    r"tabnine|amazon-q|codewhisperer|cody|sourcegraph|mentat|sweep|goose|"
    r"noreply@anthropic|noreply@google|noreply@github|github-actions|"
    r"\\bai\\b|\\bbot\\b|\\bagent\\b|\\bassistant\\b|\\bllm\\b)"
)

PROHIBITED_PATTERNS = [
    re.compile(rf"^\\s*Co-Authored-By:.*{AI_AGENTS_REGEX}.*$", re.IGNORECASE),
    re.compile(rf"^\\s*Signed-off-by:.*{AI_AGENTS_REGEX}.*$", re.IGNORECASE),
    re.compile(rf"^\\s*Authored-by:.*{AI_AGENTS_REGEX}.*$", re.IGNORECASE),
    re.compile(r"^\\s*Claude-Session:.*$", re.IGNORECASE),
    re.compile(r"^\\s*Session-ID:.*$", re.IGNORECASE),
    re.compile(r"^\\s*Generated-by:.*$", re.IGNORECASE),
    re.compile(r"^\\s*AI-Generated:.*$", re.IGNORECASE),
    re.compile(r"^\\s*Assisted-by:.*$", re.IGNORECASE),
    re.compile(rf"^\\s*🤖.*{AI_AGENTS_REGEX}.*$", re.IGNORECASE),
    re.compile(rf"^\\s*(generated|powered|authored)\\s+by\\s+.*{AI_AGENTS_REGEX}.*$", re.IGNORECASE),
]

lines = content.splitlines()
cleaned_lines = []

for line in lines:
    if any(p.match(line) for p in PROHIBITED_PATTERNS):
        continue
    cleaned_lines.append(line)

while cleaned_lines and not cleaned_lines[-1].strip():
    cleaned_lines.pop()

cleaned_content = "\\n".join(cleaned_lines) + "\\n"

if cleaned_content != content:
    with open(msg_file, "w", encoding="utf-8") as f:
        f.write(cleaned_content)

sys.exit(0)
"""

def get_system_paths():
    home = os.path.expanduser("~")
    system = platform.system()
    gemini_dir = os.path.join(home, ".gemini")

    if system == "Darwin":
        appdata = os.path.join(home, "Library", "Application Support")
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
    else:  # Linux / Unix
        xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.join(home, ".config"))
        appdata = xdg_config

    return {
        "home": home,
        "system": system,
        "gemini_dir": gemini_dir,
        "appdata": appdata,
        "config_json": os.path.join(gemini_dir, "config", "config.json"),
        "projects_dir": os.path.join(gemini_dir, "config", "projects"),
        "cli_settings": os.path.join(gemini_dir, "antigravity-cli", "settings.json"),
        "trusted_folders": os.path.join(gemini_dir, "trustedFolders.json"),
        "ide_variants": ["Antigravity", "Antigravity IDE"],
        "other_ides": ["Code", "Cursor", "Windsurf"]
    }

def get_root_key(paths):
    """Devolve a raiz a confiar. No Windows, deriva do drive do perfil do
    usuário (um perfil em D: não deve marcar C: como confiável).

    Usa ntpath explicitamente porque os.path.splitdrive só reconhece letras de
    drive quando o interpretador roda no Windows. No Windows os.path já é o
    ntpath, então o comportamento em produção é idêntico  -  a diferença é que
    assim a regra fica verificável por teste em qualquer sistema.
    """
    if paths["system"] == "Windows":
        drive = ntpath.splitdrive(paths["home"])[0]
        return (drive + "\\") if drive else "C:\\"
    return "/"

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if not content.strip():
            return {}
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Recuperação de último recurso: remove vírgula sobrando antes de } ou ].
            # Só roda quando o arquivo já é JSON inválido, para não corromper conteúdo válido.
            cleaned = re.sub(r",(\s*[}\]])", r"\1", content)
            return json.loads(cleaned)
    except Exception as e:
        print(f"  ⚠️ Aviso ao ler {path}: {e}")
        return {}

def save_json(path, data, dry_run=False):
    if dry_run:
        print(f"  [DRY-RUN] Gravaria em: {path}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)

    previous = None
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            previous = f.read()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Relê o arquivo recém-gravado: a promessa de segurança só vale se o
    # resultado final for JSON válido para o Antigravity consumir.
    try:
        with open(path, "r", encoding="utf-8") as f:
            json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        if previous is None:
            os.remove(path)
            detail = "arquivo removido (não existia antes)"
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(previous)
            detail = "conteúdo anterior restaurado"
        print(f"  ❌ Gravação inválida em {path}: {e} ({detail}).")
        raise RuntimeError(f"Falha ao validar a gravação de {path}") from e

    print(f"  ✅ Atualizado: {path}")

def merge_allow_list(existing):
    """Insere os wildcards universais e descarta entradas já cobertas por eles.

    Cada wildcard cobre todo o seu escopo, então uma regra específica como
    `command(curl ...)` vira ruído depois que `command(*)` entra na lista, e
    regras antigas costumam carregar segredos embutidos no comando salvo.
    Entradas de escopos que nenhum wildcard cobre são preservadas.
    """
    out = list(existing or [])
    for w in WILDCARDS:
        if w not in out:
            out.append(w)

    covered_scopes = {w.split("(", 1)[0] for w in WILDCARDS}
    return [
        entry for entry in out
        if entry in WILDCARDS or entry.split("(", 1)[0] not in covered_scopes
    ]

def create_backup(paths, dry_run=False):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(paths["gemini_dir"], f"backup-permissoes-{ts}")
    if dry_run:
        print(f"[*] [DRY-RUN] Criaria backup em: {backup_dir}")
        return backup_dir

    os.makedirs(os.path.join(backup_dir, "projects"), exist_ok=True)
    for p in [paths["config_json"], paths["cli_settings"], paths["trusted_folders"]]:
        if os.path.exists(p):
            fname = os.path.basename(p)
            shutil.copy2(p, os.path.join(backup_dir, fname))

    if os.path.exists(paths["projects_dir"]):
        for pf in glob.glob(os.path.join(paths["projects_dir"], "*.json")):
            shutil.copy2(pf, os.path.join(backup_dir, "projects", os.path.basename(pf)))

    for v in paths["ide_variants"]:
        ide_path = os.path.join(paths["appdata"], v, "User", "settings.json")
        if os.path.exists(ide_path):
            safe_name = f"ide_{v.replace(' ', '_')}.json"
            shutil.copy2(ide_path, os.path.join(backup_dir, safe_name))

    print(f"[*] Backup seguro criado com sucesso em: {backup_dir}")
    return backup_dir

def apply_agent_engine(paths, dry_run=False):
    print("\n[1/5] Configurando Motor Unificado Agent 2.0...")
    d = load_json(paths["config_json"])
    us = d.setdefault("userSettings", {})
    us["autoExecutionPolicy"] = "CASCADE_COMMANDS_AUTO_EXECUTION_EAGER"
    us["artifactReviewMode"] = "ARTIFACT_REVIEW_MODE_TURBO"
    us["browserJsExecutionPolicy"] = "BROWSER_JS_EXECUTION_POLICY_TURBO"
    us["enableTerminalSandbox"] = False
    us["nonWorkspaceFileAccessPolicy"] = "AGENT_SETTING_POLICY_ALLOW"
    us["includeCoAuthoredBy"] = False

    g = us.setdefault("globalPermissionGrants", {})
    g["allow"] = merge_allow_list(g.get("allow"))
    g["deny"] = []
    save_json(paths["config_json"], d, dry_run=dry_run)

def apply_projects(paths, dry_run=False):
    print("\n[2/5] Configurando Permissões dos Projetos Locais...")
    if not os.path.exists(paths["projects_dir"]):
        print("  ℹ️ Nenhum projeto cadastrado em config/projects/ ainda.")
        return

    project_files = glob.glob(os.path.join(paths["projects_dir"], "*.json"))
    if not project_files:
        print("  ℹ️ Pasta config/projects/ vazia.")
        return

    for pf in project_files:
        d = load_json(pf)
        s = d.setdefault("settings", {})
        s["fileAccessPolicy"] = "AGENT_SETTING_POLICY_ALLOW"
        s["sandboxMode"] = False
        s["autoExecutionPolicy"] = "CASCADE_COMMANDS_AUTO_EXECUTION_EAGER"
        s["artifactReviewMode"] = "ARTIFACT_REVIEW_MODE_TURBO"

        pg = d.setdefault("permissionGrants", {}).setdefault("permissionGrants", {})
        pg["allow"] = merge_allow_list(pg.get("allow"))
        pg["deny"] = []
        d["isWorkspaceOnly"] = False
        save_json(pf, d, dry_run=dry_run)

def apply_cli_and_trust(paths, dry_run=False):
    print("\n[3/5] Configurando Antigravity CLI (agy) e Trust de Pastas...")
    # CLI
    cli_d = load_json(paths["cli_settings"])
    cli_d.update({
        "agentMode": "accept-edits",
        "toolPermission": "always-proceed",
        "allowNonWorkspaceAccess": True,
        "disableWorkspaceTrustCheck": True,
        "includeCoAuthoredBy": False,
        "claudeCode.includeCoAuthoredBy": False
    })
    save_json(paths["cli_settings"], cli_d, dry_run=dry_run)

    # Trusted Folders
    trust_d = load_json(paths["trusted_folders"])
    trust_d[get_root_key(paths)] = "TRUST_PARENT"
    trust_d[paths["home"]] = "TRUST_PARENT"
    save_json(paths["trusted_folders"], trust_d, dry_run=dry_run)

def apply_ide_settings(paths, dry_run=False):
    print("\n[4/5] Configurando Antigravity IDE (VSCode Core) e Editores do Sistema...")
    found = False
    for v in paths["ide_variants"]:
        ide_path = os.path.join(paths["appdata"], v, "User", "settings.json")
        if not os.path.exists(ide_path):
            print(f"  ℹ️ IDE variante '{v}' não encontrada em: {ide_path}")
            continue
        found = True
        d = load_json(ide_path)
        d.update(IDE_KEYS)
        save_json(ide_path, d, dry_run=dry_run)
    if not found:
        print("  ℹ️ Nenhuma instalação ativa da IDE detectada no caminho padrão.")

    for other in paths.get("other_ides", []):
        other_path = os.path.join(paths["appdata"], other, "User", "settings.json")
        if os.path.exists(other_path):
            d = load_json(other_path)
            d.update(UNIVERSAL_NO_AI_COAUTHORS)
            save_json(other_path, d, dry_run=dry_run)

def apply_git_hooks(paths, dry_run=False):
    print("\n[5/5] Instalando Hook Git Global de Higienização de Commits (Sem Coautoria)...")
    git_hooks_dir = os.path.join(paths["home"], ".git-hooks")
    hook_path = os.path.join(git_hooks_dir, "commit-msg")
    if dry_run:
        print(f"  [DRY-RUN] Gravaria hook em: {hook_path}")
        return
    os.makedirs(git_hooks_dir, exist_ok=True)
    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(GIT_HOOK_CONTENT)
    os.chmod(hook_path, os.stat(hook_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"  ✅ Hook instalado: {hook_path}")
    try:
        subprocess.run(["git", "config", "--global", "core.hooksPath", git_hooks_dir], check=False, capture_output=True)
        print(f"  ✅ Git configurado globalmente: core.hooksPath = {git_hooks_dir}")
    except Exception as e:
        print(f"  ℹ️ Aviso ao configurar git global: {e}")

    # Desativação global para o Aider se for executado
    aider_conf = os.path.join(paths["home"], ".aider.conf.yml")
    if not os.path.exists(aider_conf):
        aider_content = (
            "# Desativação global de atribuição e coautoria com IA em commits\n"
            "attribute-author: false\n"
            "attribute-committer: false\n"
            "attribute-commit-message-author: false\n"
            "attribute-commit-message-committer: false\n"
        )
        try:
            with open(aider_conf, "w", encoding="utf-8") as f:
                f.write(aider_content)
            print(f"  ✅ Aider configurado sem coautoria: {aider_conf}")
        except Exception as e:
            print(f"  ℹ️ Aviso ao criar {aider_conf}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Configurador de permissões irrestritas para Google Antigravity.")
    parser.add_argument("--dry-run", action="store_true", help="Simula as alterações sem gravar nos arquivos.")
    parser.add_argument("--skip-backup", action="store_true", help="Não cria backup prévio das configurações.")
    args = parser.parse_args()

    paths = get_system_paths()
    print("======================================================================")
    print("⚡ CONFIGURADOR DE ACESSO TOTAL IRRESTRITO - GOOGLE ANTIGRAVITY")
    print(f"Sistema Detectado: {paths['system']} | Usuário: {paths['home']}")
    print("======================================================================")

    if not args.skip_backup:
        create_backup(paths, dry_run=args.dry_run)

    apply_agent_engine(paths, dry_run=args.dry_run)
    apply_projects(paths, dry_run=args.dry_run)
    apply_cli_and_trust(paths, dry_run=args.dry_run)
    apply_ide_settings(paths, dry_run=args.dry_run)
    apply_git_hooks(paths, dry_run=args.dry_run)

    print("\n======================================================================")
    print("🚀 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("Lembre-se de reiniciar o Antigravity IDE ou a CLI agy para recarregar.")
    print("Para validar o ambiente a qualquer momento, execute:")
    print("  python3 src/verify_permissions.py")
    print("======================================================================")

if __name__ == "__main__":
    main()
