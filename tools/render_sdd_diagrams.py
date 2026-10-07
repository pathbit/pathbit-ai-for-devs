#!/usr/bin/env python3
"""Renderizador de diagramas do Artigo 0005 (SDD) via Google Chrome headless.

Renderiza os HTMLs com SVG vetorial e tipografia Geist/Instrument Serif
direto nos assets PNG de alta resolucao.
"""
from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "0005_sdd_do_vibe_coding_a_engenharia_deterministica" / "assets"
DIAGRAMS_DIR = ASSETS_DIR / "diagrams"

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

TARGETS = [
    ("00_cover_sdd.html", "00_cover_sdd.png", 1200, 630),
    ("01_diagrama_chute_vs_spec.html", "01_diagrama_chute_vs_spec.png", 1200, 600),
    ("02_diagrama_spec_fonte_da_verdade.html", "02_diagrama_spec_fonte_da_verdade.png", 1200, 700),
    ("03_diagrama_custo_do_erro.html", "03_diagrama_custo_do_erro.png", 1200, 640),
    ("04_diagrama_anatomia_spec.html", "04_diagrama_anatomia_spec.png", 1200, 600),
    ("05_diagrama_ciclo_sdd.html", "05_diagrama_ciclo_sdd.png", 1200, 600),
    ("06_diagrama_janela_contexto.html", "06_diagrama_janela_contexto.png", 1200, 600),
    ("07_diagrama_mapa_metodos.html", "07_diagrama_mapa_metodos.png", 1200, 600),
    ("08_diagrama_ferramentas_fases.html", "08_diagrama_ferramentas_fases.png", 1200, 700),
    ("cover_linkedin.html", "cover_linkedin.png", 1200, 630),
]


def render():
    if not Path(CHROME).exists():
        print(f"Erro: Chrome nao encontrado em {CHROME}", file=sys.stderr)
        sys.exit(1)

    print("Renderizando diagramas SDD para PNG...")
    for html_name, png_name, width, height in TARGETS:
        html_path = DIAGRAMS_DIR / html_name
        png_path = ASSETS_DIR / png_name
        if not html_path.exists():
            print(f"  [PULAR] {html_name} nao existe")
            continue

        cmd = [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=3000",
            f"--window-size={width},{height}",
            f"--screenshot={png_path}",
            f"file://{html_path.resolve()}",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if png_path.exists() and png_path.stat().st_size > 1000:
            print(f"  [OK] {png_name} ({png_path.stat().st_size // 1024} KB)")
        else:
            print(f"  [ERRO] {png_name}: code={res.returncode}, stderr={res.stderr[:200]}")


if __name__ == "__main__":
    render()
