# 🚀 Guia de Ciclo de Vida dos Ambientes

Este guia orienta os desenvolvedores sobre como provisionar, inspecionar, pausar e destruir completamente os ambientes locais de IA no projeto **Pathbit AI for Devs**.

---

## 🎯 Abordagens Disponíveis

Oferecemos duas formas de controle de ambiente para atender diferentes fluxos de trabalho:

1. **Abordagem A (Utilitário Python `manage_env.py`):** Recomendada para o dia a dia. Executa verificações de dependências, inicia os containers, provisiona credenciais no banco SQLite e valida a inferência das APIs automaticamente.
2. **Abordagem B (Docker Compose Nativo):** Ideal para administradores de infraestrutura e pipelines de CI/CD que utilizam comandos convencionais do Docker.

---

## 🛠️ Comandos do Ciclo de Vida via Python

Cada módulo com containers (como `0002_claude_gravity_utilizando_9router` e `0003_fallback_modelos_gratuitos_9router`) possui o script `src/manage_env.py`:

### 1. Inicializar o Ambiente (`start`)

Sobe todos os containers em segundo plano, aguarda o endpoint HTTP ficar saudável e executa o provisionamento dos combos:

```bash
python3 src/manage_env.py start
```

### 2. Consultar o Estado dos Serviços (`status`)

Exibe uma visão rápida dos containers ativos e testa a resposta HTTP das portas locais:

```bash
python3 src/manage_env.py status
```

Exemplo de saída:

```text
============================================================
🔍 STATUS DO AMBIENTE CLAUDEGRAVITY
============================================================
CONTAINER ID   IMAGE                    NAMES                      STATUS
21f80dc8f517   python:3.14-alpine       claudegravity-token-sync   Up 4 minutes
4ac03e22ff19   decolua/9router:latest   claudegravity-router       Up 7 minutes (healthy)
a7f98d995e31   ollama/ollama:latest     claudegravity-ollama       Up 17 minutes (healthy)
✅ Gateway HTTP Status: 200 OK (porta 20128)
✅ Ollama HTTP Status: 200 OK (porta 11434)
```

### 3. Pausar o Ambiente (`stop`)

Interrompe a execução dos containers sem apagar dados ou configurações salvas nos volumes:

```bash
python3 src/manage_env.py stop
```

### 4. Destruição Completa do Ambiente (`destroy`)

Remove containers, redes e apaga completamente os volumes Docker (`9router_data` e `ollama_data`). Use este comando para zerar o ambiente e liberar espaço em disco:

```bash
python3 src/manage_env.py destroy
```

---

## 🐳 Comandos Equivalentes via Docker Compose Nativo

Se preferir utilizar diretamente a CLI do Docker Compose:

### Iniciar em segundo plano

Os manifestos leem `INITIAL_PASSWORD` e `JWT_SECRET` do arquivo `.env`, e falham de propósito se ele não existir  -  para que nenhum segredo fique escrito dentro do `docker-compose.yml`. Por isso, na primeira execução:

```bash
cp .env.example .env
docker compose up -d
```

### Verificar containers ativos e logs

Para checar os três serviços ativos (gateway, modelo local e sidecar de renovação contínua):

```bash
docker ps --filter "name=claudegravity"
```

Para acompanhar em tempo real o log da auto-renovação de tokens gerenciada pelo sidecar em Alpine Linux:

```bash
docker logs -f claudegravity-token-sync
```

### Pausar serviços

```bash
docker compose stop
```

### Destruir tudo e remover volumes persistentes

```bash
docker compose down -v --remove-orphans
```

---

## 🌐 Mapeamento de Portas e Serviços

| Serviço | Nome do Container | Porta Host | Finalidade Principal |
| :--- | :--- | :---: | :--- |
| **9Router Gateway** | `claudegravity-router` | `20128` | Proxy reverso, multi-provedor e tradução Anthropic Messages |
| **Ollama Local** | `claudegravity-ollama` | `11434` | Servidor local de inferência para modelos de código offline |
| **Token Sync Sidecar** | `claudegravity-token-sync` | Interno | Daemon em Python 3.14 Alpine para auto-renovação de tokens e prevenção do bug ISO |

---

## ⚠️ Boas Práticas e Dicas Operacionais

- Se a porta `20128` estiver ocupada por outra aplicação, consulte o guia [SOLUCAO_PROBLEMAS_COMUNS.md](./SOLUCAO_PROBLEMAS_COMUNS.md).
- O container sidecar `claudegravity-token-sync` roda silenciosamente consumindo apenas ~14 MB de RAM. Ele checa a validade do token a cada 5 minutos e renova automaticamente 15 minutos antes de expirar, eliminando erros 401 e 503.
- Antes de destruir o ambiente, lembre-se de que os dados de chaves configurados na interface gráfica serão apagados junto com o volume `9router_data`. Ao subir novamente, o script `setup_combos.py` ou `sync_antigravity_token.py` recriará as configurações automaticamente a partir das variáveis do seu `.env`.
