.PHONY: test test-container test-gateway test-arsenal test-local up down logs clean

VENV ?= .venv
PYTHON ?= $(shell which $(VENV)/bin/python3 2>/dev/null || which python3 2>/dev/null)

# Executa todos os testes de integracao via container Docker (zero dependencias no host alem do Docker)
test: test-container

test-container:
	./run_tests.sh

test-gateway:
	docker run --rm --network claudegravity_default -v "$$(pwd)":/app -w /app \
	  -e ROUTER_URL=http://claudegravity-router:20128 \
	  -e ANTHROPIC_BASE_URL=http://claudegravity-router:20128 \
	  python:3.14-alpine python3 0002_claude_gravity_utilizando_9router/src/test_gateway.py

test-arsenal:
	docker run --rm --network claudegravity_default -v "$$(pwd)":/app -w /app \
	  -e ROUTER_URL=http://claudegravity-router:20128 \
	  -e ANTHROPIC_BASE_URL=http://claudegravity-router:20128 \
	  python:3.14-alpine python3 0003_fallback_modelos_gratuitos_9router/src/test_arsenal.py

# Testes locais opcionais no ambiente virtual
test-local:
	@if [ -x "$(VENV)/bin/python3" ]; then \
		echo "Executando testes locais com $(VENV)..."; \
		$(VENV)/bin/python3 0002_claude_gravity_utilizando_9router/src/verify_setup.py; \
		$(VENV)/bin/python3 0002_claude_gravity_utilizando_9router/src/test_gateway.py; \
		$(VENV)/bin/python3 0003_fallback_modelos_gratuitos_9router/src/test_arsenal.py; \
	else \
		echo "Ambiente virtual local nao encontrado. Executando em container..."; \
		./run_tests.sh; \
	fi

up:
	docker compose -f 0002_claude_gravity_utilizando_9router/docker-compose.yml up -d

down:
	docker compose -f 0002_claude_gravity_utilizando_9router/docker-compose.yml down

logs:
	docker logs -f router-sync

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
