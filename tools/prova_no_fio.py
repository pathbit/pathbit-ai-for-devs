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

Artefatos gerados ficam em tmp/prova_no_fio/, nunca no diretório de código.
"""

import http.server
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading

RAIZ = pathlib.Path(__file__).resolve().parent.parent
TOKEN_SONDA = "sonda-local-sem-credenciais"

# Pedir um modelo da Anthropic de propósito é o coração do teste: é assim que se
# verifica que modelOverrides intercepta em vez de deixar passar.
SESSOES = [
    ("sessão normal", []),
    ("--model claude-opus-5", ["--model", "claude-opus-5"]),
    ("--model claude-sonnet-5[1m]", ["--model", "claude-sonnet-5[1m]"]),
]


def cenarios():
    encontrados = []
    for exemplo in sorted(RAIZ.glob("0*/examples/.claude/settings.local.json*.example")):
        modulo = exemplo.parent.parent.parent
        rotulo = modulo.name[:4]
        variante = exemplo.name.replace("settings.local.json", "").replace(".example", "").strip(".")
        encontrados.append((f"{rotulo}{'/' + variante if variante else ''}", exemplo))
    return encontrados


class Sonda(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def responder(self, resposta, tipo="application/json"):
        self.send_response(200)
        self.send_header("content-type", tipo)
        self.send_header("content-length", str(len(resposta)))
        self.end_headers()
        self.wfile.write(resposta)

    def do_POST(self):
        rota = self.path.split("?", 1)[0]
        if rota == "/v1/messages/count_tokens":
            self.responder(b'{"input_tokens":1}')
            return
        if rota != "/v1/messages":
            self.send_error(404)
            return
        try:
            corpo = json.loads(self.rfile.read(int(self.headers.get("content-length", 0))))
        except (ValueError, TypeError):
            self.send_error(400)
            return
        self.server.registro.append({
            "model": corpo.get("model"),
            "bearer": self.headers.get("authorization") == f"Bearer {TOKEN_SONDA}",
            "x_api_key": bool(self.headers.get("x-api-key")),
            "tools": [t.get("type") or t.get("name") for t in corpo.get("tools", []) if isinstance(t, dict)],
        })
        mensagem = {
            "id": "msg_sonda", "type": "message", "role": "assistant",
            "model": corpo.get("model", "?"),
            "content": [{"type": "text", "text": "OK"}],
            "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 1, "output_tokens": 1},
        }
        if not corpo.get("stream"):
            self.responder(json.dumps(mensagem).encode())
            return
        eventos = [
            {"type": "message_start", "message": {**mensagem, "content": [], "stop_reason": None}},
            {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
            {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "OK"}},
            {"type": "content_block_stop", "index": 0},
            {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None},
             "usage": {"output_tokens": 1}},
            {"type": "message_stop"},
        ]
        sse = "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in eventos)
        self.responder(sse.encode(), "text/event-stream")

    def do_GET(self):
        self.responder(b'{"data":[]}')


def executa(rotulo, template, destino):
    resultados = []
    with http.server.HTTPServer(("127.0.0.1", 0), Sonda) as servidor:
        servidor.registro = []
        thread = threading.Thread(target=servidor.serve_forever, daemon=True)
        thread.start()
        try:
            cfg = json.loads(template.read_text(encoding="utf-8"))
            cfg.setdefault("env", {})["ANTHROPIC_BASE_URL"] = f"http://127.0.0.1:{servidor.server_port}"
            cfg["env"]["ANTHROPIC_AUTH_TOKEN"] = TOKEN_SONDA
            arquivo = destino / f"sonda_{rotulo.replace('/', '_')}.json"
            arquivo.write_text(json.dumps(cfg, indent=4, ensure_ascii=False), encoding="utf-8")
            with tempfile.TemporaryDirectory(dir=destino) as workspace:
                env = {k: os.environ[k] for k in ("PATH", "LANG", "LC_ALL", "SYSTEMROOT") if k in os.environ}
                env["CLAUDE_CONFIG_DIR"] = workspace
                env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
                for sessao, extra in SESSOES:
                    inicio = len(servidor.registro)
                    try:
                        processo = subprocess.run(
                            ["claude", "--setting-sources", "", "--strict-mcp-config", "--settings", str(arquivo),
                             "-p", "Responda OK.", "--max-turns", "1", *extra],
                            cwd=workspace, env=env, capture_output=True, text=True, timeout=45,
                        )
                        status = str(processo.returncode)
                    except subprocess.TimeoutExpired:
                        status = "tempo limite atingido"
                    resultados.append((sessao, status, servidor.registro[inicio:]))
        finally:
            servidor.shutdown()
            thread.join()
    return resultados


def main():
    filtro = sys.argv[1] if len(sys.argv) > 1 else None
    if not shutil.which("claude"):
        print("[!] O binário 'claude' não está no PATH -- não há o que provar sem ele.")
        return 1

    destino = RAIZ / "tmp" / "prova_no_fio"
    destino.mkdir(parents=True, exist_ok=True)

    print("=" * 92)
    print("O QUE A CLI REALMENTE ENVIA NO FIO")
    print("três sessões por cenário: normal, --model claude-opus-5, --model claude-sonnet-5[1m]")
    print("=" * 92)

    problemas = 0
    total = 0
    selecionados = [(rotulo, template) for rotulo, template in cenarios() if not filtro or rotulo.startswith(filtro)]
    if not selecionados:
        print("[!] Nenhum cenário correspondente ao filtro.")
        return 1
    for rotulo, template in selecionados:
        sessoes = executa(rotulo, template, destino)
        registro = [req for _, _, pedidos in sessoes for req in pedidos]
        for sessao, status, pedidos in sessoes:
            print(f"\n{rotulo} · {sessao}: {len(pedidos)} requisição(ões) / saída {status}")
            if status != "0" or not pedidos or any(not pedido["model"] for pedido in pedidos):
                print("   A sessão precisa concluir com sucesso e enviar ao menos uma mensagem com modelo.")
                problemas += 1
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
