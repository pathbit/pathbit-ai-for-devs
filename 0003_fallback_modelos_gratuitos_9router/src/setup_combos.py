"""Script de provisionamento e configuração automática de combos no 9Router.

Este utilitário cadastra diretamente no banco SQLite do 9Router os combos
de modelos gratuitos e fallback hierárquico.
"""

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

DEFAULT_CONTAINER = "claudegravity-router"
# Resolvida no uso, dentro de list_local_ollama_models: no import o load_dotenv()
# ainda nao rodou, e um OLLAMA_BASE_URL do .env seria ignorado.
OLLAMA_LOCAL_PREFIX = "openai-compatible-chat-ollama-local/"

COMBOS = [
    {
        "id": "combo_claudegravity_fallback",
        "name": "claudegravity-fallback",
        "kind": "llm",
        "models": [
            "ag/gemini-3.8-flash-high",
            "ag/gemini-3.7-flash-high",
            "ag/gemini-3.6-flash-high",
            "ag/claude-sonnet-4-6",
            "ag/gpt-oss-120b-medium",
        ]
    },
    {
        "id": "combo_arsenal_supremo",
        "name": "arsenal-supremo",
        "kind": "llm",
        "models": [
            "ag/gemini-3.8-flash-high",
            "ag/gemini-3.7-flash-high",
            "ag/gemini-3.6-flash-high",
            "openrouter/nvidia/nemotron-3.5-lightning:free",
            "groq/openai/gpt-oss-120b",
            "mistral/codestral-latest",
            "openai-compatible-chat-ollama-local/qwen2.5-coder:latest",
        ]
    },
    {
        "id": "combo_arsenal_rapido",
        "name": "arsenal-rapido",
        "kind": "llm",
        "models": [
            "groq/openai/gpt-oss-120b",
            "mistral/codestral-latest",
            "ag/gemini-3.7-flash-high",
            "ag/gemini-3.6-flash-high",
        ]
    },
    {
        "id": "combo_arsenal_offline",
        "name": "arsenal-offline",
        "kind": "llm",
        "models": [
            "openai-compatible-chat-ollama-local/qwen2.5-coder:latest",
        ]
    },
]


def run_node_script(container_name, script, *args, check=True):
    """Executa um script Node dentro do container.

    Os valores variáveis trafegam por process.argv, nunca interpolados no código -
    uma chave com aspas ou barra invertida quebraria (ou injetaria código no) script.
    """
    cmd = ["docker", "exec", container_name, "node", "-e", script, *[str(a) for a in args]]
    return subprocess.run(cmd, check=check)


def load_dotenv():
    """Carrega variáveis de ambiente de arquivos .env locais se existirem."""
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.getcwd(), ".env"),
    ]
    for p in search_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass


def get_providers_config():
    load_dotenv()
    return [
        {
            "provider": "groq",
            "name": "Groq Cloud PathBit",
            "authType": "apikey",
            "apiKey": os.environ.get("GROQ_API_KEY", "")
        },
        {
            "provider": "openrouter",
            "name": "OpenRouter PathBit",
            "authType": "apikey",
            "apiKey": os.environ.get("OPENROUTER_API_KEY", "")
        },
        {
            "provider": "gemini",
            "name": "Google AI Studio PathBit",
            "authType": "apikey",
            "apiKey": os.environ.get("GEMINI_API_KEY", "")
        },
        {
            "provider": "ollama",
            "name": "Ollama Cloud PathBit",
            "authType": "apikey",
            "apiKey": os.environ.get("OLLAMA_API_KEY", "")
        },
        {
            "provider": "mistral",
            "name": "Mistral AI PathBit",
            "authType": "apikey",
            "apiKey": os.environ.get("MISTRAL_API_KEY", "")
        },
    ]


