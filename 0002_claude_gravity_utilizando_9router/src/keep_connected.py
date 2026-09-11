#!/usr/bin/env python3
"""
==============================================================================
Keep Connected (Renovacao Preventiva da Credencial Antigravity)
Mantem a conexao do Antigravity sempre valida no 9Router, renovando o token
antes que o gateway precise renova-lo por conta propria.
==============================================================================

Por que isto existe:

O token OAuth do Antigravity dura cerca de uma hora. Quando ele se aproxima do
fim, o proprio 9Router renova  -  e, ao gravar o resultado, escreve o campo
`expiresAt` como string ISO ("2026-09-11T02:05:25.091Z") em vez de epoch em
milissegundos. A partir dai qualquer comparacao de validade falha, porque
Number("2026-09-11T...") e NaN, e a conexao passa a ser tratada como expirada
mesmo estando ativa. O sintoma e um HTTP 503 que parece desconexao.

A correcao e preventiva: renovar antes do gateway, gravando `expiresAt` como
numero. Este script confere o estado e so age quando falta pouco, entao pode
rodar em laco sem desperdicar chamada.

Uso:
    python3 src/keep_connected.py              # confere uma vez e sai
    python3 src/keep_connected.py --daemon     # fica renovando em segundo plano
    python3 src/keep_connected.py --margem 600 # renova com 10 min de folga
"""

import argparse
import json
import os
import subprocess
import sys
import time

DEFAULT_CONTAINER = "claudegravity-router"
MARGEM_PADRAO = 900          # renova quando faltar 15 min ou menos
INTERVALO_PADRAO = 300       # confere a cada 5 min no modo daemon

LEITURA_JS = (
    "const db=require('/app/node_modules/better-sqlite3')"
    "('/app/data/db/data.sqlite');"
    "const r=db.prepare(\"SELECT data FROM providerConnections "
    "WHERE provider='antigravity'\").get();"
    "console.log(r ? r.data : '');"
)


def ler_conexao(container):
    """Devolve o dicionário de credenciais gravado no gateway, ou None."""
    try:
        saida = subprocess.run(
            ["docker", "exec", container, "node", "-e", LEITURA_JS],
            capture_output=True, text=True, timeout=30,
        )
    except (subprocess.SubprocessError, OSError) as e:
        print(f"[!] Não foi possível consultar o container: {e}", file=sys.stderr)
        return None
    if saida.returncode != 0:
        # Distinguir "container não respondeu" de "credencial ausente": colapsar os
        # dois em None esconderia docker parado atrás de uma mensagem enganosa.
        erro = (saida.stderr or "").strip()[:200]
        print(f"[!] O container '{container}' não respondeu: {erro}", file=sys.stderr)
        return None
    bruto = saida.stdout.strip()
    if not bruto:
        return None
    try:
        dados = json.loads(bruto)
    except json.JSONDecodeError:
        return None
    # Um escalar JSON válido passaria pelo teste de diagnosticar e estouraria no .get
    return dados if isinstance(dados, dict) else None


def diagnosticar(dados):
    """Classifica o estado da credencial: (situacao, segundos_restantes)."""
    if not dados:
        return "ausente", 0
    valor = dados.get("expiresAt")
    if isinstance(valor, str):
        # É o caso que este script existe para corrigir: o gateway regravou
        # como string ISO e a checagem de validade dele passou a falhar.
        return "corrompido", 0
    if not isinstance(valor, (int, float)):
        return "corrompido", 0
    restante = int((valor - time.time() * 1000) / 1000)
    return ("valido" if restante > 0 else "expirado"), restante


def renovar():
    """Chama o sincronizador oficial do artigo, que grava expiresAt numérico."""
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "sync_antigravity_token.py")
    try:
        r = subprocess.run([sys.executable, script], capture_output=True,
                           text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return False, ["o sincronizador não respondeu em 120s"]
    return r.returncode == 0, (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]


def ciclo(container, margem, silencioso=False):
    """Uma passagem: diagnostica e renova se necessário. Devolve True se renovou."""
    situacao, restante = diagnosticar(ler_conexao(container))
    precisa = situacao in ("ausente", "corrompido", "expirado") or restante <= margem

    if not precisa:
        if not silencioso:
            print(f"[=] Credencial válida por mais {restante // 60} min. Nada a fazer.")
        return False

    motivo = {
        "ausente": "nenhuma credencial encontrada",
        "corrompido": "expiresAt gravado como texto pelo gateway",
        "expirado": "token vencido"
    }.get(situacao, f"faltam {restante // 60} min, abaixo da margem")

    print(f"[*] Renovando: {motivo}.")
    ok, ultima = renovar()

    # Sair com código zero não prova nada: só o estado gravado prova. Sem esta
    # conferência, um container ausente produziria "renovada" com 0 min de validade.
    situacao, restante = diagnosticar(ler_conexao(container))
    if ok and situacao == "valido" and restante > 0:
        print(f"[+] Credencial renovada. Válida por mais {restante // 60} min.")
        return True

    if situacao == "ausente":
        detalhe = f"nenhuma credencial gravada em '{container}'. O container está no ar?"
    elif situacao == "corrompido":
        detalhe = "o campo expiresAt continua inválido após a renovação."
    else:
        detalhe = ultima[0] if ultima and ultima[0] else "o sincronizador não gravou credencial válida."
    print(f"[!] Renovação não teve efeito: {detalhe}", file=sys.stderr)
    return False


def main():
    p = argparse.ArgumentParser(
        description="Mantém a credencial do Antigravity válida no 9Router.")
    p.add_argument("--container", default=DEFAULT_CONTAINER,
                   help=f"Container do gateway (padrão: {DEFAULT_CONTAINER})")
    p.add_argument("--margem", type=int, default=MARGEM_PADRAO,
                   help=f"Renovar quando faltar este tempo, em segundos (padrão: {MARGEM_PADRAO})")
    p.add_argument("--intervalo", type=int, default=INTERVALO_PADRAO,
                   help=f"Intervalo entre conferências no modo daemon (padrão: {INTERVALO_PADRAO})")
    p.add_argument("--daemon", action="store_true",
                   help="Fica conferindo em laço, em vez de sair após uma passagem")
    args = p.parse_args()

    if not args.daemon:
        # Nada a fazer também é sucesso: o que importa é a credencial estar utilizável
        # ao final. Sai com código 1 apenas quando a renovação era necessária e falhou.
        situacao, restante = diagnosticar(ler_conexao(args.container))
        precisava = situacao != "valido" or restante <= args.margem
        houve = ciclo(args.container, args.margem)
        sys.exit(1 if (precisava and not houve) else 0)

    print(f"[*] Modo contínuo: conferindo a cada {args.intervalo // 60} min, "
          f"margem de {args.margem // 60} min. Ctrl+C para encerrar.")
    try:
        while True:
            ciclo(args.container, args.margem, silencioso=True)
            time.sleep(args.intervalo)
    except KeyboardInterrupt:
        print("\n[*] Encerrado.")


if __name__ == "__main__":
    main()
