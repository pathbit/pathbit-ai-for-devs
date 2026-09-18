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
- **Regras dos settings**, aplicadas a todos os módulos: credencial em
  `ANTHROPIC_AUTH_TOKEN` (nunca `ANTHROPIC_API_KEY`, que dispara diálogo
  interativo), advisor desligado pelo kill switch, `ANTHROPIC_BASE_URL` sem o
  sufixo `/v1`, e nenhum token real dentro de um template versionado.
- **Autoria dos commits**: nenhum commit do histórico carrega assinatura
  sintética de coautoria de IA. A regra está em PADROES_ENGENHARIA_IA.md; o hook
  `commit-msg` a aplica na hora de commitar, mas ele não é versionado -- esta
  verificação vale em qualquer clone e em CI.
- **Links internos**: todo link relativo entre documentos aponta para um arquivo
  que existe.
"""

import json
import pathlib
import re
import subprocess
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


def valida_settings_de_todos_os_modulos():
    """Aplica a todos os artigos as regras que nasceram de falhas reais.

    Cada verificação aqui corresponde a um sintoma que já custou tempo de
    diagnóstico: credencial que dispara diálogo interativo, advisor derrubando a
    sessão contra um provedor de terceiros, URL base que vira /v1/v1/messages e
    token real esquecido dentro de um template versionado.
    """
    print("\n== Regras dos settings em todos os módulos")
    encontrados = 0
    for exemplo in sorted(RAIZ.glob("0*/examples/.claude/*.example")):
        rel = exemplo.relative_to(RAIZ)
        try:
            cfg = json.loads(exemplo.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            falha(f"{rel}: JSON inválido ({exc.msg} na linha {exc.lineno})")
            encontrados += 1
            continue
        env = cfg.get("env", {})

        if "ANTHROPIC_API_KEY" in env:
            falha(f"{rel}: usa ANTHROPIC_API_KEY (dispara aprovação interativa; use ANTHROPIC_AUTH_TOKEN)")
            encontrados += 1
        if not env.get("ANTHROPIC_AUTH_TOKEN"):
            falha(f"{rel}: falta ANTHROPIC_AUTH_TOKEN no bloco env")
            encontrados += 1
        if env.get("CLAUDE_CODE_DISABLE_ADVISOR_TOOL") != "1":
            falha(f"{rel}: falta CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 (o advisor derruba a sessão em provedor de terceiros)")
            encontrados += 1
        if "advisorModel" in cfg or "CLAUDE_CODE_ENABLE_EXPERIMENTAL_ADVISOR_TOOL" in env:
            falha(f"{rel}: chave obsoleta do advisor (use apenas o kill switch)")
            encontrados += 1

        base = env.get("ANTHROPIC_BASE_URL", "")
        if base.rstrip("/").endswith("/v1"):
            falha(f"{rel}: ANTHROPIC_BASE_URL termina em /v1 — a CLI anexa /v1/messages e a rota vira /v1/v1/messages")
            encontrados += 1

        # Um token real dentro de um arquivo versionado é o pior erro possível
        # aqui. Placeholders seguem o padrão "sk-sua-chave-do-<provedor>", então
        # o que caracteriza suspeita é um valor com cara de segredo: comprimento
        # de credencial e sem nenhuma das palavras de template.
        token = env.get("ANTHROPIC_AUTH_TOKEN", "")
        e_placeholder = any(p in token.lower() for p in ("sua-chave", "sua_chave", "your-key", "coloque", "aqui", "example", "xxx"))
        if token.startswith("sk-") and len(token) >= 24 and not e_placeholder:
            falha(f"{rel}: template versionado contém o que parece ser uma credencial real ({token[:12]}...)")
            encontrados += 1

    if not encontrados:
        ok("todos os templates seguem as regras (AUTH_TOKEN, advisor desligado, URL sem /v1, sem credencial real)")


def valida_autoria_dos_commits():
    """Confere que nenhum commit carrega assinatura sintética de coautoria de IA.

    A regra está em docs/PADROES_ENGENHARIA_IA.md: todo commit deve refletir
    exclusivamente autoria humana. O `commit-msg` instalado pelo artigo 0001
    higieniza a mensagem na hora de commitar, mas ele vive em `.git/hooks`, que
    não é versionado -- um clone novo, ou uma máquina onde o hook não foi
    instalado, aceita o trailer sem reclamar. Esta verificação roda a partir do
    repositório e por isso vale em qualquer clone e em CI.
    """
    print("\n== Autoria dos commits")
    proibidos = re.compile(
        r"^\s*(Co-Authored-By|Signed-off-by|Authored-by):.*"
        r"(claude|anthropic|gemini|antigravity|openai|gpt|copilot|cursor|devin|"
        r"windsurf|codeium|aider|cline|bot|noreply@)"
        r"|^\s*(Claude-Session|Session-ID|Generated-by|AI-Generated|Assisted-by):"
        r"|Generated with \[?Claude Code"
        r"|claude\.ai/code/session"
        r"|^\s*🤖",
        re.IGNORECASE | re.MULTILINE,
    )
    try:
        bruto = subprocess.run(
            ["git", "log", "--format=%H%x1f%s%x1f%B%x1e"],
            cwd=RAIZ, capture_output=True, text=True, timeout=60,
        )
    except Exception as exc:
        aviso(f"não foi possível ler o histórico ({exc})")
        return
    if bruto.returncode != 0:
        aviso("não é um repositório git ou o histórico está indisponível")
        return

    sujos = 0
    total = 0
    for registro in bruto.stdout.split("\x1e"):
        if not registro.strip():
            continue
        total += 1
        partes = registro.strip("\n").split("\x1f")
        if len(partes) < 3:
            continue
        sha, assunto, corpo = partes[0][:7], partes[1], partes[2]
        achado = proibidos.search(corpo)
        if achado:
            linha = achado.group(0).strip().splitlines()[0]
            falha(f"commit {sha} ({assunto[:48]}) tem assinatura de IA: {linha[:60]}")
            sujos += 1
    if not sujos:
        ok(f"{total} commits, todos com autoria exclusivamente humana")

    # A origem da reincidência não fica em repositório nenhum: `includeCoAuthoredBy`
    # tem `true` como padrão, e os settings de projeto só protegem o próprio projeto.
    global_settings = pathlib.Path.home() / ".claude" / "settings.json"
    try:
        valor = json.loads(global_settings.read_text(encoding="utf-8")).get("includeCoAuthoredBy")
    except Exception:
        valor = None
    if valor is False:
        ok("~/.claude/settings.json tem includeCoAuthoredBy=false (vale para todos os repos)")
    else:
        aviso("~/.claude/settings.json não define includeCoAuthoredBy=false -- o padrão é true "
              "e o trailer volta em qualquer repo sem settings próprio")


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
    valida_settings_de_todos_os_modulos()
    valida_autoria_dos_commits()
    valida_links_internos()
    print("\n" + "=" * 72)
    if falhas:
        print(f"RESULTADO: {len(falhas)} falha(s), {len(avisos)} aviso(s)")
        return 1
    print(f"RESULTADO: consistente ({len(avisos)} aviso(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
