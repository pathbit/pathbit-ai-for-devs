"""Verificador de consistência do DeepClaude (Artigo 0004).

Confere três coisas que, quando erradas, produzem sintomas difíceis de
diagnosticar no Claude Code:

1. Os templates `.example` e a cópia ativa `settings.local.json` são JSON válido
   e coerente entre si (modelo, URL base e papéis apontando para o mesmo lugar).
2. Nenhum identificador de modelo carrega o sufixo `[1m]`. A CLI do Claude Code
   remove esse sufixo antes de enviar a requisição, então o erro passa
   despercebido ali e só aparece quando o mesmo nome é usado em um script, num
   `curl` ou num combo do 9Router -- onde o provedor faz busca exata e recusa.
3. O arquivo global `~/.claude/settings.json` não foi contaminado com um modelo
   de terceiros. Isso acontece ao apertar Enter no menu `/model` (que significa
   "salvar como padrão"), e o destino da gravação é sempre o escopo `userSettings`
   -- ou seja, o arquivo global -- mesmo em sessões iniciadas com `--settings`.

Opcionalmente (`--online`) dispara uma inferência real contra o provedor
configurado, provando a integração de ponta a ponta.

Uso:
    python3 verify_deepclaude.py            # validação offline (não faz rede)
    python3 verify_deepclaude.py --online   # inclui uma chamada real à API
    python3 verify_deepclaude.py --fix-global  # remove a chave "model" vazada
    python3 verify_deepclaude.py --online --insecure  # rede com proxy TLS corporativo
"""

import json
import os
import pathlib
import ssl
import sys
import urllib.error
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CLAUDE_DIR = RAIZ / "examples" / ".claude"
ATIVO = CLAUDE_DIR / "settings.local.json"
TEMPLATES = ["settings.local.json.deepseek.example", "settings.local.json.orcarouter.example"]
GLOBAL = pathlib.Path.home() / ".claude" / "settings.json"

# Chaves que, se faltarem, produzem os sintomas descritos no artigo.
OBRIGATORIAS_ENV = [
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_DISABLE_ADVISOR_TOOL",
    "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT",
]
PAPEIS = ["OPUS", "SONNET", "FABLE", "HAIKU"]

# Valores de template: presentes no arquivo, mas sem credencial real.
PLACEHOLDERS = {"sk-sua-chave-do-DEEPSEEK-PLATFORM", "sk-sua-chave-do-ORCA-ROUTER", ""}

falhas = []
avisos = []


def ok(msg):
    print(f"  [OK]    {msg}")


def erro(msg):
    print(f"  [FALHA] {msg}")
    falhas.append(msg)


def aviso(msg):
    print(f"  [AVISO] {msg}")
    avisos.append(msg)


def carregar(caminho):
    """Lê um settings do Claude Code, tratando JSON inválido como falha explícita.

    A CLI descarta um settings malformado em silêncio e cai na tela de login da
    Anthropic, o que faz o usuário procurar o problema no lugar errado.
    """
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        erro(f"{caminho.name}: JSON inválido na linha {exc.lineno}, coluna {exc.colno} ({exc.msg})")
        return None


def modelos_declarados(cfg):
    """Extrai todo identificador de modelo declarado, venha de onde vier."""
    encontrados = []
    if isinstance(cfg.get("model"), str):
        encontrados.append(("model", cfg["model"]))
    env = cfg.get("env", {})
    for chave, valor in env.items():
        if "MODEL" in chave and not chave.endswith(("_NAME", "_DESCRIPTION")) and isinstance(valor, str):
            encontrados.append((f"env.{chave}", valor))
    for i, opcao in enumerate(cfg.get("modelPicker", {}).get("options", [])):
        if isinstance(opcao.get("model"), str):
            encontrados.append((f"modelPicker[{i}]", opcao["model"]))
    for alias, destino in cfg.get("modelOverrides", {}).items():
        if isinstance(destino, str):
            encontrados.append((f"modelOverrides.{alias}", destino))
    return encontrados


def validar(caminho, cfg, exige_token_real=False):
    nome = caminho.name
    print(f"\n-- {nome}")

    env = cfg.get("env", {})
    for chave in OBRIGATORIAS_ENV:
        if chave in env:
            ok(f"{chave} presente")
        else:
            erro(f"{nome}: falta {chave} no bloco env")

    # ANTHROPIC_API_KEY exige confirmação interativa e grava aprovação no estado
    # global; ANTHROPIC_AUTH_TOKEN vai direto no header Authorization.
    if "ANTHROPIC_API_KEY" in env:
        erro(f"{nome}: usa ANTHROPIC_API_KEY (troque por ANTHROPIC_AUTH_TOKEN)")

    base = env.get("ANTHROPIC_BASE_URL", "")
    if base.rstrip("/").endswith("/v1"):
        erro(f"{nome}: ANTHROPIC_BASE_URL termina em /v1 -- a CLI anexa /v1/messages e gera /v1/v1/messages")
    elif base:
        ok(f"URL base sem /v1: {base}")

    for papel in PAPEIS:
        if f"ANTHROPIC_DEFAULT_{papel}_MODEL" not in env:
            aviso(f"{nome}: papel {papel} não mapeado (o menu /model cai no rótulo genérico)")

    # O sufixo [1m] e a razão de existir deste verificador.
    for origem, modelo in modelos_declarados(cfg):
        if "[1m]" in modelo.lower():
            erro(f"{nome}: sufixo [1m] em {origem} = {modelo!r} -- use o identificador canônico")

    if cfg.get("modelPicker", {}).get("replaceBuiltInOptions") is True:
        ok("modelPicker com replaceBuiltInOptions: os modelos Anthropic não aparecem no /model")
    else:
        aviso(f"{nome}: sem replaceBuiltInOptions -- o menu /model mostrará também os modelos Anthropic")

    token = env.get("ANTHROPIC_AUTH_TOKEN", "")
    if exige_token_real:
        if token in PLACEHOLDERS:
            erro(f"{nome}: ANTHROPIC_AUTH_TOKEN ainda é o valor de template -- coloque sua chave real")
        else:
            ok(f"token real configurado ({token[:12]}...)")
    elif token not in PLACEHOLDERS:
        erro(f"{nome}: é um template versionado e contém uma credencial real -- nunca comite isso")
    else:
        ok("template sem credencial real")


