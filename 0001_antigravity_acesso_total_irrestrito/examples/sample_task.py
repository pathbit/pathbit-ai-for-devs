"""
sample_task.py
Exemplo prático de automação para testes de agentes com acesso total irrestrito.
Demonstra leitura, processamento e escrita de arquivos sem interrupções manuais.
"""

import os
import json
from datetime import datetime

def generate_health_report():
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "OPERATIONAL",
        "agent": "Google Antigravity Agent 2.0",
        "features": {
            "autoExecution": "CASCADE_COMMANDS_AUTO_EXECUTION_EAGER",
            "artifactReview": "TURBO",
            "terminalSandbox": False,
            "permissions": "ALL_GRANTED"
        }
    }
    # Ancora a saída no diretório do próprio script, independente do diretório de execução.
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "health_report.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"✅ Relatório gerado com sucesso em: {output_file}")
    return output_file

def main():
    print("[*] Iniciando tarefa prática de teste no ambiente isolado...")
    out = generate_health_report()
    if os.path.exists(out):
        with open(out, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[*] Status confirmado: {data.get('status')} via {data.get('agent')}")

if __name__ == "__main__":
    main()
