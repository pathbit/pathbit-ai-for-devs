#!/usr/bin/env python3
"""Lista as travas de cota gravadas pelo 9Router em cada conta conectada.

E o laco de realimentacao do dimensionamento: projecao diz quantas contas voce
DEVERIA ter; esta tabela diz se voce acertou. Conta que trava todo dia esta
subdimensionada; conta que nunca trava e folga que absorve mais gente.

Dois campos, dois significados diferentes:

  rateLimitedUntil  -- prazo em que a janela do provedor reabre para a conta
                       INTEIRA, gravado em epoch de milissegundos.
  modelLock_<...>   -- prazo por FAMILIA de modelo. E o formato tipico do
                       Antigravity: o Gemini cai e o resto da conta segue vivo.

Nao confunda nenhum dos dois com validade de credencial (`expiresAt`), que e
outro relogio e se resolve com renovacao, nao com mais conta. O `9rtksync
--status` mostra aquele; este script mostra estes.

Le o banco pelo proprio container do gateway, como `verify_setup.py` e
`keep_connected.py` ja fazem -- o SQLite vive no volume `9router_data`, e nao
no disco do host.
"""

import json
import subprocess
import sys
from datetime import datetime

CONTAINER = "claudegravity-router"
DB_PATH = "/app/data/db/data.sqlite"

# Le apenas nome, provedor e as marcas de trava. Nenhum token e lido ou impresso.
READ_JS = (
    "const db=require('/app/node_modules/better-sqlite3')"
    f"('{DB_PATH}');"
    "const rows=db.prepare('SELECT name, provider, data FROM providerConnections"
    " ORDER BY provider, name').all().map(r=>{"
    "const d=JSON.parse(r.data||'{}');"
    "return {name:r.name, provider:r.provider,"
    " rateLimitedUntil:d.rateLimitedUntil||null,"
    " modelLocks:Object.keys(d).filter(k=>k.startsWith('modelLock_'))};});"
    "console.log(JSON.stringify(rows));"
)


def read_connections(container):
    """Devolve as conexoes registradas, ou encerra com mensagem util."""
    try:
        result = subprocess.run(
            ["docker", "exec", container, "node", "-e", READ_JS],
            capture_output=True, text=True, timeout=30,
        )
    except (subprocess.SubprocessError, OSError) as error:
        print(f"[!] Nao consegui falar com o container '{container}': {error}")
        sys.exit(1)
    if result.returncode != 0:
        print(f"[!] O container '{container}' recusou a leitura do banco.")
        print(f"    {result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ''}")
        print("    Confira se a stack esta de pe: docker ps --filter name=claudegravity")
        sys.exit(1)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("[!] Resposta do gateway em formato inesperado. O schema pode ter mudado.")
        sys.exit(1)


def format_deadline(epoch_ms):
    """Converte o prazo em ms para hora local, ou '-' quando nao ha trava."""
    if not epoch_ms:
        return "-"
    try:
        return datetime.fromtimestamp(int(epoch_ms) / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError, OverflowError):
        # Prazo gravado em formato que nao e epoch numerico: e o mesmo tipo de
        # defeito que a "Falha 2" do artigo descreve para o `expiresAt`.
        return f"ilegivel ({epoch_ms!r})"


def main():
    container = sys.argv[1] if len(sys.argv) > 1 else CONTAINER
    connections = read_connections(container)
    if not connections:
        print("Nenhuma conexao registrada no gateway.")
        return

    print(f"{'conta':<26} {'provedor':<36} {'trava geral ate':<20} travas por familia")
    print("-" * 104)
    locked = 0
    for entry in connections:
        locks = entry.get("modelLocks") or []
        deadline = format_deadline(entry.get("rateLimitedUntil"))
        if deadline != "-" or locks:
            locked += 1
        print(f"{entry['name'][:26]:<26} {entry['provider'][:36]:<36} "
              f"{deadline:<20} {len(locks)}"
              + (f"  ({', '.join(sorted(locks))})" if locks else ""))
    print("-" * 104)
    print(f"{len(connections)} conexoes, {locked} com alguma trava ativa neste instante.")
    print("Conte as travas por conta por dia durante uma semana: e a unica")
    print("evidencia de que o numero de contas acertou ou errou.")


if __name__ == "__main__":
    main()
