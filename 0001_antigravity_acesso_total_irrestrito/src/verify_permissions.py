#!/usr/bin/env python3
"""
verify_permissions.py
Diagnóstico automatizado da integridade e das permissões irrestritas do Google Antigravity.
Verifica o motor Agent 2.0, projetos locais, CLI agy, trust de pastas e configurações da IDE.
"""

import os
import sys
import json
import glob
import platform

WILDCARDS = [
    "read_file(/)",
    "write_file(/)",
    "command(*)",
    "read_url(*)",
    "execute_url(*)",
    "mcp(*)"
]

def get_paths():
    home = os.path.expanduser("~")
    system = platform.system()
    gemini_dir = os.path.join(home, ".gemini")

    if system == "Darwin":
        appdata = os.path.join(home, "Library", "Application Support")
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
    else:
        appdata = os.environ.get("XDG_CONFIG_HOME", os.path.join(home, ".config"))

    return {
        "home": home,
        "system": system,
        "config_json": os.path.join(gemini_dir, "config", "config.json"),
        "projects_dir": os.path.join(gemini_dir, "config", "projects"),
        "cli_settings": os.path.join(gemini_dir, "antigravity-cli", "settings.json"),
        "trusted_folders": os.path.join(gemini_dir, "trustedFolders.json"),
        "ide_dirs": [
            os.path.join(appdata, "Antigravity", "User", "settings.json"),
            os.path.join(appdata, "Antigravity IDE", "User", "settings.json")
        ]
    }

def check_agent_engine(paths):
    print("\n[1/5] Verificando Motor Unificado Agent 2.0 (config/config.json)...")
    p = paths["config_json"]
    if not os.path.exists(p):
        print(f"  ❌ Arquivo não encontrado: {p}")
        return False

    try:
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
        us = d.get("userSettings", {})
        policy = us.get("autoExecutionPolicy")
        review = us.get("artifactReviewMode")
        sandbox = us.get("enableTerminalSandbox")
        browser_js = us.get("browserJsExecutionPolicy")
        non_workspace = us.get("nonWorkspaceFileAccessPolicy")
        grants = us.get("globalPermissionGrants", {})
        allow = grants.get("allow", [])
        deny = grants.get("deny", [])

        ok = True
        if policy == "CASCADE_COMMANDS_AUTO_EXECUTION_EAGER":
            print("  ✅ autoExecutionPolicy: EAGER (Execução automática desimpedida)")
        else:
            print(f"  ⚠️ autoExecutionPolicy: {policy} (Esperado: CASCADE_COMMANDS_AUTO_EXECUTION_EAGER)")
            ok = False

        if review == "ARTIFACT_REVIEW_MODE_TURBO":
            print("  ✅ artifactReviewMode: TURBO (Revisão de artefatos desativada)")
        else:
            print(f"  ⚠️ artifactReviewMode: {review} (Esperado: ARTIFACT_REVIEW_MODE_TURBO)")
            ok = False

        if sandbox is False:
            print("  ✅ enableTerminalSandbox: False (Comandos rodam fora de sandbox)")
        else:
            print(f"  ⚠️ enableTerminalSandbox: {sandbox} (Esperado: False)")
            ok = False

        if browser_js == "BROWSER_JS_EXECUTION_POLICY_TURBO":
            print("  ✅ browserJsExecutionPolicy: TURBO (JavaScript liberado no navegador do agente)")
        else:
            print(f"  ⚠️ browserJsExecutionPolicy: {browser_js} (Esperado: BROWSER_JS_EXECUTION_POLICY_TURBO)")
            ok = False

        if non_workspace == "AGENT_SETTING_POLICY_ALLOW":
            print("  ✅ nonWorkspaceFileAccessPolicy: ALLOW (Leitura fora da pasta do projeto liberada)")
        else:
            print(f"  ⚠️ nonWorkspaceFileAccessPolicy: {non_workspace} (Esperado: AGENT_SETTING_POLICY_ALLOW)")
            ok = False

        missing_wildcards = [w for w in WILDCARDS if w not in allow]
        if not missing_wildcards:
            print(f"  ✅ Todos os {len(WILDCARDS)} wildcards de permissão estão presentes em allow.")
        else:
            print(f"  ⚠️ Faltam wildcards em allow: {missing_wildcards}")
            ok = False

        if not deny:
            print("  ✅ deny: [] (Lista de bloqueios vazia - Precedência limpa)")
        else:
            print(f"  ℹ️ Regras customizadas em deny: {deny}")

        return ok
    except Exception as e:
        print(f"  ❌ Erro ao analisar {p}: {e}")
        return False