def list_local_ollama_models():
    """Retorna os modelos disponíveis no Ollama local, ou None se o serviço não responder."""
    try:
        with urllib.request.urlopen(f"{os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/tags", timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [m.get("name", "") for m in data.get("models", [])]
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return None


def check_ollama_models():
    """Avisa quando um combo depende de um modelo local que ainda não foi baixado.

    Sem esta checagem o combo offline é cadastrado com sucesso e só falha na
    primeira inferência, quando o usuário já acha que o arsenal está pronto.
    """
    required = sorted({
        model[len(OLLAMA_LOCAL_PREFIX):]
        for combo in COMBOS
        for model in combo["models"]
        if model.startswith(OLLAMA_LOCAL_PREFIX)
    })
    if not required:
        return

    available = list_local_ollama_models()
    if available is None:
        print(f"  [!] Ollama local não respondeu em {f"{os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/tags"}.")
        print("      Os combos que dependem dele serão cadastrados, mas falharão na inferência.")
        print("      Suba o serviço com: docker compose up -d ollama")
        return

    missing = [m for m in required if m not in available]
    if missing:
        print(f"  [!] Modelos ausentes no Ollama local: {', '.join(missing)}")
        for model in missing:
            base = model.split(":")[0]
            print(f"      Baixe com: docker exec -it claudegravity-ollama ollama pull {base}:0.5b")
            print(f"      E marque a tag esperada: docker exec claudegravity-ollama ollama cp {base}:0.5b {model}")
    else:
        print(f"  [+] Ollama local pronto com: {', '.join(required)}")


def check_container(container_name):
    """Verifica se o container do 9Router está em execução."""
    try:
        res = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return container_name in res.stdout.strip()
    except Exception:
        return False


def provision_providers_sqlite(container_name):
    """Insere ou atualiza os provedores gratuitos no banco SQLite do 9Router."""
    providers = get_providers_config()
    print(f"[*] Provisionando conexões de provedores no container {container_name}...")
    for p in providers:
        prov = p["provider"]
        pname = p["name"]
        ptype = p["authType"]
        pkey = p["apiKey"]
        if not pkey:
            print(f"  [i] Provedor {prov} pulado (chave de API não informada no ambiente ou .env)")
            continue

        node_script = """
const db = require('/app/node_modules/better-sqlite3')('/app/data/db/data.sqlite');
const now = new Date().toISOString();
const [provider, authType, name, apiKey] = process.argv.slice(1);
const connData = JSON.stringify({
  apiKey: apiKey,
  testStatus: "unknown",
  providerSpecificData: {
    connectionProxyEnabled: false,
    connectionProxyUrl: "",
    connectionNoProxy: ""
  }
});

const existing = db.prepare("SELECT id FROM providerConnections WHERE provider = ?").get(provider);
if (existing) {
  db.prepare("UPDATE providerConnections SET data = ?, isActive = 1, updatedAt = ? WHERE provider = ?")
    .run(connData, now, provider);
} else {
  const id = require('crypto').randomUUID();
  db.prepare("INSERT INTO providerConnections (id, provider, authType, name, priority, isActive, data, createdAt, updatedAt) VALUES (?, ?, ?, ?, 10, 1, ?, ?, ?)")
    .run(id, provider, authType, name, connData, now, now);
}
"""
        run_node_script(container_name, node_script, prov, ptype, pname, pkey)
        print(f"  [+] Provedor configurado: {prov} ({pname})")


def provision_combos_sqlite(container_name):
    """Insere ou atualiza os combos no banco SQLite do 9Router."""
    print(f"[*] Provisionando combos no container {container_name}...")
    for combo in COMBOS:
        cid = combo["id"]
        cname = combo["name"]
        ckind = combo["kind"]
        cmodels = json.dumps(combo["models"])

        node_script = """
const db = require('/app/node_modules/better-sqlite3')('/app/data/db/data.sqlite');
const now = new Date().toISOString();
const [id, name, kind, models] = process.argv.slice(1);
db.prepare('INSERT OR REPLACE INTO combos (id, name, kind, models, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, ?)')
  .run(id, name, kind, models, now, now);
"""
        run_node_script(container_name, node_script, cid, cname, ckind, cmodels)
        print(f"  [+] Combo cadastrado: {cname} ({len(combo['models'])} modelos)")


def provision_ollama_local_node(container_name):
    """Configura o nó OpenAI-compatível do Ollama Local no 9Router para streaming SSE nativo."""
    node_id = "openai-compatible-chat-ollama-local"
    node_script = """
const db = require('/app/node_modules/better-sqlite3')('/app/data/db/data.sqlite');
const now = new Date().toISOString();
const nodeId = process.argv[1];

const nodeData = JSON.stringify({
  prefix: 'ollama-local',
  apiType: 'chat',
  baseUrl: 'http://host.docker.internal:11434/v1'
});
db.prepare('INSERT OR REPLACE INTO providerNodes (id, type, name, data, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?, ?)')
  .run(nodeId, 'openai-compatible', 'Ollama Local', nodeData, now, now);

const connData = JSON.stringify({
  apiKey: 'ollama',
  testStatus: 'ok',
  providerSpecificData: {
    baseUrl: 'http://host.docker.internal:11434/v1',
    apiType: 'chat'
  }
});
db.prepare('INSERT OR REPLACE INTO providerConnections (id, provider, authType, name, priority, isActive, data, createdAt, updatedAt) VALUES (?, ?, ?, ?, 50, 1, ?, ?, ?)')
  .run('conn_ollama_local_fixed', nodeId, 'apikey', 'Ollama Local Host', connData, now, now);
"""
    run_node_script(container_name, node_script, node_id)
    print("  [+] Nó Ollama Local provisionado via endpoint OpenAI-compatible (100% SSE streaming)")


def main():
    container = os.environ.get("ROUTER_CONTAINER", DEFAULT_CONTAINER)
    if not check_container(container):
        alt = "9router-arsenal-fallback"
        if check_container(alt):
            container = alt
        else:
            print(f"[!] Erro: container {container} não encontrado ou inativo.")
            print("[!] Inicie o container com: docker compose up -d")
            sys.exit(1)

    provision_providers_sqlite(container)
    provision_ollama_local_node(container)
    print("[*] Verificando disponibilidade dos modelos locais...")
    check_ollama_models()
    provision_combos_sqlite(container)
    print("[*] Provisionamento concluído com sucesso!")
    print("[*] Valide a cascata completa com: python3 src/test_arsenal.py")


if __name__ == "__main__":
    main()
