#!/usr/bin/env python3
"""
restore_permissions.py
Ferramenta para restaurar backups de configurações de permissões do Google Antigravity.
"""

import os
import sys
import glob
import shutil
import platform
import argparse

from setup_permissions import create_backup, get_system_paths

def get_gemini_dir():
    return os.path.join(os.path.expanduser("~"), ".gemini")

def list_backups(gemini_dir):
    pattern = os.path.join(gemini_dir, "backup-permissoes-*")
    dirs = sorted(glob.glob(pattern))
    return dirs

def copy_preserving(src, dest):
    """Copia o arquivo criando o diretório de destino caso ele ainda não exista."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(src, dest)

def has_restorable_content(backup_dir):
    """Confirma que o diretório de backup tem ao menos um arquivo restaurável."""
    for name in ["config.json", "settings.json", "trustedFolders.json"]:
        if os.path.exists(os.path.join(backup_dir, name)):
            return True
    if glob.glob(os.path.join(backup_dir, "projects", "*.json")):
        return True
    return bool(glob.glob(os.path.join(backup_dir, "ide_*.json")))

def restore_backup(backup_dir):
    gemini_dir = get_gemini_dir()
    home = os.path.expanduser("~")
    system = platform.system()

    # Valida a origem antes de tocar em qualquer coisa: um backup vazio ou
    # corrompido não pode render um backup extra e nenhuma restauração.
    if not has_restorable_content(backup_dir):
        print(f"❌ Backup inválido: {backup_dir} não contém nenhum arquivo restaurável.")
        print("   Nada foi alterado. Liste os backups com:")
        print("     python3 src/restore_permissions.py --list")
        return False

    if system == "Darwin":
        appdata = os.path.join(home, "Library", "Application Support")
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
    else:
        appdata = os.environ.get("XDG_CONFIG_HOME", os.path.join(home, ".config"))

    # Preserva o estado atual antes de sobrescrever, permitindo desfazer a restauração.
    print("[*] Criando backup do estado atual antes de restaurar...")
    create_backup(get_system_paths())

    print(f"[*] Restaurando backup a partir de: {backup_dir}")

    # 1. config.json
    src_cfg = os.path.join(backup_dir, "config.json")
    if os.path.exists(src_cfg):
        dest = os.path.join(gemini_dir, "config", "config.json")
        copy_preserving(src_cfg, dest)
        print(f"  ✅ Restaurado: {dest}")

    # 2. settings.json do CLI
    src_cli = os.path.join(backup_dir, "settings.json")
    if os.path.exists(src_cli):
        dest = os.path.join(gemini_dir, "antigravity-cli", "settings.json")
        copy_preserving(src_cli, dest)
        print(f"  ✅ Restaurado: {dest}")

    # 3. trustedFolders.json
    src_tf = os.path.join(backup_dir, "trustedFolders.json")
    if os.path.exists(src_tf):
        dest = os.path.join(gemini_dir, "trustedFolders.json")
        copy_preserving(src_tf, dest)
        print(f"  ✅ Restaurado: {dest}")

    # 4. Projetos
    src_proj = os.path.join(backup_dir, "projects")
    if os.path.exists(src_proj):
        dest_proj = os.path.join(gemini_dir, "config", "projects")
        for f in glob.glob(os.path.join(src_proj, "*.json")):
            copy_preserving(f, os.path.join(dest_proj, os.path.basename(f)))
        print(f"  ✅ Projetos restaurados em: {dest_proj}")

    # 5. IDE settings
    for v in ["Antigravity", "Antigravity IDE"]:
        safe_name = f"ide_{v.replace(' ', '_')}.json"
        src_ide = os.path.join(backup_dir, safe_name)
        if os.path.exists(src_ide):
            dest = os.path.join(appdata, v, "User", "settings.json")
            copy_preserving(src_ide, dest)
            print(f"  ✅ Restaurado IDE ({v}): {dest}")

    print("\n🎉 Restauração concluída. Reinicie o Antigravity IDE ou agy.")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Restaurador de backups de permissões do Google Antigravity."
    )
    parser.add_argument("--latest", action="store_true", help="Restaura o backup mais recente automaticamente.")
    parser.add_argument("--list", action="store_true", help="Apenas lista os backups disponíveis.")
    args = parser.parse_args()

    gemini_dir = get_gemini_dir()
    backups = list_backups(gemini_dir)

    print("======================================================================")
    print("📦 RESTAURADOR DE BACKUPS - GOOGLE ANTIGRAVITY")
    print("======================================================================")

    if not backups:
        print("ℹ️ Nenhum diretório de backup encontrado em ~/.gemini/backup-permissoes-*")
        return

    print("Backups disponíveis:")
    for idx, b in enumerate(backups, 1):
        print(f"  [{idx}] {os.path.basename(b)}")

    if args.list:
        return

    if args.latest:
        if not restore_backup(backups[-1]):
            sys.exit(1)
    else:
        print("\nPara restaurar o mais recente automaticamente:")
        print("  python3 src/restore_permissions.py --latest")

if __name__ == "__main__":
    main()
