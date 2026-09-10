"""Módulo de exemplo para testes do Claude Code com o Arsenal de Fallback."""

from typing import List, Dict


def process_event_stream(events: List[Dict[str, str]]) -> List[str]:
    """Processa e formata eventos recebidos de uma fila."""
    processed = []
    for evt in events:
        level = evt.get("level", "INFO").upper()
        msg = evt.get("message", "Sem conteúdo")
        processed.append(f"[{level}] {msg}")
    return processed


def main():
    events = [
        {"level": "info", "message": "Iniciando conexão com gateway 9Router"},
        {"level": "warning", "message": "Rate limit detectado, executando fallback automático"},
        {"level": "info", "message": "Inferência concluída com sucesso via modelo secundário"},
    ]
    for line in process_event_stream(events):
        print(line)


if __name__ == "__main__":
    main()
