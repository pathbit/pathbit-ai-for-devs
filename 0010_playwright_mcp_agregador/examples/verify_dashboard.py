#!/usr/bin/env python3
"""Exercise the real aggregator with the pinned Playwright MCP server."""

import argparse
import itertools
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import monotonic, sleep
from urllib.parse import urlsplit
from urllib.request import urlopen

TARGET = "MCP no Agregador"
OTHER = "Roteamento no OpenCode"
CONTROL = 'Arquitetura'
GRID = "#articlesGrid"


class MCP:
    def __init__(self, process):
        self.process = process
        self.ids = itertools.count(1)

    def send(self, method, params, *, notification=False):
        payload = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notification:
            payload["id"] = next(self.ids)
        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()
        if notification:
            return
        for line in self.process.stdout:
            response = json.loads(line)
            if response.get("id") == payload["id"]:
                if "error" in response:
                    raise RuntimeError(response["error"])
                return response["result"]
        raise RuntimeError(f"MCP server stopped while processing {method}")

    def tool(self, name, **arguments):
        result = self.send("tools/call", {"name": name, "arguments": arguments})
        text = "\n".join(item.get("text", "") for item in result["content"])
        if result.get("isError"):
            raise RuntimeError(text)
        return text


def wait_for_grid(mcp, *, present, absent=()):
    deadline = monotonic() + 10
    while monotonic() < deadline:
        snapshot = mcp.tool("browser_snapshot", target=GRID)
        if all(title in snapshot for title in present) and all(title not in snapshot for title in absent):
            return
        sleep(0.1)
    raise AssertionError(snapshot)


def favorites(base):
    with urlopen(base + "/favoritos", timeout=3) as response:
        return {item["titulo"] for item in json.load(response)}


def verify(mcp, base):
    mcp.send("initialize", {
        "protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "pathbit-aggregator-lab", "version": "1.0"},
    })
    mcp.send("notifications/initialized", {}, notification=True)
    expected_control = '=Arquitetura, "em prática"'
    assert favorites(base) == {expected_control}, "Start with a fresh database from the lab seed."

    mcp.tool("browser_navigate", url=base + "/")
    mcp.tool("browser_wait_for", text="Agregador de Notícias com Resumo por IA")
    wait_for_grid(mcp, present=(TARGET, OTHER, CONTROL))
    mcp.tool("browser_type", target="#searchInput", element="Busca de artigos", text=TARGET)
    wait_for_grid(mcp, present=(TARGET,), absent=(OTHER, CONTROL))
    print("Search narrowed the article grid.", flush=True)

    favorite_button = f'{GRID} .article-card:has(a[href="https://example.org/mcp"]) .btn-fav'
    mcp.tool("browser_click", target=favorite_button, element="Favoritar o artigo MCP no Agregador")
    mcp.tool("browser_wait_for", text="Adicionado aos favoritos")
    assert favorites(base) == {expected_control, TARGET}
    mcp.tool("browser_click", target="#btnToggleFavoritos", element="Apenas Favoritos")
    mcp.tool("browser_wait_for", text="Exibindo Favoritos")
    wait_for_grid(mcp, present=(TARGET,), absent=(OTHER, CONTROL))
    print("Favoriting updated the UI and the server list.", flush=True)

    mcp.tool("browser_navigate", url=base + "/")
    wait_for_grid(mcp, present=(TARGET, OTHER, CONTROL))
    mcp.tool("browser_click", target="#btnToggleFavoritos", element="Apenas Favoritos")
    wait_for_grid(mcp, present=(TARGET, CONTROL), absent=(OTHER,))
    assert favorites(base) == {expected_control, TARGET}
    print("Favorite persisted after a new page load.", flush=True)

    mcp.tool("browser_click", target=favorite_button, element="Remover o artigo dos favoritos")
    mcp.tool("browser_wait_for", text="Removido dos favoritos")
    wait_for_grid(mcp, present=(CONTROL,), absent=(TARGET, OTHER))
    assert favorites(base) == {expected_control}
    print("Removal preserved the control favorite.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:19810")
    base = parser.parse_args().url.rstrip("/")
    url = urlsplit(base)
    if url.scheme != "http" or url.hostname != "127.0.0.1" or url.username or url.path or url.query or url.fragment:
        parser.error("Use a loopback HTTP URL for the disposable lab, such as http://127.0.0.1:19810.")
    config = json.loads(Path(__file__).with_name(".mcp.json").read_text())["mcpServers"]["playwright"]
    with TemporaryDirectory(prefix="pathbit-playwright-") as artifacts, subprocess.Popen(
        [config["command"], *config["args"]], cwd=artifacts, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
    ) as process:
        mcp = MCP(process)
        try:
            verify(mcp, base)
            mcp.tool("browser_close")
        finally:
            process.terminate()


if __name__ == "__main__":
    main()
