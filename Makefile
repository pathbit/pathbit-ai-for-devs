.PHONY: setup test test-container test-gateway test-arsenal test-local valida-docs valida-consistencia valida-deepclaude prova-no-fio valida-paineis up down logs clean

VENV ?= .venv
PYTHON ?= $(shell which $(VENV)/bin/python3 2>/dev/null || which python3 2>/dev/null)

# Prepara o clone: ativa o hook que impede assinatura de coautoria de IA nos
# commits. O Git nao versiona .git/hooks, entao cada clone precisa fazer isso uma
# vez -- foi a ausencia desse passo que deixou quatro commits assinados passarem.
setup:
	@git config core.hooksPath .githooks
	@echo "core.hooksPath = $$(git config --get core.hooksPath)"
	@echo "Hook de autoria ativo. Regras do repositorio: AGENTS.md"

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

# Confere que os composes dos artigos batem com os projetos RTK: imagem, porta
# interna publicada e variaveis de ambiente. Um artigo publicado que manda o
# leitor copiar um compose divergente e um artigo quebrado, e nada avisa.
# Nao precisa de container de pe.
valida-docs:
	$(PYTHON) tools/valida_artigos_x_rtk.py

# Confere que os artigos publicados descrevem o repositorio como ele esta hoje:
# JSON transcrito x arquivo .example, imagens citadas x assets em disco, links
# relativos e convencao de nomes dos settings. Nao precisa de rede nem container.
valida-consistencia:
	$(PYTHON) tools/valida_consistencia_artigos.py

# Verificador do artigo 0004: sintaxe dos settings, sufixo [1m], credencial nos
# templates e contaminacao do settings global. Com ONLINE=1 faz inferencia real.
valida-deepclaude:
	$(PYTHON) 0004_deep_claude_alternativa_claudegravity/src/verify_deepclaude.py $(if $(ONLINE),--online,)

# Prova, na requisicao HTTP, o que os artigos prometem: sobe uma sonda local que
# finge ser a API da Anthropic, roda o Claude Code de verdade com o settings de
# cada artigo e mostra o que saiu no fio. Pede um modelo da Anthropic de
# proposito (--model claude-opus-5) para verificar que modelOverrides intercepta.
# Nao precisa de gateway de pe nem de credencial real.
prova-no-fio:
	$(PYTHON) tools/prova_no_fio.py $(ARTIGO)

# Validacao HTTP dos paineis das stacks. Exige as stacks de pe e as credenciais
# no ambiente -- veja o cabecalho do script; ele TROCA a senha do painel.
valida-paineis:
	./tools/valida_paineis.sh

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
