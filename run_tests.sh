#!/bin/sh
set -e

echo "======================================================================"
echo "🧪 Executando testes em container Docker (zero dependencias na maquina)"
echo "======================================================================"

if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Erro: Docker nao encontrado. O unico pre-requisito e ter o Docker instalado." >&2
    exit 1
fi

NETWORK="claudegravity_default"
if ! docker network inspect "$NETWORK" >/dev/null 2>&1; then
    echo "ℹ️  Rede $NETWORK nao encontrada. Iniciando os containers via docker compose..."
    docker compose -f 0002_claude_gravity_utilizando_9router/docker-compose.yml up -d
fi

echo "[1/2] Testando conectividade e modelos via gateway (0002 test_gateway.py)..."
docker run --rm --network "$NETWORK" -v "$(pwd)":/app -w /app \
  -e ROUTER_URL=http://claudegravity-router:20128 \
  -e ANTHROPIC_BASE_URL=http://claudegravity-router:20128 \
  python:3.14-alpine python3 0002_claude_gravity_utilizando_9router/src/test_gateway.py

echo ""
echo "[2/2] Testando cascata de combos e modelos gratuitos (0003 test_arsenal.py)..."
docker run --rm --network "$NETWORK" -v "$(pwd)":/app -w /app \
  -e ROUTER_URL=http://claudegravity-router:20128 \
  -e ANTHROPIC_BASE_URL=http://claudegravity-router:20128 \
  python:3.14-alpine python3 0003_fallback_modelos_gratuitos_9router/src/test_arsenal.py

echo ""
echo "======================================================================"
echo "✅ Todos os testes executados com 100% de sucesso via container!"
echo "======================================================================"
