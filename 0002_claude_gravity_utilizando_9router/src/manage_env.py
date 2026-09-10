#!/usr/bin/env python3
"""
Pathbit AI for Devs - Gerenciador de Ciclo de Vida do Ambiente (ClaudeGravity)
Suporta criação, parada, destruição completa e diagnóstico do ambiente.
Uso:
  python3 src/manage_env.py start     # Sobe containers, sincroniza credenciais e valida
  python3 src/manage_env.py stop      # Pausa containers sem deletar dados
  python3 src/manage_env.py destroy   # DESTRÓI containers e volumes completamente (-v)
  python3 src/manage_env.py status    # Exibe a saude do container e do gateway HTTP
"""

import sys
import os
import subprocess
import time
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_cmd(cmd, check=True):
    print(f"[*] Executando: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=BASE_DIR, check=check)

def check_gateway_ready(timeout=30):
    url = "http://localhost:20128/api/auth/status"
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False

def start():
    print("=" * 60)
    print("🚀 INICIANDO AMBIENTE CLAUDEGRAVITY (9ROUTER)")
    print("=" * 60)
    run_cmd(["docker", "compose", "up", "-d"])
    print("[*] Aguardando gateway 9Router inicializar na porta 20128...")
    if check_gateway_ready():
        print("✅ Gateway 9Router pronto e respondendo!")
    else:
        print("⚠️ Gateway demorou para responder. Verifique com 'docker compose logs'.")

    sync_script = os.path.join(BASE_DIR, "src", "sync_antigravity_token.py")
    if os.path.exists(sync_script):
        print("\n[*] Sincronizando credenciais OAuth Antigravity...")
        subprocess.run([sys.executable, sync_script], cwd=BASE_DIR)

    verify_script = os.path.join(BASE_DIR, "src", "verify_setup.py")
    if os.path.exists(verify_script):
        print("\n[*] Validando integridade do ambiente...")
        subprocess.run([sys.executable, verify_script], cwd=BASE_DIR)

def stop():
    print("=" * 60)
    print("⏸️  PAUSANDO CONTAINERS (SEM DELETAR DADOS)")
    print("=" * 60)
    run_cmd(["docker", "compose", "stop"], check=False)
    print("✅ Containers pausados.")

def destroy():
    print("=" * 60)
    print("💣 DESTRUINDO AMBIENTE COMPLETO (CONTAINERS + VOLUMES)")
    print("=" * 60)
    run_cmd(["docker", "compose", "down", "-v", "--remove-orphans"], check=False)
    print("✅ Todos os containers, redes e volumes Docker foram destruidos.")
    print("O ambiente está limpo.")

def status():
    print("=" * 60)
    print("🔍 STATUS DO AMBIENTE CLAUDEGRAVITY")
    print("=" * 60)
    run_cmd(["docker", "ps", "--filter", "name=claudegravity-router"], check=False)
    try:
        req = urllib.request.urlopen("http://localhost:20128/api/auth/status", timeout=2)
        print(f"✅ Gateway HTTP Status: {req.status} OK")
    except Exception as e:
        print(f"❌ Gateway HTTP Offline: {e}")

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ["start", "stop", "destroy", "status"]:
        print(__doc__)
        sys.exit(1)
    
    action = sys.argv[1]
    if action == "start":
        start()
    elif action == "stop":
        stop()
    elif action == "destroy":
        destroy()
    elif action == "status":
        status()

if __name__ == "__main__":
    main()