def checar_global(corrigir=False):
    """Detecta a contaminação descrita na seção 'A Armadilha do /model'."""
    print("\n-- ~/.claude/settings.json (arquivo global do usuário)")
    cfg = carregar(GLOBAL)
    if cfg is None:
        ok("sem arquivo global (nada a verificar)")
        return
    modelo = cfg.get("model")
    if modelo is None:
        ok('nenhuma chave "model" gravada -- ambiente global limpo')
        return
    # Um modelo Anthropic aqui é escolha legítima do usuário; um de terceiros
    # quase sempre é vazamento do Enter no /model.
    if modelo.startswith("claude-") or modelo in ("default", "sonnet", "opus", "haiku", "fable"):
        ok(f'"model": {modelo!r} -- modelo Anthropic, provavelmente intencional')
        return
    erro(f'"model": {modelo!r} vazou para o arquivo global -- toda nova sessão abrirá com esse modelo')
    if corrigir:
        cfg.pop("model")
        GLOBAL.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  [FIX]   chave removida de {GLOBAL}")
        falhas.pop()
    else:
        print("          Rode novamente com --fix-global para remover a chave.")


def contexto_tls(inseguro=False):
    """Monta o contexto TLS tolerando redes com inspeção de tráfego.

    O Python valida contra o próprio bundle de CAs, não contra o keychain do
    sistema. Em redes corporativas com proxy TLS (o certificado da cadeia é
    emitido localmente), o `curl` funciona e o script falha -- o que parece um
    erro de configuração do artigo, mas é do ambiente. SSL_CERT_FILE resolve
    sem afrouxar nada; --insecure fica como último recurso consciente.
    """
    if inseguro:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return ssl.create_default_context()


def testar_online(cfg, inseguro=False):
    """Dispara uma inferência real: é o que separa 'configurado' de 'funcionando'."""
    env = cfg.get("env", {})
    base = env.get("ANTHROPIC_BASE_URL", "").rstrip("/")
    token = env.get("ANTHROPIC_AUTH_TOKEN", "")
    modelo = cfg.get("model") or env.get("ANTHROPIC_MODEL")
    print(f"\n-- inferência real em {base} com {modelo}")
    if token in PLACEHOLDERS:
        erro("token de template: não há como testar a conexão")
        return
    corpo = json.dumps({
        "model": modelo,
        "max_tokens": 32,
        "messages": [{"role": "user", "content": "Responda somente: OK"}],
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/v1/messages",
        data=corpo,
        headers={
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
            "Authorization": f"Bearer {token}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120, context=contexto_tls(inseguro)) as resp:
            dados = json.loads(resp.read())
        texto = "".join(b.get("text", "") for b in dados.get("content", []) if b.get("type") == "text")
        ok(f"HTTP {resp.status} -- modelo respondeu {texto.strip()!r} (servido por {dados.get('model')})")
    except urllib.error.HTTPError as exc:
        detalhe = exc.read().decode("utf-8", "replace")[:300]
        erro(f"HTTP {exc.code}: {detalhe}")
        if exc.code == 404 and "[1m]" in str(modelo):
            print("          O sufixo [1m] não existe no catálogo do provedor (veja a seção sobre [1m]).")
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, ssl.SSLCertVerificationError):
            aviso("TLS não validado: esta rede usa proxy com certificado próprio, não é erro da configuração")
            print("          Aponte o Python para a CA da sua rede:  export SSL_CERT_FILE=/caminho/ca.pem")
            print("          Ou repita com --insecure para pular a verificação nesta execução.")
            return
        erro(f"falha de rede: {exc.reason}")


def main():
    online = "--online" in sys.argv
    corrigir = "--fix-global" in sys.argv
    inseguro = "--insecure" in sys.argv

    print("=" * 72)
    print("Verificador DeepClaude -- Artigo 0004")
    print("=" * 72)

    for nome in TEMPLATES:
        caminho = CLAUDE_DIR / nome
        cfg = carregar(caminho)
        if cfg is None:
            erro(f"{nome}: template ausente em {CLAUDE_DIR}")
            continue
        validar(caminho, cfg)

    cfg_ativo = carregar(ATIVO)
    if cfg_ativo is None:
        print(f"\n-- {ATIVO.name}")
        aviso("cópia ativa não encontrada -- copie um template antes de abrir o Claude Code:")
        print(f"          cp {CLAUDE_DIR.name}/{TEMPLATES[1]} {CLAUDE_DIR.name}/{ATIVO.name}")
    else:
        validar(ATIVO, cfg_ativo, exige_token_real=True)
        if online:
            testar_online(cfg_ativo, inseguro=inseguro)

    checar_global(corrigir=corrigir)

    print("\n" + "=" * 72)
    if falhas:
        print(f"RESULTADO: {len(falhas)} falha(s), {len(avisos)} aviso(s)")
        for f in falhas:
            print(f"  - {f}")
        return 1
    print(f"RESULTADO: tudo consistente ({len(avisos)} aviso(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
