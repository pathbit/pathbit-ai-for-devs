#!/usr/bin/env python3
"""Exercita os contratos HTTP do Agregador SDD com um SQLite descartável."""

import argparse
from contextlib import contextmanager
from email.utils import format_datetime
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

RAIZ = Path(__file__).resolve().parents[2]
APP = RAIZ / "0005_sdd_do_vibe_coding_a_engenharia_deterministica"
TITULO = "Daily newsletter de autenticação"


class Feed(BaseHTTPRequestHandler):
    def do_GET(self):
        data = format_datetime(datetime.now(timezone.utc), usegmt=True)
        rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Feed de contratos</title>
<link>https://example.org/</link><description>Observações locais</description>
<item><title>{TITULO}</title><link>https://example.org/auth</link>
<description>A equipe reforçou a segurança do serviço após revisar a autenticação. Os operadores podem agora confirmar a configuração no painel.</description>
<pubDate>{data}</pubDate></item>
<item><title>SQLite no backend</title><link>https://example.org/sqlite</link>
<description>Uma aplicação armazena os artigos localmente.</description><pubDate>{data}</pubDate></item>
</channel></rss>""".encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/rss+xml; charset=utf-8")
        self.send_header("Content-Length", str(len(rss)))
        self.end_headers()
        self.wfile.write(rss)

    def log_message(self, *_args):
        pass


@contextmanager
def servir_feed():
    with ThreadingHTTPServer(("127.0.0.1", 0), Feed) as servidor:
        thread = threading.Thread(target=servidor.serve_forever)
        thread.start()
        try:
            yield f"http://127.0.0.1:{servidor.server_port}/noticias.xml"
        finally:
            servidor.shutdown()
            thread.join()


@contextmanager
def iniciar_app(app):
    with tempfile.TemporaryDirectory(prefix="gate-sdd-") as pasta:
        config = {
            **os.environ,
            "PORT": "0",
            "HOST": "127.0.0.1",
            "NODE_ENV": "production",
            "DATABASE_PATH": str(Path(pasta) / "contratos.sqlite"),
            "ANTHROPIC_BASE_URL": "",
            "ANTHROPIC_API_KEY": "",
            "ANTHROPIC_AUTH_TOKEN": "",
        }
        log = Path(pasta) / "servidor.log"
        with log.open("w", encoding="utf-8") as saida, subprocess.Popen(
            ["node", "src/server.js"], cwd=app, env=config, stdout=saida, stderr=subprocess.STDOUT
        ) as processo:
            try:
                for _ in range(100):
                    porta = re.search(r"Dashboard: http://127\.0\.0\.1:(\d+)", log.read_text(encoding="utf-8"))
                    if porta:
                        yield f"http://127.0.0.1:{porta[1]}"
                        break
                    if processo.poll() is not None:
                        raise RuntimeError("O servidor encerrou. Instale as dependências do artigo 0005 com npm ci.")
                    time.sleep(0.1)
                else:
                    raise RuntimeError("O Agregador não iniciou no tempo previsto.")
            finally:
                if processo.poll() is None:
                    processo.terminate()
                    try:
                        processo.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        processo.kill()
                        processo.wait()


def chamar(base, caminho, metodo="GET", payload=None):
    dados = json.dumps(payload).encode() if payload is not None else None
    pedido = Request(base + caminho, data=dados, method=metodo)
    if dados is not None:
        pedido.add_header("Content-Type", "application/json")
    try:
        with urlopen(pedido, timeout=8) as resposta:
            return resposta.status, json.load(resposta)
    except HTTPError as erro:
        with erro:
            return erro.code, json.load(erro)


def verificar(base, url_feed, resultados):
    def registrar(nome, condicao):
        resultados.append({"contrato": nome, "aprovado": bool(condicao)})

    status, itens = chamar(base, "/artigos")
    registrar("Banco novo começa sem artigos", status == 200 and itens == [])

    status, importacao = chamar(base, "/feeds/importar", "POST", {"url": url_feed})
    registrar("Importação inicial cria dois artigos", status == 200 and importacao.get("importados") == 2)
    status, repeticao = chamar(base, "/feeds/importar", "POST", {"url": url_feed})
    registrar("Segunda importação não duplica artigos", status == 200 and repeticao.get("importados") == 0)

    status, seguranca = chamar(base, "/artigos?categoria=Seguran%C3%A7a")
    categoria_correta = status == 200 and [a["titulo"] for a in seguranca] == [TITULO]
    registrar("Filtro retorna só o artigo de Segurança", categoria_correta)
    status, busca = chamar(base, "/artigos?busca=autentica%C3%A7%C3%A3o")
    busca_correta = status == 200 and [a["titulo"] for a in busca] == [TITULO]
    registrar("Busca encontra o título acentuado", busca_correta)
    status, _ = chamar(base, "/artigos?limit=invalido")
    registrar("Paginação inválida retorna 422", status == 422)

    if busca_correta:
        artigo = busca[0]["id"]
        rota = f"/artigos/{artigo}/resumir"
        status1, primeiro = chamar(base, rota, "POST")
        status2, segundo = chamar(base, rota, "POST")
        texto = primeiro.get("resumo")
        registrar("Resumo é criado e recuperado do cache",
                  status1 == status2 == 200 and texto and texto == segundo.get("resumo")
                  and primeiro.get("cached") is False and segundo.get("cached") is True)

        rota = f"/artigos/{artigo}/favoritar"
        marcado, _ = chamar(base, rota, "POST")
        status, favoritos = chamar(base, "/artigos?favoritos=true&limit=1")
        removido, _ = chamar(base, rota, "DELETE")
        status_final, depois = chamar(base, "/favoritos")
        registrar("Favorito aparece no filtro e desaparece após remoção",
                  marcado == removido == status == status_final == 200
                  and [a["id"] for a in favoritos] == [artigo] and depois == [])
    else:
        registrar("Resumo é criado e recuperado do cache", False)
        registrar("Favorito aparece no filtro e desaparece após remoção", False)

    status, digest = chamar(base, "/digest/hoje")
    totais = digest.get("estatisticas", {})
    registrar("Digest contabiliza artigos, resumos e favoritos",
              status == 200 and totais.get("totalArtigosBanco") == 2
              and totais.get("totalResumidos") == 1 and totais.get("totalFavoritos") == 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, default=APP, help="Pasta do Agregador candidata.")
    parser.add_argument("--relatorio", type=Path, help="Destino opcional do resultado em JSON.")
    args = parser.parse_args()
    resultados = []
    erro = None
    try:
        with servir_feed() as feed, iniciar_app(args.app.resolve()) as base:
            verificar(base, feed, resultados)
    except (OSError, RuntimeError, TypeError, KeyError, ValueError, AttributeError) as falha:
        erro = str(falha)
    aprovado = not erro and len(resultados) == 9 and all(caso["aprovado"] for caso in resultados)
    for caso in resultados:
        print(f"[{'OK' if caso['aprovado'] else 'FALHA'}] {caso['contrato']}")
    if erro:
        print(f"[ERRO] {erro}")
    print("Release aprovada." if aprovado else "Release bloqueada.")
    if args.relatorio:
        args.relatorio.write_text(
            json.dumps({"aprovado": aprovado, "contratos": resultados, "erro": erro}, ensure_ascii=False, indent=2)
            + "\n", encoding="utf-8"
        )
    return 0 if aprovado else 1


if __name__ == "__main__":
    raise SystemExit(main())
