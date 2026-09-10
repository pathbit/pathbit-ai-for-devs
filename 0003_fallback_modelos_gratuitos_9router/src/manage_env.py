#!/usr/bin/env python3
"""
Pathbit AI for Devs - Gerenciador de Ciclo de Vida do Ambiente (Arsenal de Fallback)
Suporta criação, parada, destruição completa e diagnóstico do ambiente.
Uso:
  python3 src/manage_env.py start     # Sobe 9Router e Ollama, provisiona combos e valida
  python3 src/manage_env.py stop      # Pausa containers sem deletar dados
  python3 src/manage_env.py destroy   # DESTRÓI containers e volumes completamente (-v)
  python3 src/manage_env.py status    # Exibe a saude dos containers e endpoints HTTP
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

def check_service_ready(url, timeout=30):
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
    print("🚀 INICIANDO AMBIENTE DO ARSENAL DE FALLBACK (9ROUTER + OLLAMA)")
    print("=" * 60)
    run_cmd(["docker", "compose", "up", "-d"])
    print("[*] Aguardando servicos estarem prontos...")
    if check_service_ready("http://localhost:20128/api/auth/status"):
        print("✅ Gateway 9Router pronto na porta 20128!")
    else:
        print("⚠️ 9Router demorou para responder.")

    if check_service_ready("http://localhost:11434/api/tags"):
        print("✅ Servico Ollama pronto na porta 11434!")
    else:
        print("⚠️ Ollama demorou para responder.")

    # Executa provisionamento idempotente dos combos
    setup_script = os.path.join(BASE_DIR, "src", "setup_combos.py")
    if os.path.exists(setup_script):
        print("\n[*] Provisionando combos de fallback no 9Router...")
        subprocess.run([sys.executable, setup_script], cwd=BASE_DIR)

    # Executa teste do arsenal
    test_script = os.path.join(BASE_DIR, "src", "test_arsenal.py")
    if os.path.exists(test_script):
        print("\n[*] Validando inferencia dos combos...")
        subprocess.run([sys.executable, test_script], cwd=BASE_DIR)

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
    print("🔍 STATUS DO AMBIENTE DO ARSENAL")
    print("=" * 60)
    run_cmd(["docker", "ps", "--filter", "name=claudegravity-router", "--filter", "name=claudegravity-ollama"], check=False)
    try:
        req = urllib.request.urlopen("http://localhost:20128/api/auth/status", timeout=2)
        print(f"✅ 9Router HTTP Status: {req.status} OK (porta 20128)")
    except Exception as e:
        print(f"❌ 9Router Offline: {e}")

    try:
        req2 = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        print(f"✅ Ollama HTTP Status: {req2.status} OK (porta 11434)")
    except Exception as e:
        print(f"❌ Ollama Offline: {e}")

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
