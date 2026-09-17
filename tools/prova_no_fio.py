#!/usr/bin/env python3
"""Prova, na requisição HTTP, o que cada artigo promete sobre o Claude Code.

Inspecionar o `settings.local.json` mostra a *intenção*. O que os artigos afirmam
é sobre o *comportamento*: que nenhum modelo da Anthropic é usado, que o sufixo
`[1m]` não viaja, que o advisor não é anexado e que a credencial vai por
`Authorization: Bearer`. Nada disso se comprova lendo arquivo.

Este script sobe uma sonda HTTP local que finge ser a API da Anthropic, roda o
Claude Code de verdade apontado para ela com o settings de cada artigo, e mostra
exatamente o que saiu no fio.

Para cada artigo são disparadas três sessões:

1. sessão normal, sem `--model`;
2. `--model claude-opus-5`  -- pedindo explicitamente um modelo da Anthropic;
3. `--model claude-sonnet-5[1m]` -- modelo da Anthropic com o sufixo de 1M.

Se `modelOverrides` estiver correto, nas três o que chega na sonda é um modelo
do provedor configurado, nunca um `claude-*`.

Uso:
    python3 tools/prova_no_fio.py            # todos os artigos
    python3 tools/prova_no_fio.py 0004       # só os cenários de um artigo
"""

import http.server
import json
import pathlib
import shutil
import socket
import subprocess
import sys
import threading

RAIZ = pathlib.Path(__file__).resolve().parent.parent

# Pedir um modelo da Anthropic de propósito é o coração do teste: é assim que se
# verifica que modelOverrides intercepta em vez de deixar passar.
SESSOES = [
    ("sessão normal", []),
    ("--model claude-opus-5", ["--model", "claude-opus-5"]),
    ("--model claude-sonnet-5[1m]", ["--model", "claude-sonnet-5[1m]"]),
]


def cenarios():
    encontrados = []
    for exemplo in sorted(RAIZ.glob("0*/examples/.claude/*.example")):
        modulo = exemplo.parent.parent.parent
        rotulo = modulo.name[:4]
        variante = exemplo.name.replace("settings.local.json", "").replace(".example", "").strip(".")
        encontrados.append((f"{rotulo}{'/' + variante if variante else ''}", exemplo))
    return encontrados


class Sonda(http.server.BaseHTTPRequestHandler):
    registro = None

    def log_message(self, *args):
        pass

    def do_POST(self):
        tamanho = int(self.headers.get("content-length", 0))
        try:
            corpo = json.loads(self.rfile.read(tamanho))
        except Exception:
            corpo = {}
        Sonda.registro.append({
            "model": corpo.get("model"),
            "bearer": (self.headers.get("authorization") or "").startswith("Bearer "),
            "x_api_key": bool(self.headers.get("x-api-key")),
            "tools": [t.get("type") or t.get("name") for t in corpo.get("tools", []) if isinstance(t, dict)],
        })
        resposta = json.dumps({
            "id": "msg_sonda", "type": "message", "role": "assistant",
            "model": corpo.get("model", "?"),
            "content": [{"type": "text", "text": "OK"}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 1, "output_tokens": 1},
        }).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(resposta)))
        self.end_headers()
        self.wfile.write(resposta)

    def do_GET(self):
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"data":[]}')


def porta_livre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def executa(rotulo, template, destino):
    Sonda.registro = []
    porta = porta_livre()
    servidor = http.server.HTTPServer(("127.0.0.1", porta), Sonda)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()

    cfg = json.loads(template.read_text(encoding="utf-8"))
    cfg.setdefault("env", {})["ANTHROPIC_BASE_URL"] = f"http://127.0.0.1:{porta}"
    cfg["env"]["ANTHROPIC_AUTH_TOKEN"] = "sk-token-de-teste-da-sonda"
    arquivo = destino / f"sonda_{rotulo.replace('/', '_')}.json"
    arquivo.write_text(json.dumps(cfg, indent=4, ensure_ascii=False), encoding="utf-8")

    cwd = template.parent.parent
    for _, extra in SESSOES:
        subprocess.run(
            ["claude", "--settings", str(arquivo), "-p", "oi", "--max-turns", "1"] + extra,
            cwd=cwd, capture_output=True, timeout=180,
        )
    servidor.shutdown()
    return list(Sonda.registro)


def main():
    filtro = sys.argv[1] if len(sys.argv) > 1 else None
    if not shutil.which("claude"):
        print("[!] O binário 'claude' não está no PATH -- não há o que provar sem ele.")
        return 1

    destino = pathlib.Path(__file__).parent / ".prova_no_fio"
    destino.mkdir(exist_ok=True)

    print("=" * 92)
    print("O QUE A CLI REALMENTE ENVIA NO FIO")
    print("três sessões por cenário: normal, --model claude-opus-5, --model claude-sonnet-5[1m]")
    print("=" * 92)

    problemas = 0
    total = 0
    for rotulo, template in cenarios():
        if filtro and not rotulo.startswith(filtro):
            continue
        registro = executa(rotulo, template, destino)
        total += len(registro)
        modelos = sorted({r["model"] for r in registro if r["model"]})
        antropicos = [m for m in modelos if m.startswith("claude-")]
        com_1m = [m for m in modelos if "[1m]" in m]
        advisor = [t for r in registro for t in r["tools"] if "advisor" in str(t).lower()]
        sem_bearer = [r for r in registro if not r["bearer"]]
        com_api_key = [r for r in registro if r["x_api_key"]]

        print(f"\n{rotulo}   ({len(registro)} requisições)")
        print(f"   modelos no fio......: {', '.join(modelos) or '(nenhuma requisição capturada)'}")
        for nome, achado in (("modelo Anthropic", antropicos), ("sufixo [1m]", com_1m),
                             ("advisor nas tools", advisor), ("requisições sem Bearer", sem_bearer),
                             ("header x-api-key", com_api_key)):
            if achado:
                print(f"   {nome:.<20}: {achado}   <-- FALHA")
                problemas += 1
            else:
                print(f"   {nome:.<20}: NENHUM")

    print("\n" + "=" * 92)
    if problemas:
        print(f"RESULTADO: {problemas} problema(s) em {total} requisições")
        return 1
    print(f"RESULTADO: {total} requisições capturadas, nenhum modelo da Anthropic, nenhum [1m],")
    print("           nenhum advisor, credencial sempre por Authorization: Bearer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
