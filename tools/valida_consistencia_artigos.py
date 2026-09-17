#!/usr/bin/env python3
"""Confere que os artigos publicados descrevem o repositório como ele está hoje.

Um artigo é publicado uma vez e lido por muito tempo. Quando um arquivo é
renomeado, um print é substituído ou uma configuração muda, o texto continua
afirmando o que era verdade antes -- e o leitor segue instruções que não
funcionam mais, sem ter como saber que o errado é o texto.

O que se confere aqui:

- **JSON transcrito x arquivo real**: todo bloco ```json de configuração citado
  num artigo precisa existir, byte a byte, como um `.example` versionado. Foi a
  divergência mais cara de todas: o leitor copia do artigo e recebe um arquivo
  diferente do que o repositório entrega.
- **Imagens**: toda imagem referenciada existe, e toda imagem existente é
  referenciada. Um asset órfão normalmente significa um print substituído cujo
  texto ficou para trás.
- **Nomes de arquivo**: nenhum artigo pode citar `.claude/settings.json`, já que
  a convenção do repositório é `settings.local.json`.
- **Sufixo `[1m]`**: não pode aparecer em nenhum identificador de modelo de
  terceiros, nem nos exemplos nem no corpo dos artigos.
- **Links internos**: todo link relativo entre documentos aponta para um arquivo
  que existe.
"""

import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
falhas = []
avisos = []


def falha(msg):
    falhas.append(msg)
    print(f"  [FALHA] {msg}")


def aviso(msg):
    avisos.append(msg)
    print(f"  [AVISO] {msg}")


def ok(msg):
    print(f"  [OK]    {msg}")


def artigos():
    return sorted(RAIZ.glob("0*/article/ARTICLE.md"))


def valida_json_transcrito():
    print("\n== JSON transcrito nos artigos x arquivos .example")
    for artigo in artigos():
        modulo = artigo.parent.parent
        exemplos = sorted((modulo / "examples" / ".claude").glob("*.example"))
        if not exemplos:
            continue
        texto = artigo.read_text(encoding="utf-8")
        blocos = []
        for bruto in re.findall(r"```json\n(.*?)\n```", texto, re.S):
            try:
                blocos.append(json.loads(bruto))
            except json.JSONDecodeError:
                pass  # blocos ilustrativos com comentários não são configuração completa
        for exemplo in exemplos:
            try:
                real = json.loads(exemplo.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                falha(f"{exemplo.relative_to(RAIZ)}: JSON inválido ({exc.msg} na linha {exc.lineno})")
                continue
            if any(bloco == real for bloco in blocos):
                ok(f"{modulo.name}: {exemplo.name} idêntico ao transcrito no artigo")
            else:
                falha(f"{modulo.name}: {exemplo.name} diverge do JSON publicado no artigo")


def valida_imagens():
    print("\n== Imagens referenciadas x assets em disco")
    for artigo in artigos():
        modulo = artigo.parent.parent
        assets = modulo / "assets"
        if not assets.is_dir():
            continue
        texto = artigo.read_text(encoding="utf-8")
        citadas = {pathlib.Path(m).name for m in re.findall(r"!\[[^\]]*\]\(\.\./assets/([^)]+)\)", texto)}
        em_disco = {p.name for p in assets.glob("*.png")}
        # covers de rede social não aparecem no corpo do artigo por desenho
        em_disco -= {"cover_linkedin.png"}
        for faltando in sorted(citadas - em_disco):
            falha(f"{modulo.name}: o artigo cita {faltando}, que não existe em assets/")
        orfas = sorted(em_disco - citadas)
        for orfa in orfas:
            aviso(f"{modulo.name}: {orfa} existe em assets/ mas não é citada no artigo")
        if not (citadas - em_disco) and not orfas:
            ok(f"{modulo.name}: {len(citadas)} imagens, todas citadas e presentes")
        elif not (citadas - em_disco):
            ok(f"{modulo.name}: {len(citadas)} imagens citadas, todas presentes")


def valida_convencao_de_nomes():
    print("\n== Convenção de nomes dos settings")
    # Distinguir instrução de explicação é o ponto: os artigos *precisam* citar
    # `.claude/settings.json` ao ensinar a diferença entre os dois escopos. O que
    # não pode existir é um comando mandando o leitor usar o nome antigo.
    comandos = [
        re.compile(r"--settings\s+\.?/?\.claude/settings\.json"),
        re.compile(r"\bcp\s+\S*\.claude/settings\.json"),
        re.compile(r"open\(['\"]\.claude/settings\.json"),
    ]
    encontrados = 0
    for doc in sorted(RAIZ.rglob("*.md")):
        if ".git" in doc.parts:
            continue
        for linha_num, linha in enumerate(doc.read_text(encoding="utf-8").split("\n"), 1):
            if any(p.search(linha) for p in comandos):
                falha(f"{doc.relative_to(RAIZ)}:{linha_num}: comando usa .claude/settings.json (use settings.local.json)")
                encontrados += 1
    if not encontrados:
        ok("nenhum comando instrui o leitor a usar .claude/settings.json")


def valida_sufixo_1m():
    print("\n== Sufixo [1m] em modelos de terceiros")
    encontrados = 0
    for exemplo in sorted(RAIZ.glob("0*/examples/.claude/*.example")):
        texto = exemplo.read_text(encoding="utf-8")
        for linha_num, linha in enumerate(texto.split("\n"), 1):
            if "[1m]" in linha:
                falha(f"{exemplo.relative_to(RAIZ)}:{linha_num}: identificador com sufixo [1m]")
                encontrados += 1
    if not encontrados:
        ok("nenhum arquivo de exemplo usa o sufixo [1m]")


def valida_links_internos():
    print("\n== Links relativos entre documentos")
    quebrados = 0
    for doc in sorted(RAIZ.rglob("*.md")):
        if ".git" in doc.parts:
            continue
        texto = doc.read_text(encoding="utf-8")
        for alvo in re.findall(r"\]\((\.\.?/[^)#]+)(?:#[^)]*)?\)", texto):
            destino = (doc.parent / alvo).resolve()
            if not destino.exists():
                falha(f"{doc.relative_to(RAIZ)}: link quebrado -> {alvo}")
                quebrados += 1
    if not quebrados:
        ok("todos os links relativos apontam para arquivos existentes")


def main():
    print("=" * 72)
    print("Consistência dos artigos x repositório")
    print("=" * 72)
    valida_json_transcrito()
    valida_imagens()
    valida_convencao_de_nomes()
    valida_sufixo_1m()
    valida_links_internos()
    print("\n" + "=" * 72)
    if falhas:
        print(f"RESULTADO: {len(falhas)} falha(s), {len(avisos)} aviso(s)")
        return 1
    print(f"RESULTADO: consistente ({len(avisos)} aviso(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