def check_projects(paths):
    print("\n[2/5] Verificando Configurações de Projetos Locais...")
    p_dir = paths["projects_dir"]
    if not os.path.exists(p_dir):
        print(f"  ℹ️ Pasta {p_dir} não existe (nenhum projeto customizado).")
        return True

    files = glob.glob(os.path.join(p_dir, "*.json"))
    if not files:
        print("  ℹ️ Nenhum projeto cadastrado em config/projects/.")
        return True

    all_ok = True
    for pf in files:
        name = os.path.basename(pf)
        try:
            with open(pf, "r", encoding="utf-8") as f:
                d = json.load(f)
            pg = d.get("permissionGrants", {}).get("permissionGrants", {})
            allow = pg.get("allow", [])
            missing = [w for w in WILDCARDS if w not in allow]
            if not missing:
                print(f"  ✅ Projeto '{name}': 6/6 wildcards ativos")
            else:
                print(f"  ⚠️ Projeto '{name}': faltam {missing}")
                all_ok = False
        except Exception as e:
            print(f"  ❌ Erro ao ler projeto '{name}': {e}")
            all_ok = False
    return all_ok

def check_cli(paths):
    print("\n[3/5] Verificando Antigravity CLI (agy)...")
    p = paths["cli_settings"]
    if not os.path.exists(p):
        print(f"  ❌ Arquivo não encontrado: {p}")
        return False

    try:
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
        mode = d.get("agentMode")
        tool = d.get("toolPermission")

        ok = True
        if mode == "accept-edits":
            print("  ✅ agentMode: accept-edits (Edições sem confirmação)")
        else:
            print(f"  ⚠️ agentMode: {mode} (Esperado: accept-edits)")
            ok = False

        if tool == "always-proceed":
            print("  ✅ toolPermission: always-proceed (Ferramentas auto-aprovadas)")
        else:
            print(f"  ⚠️ toolPermission: {tool} (Esperado: always-proceed)")
            ok = False

        return ok
    except Exception as e:
        print(f"  ❌ Erro ao analisar {p}: {e}")
        return False

def check_trusted_folders(paths):
    print("\n[4/5] Verificando Confiança de Pastas (trustedFolders.json)...")
    p = paths["trusted_folders"]
    if not os.path.exists(p):
        print(f"  ❌ Arquivo não encontrado: {p}")
        return False

    try:
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)

        ok = True
        # No Windows a raiz confiável vem do drive do perfil: um usuário com
        # perfil em D: não deve depender de C: estar marcado.
        if paths["system"] == "Windows":
            drive = os.path.splitdrive(paths["home"])[0]
            root_key = (drive + os.sep) if drive else "C:\\"
        else:
            root_key = "/"
        if d.get(root_key) == "TRUST_PARENT":
            print(f"  ✅ Raiz do sistema ({root_key}) com status TRUST_PARENT")
        else:
            print(f"  ⚠️ Raiz do sistema ({root_key}) sem TRUST_PARENT")
            ok = False

        if d.get(paths["home"]) == "TRUST_PARENT":
            print(f"  ✅ Home do usuário ({paths['home']}) com status TRUST_PARENT")
        else:
            print("  ℹ️ Home sem entrada explícita em trustedFolders")

        return ok
    except Exception as e:
        print(f"  ❌ Erro ao ler {p}: {e}")
        return False

def check_ide(paths):
    print("\n[5/5] Verificando Configurações da IDE (VSCode Core)...")
    found_any = False
    all_ok = True

    for p in paths["ide_dirs"]:
        if not os.path.exists(p):
            continue
        found_any = True
        v_name = "Antigravity IDE" if "Antigravity IDE" in p else "Antigravity"
        try:
            with open(p, "r", encoding="utf-8") as f:
                d = json.load(f)

            policy = d.get("antigravity.agent.terminal.autoExecutionPolicy")
            yolo = d.get("geminicodeassist.agentYoloMode")
            trust = d.get("security.workspace.trust.enabled")

            if policy == "always" and yolo is True and trust is False:
                print(f"  ✅ IDE ({v_name}): autoExecutionPolicy='always', YOLO=True, Trust=False")
            else:
                print(f"  ⚠️ IDE ({v_name}): chaves incompletas (policy={policy}, yolo={yolo}, trust={trust})")
                all_ok = False
        except Exception as e:
            print(f"  ❌ Erro ao ler {p}: {e}")
            all_ok = False

    if not found_any:
        print("  ℹ️ Nenhuma instalação local de IDE detectada no caminho padrão.")
        return True
    return all_ok

def main():
    paths = get_paths()
    print("======================================================================")
    print("🔍 DIAGNÓSTICO DE PERMISSÕES E ACESSO TOTAL - GOOGLE ANTIGRAVITY")
    print(f"Plataforma: {paths['system']} | Usuário: {paths['home']}")
    print("======================================================================")

    r1 = check_agent_engine(paths)
    r2 = check_projects(paths)
    r3 = check_cli(paths)
    r4 = check_trusted_folders(paths)
    r5 = check_ide(paths)

    print("\n======================================================================")
    if all([r1, r2, r3, r4, r5]):
        print("🎉 ESTADO PERFEITO: TODAS AS CONFIGURAÇÕES ESTÃO 100% APLICADAS!")
        print("O Google Antigravity está pronto para operar com autonomia desimpedida.")
    else:
        print("⚠️ ALGUNS ITENS REQUEREM ATENÇÃO OU APLICAÇÃO.")
        print("Para corrigir automaticamente, execute:")
        print("  python3 src/setup_permissions.py")
    print("======================================================================")

if __name__ == "__main__":
    main()
