#!/bin/sh
set -eu

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ROUTER_NETWORK="${ROUTER_NETWORK:-claudegravity_default}"
ROUTER_URL="${ROUTER_URL:-http://claudegravity-router:20128}"
escopo="${1:-todos}"
if [ "$#" -gt 0 ]; then
    shift
fi

case "$escopo" in
    todos|0002|0003) ;;
    *)
        echo "Uso: $0 [todos|0002|0003] [argumentos do teste]" >&2
        exit 2
        ;;
esac

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker não encontrado." >&2
    exit 1
fi
if ! docker network inspect "$ROUTER_NETWORK" >/dev/null 2>&1; then
    echo "Rede $ROUTER_NETWORK indisponível. Suba a stack do artigo e conclua o provisionamento." >&2
    exit 1
fi

executar() {
    docker run --rm --network "$ROUTER_NETWORK" -v "$ROOT_DIR:/app:ro" -w /app \
        -e "ANTHROPIC_BASE_URL=$ROUTER_URL" -e ANTHROPIC_API_KEY \
        python:3.14-alpine python3 "$@"
}

case "$escopo" in
    todos)
        executar 0002_claude_gravity_utilizando_9router/src/test_gateway.py
        executar 0003_fallback_modelos_gratuitos_9router/src/test_arsenal.py
        ;;
    0002)
        executar 0002_claude_gravity_utilizando_9router/src/test_gateway.py "$@"
        ;;
    0003)
        executar 0003_fallback_modelos_gratuitos_9router/src/test_arsenal.py "$@"
        ;;
esac
