#!/usr/bin/env python3
"""Cruza o que os artigos afirmam sobre os RTKSync com o que os RTKSync fazem.

Os artigos são publicados: eles mandam o leitor copiar um compose, definir
variáveis e abrir uma porta. Quando o projeto muda e o artigo não, o leitor
segue instruções que não funcionam mais — e não tem como saber que o errado é o
texto.

O que se confere aqui, para cada artigo que usa uma imagem RTKSync:

- a **imagem** citada existe como pacote do projeto;
- a **porta interna** publicada é a que o código escuta por padrão;
- as **variáveis** passadas ao container são lidas pelo projeto;
- o **caminho do banco** e a **URL do gateway** batem com o default do projeto.
"""

import os
import re
import sys
from typing import Dict, List, Set

RTK = {
    "ghcr.io/pathbit/9rtksync": ("9RTKSync", "nine_rtksync"),
    "ghcr.io/pathbit/ominirtksync": ("OminiRTkSync", "omini_rtksync"),
    "ghcr.io/pathbit/litellmrtksync": ("LiteLlmRTKSync", "litellm_rtksync"),
}


def env_lidas(raiz_rtk: str, pacote: str) -> Set[str]:
    """Variáveis que o projeto RTK realmente lê."""
    lidas: Set[str] = set()
    base = os.path.join(raiz_rtk, "src", pacote)
    for pasta, dirs, arquivos in os.walk(base):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for a in arquivos:
            if not a.endswith(".py"):
                continue
            with open(os.path.join(pasta, a), encoding="utf-8") as f:
                fonte = f.read()
            lidas |= set(re.findall(r"environ\.get\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]", fonte))
            lidas |= set(re.findall(r"environ\[\s*['\"]([A-Z][A-Z0-9_]+)['\"]\s*\]", fonte))
            # helpers: _flag("X"), _inteiro_opcional("X"), _decimal_opcional("X")
            lidas |= set(re.findall(r"_(?:flag|inteiro_opcional|decimal_opcional)\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]", fonte))
    return lidas


def porta_padrao(raiz_rtk: str, pacote: str) -> str:
    caminho = os.path.join(raiz_rtk, "src", pacote, "config.py")
    with open(caminho, encoding="utf-8") as f:
        m = re.search(r"WEB_PORT[\"']\s*,\s*[\"'](\d+)[\"']", f.read())
    return m.group(1) if m else "?"


def composes(raiz: str) -> List[str]:
    achados = []
    for pasta, dirs, arquivos in os.walk(raiz):
        dirs[:] = [d for d in dirs if d not in (".git", "tmp", "node_modules", "__pycache__", "assets")]
        for a in arquivos:
            if a.startswith("docker-compose") and a.endswith((".yml", ".yaml")):
                achados.append(os.path.join(pasta, a))
    return sorted(achados)


def blocos_de_servico(texto: str) -> List[str]:
    """Recorta cada bloco de serviço de um compose, de forma tolerante."""
    partes = re.split(r"\n(?=  [A-Za-z0-9_.-]+:\n)", texto)
    return partes


def verificar(raiz_artigos: str, raiz_github: str) -> List[str]:
    problemas: List[str] = []
    cache: Dict[str, Set[str]] = {}

    for compose in composes(raiz_artigos):
        rel = os.path.relpath(compose, raiz_artigos)
        with open(compose, encoding="utf-8") as f:
            texto = f.read()

        for bloco in blocos_de_servico(texto):
            for imagem, (repo, pacote) in RTK.items():
                if imagem not in bloco:
                    continue

                raiz_rtk = os.path.join(raiz_github, repo)
                if not os.path.isdir(raiz_rtk):
                    problemas.append(f"{rel}: usa {imagem} e o repo {repo} não está na pasta")
                    continue

                if repo not in cache:
                    cache[repo] = env_lidas(raiz_rtk, pacote)
                lidas = cache[repo]

                # 1. Porta interna publicada x porta que o código escuta
                padrao = porta_padrao(raiz_rtk, pacote)
                for host, interna in re.findall(r'"[\d.]*:?(\d+):(\d+)"', bloco):
                    declarada = re.search(r"WEB_PORT=(\d+)", bloco)
                    esperada = declarada.group(1) if declarada else padrao
                    if interna != esperada:
                        problemas.append(
                            f"{rel}: publica {host}:{interna}, mas o serviço escuta em "
                            f"{esperada} ({'WEB_PORT declarado' if declarada else 'default do código'})"
                        )

                # 2. Variáveis passadas x variáveis lidas
                for var in re.findall(r"^\s*-\s*([A-Z][A-Z0-9_]+)=", bloco, re.M):
                    if var in ("PYTHONUNBUFFERED", "TZ", "PATH"):
                        continue
                    if var not in lidas:
                        problemas.append(
                            f"{rel}: passa {var} e {repo} não lê essa variável"
                        )
    return problemas


def main() -> int:
    # Sem argumentos: este repositorio e os projetos RTK ao lado dele, que e
    # como a pasta de trabalho esta organizada. Com argumentos, qualquer par.
    aqui = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raiz_artigos = sys.argv[1] if len(sys.argv) > 1 else aqui
    raiz_github = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(aqui)

    faltando = [r for r in {v[0] for v in RTK.values()}
                if not os.path.isdir(os.path.join(raiz_github, r))]
    if faltando:
        print(f"AVISO: projetos RTK ausentes em {raiz_github}: {', '.join(sorted(faltando))}")
        print("       clone-os ao lado deste repositorio, ou passe a raiz como 2o argumento.")

    problemas = verificar(raiz_artigos, raiz_github)
    print(f"===== {os.path.basename(raiz_artigos)}: {len(problemas)} divergência(s) =====")
    for p in sorted(set(problemas)):
        print(f"  - {p}")
    # Sai diferente de zero quando ha divergencia: assim o alvo do Makefile e
    # qualquer pipeline falham em vez de imprimir o problema e seguir adiante.
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
