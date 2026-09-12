# ClaudeGravity e o Roteamento de Modelos Gemini no Claude Code via 9Router

![Capa do Artigo - ClaudeGravity](../assets/00_cover_claudegravity.png)

Todo desenvolvedor que já usou o **Claude Code** em projetos de verdade sabe que ele é, atualmente, um dos melhores *harnesses* de desenvolvimento autônomo do mercado. A capacidade de navegar na árvore de arquivos, inspecionar código com LSP, disparar comandos bash, acionar subagentes em paralelo e iterar sobre correções de testes coloca a CLI da Anthropic em uma classe própria.

O problema começa na ponta da inferência: **a conta de tokens e o limite de taxa (rate limit)**. Dependendo da densidade do repositório e do número de arquivos processados, uma tarde de refatorações complexas consome cotas pesadas ou trava o fluxo de trabalho no meio de uma depuração crítica.

Do outro lado da mesa, temos o **Google Antigravity (Google AI Pro)**: uma das infraestruturas de inteligência artificial mais potentes da atualidade, equipada com os modelos **Gemini 3.8 Flash**, **Gemini 3.7 Flash**, **Gemini 3.6 Flash**, **Gemini 3.1 Pro**, além de variantes abertas como o **GPT-OSS 120B** e instâncias do próprio **Claude 4.6 (Sonnet e Opus)** embutidas no ecossistema do Google. Tudo isso com uma janela massiva de contexto de 1 milhão de tokens e tempo de resposta rápido.

A comunidade de engenharia já provou o valor de desacoplar o harness do provedor quando criou o movimento *DeepClaude* (Claude Code operando com modelos DeepSeek). Agora, levamos essa ideia ao nível de engenharia profissional: apresentamos o **ClaudeGravity**, arquitetura que une o harness do Claude Code com o poder dos modelos Gemini da sua conta Google AI Pro, orquestrado através do gateway inteligente **9Router**.

E o melhor: **sem pagar tokens adicionais na API do Google AI Studio**. Você utiliza legitimamente a capacidade computacional da assinatura que você já possui.

> Caso você ainda não tenha configurado o seu ambiente Google Antigravity para autonomia total e sem confirmações manuais, recomendamos iniciar pelo [Artigo 0001 - Google Antigravity com Acesso Total Irrestrito e sem Interrupções](../../0001_antigravity_acesso_total_irrestrito/article/ARTICLE.md), no qual cobrimos o destravamento do motor Agent 2.0 e da CLI `agy`.

---

## A Arquitetura do ClaudeGravity

Abaixo está o fluxo operacional de ponta a ponta que implementaremos neste artigo:

![Arquitetura ClaudeGravity](../assets/01_diagrama_arquitetura_claudegravity.png)

> **Figura 1:** Arquitetura operacional do ClaudeGravity, conectando o Claude Code CLI aos modelos Gemini do Google Antigravity através do gateway 9Router em container Docker.

A arquitetura resolve três problemas fundamentais de uma só vez:

1. **Tradução de Protocolo:** O Claude Code espera falar a especificação Anthropic Messages API. O Google Cloud Code opera no protocolo proprietário do Gemini/Google Code Assist. O 9Router traduz requisições, respostas em streaming (SSE) e assinaturas de *tool calling* de forma bidirecional e transparente.
2. **Compressão RTK (Token Saver):** Em fluxos de desenvolvimento com agentes, saídas de comandos como `git diff`, `grep` e relatórios de linter despejam milhares de tokens inúteis. O 9Router inclui um compressor de payloads de ferramentas baseado no algoritmo RTK, ativo por padrão, com filtros dedicados para `git diff`, `git status`, `git log`, `grep`, `tree`, `ls`, `find` e saídas de build. A economia real depende do tipo de saída que o agente produz.
3. **Gestão de Sessão e Renovação Contínua de Tokens:** Em vez de chaves de API estáticas com limites rígidos de faturamento, a conexão utiliza OAuth 2.0 com renovação automática de tokens em segundo plano (*auto token refresh*).

---

## Por que 9Router e Não Google AI Studio?

Uma dúvida comum de quem começa a explorar essa integração é: *"Por que não simplesmente criar uma API Key no Google AI Studio e apontar o Claude Code para ela?"*

A resposta é econômica e operacional. A API Key do AI Studio é faturada por token no cartão de crédito, o que transforma qualquer loop de agente em risco de fatura surpresa. Já o Antigravity opera dentro da assinatura AI Pro que você já paga, com renovação automática de credenciais, compressão de payload e fallback entre contas  -  recursos que, pela via da API Key, você teria de implementar sozinho. O comparativo completo com as demais abordagens está na seção [Comparativo entre Claude Nativo, DeepClaude e ClaudeGravity](#comparativo-entre-claude-nativo-deepclaude-e-claudegravity).

Usar a conta do Antigravity não é ilegal nem viola termos de serviço quando feito para uso pessoal e de desenvolvimento: você está exercendo a computação do seu plano profissional do Google diretamente em seu terminal de trabalho, utilizando o gateway como um adaptador de protocolo local.

---

## Subindo o Gateway 9Router via Docker (Método Recomendado)

O melhor modelo operacional para executar o 9Router é através de um container Docker isolado. Isso garante que dependências do Node.js, bibliotecas nativas de SQLite e portas de rede não colidam com suas ferramentas do dia a dia.

### 1. O arquivo `docker-compose.yml`

No repositório do projeto, estruturamos o serviço da seguinte forma:

```yaml
name: claudegravity

services:
  9router:
    image: decolua/9router:latest
    container_name: claudegravity-router
    restart: unless-stopped
    ports:
      # Apenas localhost: o gateway carrega credenciais reais (OAuth do Antigravity
      # e chaves dos provedores) e nao deve ficar acessivel na rede local.
      - "127.0.0.1:20128:20128"
    volumes:
      - 9router_data:/app/data
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - DATA_DIR=/app/data
      - PORT=20128
      - HOSTNAME=0.0.0.0
      - NEXT_PUBLIC_BASE_URL=http://localhost:20128
      - NODE_ENV=production
      # Credenciais lidas do arquivo .env local (nunca versionado)
      - INITIAL_PASSWORD=${INITIAL_PASSWORD:?defina INITIAL_PASSWORD no arquivo .env}
      - JWT_SECRET=${JWT_SECRET:?defina JWT_SECRET no arquivo .env}
      - REQUIRE_API_KEY=false
      - REQUIRE_LOGIN=false
    command: ["/bin/sh", "-c", "cp /app/open-sse/providers/shared.js /app/data/shared.js 2>/dev/null || true; exec node server.js"]
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://127.0.0.1:20128/dashboard"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s

  9rtksync:
    # 9RTKSync: 9Router Universal Token & Connection Synchronizer (https://github.com/pathbit/9RTKSync)
    image: ghcr.io/pathbit/9rtksync:latest
    container_name: router-sync
    restart: unless-stopped
    ports:
      - "127.0.0.1:9190:9190"
    volumes:
      - 9router_data:/app/data
      - ${HOME}:/root/host:ro
    environment:
      - PYTHONUNBUFFERED=1
      - HOST_HOME=/root/host
      - DB_PATH=/app/data/db/data.sqlite
      - ROUTER_URL=http://9router:20128
      - SYNC_INTERVAL=300
      - REFRESH_MARGIN=900
      - MODULE=0002
      - ENABLE_WEB_DASHBOARD=1
      - WEB_PORT=9190
      # O painel exige autenticacao. Sem estas duas variaveis a stack sobe, mas
      # o navegador responde 401 e nao ha senha documentada para informar.
      - DASHBOARD_USER=${DASHBOARD_USER:-admin}
      - DASHBOARD_PASSWORD=${DASHBOARD_PASSWORD:?defina DASHBOARD_PASSWORD no .env}
    depends_on:
      9router:
        condition: service_healthy

volumes:
  9router_data:
```

Cinco decisões de engenharia neste manifesto:

* **`extra_hosts: ["host.docker.internal:host-gateway"]`** garante compatibilidade entre plataformas (macOS, Linux e Windows WSL2), permitindo que o container resolva o endereço do host local de forma idêntica em qualquer distribuição.
* **Senha e segredo JWT vêm do `.env`**, nunca literais no arquivo versionado. A sintaxe `${VAR:?mensagem}` interrompe a subida com um erro claro caso a variável não exista, em vez de silenciosamente aplicar um padrão fraco.
* **`healthcheck` ativo:** sem ele, a diretiva `restart: unless-stopped` só reage quando o processo morre  -  um container travado, mas vivo, permaneceria roteando para o vazio. A sonda HTTP a cada 30 segundos marca o container como `unhealthy` e torna o problema visível no `docker ps`.
* **Porta publicada apenas em `127.0.0.1`:** o gateway guarda o token OAuth da sua conta Google e as chaves dos provedores. Publicar como `"20128:20128"` o exporia em todas as interfaces de rede, permitindo que qualquer máquina da mesma rede consumisse sua cota. O prefixo de loopback restringe o acesso à própria máquina.
* **Guardião de sincronização contínua (`9RTKSync`):** baseado na imagem oficial `ghcr.io/pathbit/9rtksync:latest` do projeto [9RTKSync](https://github.com/pathbit/9RTKSync) (*9Router Universal Token & Connection Synchronizer*), roda em ambiente virtual isolado (`/opt/venv`), consome apenas ~18 MB de RAM e valida a saúde das conexões do [9Router](https://github.com/decolua/9router) continuamente com auto-cura e dashboard web embutido na porta 9190.

> **Sobre a tag `:latest`:** o manifesto acompanha a última versão publicada do gateway. A contrapartida é conhecida: os scripts deste artigo dependem de um endpoint interno (`/api/auth/status`) e do schema SQLite do gateway (tabelas `providerConnections` e `combos`), e uma atualização pode mexer em qualquer um dos dois. Por isso o `verify_setup.py` existe  -  ele confere justamente esses pontos. Depois de um `docker compose pull`, rode `python3 src/verify_setup.py`: ele confere o endpoint e a tabela `combos`, e se qualquer um mudar, você descobre ali, e não no meio de uma refatoração. Se precisar congelar o ambiente para uma demonstração, troque `:latest` pela versão exata que estiver rodando, que o `docker inspect claudegravity-router` mostra.

### 2. Inicializando o serviço

Primeiro crie o arquivo `.env` a partir do modelo, definindo a senha do dashboard e o segredo JWT:

```bash
cp .env.example .env
```

Em seguida suba o serviço:

```bash
docker compose up -d
```

Verifique a saúde dos containers:

```bash
# Conferir status dos containers do ambiente
docker ps --filter "name=claudegravity"

# Inspecionar os logs do sidecar de renovacao de tokens
docker logs -f claudegravity-token-sync
```

![Container Docker Rodando](../assets/02_docker_container_running.png)

> **Figura 2:** Evidência dos containers `claudegravity-router` e `claudegravity-token-sync` em execução saudável na porta local `20128`.

---

## Alternativa de Instalação Nativa na Máquina (CLI / NPM)

Caso você não utilize Docker ou queira testar diretamente no ambiente local da máquina:

```bash
# Instalação global do pacote oficial do 9Router
npm install -g 9router

# Inicialização do serviço
PORT=20128 9router
```

O serviço iniciará imediatamente e abrirá a porta `http://localhost:20128`. Ambos os métodos (Docker e Nativo) operam exatamente com os mesmos endpoints e capacidades.

---

## Conectando a Conta Antigravity (Google AI Pro)

Com o gateway em execução, abra seu navegador em:

👉 **[http://localhost:20128/dashboard](http://localhost:20128/dashboard)**

Se a tela de login for exibida, insira a senha que você definiu em `INITIAL_PASSWORD` no arquivo `.env`:

![Tela de Login do 9Router](../assets/03_9router_login.png)

> **Figura 3:** Tela de autenticação inicial do 9Router.

Após entrar, navegue até a aba **Endpoint & Key**. O gateway já exibe a URL local `http://localhost:20128/v1` e permite gerar ou visualizar chaves de API para os clientes CLI:

![Dashboard do 9Router](../assets/04_9router_dashboard.png)

> **Figura 4:** Painel de configuração de API Endpoint e gerenciamento de chaves de acesso.

> **Sobre a chave que aparece nos exemplos deste artigo.** Todos os blocos usam o placeholder `sk-sua-chave-do-9router`. A chave real é **gerada localmente na primeira execução** de `src/sync_antigravity_token.py`: o script sorteia um valor aleatório exclusivo da sua máquina, registra no gateway e grava no arquivo `.env` do módulo, que não é versionado. O script imprime a chave no terminal para você copiá-la. Nenhuma chave fixa é distribuída no repositório  -  se fosse, seria uma senha única compartilhada por todos os leitores, válida em qualquer instalação do tutorial.

### O Papel Mandatório do Dashboard Aberto com a Conta Licenciada

Um dos pontos mais críticos para o sucesso da integração entre Claude Code, 9Router e Google Antigravity reside na forma como a sessão de autenticação é estabelecida e mantida.

Para que a ponte de inferência funcione de ponta a ponta sem erros de permissão, **o dashboard do 9Router (`http://localhost:20128/dashboard`) deve ser aberto no navegador exatamente sob a conta Google titular da licença Antigravity (Google AI Pro, Google One AI Premium ou Workspace com Gemini)**.

Manter a aba do dashboard aberta no navegador durante suas sessões de desenvolvimento atende a três propósitos operacionais vitais:

1. **Contexto de Sessão e Fluxo OAuth no Navegador:** O 9Router utiliza o mecanismo de autenticação web do Google para negociar e validar os tokens de autorização da API Code Assist. O navegador precisa estar com a sessão da conta licenciada ativa para que o handshake OAuth conceda os escopos corretos de inferência sem atrito.
2. **Observabilidade Operacional em Tempo Real:** O dashboard exibe instantaneamente o status do provedor (`active • OAuth #1`), o volume de requisições por minuto, o tempo de resposta em milissegundos e o percentual de tokens economizados pelo compressor RTK. Se uma rajada de requisições exceder a cota momentânea de taxa (RPM), o painel reflete o estado imediatamente, permitindo ação preventiva.
3. **Detecção e Renovação Visual de Sessão:** Caso ocorra alternância de rede, troca de IP ou revogação temporária de credenciais pelo Google, o card do provedor no dashboard altera seu status visual, indicando a necessidade de revalidação antes que o Claude Code enfrente erros no meio de uma refatoração crítica.

### A Armadilha das Múltiplas Contas Google no Navegador

Na rotina diária de desenvolvimento de software, é quase unânime que engenheiros mantenham múltiplos perfis Google logados no mesmo navegador: um e-mail pessoal gratuito (`dev.silva@gmail.com`), um e-mail corporativo (`nome@empresa.com`), e-mails acadêmicos ou contas de clientes.

Essa convivência de perfis é a **principal causa de falhas misteriosas** ao conectar o 9Router pela primeira vez:

* **O Mecanismo da Falha:** Quando você clica em **+ Add Connection** no 9Router, o Google abre a tela padrão de autorização OAuth. Se o seu navegador estiver com o perfil pessoal padrão selecionado e esse perfil **não possuir a assinatura Google AI Pro / Antigravity**, o fluxo de autenticação completa sem erros aparentes. O Google emite o token e o 9Router exibe a conexão como `active`.
* **O Sintoma Silencioso no Terminal:** Embora a conexão aparente estar saudável, no instante em que o Claude Code ou o script de teste solicita inferência para `ag/gemini-3.8-flash-high`, os servidores do Google Code Assist recusam a chamada e devolvem erros como:
  - `HTTP 403 Forbidden` (`PERMISSION_DENIED` ou `ResourceExhausted`);
  - `HTTP 404 Model Not Found` (o modelo Gemini Flash High e as instâncias Antigravity simplesmente não são liberadas para contas sem o plano Pro);
  - Bloqueio imediato por ausência de cota de inferência de engenharia.
* **A Causa Raiz:** O Google valida a cota de computação contra a assinatura atrelada ao e-mail proprietário da credencial OAuth. Uma conta gratuita gera um token OAuth sintaticamente perfeito, mas sem qualquer permissão de inferência para os modelos do Antigravity.

> **Regra Prática de Blindagem:** Antes de iniciar a vinculação, abra uma aba em `https://myaccount.google.com` no mesmo navegador e confirme visualmente que o avatar e o endereço exibidos pertencem à conta titular da assinatura Google AI Pro / Antigravity. Caso seu navegador utilize perfis separados (Chrome Profiles, Arc Spaces ou Edge Profiles), abra o dashboard do 9Router exclusivamente na janela do perfil que detém a licença.

### Vinculando a Conta Google no Menu Providers

Com a conta Google correta ativa no navegador, execute o pareamento formal no gateway:

1. No menu lateral do dashboard, clique em **Providers** (`http://localhost:20128/dashboard/providers`).
2. Na seção **OAuth Providers**, localize o card **Antigravity**:

![Catálogo de Provedores](../assets/05_9router_providers.png)

> **Figura 5:** Visão geral de provedores com suporte nativo a Antigravity, Claude Code, OpenAI Codex e Kiro.

3. Clique no card **Antigravity**. O 9Router exibirá o painel de gerenciamento do provedor aguardando a configuração da primeira credencial (com 0 conexões ativas):

![Painel do Provedor Antigravity](../assets/06_9router_antigravity_provider.png)

> **Figura 6:** Painel de conexões e modelos do provedor Antigravity no 9Router antes da autenticação (0 conexões ativas e botão para adicionar conexão).

4. Clique no botão **+ Add Connection**. Uma janela segura de autenticação Google será aberta. Certifique-se de selecionar a conta Google titular da sua assinatura AI Pro e aprove o consentimento de acesso.
5. O 9Router completará o handshake OAuth, registrará o `projectId` e atualizará o status da conexão para **`active • OAuth #1`**:

![Provedor Antigravity Conectado](../assets/07_9router_antigravity_connected.png)

> **Figura 7:** Provedor Antigravity com a conta Google AI Pro ativa (`active • OAuth #1`) e catálogo completo de modelos Gemini disponíveis para roteamento.

### Protocolo de Validação Visual no Dashboard e Recuperação de Conexão

Após completar a vinculação, execute a verificação visual no painel:

1. **Status da Conexão:** No card Antigravity, o rótulo deve exibir expressamente `active • OAuth #1` em verde.
2. **Catálogo de Modelos Habilitados:** A lista deve exibir os 20 modelos disponíveis (Gemini 3.8, Gemini 3.7, Gemini 3.6, Gemini 3.1 Pro e variantes auxiliares).
3. **Como Corrigir se a Conta Errada Foi Vinculada:**
   Caso você perceba que vinculou uma conta pessoal sem assinatura ou se os testes apontarem erro 403:
   - No card Antigravity em `http://localhost:20128/dashboard/providers`, localize a conexão ativa e clique no ícone de lixeira (**Delete Connection**).
   - Abra uma aba em `myaccount.google.com` no mesmo navegador e alterne o usuário ativo para a conta detentora da licença Antigravity.
   - Retorne ao painel do 9Router, clique novamente em **+ Add Connection** e selecione a conta licenciada.

### Validação Automatizada de Inferência via Terminal

Não basta a interface indicar que está conectado: na engenharia de software de ponta, tudo deve ser testado, provado e validado via código executável.

Disponibilizamos no repositório o script `src/test_gateway.py` para atestar a comunicação real com a API do Google:

```bash
python3 src/test_gateway.py
```

O utilitário executa quatro baterias de verificação automática:

1. **Disponibilidade do Endpoint Local:** Confirma que o 9Router está saudável na porta `20128` (retornando `HTTP 200`).
2. **Listagem do Catálogo:** Valida a presença dos identificadores com prefixo `ag/`.
3. **Inferência Direta no Gemini 3.8 Flash High:** Envia a mensagem `"Responda apenas: PONG - ClaudeGravity Operacional"` diretamente para o endpoint `/v1/messages` simulando uma chamada real do Claude Code.
4. **Resiliência do Combo de Fallback:** Envia a mesma inferência para o combo virtual `claudegravity-fallback`.

A saída no terminal comprova o sucesso em tempo real:

```text
======================================================================
🧪 TESTE DE INTEGRACAO CLAUDEGRAVITY & GATEWAY 9ROUTER
======================================================================
🔍 [1/4] Verificando disponibilidade do gateway 9Router em http://localhost:20128...
✅ Gateway 9Router está online e respondendo (HTTP 200)!

🔍 [2/4] Listando modelos Antigravity registrados...
✅ Total de modelos Antigravity identificados: 20
Modelos em destaque:
   • ag/gemini-3.8-flash-high
   • ag/gemini-3.8-flash-medium
   • ag/gemini-3.8-flash-low
   • ag/gemini-3.8-flash
   • ag/gemini-3.7-flash-high
   • ag/gemini-3.7-flash-medium

🔍 [3/4] Testando ClaudeGravity Principal (ag/gemini-3.8-flash-high direto via Antigravity Pro) (ag/gemini-3.8-flash-high)...
✅ Status HTTP 200 recebido em 1.06s!
💬 Resposta do modelo: PONG - ClaudeGravity Operacional

🔍 [4/4] Testando ClaudeGravity Resiliente com Fallback Free (claudegravity-fallback) (claudegravity-fallback)...
✅ Status HTTP 200 recebido em 1.28s!
💬 Resposta do modelo: PONG - ClaudeGravity Operacional

======================================================================
🎉 TODOS OS TESTES PASSARAM COM SUCESSO!
O ClaudeGravity está 100% operacional no modelo Principal e no Fallback.
```

Se o teste retornar `HTTP 200` e a resposta `PONG - ClaudeGravity Operacional` for impressa, sua conta Google licenciada está rigorosamente comprovada e pronta para assumir cargas pesadas de trabalho com o Claude Code.

---

## O Catálogo Completo de Modelos Disponíveis

Com a conta Antigravity conectada, o Claude Code passa a ter acesso aos seguintes identificadores de modelo:

### 1. Família Gemini 3.8 (Recomendado como Primário)
- **`ag/gemini-3.8-flash-high`**: Variante topo de linha com nível máximo de raciocínio encadeado (*high thinking*). Ideal para refatorações profundas de código, depuração de bugs complexos e planejamento de arquitetura.
- **`ag/gemini-3.8-flash-medium`**: Equilíbrio entre profundidade de análise e tempo de resposta.
- **`ag/gemini-3.8-flash-low`**: Execução veloz com raciocínio leve.
- **`ag/gemini-3.8-flash`**: Alias padrão para a geração 3.8.

### 2. Família Gemini 3.7
- **`ag/gemini-3.7-flash-high`**: Modelo com raciocínio híbrido ágil, excelente para geração de testes unitários e revisões de PR.
- **`ag/gemini-3.7-flash-medium`** e **`ag/gemini-3.7-flash-low`**.

### 3. Família Gemini 3.6
- **`ag/gemini-3.6-flash-high`**: Excelente para tarefas de alta frequência com baixa latência.
- **`ag/gemini-3.6-flash-medium`** e **`ag/gemini-3.6-flash-low`**.

### 4. Família Gemini 3 (Econômica)
- **`ag/gemini-3-flash`** e **`ag/gemini-3-flash-agent`**: variantes base e agêntica da geração 3, úteis como camada barata de fallback em tarefas de baixa complexidade.

> **A família 3.5 saiu do ar.** Os identificadores `ag/gemini-3.5-*` ainda aparecem no catálogo do gateway, mas o `-high` responde `404` e as variantes `-low` devolvem a mensagem do próprio Google: *"Gemini 3.5 Flash is no longer available. Please switch to Gemini 3.7 Flash"*. É um bom lembrete de que o catálogo listado pelo provedor nem sempre reflete o que está realmente servindo  -  valide antes de colocar um identificador na sua cascata.

### 5. Modelos Gemini Pro (Não Flash) & Agentes
- **`ag/gemini-pro-agent`**: Gemini 3.1 Pro configurado para planejamento autônomo e raciocínio formal.
- **`ag/gemini-3.1-pro-low`**: Versão otimizada para respostas diretas sem overhead de inferência prolongada.

### 6. Modelos Adicionais via Antigravity
- **`ag/claude-sonnet-4-6`**: Instância do Claude Sonnet 4.6 Thinking servida na infraestrutura do Google Cloud.
- **`ag/claude-opus-4-6-thinking`**: Instância do Claude Opus 4.6 Thinking.
- **`ag/gpt-oss-120b-medium`**: Modelo open-weights de 120 bilhões de parâmetros.

> Os 17 identificadores acima são os que respondem. O gateway expõe 20 com prefixo `ag/`: os 3 restantes são a família `ag/gemini-3.5-*` do aviso anterior, que continua catalogada mesmo depois de sair do ar. A lista viva sempre pode trazer mais entradas do que as utilizáveis, então confira a do seu ambiente e valide antes de adotar: `curl -s -H "x-api-key: $ANTHROPIC_API_KEY" http://localhost:20128/v1/models`.

---

## Configuração do Claude Code com Zero Interrupções

Um dos maiores pesadelos ao utilizar agentes no terminal é a interrupção constante:

```text
Allow bash command: git status? [y/N]
Allow read file: src/index.ts? [y/N]
Allow edit file: src/index.ts? [y/N]
```

Em loops autônomos, esse comportamento torna a experiência impraticável. Por isso o ClaudeGravity adota **`--dangerously-skip-permissions`** como requisito  -  o mesmo princípio vale para a CLI oficial do Antigravity (`agy --dangerously-skip-permissions`). O efeito exato de cada flag está detalhado na tabela da seção [Anatomia das Variáveis de Ambiente](#anatomia-das-variáveis-de-ambiente-e-flags-avançadas).

### Guia Integrado de Ferramentas CLI no 9Router

O painel do 9Router disponibiliza a aba dedicada **CLI Tools** com instruções de integração direta para ferramentas como Claude Code e OpenAI Codex:

![Painel de Ferramentas CLI no 9Router](../assets/08_9router_cli_tools.png)

> **Figura 8:** Painel CLI Tools do 9Router com templates prontos de configuração para harnesses agênticos.

Ao selecionar **Claude Code**, o gateway apresenta as instruções com as variáveis de ambiente necessárias para a conexão:

![Instruções de Configuração do Claude Code](../assets/09_9router_claude_code_config.png)

> **Figura 9:** Instruções integradas do 9Router demonstrando a parametrização do Claude Code.

### Configurando o Claude Code a partir dos Modelos Example

Para que toda sessão do Claude Code inicie com as permissões completas e os modelos Gemini já mapeados, disponibilizamos modelos `.example` dentro da pasta de testes do artigo (`examples/.claude/`). Para inicializar sua configuração local:

```bash
cp examples/.claude/settings.json.example examples/.claude/settings.json
cp examples/.claude/settings.local.json.example examples/.claude/settings.local.json
cp .env.example .env
```

#### O que preencher no `.env`

A maior parte das variáveis já vem com valor funcional. Apenas estas exigem sua atenção:

| Variável | Obrigatória? | O que colocar |
| :--- | :--- | :--- |
| `INITIAL_PASSWORD` | **Sim** | Senha do painel do 9Router. O `docker compose` recusa subir sem ela. |
| `JWT_SECRET` | **Sim** | Valor longo e aleatório para assinar as sessões do painel. Gere com `openssl rand -hex 32`. |
| `ANTHROPIC_API_KEY` | **Sim** | Não invente: é impressa pelo `src/sync_antigravity_token.py` na primeira execução e gravada aqui automaticamente. |
| `ANTHROPIC_BASE_URL` | Já preenchida | `http://localhost:20128`, sem o sufixo `/v1` (a CLI o acrescenta sozinha). |

Não há chave de provedor externo neste artigo: a autenticação com o Google acontece via OAuth, reaproveitando a sessão do Antigravity que já está na sua máquina.

#### Os dois arquivos de configuração do Claude Code

Ambos ficam em `examples/.claude/`, isolados do restante do repositório  -  por isso não interferem no projeto em que você estiver trabalhando.

| Arquivo | Papel | Contém |
| :--- | :--- | :--- |
| `settings.json` | Versão do projeto, compartilhável com o time | A configuração completa: modelo padrão, os quatro papéis, `modelPicker`, `modelOverrides`, permissões e `env` |
| `settings.local.json` | A mesma configuração, na sua máquina | O **mesmo conteúdo**. Existe para ficar fora do controle de versão e **tem precedência** sobre o anterior |

Os dois são versionados apenas na forma `.example`; as cópias ativas ficam fora do controle de versão.

#### Estrutura do `settings.json.example`

```json
{
  "model": "ag/gemini-3.8-flash-high",
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:20128",
    "ANTHROPIC_API_KEY": "sk-sua-chave-do-9router",
    "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1",
    "ANTHROPIC_DEFAULT_FABLE_MODEL": "ag/gemini-pro-agent",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "ag/gemini-3.8-flash-high",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "ag/gemini-3.7-flash-high",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "ag/gemini-3.6-flash-high",
    "ANTHROPIC_MODEL": "ag/gemini-3.8-flash-high",
    "CLAUDE_CODE_ENABLE_EXPERIMENTAL_ADVISOR_TOOL": "1"
  },
  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": [
      "Bash(*)",
      "Read(*)",
      "Edit(*)",
      "Write(*)",
      "Glob(*)",
      "Grep(*)",
      "WebFetch(*)",
      "WebSearch(*)",
      "NotebookEdit(*)",
      "TodoWrite(*)",
      "Agent(*)",
      "Skill(*)"
    ]
  },
  "skipDangerousModePermissionPrompt": true,
  "includeCoAuthoredBy": false,
  "advisorModel": "ag/gemini-pro-agent",
  "modelPicker": {
    "replaceBuiltInOptions": true,
    "options": [
      {
        "model": "ag/gemini-3.8-flash-high",
        "label": "Gemini 3.8 Flash High",
        "description": "Primario: raciocinio alto, 1M de contexto",
        "behavesAs": "claude-opus-4-8"
      },
      {
        "model": "ag/gemini-pro-agent",
        "label": "Gemini 3.1 Pro High",
        "description": "O mais denso da conta. Use com parcimonia",
        "behavesAs": "claude-opus-4-8"
      },
      {
        "model": "ag/gemini-3.7-flash-high",
        "label": "Gemini 3.7 Flash High",
        "description": "Trabalho corrente",
        "behavesAs": "claude-sonnet-4-6"
      },
      {
        "model": "ag/gemini-3.6-flash-high",
        "label": "Gemini 3.6 Flash High",
        "description": "Latencia minima, alta frequencia",
        "behavesAs": "claude-haiku-4-5-20251001"
      },
      {
        "model": "ag/claude-sonnet-4-6",
        "label": "Claude Sonnet 4.6",
        "description": "Sonnet servido pelo Antigravity",
        "behavesAs": "claude-sonnet-4-6"
      },
      {
        "model": "ag/claude-opus-4-6-thinking",
        "label": "Claude Opus 4.6 Thinking",
        "description": "Opus Thinking servido pelo Antigravity",
        "behavesAs": "claude-opus-4-8"
      },
      {
        "model": "ag/gpt-oss-120b-medium",
        "label": "GPT-OSS 120B",
        "description": "Pesos abertos via Antigravity",
        "behavesAs": "claude-sonnet-4-6"
      },
      {
        "model": "claudegravity-fallback",
        "label": "ClaudeGravity Resiliente (combo)",
        "description": "5 niveis. Use quando a cota de uma familia estourar",
        "behavesAs": "claude-opus-4-8"
      },
      {
        "model": "claudegravity-thinking",
        "label": "ClaudeGravity Thinking (combo)",
        "description": "4 niveis, comeca no Opus 4.6. Nao depende da cota do Gemini",
        "behavesAs": "claude-opus-4-8"
      }
    ]
  },
  "modelOverrides": {
    "claude-fable-5-1": "ag/gemini-pro-agent",
    "claude-opus-5": "ag/gemini-3.8-flash-high",
    "claude-sonnet-5": "ag/gemini-3.7-flash-high"
  }
}
```

#### Estrutura do `settings.local.json.example` (Menu `/model`)

```json
{
  "model": "ag/gemini-3.8-flash-high",
  "advisorModel": "ag/gemini-pro-agent",
  "modelPicker": {
    "replaceBuiltInOptions": true,
    "options": [
      {
        "model": "ag/gemini-3.8-flash-high",
        "label": "Gemini 3.8 Flash High",
        "description": "Primario: raciocinio alto, 1M de contexto",
        "behavesAs": "claude-opus-4-8"
      },
      {
        "model": "ag/gemini-pro-agent",
        "label": "Gemini 3.1 Pro High",
        "description": "O mais denso da conta. Use com parcimonia",
        "behavesAs": "claude-opus-4-8"
      },
      {
        "model": "ag/gemini-3.7-flash-high",
        "label": "Gemini 3.7 Flash High",
        "description": "Trabalho corrente",
        "behavesAs": "claude-sonnet-4-6"
      },
      {
        "model": "ag/gemini-3.6-flash-high",
        "label": "Gemini 3.6 Flash High",
        "description": "Latencia minima, alta frequencia",
        "behavesAs": "claude-haiku-4-5-20251001"
      },
      {
        "model": "ag/claude-sonnet-4-6",
        "label": "Claude Sonnet 4.6",
        "description": "Sonnet servido pelo Antigravity",
        "behavesAs": "claude-sonnet-4-6"
      },
      {
        "model": "ag/claude-opus-4-6-thinking",
        "label": "Claude Opus 4.6 Thinking",
        "description": "Opus Thinking servido pelo Antigravity",
        "behavesAs": "claude-opus-4-8"
      },
      {
        "model": "ag/gpt-oss-120b-medium",
        "label": "GPT-OSS 120B",
        "description": "Pesos abertos via Antigravity",
        "behavesAs": "claude-sonnet-4-6"
      },
      {
        "model": "claudegravity-fallback",
        "label": "ClaudeGravity Resiliente (combo)",
        "description": "5 niveis. Use quando a cota de uma familia estourar",
        "behavesAs": "claude-opus-4-8"
      },
      {
        "model": "claudegravity-thinking",
        "label": "ClaudeGravity Thinking (combo)",
        "description": "4 niveis, comeca no Opus 4.6. Nao depende da cota do Gemini",
        "behavesAs": "claude-opus-4-8"
      }
    ]
  },
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:20128",
    "ANTHROPIC_API_KEY": "sk-sua-chave-do-9router",
    "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1",
    "ANTHROPIC_DEFAULT_FABLE_MODEL": "ag/gemini-pro-agent",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "ag/gemini-3.8-flash-high",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "ag/gemini-3.7-flash-high",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "ag/gemini-3.6-flash-high",
    "ANTHROPIC_MODEL": "ag/gemini-3.8-flash-high",
    "CLAUDE_CODE_ENABLE_EXPERIMENTAL_ADVISOR_TOOL": "1"
  },
  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": [
      "Bash(*)",
      "Read(*)",
      "Edit(*)",
      "Write(*)",
      "Glob(*)",
      "Grep(*)",
      "WebFetch(*)",
      "WebSearch(*)",
      "NotebookEdit(*)",
      "TodoWrite(*)",
      "Agent(*)",
      "Skill(*)"
    ]
  },
  "skipDangerousModePermissionPrompt": true,
  "includeCoAuthoredBy": false,
  "modelOverrides": {
    "claude-fable-5-1": "ag/gemini-pro-agent",
    "claude-opus-5": "ag/gemini-3.8-flash-high",
    "claude-sonnet-5": "ag/gemini-3.7-flash-high"
  }
}
```

### Anatomia das Variáveis de Ambiente e Flags Avançadas

Para obter o máximo desempenho e estabilidade ao operar o Claude Code conectado a modelos externos, configuramos uma série de flags de tempo de execução fundamentais:

| Variável / Flag | Função Técnica no Claude Code | Por que é Essencial no ClaudeGravity |
| :--- | :--- | :--- |
| `ANTHROPIC_BASE_URL` | Redireciona as chamadas de API do endpoint oficial da Anthropic para o gateway local (`http://localhost:20128`). | O Claude Code anexa internamente `/v1/messages`. Declarar a URL **sem** o sufixo `/v1` produz a rota limpa `/v1/messages`. O 9Router tolera a forma duplicada `/v1/v1/messages` graças a um interceptador de compatibilidade, mas proxies estritos não - por isso a recomendação vale como boa prática portável. |
| `ANTHROPIC_API_KEY` | Chave de autorização fornecida ao cliente HTTP. | Utiliza a chave gerada no 9Router (`sk-...`) para autorizar a sessão no proxy local. |
| `--dangerously-skip-permissions` | Desabilita completamente as confirmações interativas de terminal (`[y/N]`) para ferramentas de arquivo e bash. | Torna o agente 100% autônomo. Sem essa flag, o desenvolvedor precisa apertar `y` a cada linha de teste executada ou arquivo modificado. |
| `bypassPermissions` | Modo padrão declarado dentro de `.claude/settings.json` na seção `permissions`. | Garante que subagentes, ferramentas e comandos herdados iniciem sem restrições. |
| `skipDangerousModePermissionPrompt` | Suprime o diálogo de aviso inicial do Claude Code sobre estar rodando em modo desprotegido. | Elimina o prompt de confirmação inicial toda vez que uma nova sessão é disparada. |
| `includeCoAuthoredBy: false` | Impede que o Claude Code anexe trailers de coautoria (`Co-Authored-By`) nos commits. | Assegura autoria estritamente humana nos commits e preserva a integridade do histórico do repositório. |
| `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1` | Desativa a restrição rígida de contagem de janela de contexto baseada exclusivamente nos modelos proprietários da Anthropic. | Permite que o Claude Code utilize os identificadores `ag/gemini-*` sem reclamar de tamanho de janela desconhecido. |

---

### Um `modelOverrides` Curto, e Só Onde Faz Falta

A chave `modelOverrides` traduz o identificador pedido pela CLI para um modelo do gateway. A tentação
é mapear tudo  -  chegamos a escrever 33 entradas cobrindo cada família com e sem sufixo de janela.
Foi trabalho desperdiçado, e a medição mostrou por quê.

Com o `modelPicker` substituindo a lista nativa e os quatro papéis declarados, testamos **removendo o
bloco por completo**. Nada quebrou na operação normal, e nenhum consumidor pediu um `claude-*`: o
`sdk` foi para o combo padrão e o `generate_session_title` para o modelo do papel Haiku. O bloco só faz falta
num caso, e é bem específico:

| Cenário | Precisa de override? |
| :--- | :--- |
| Operação normal, sem `--model` | Não |
| Alias curto (`--model opus`, `sonnet`, `fable`) | Não, a CLI resolve pelo papel |
| Combo próprio (`--model claudegravity-fallback`) | Não |
| **Identificador da geração corrente pinado antes** (`claude-opus-5[1m]`) | **Sim** |

O caso que sobra é o de um `settings.local.json` que ficou apontando para um modelo escolhido no menu
antes de você trocar a configuração. Para isso bastam **três entradas**, uma por família:

```json
"modelOverrides": {
  "claude-fable-5-1": "ag/gemini-pro-agent",
  "claude-opus-5":    "ag/gemini-3.8-flash-high",
  "claude-sonnet-5":  "ag/gemini-3.7-flash-high"
}
```

**Não é preciso duplicar com o sufixo de janela.** A CLI normaliza o identificador antes de consultar
o mapa, e o próprio binário trata o sufixo como opcional no padrão que usa para reconhecer modelos:

```text
(?:[-@]\d{8})?(?:-v\d+(?::\d+)?)?(?:\[[12]m\])?$
```

Verificamos na prática: com apenas `claude-opus-5` declarado, `--model claude-opus-5[1m]` resolve
normalmente. Uma entrada por família dá conta das duas formas.

Repare que o destino de cada linha é o **mesmo modelo do papel correspondente**: o pin antigo passa a
resolver exatamente para onde o papel já apontava, sem introduzir um terceiro comportamento. Se você
preferir que um pin esquecido caia na cascata em vez de num modelo único, troque o destino por
`claudegravity-fallback`  -  é a mesma escolha entre previsibilidade e resiliência que a seção
[Modelo Individual ou Combo](#modelo-individual-ou-combo-e-a-escolha-do-padrão) detalha. E, quando a CLI
ganhar uma geração nova, é uma linha por família  -  ou simplesmente apague o pin e deixe os papéis
trabalharem.

## Quando Parece Desconexão, mas é Outra Coisa

Duas falhas diferentes chegam ao terminal com a mesma cara  -  `API Error: 503`  -  e a confusão custa
tempo. Vale separar, porque a correção de uma não serve para a outra.

### Falha 1 - a cota da família estourou

A cota do Antigravity é contabilizada **por família de modelo**, não pela conta inteira. Quando o teto
do Gemini é atingido, o gateway registra:

```text
[AG_QUOTA] CACHE_BLOCK gemini-3.8-flash-high - skip upstream until 23:47:37
[AUTH] antigravity | all 1 accounts locked for gemini-3.8-flash-high (reset after 2h)
```

Uma verificação modelo a modelo durante um desses bloqueios mostra o alcance real:

| Modelo | Estado durante o bloqueio |
| :--- | :--- |
| `ag/gemini-3.8-flash-high` · `3.7` · `3.6` · `pro-agent` | **503** |
| `ag/claude-opus-4-6-thinking` | OK, 3,8s |
| `ag/claude-sonnet-4-6` | OK, 1,4s |
| `ag/gpt-oss-120b-medium` | OK, 0,8s |

A conta continua saudável: apenas uma família ficou indisponível. Quem estivesse num `ag/gemini-*`
via a sessão morrer a cada mensagem; quem estivesse num combo seguiu trabalhando, porque a cascata
desce até achar quem responda:

```text
[COMBO] Trying model 1/5: ag/gemini-3.8-flash-high  -> failed {"status":503}
[COMBO] Trying model 2/5: ag/gemini-3.7-flash-high  -> failed {"status":503}
[COMBO] Trying model 3/5: ag/gemini-3.6-flash-high  -> failed {"status":503}
[COMBO] Trying model 4/5: ag/claude-sonnet-4-6      -> succeeded
```

Os três saltos custaram menos de um segundo no total, porque o gateway guarda o bloqueio em cache e
nem tenta o upstream  -  a resposta chegou em 1,97s. Este é o trade-off que a seção
[Modelo Individual ou Combo](#modelo-individual-ou-combo-e-a-escolha-do-padrão) resolve.

> **Round-Robin não resolve este caso com uma conta só.** Ele distribui chamadas entre conexões
> distintas, e a cota é contabilizada pelo Google por conta. Cadastrar a mesma conta duas vezes cria
> duas entradas no gateway, mas o teto continua sendo um. Só aliviam de verdade: uma segunda conta
> Google com assinatura própria, ou provedores fora do Antigravity, que é o caminho do
> [Artigo 0003](../../0003_fallback_modelos_gratuitos_9router/article/ARTICLE.md).

### Falha 2 - a credencial foi gravada em formato que quebra a validação

Esta é sutil e se manifesta como desconexão espontânea depois de cerca de uma hora de uso.

O token OAuth dura aproximadamente uma hora. Quando se aproxima do fim, o próprio 9Router renova  -  e,
ao gravar o resultado, escreve o campo `expiresAt` como **string ISO** em vez de epoch em
milissegundos:

```text
expiresAt valor : "2026-09-11T02:05:25.091Z"
expiresAt tipo  : string
comparacao > now: false
```

`Number("2026-09-11T02:05:25.091Z")` é `NaN`, e `NaN > Date.now()` é sempre falso. A partir dali a
credencial é tratada como vencida mesmo estando ativa, com `isActive: 1`, `testStatus: active` e
`backoffLevel: 0` no banco. Nada no painel indica problema.

A correção é preventiva: renovar **antes** do gateway precisar renovar, gravando o campo como número.
É o que o `src/keep_connected.py` faz.

```bash
# Confere e corrige, se necessario
python3 src/keep_connected.py

# Mantem valida enquanto voce trabalha, conferindo a cada 5 minutos
python3 src/keep_connected.py --daemon
```

Ele só age quando precisa. Com o token novo, sai sem gastar chamada:

```text
[=] Credencial válida por mais 58 min. Nada a fazer.
```

E, diante do campo corrompido, reconhece a causa pelo nome:

```text
[*] Renovando: expiresAt gravado como texto pelo gateway.
[+] Credencial renovada. Válida por mais 59 min.
```

Deixe o modo `--daemon` rodando num terminal à parte durante sessões longas, ou utilize a solução definitiva: o container dedicado `9RTKSync`.

### Auto-Renovação Definitiva com o Container router-sync

Para que a sincronização e renovação de credenciais não dependa de terminais abertos ou de intervenções manuais, o `docker-compose.yml` deste projeto provisiona o serviço oficial `9rtksync` com o container `router-sync` (baseado no repositório [9RTKSync](https://github.com/pathbit/9RTKSync) · *9Router Universal Token & Connection Synchronizer*):

1. **Imagem OCI e Isolamento em Virtual Environment:** Baseado na imagem oficial `ghcr.io/pathbit/9rtksync:latest`, executa em Python 3.14 Alpine com ambiente virtual dedicado (`/opt/venv`), consumindo apenas ~18 MB de RAM e 0% de CPU.
2. **Isolamento de Credenciais e Auto-Cura Universal:** O container monta o banco SQLite compartilhado (`9router_data:/app/data`) e o diretório home do usuário host (`${HOME}:/root/host:ro`) em modo estritamente somente-leitura (`:ro`), descobrindo e sincronizando credenciais de múltiplos provedores locais (Google Antigravity, Claude, GitHub Copilot, Codex, Kiro, Codeium), curando divergências de datas e renovando tokens preventivamente 15 minutos antes da expiração.
3. **Dashboard Web em Tempo Real:** Servidor HTTP embutido expondo a interface web e endpoints de monitoramento em `http://localhost:9190` e `http://localhost:9190/healthz`. A interface exige autenticação: informe as variáveis `DASHBOARD_USER` e `DASHBOARD_PASSWORD` no `.env` — o `docker compose` recusa subir sem a senha, justamente para que nenhuma credencial de fábrica circule em arquivo de exemplo. O endpoint `/healthz` continua aberto, para o healthcheck do container.

Para acompanhar a operação contínua do guardião no terminal:

```bash
docker logs -f router-sync
```

Com essa arquitetura, você pode desenvolver ininterruptamente no [9Router](https://github.com/decolua/9router) sem se preocupar com sessões derrubadas ou tokens expirados.

---

### Modelo Individual ou Combo e a Escolha do Padrão

A falha de cota da seção anterior deixa uma decisão em aberto, e ela vale para o `"model"` e para os
quatro papéis: apontar cada um para um **modelo individual** ou para um **combo**?

Este artigo provisiona dois combos, que ficam no seletor ao lado dos modelos individuais:

| Combo | Cascata | Serve para |
| :--- | :--- | :--- |
| `claudegravity-fallback` | Gemini 3.8 → 3.7 → 3.6 → Sonnet 4.6 → GPT-OSS 120B | Prefere Gemini e cai para os demais |
| `claudegravity-thinking` | Opus 4.6 Thinking → Sonnet 4.6 → Gemini 3.8 → GPT-OSS 120B | Raciocínio denso, e **não depende da cota do Gemini** |

E os arquivos `.example` apontam o padrão e os quatro papéis para **modelos individuais**. É uma
escolha deliberada, com uma contrapartida conhecida:

| | Modelo individual (`ag/gemini-3.8-flash-high`) | Combo (`claudegravity-fallback`) |
| :--- | :--- | :--- |
| **Consumo** | Previsível: você sabe qual modelo atendeu cada chamada | Varia com o nível que respondeu |
| **Cota estourada** | Para de responder até o teto liberar | Desce a cascata em menos de 1s |
| **Depuração** | Direta: um identificador, um provedor | Exige ler o log do gateway para saber quem atendeu |
| **Papel Haiku** | Acionado em toda sessão; é o primeiro a denunciar bloqueio | Absorve o bloqueio silenciosamente |

O papel Haiku merece atenção redobrada nos dois arranjos, porque é o mais exercitado: a CLI o aciona
em **toda sessão** para gerar o título da conversa. Se a família dele estourar, você percebe antes de
qualquer outra coisa.

> **Regra prática:** modelo individual dá previsibilidade de consumo e é o padrão deste artigo. Combo
> dá resiliência e é o que você aciona  -  pelo `/model`, por `--model`, ou apontando os papéis para
> ele  -  no dia em que a cota de uma família estourar. Os dois arranjos estão provisionados e
> testados; a escolha é sua, e pode mudar no meio do caminho.

---

## Tirando os Modelos da Anthropic do Menu

Mapear identificadores um a um resolve o sintoma, mas envelhece: a cada geração nova de modelos a CLI
passa a emitir identificadores que o seu mapa não tem, e o erro `There's an issue with the selected
model` volta. Há uma saída melhor, e ela deixa o menu `/model` mostrando **apenas os seus modelos**.

São duas chaves do `modelPicker`:

- **`replaceBuiltInOptions: true`** substitui a lista nativa em vez de somar a ela. O menu passa a
  exibir só o que você declarou.
- **`behavesAs`** resolve o outro lado. A CLI precisa saber o que esperar de um identificador que ela
  não conhece, e a própria mensagem de erro diz como informar: *"isn't described by this version's
  model catalog; update Claude Code, or map it with `behavesAs` on a modelPicker row"*. O valor é o
  **ID de um modelo que a CLI conhece**, e serve de referência de capacidade.

Um recorte das nove linhas declaradas nos arquivos deste artigo  -  o bloco completo está na seção
[Estrutura do `settings.json.example`](#estrutura-do-settingsjsonexample):

```json
{
  "modelPicker": {
    "replaceBuiltInOptions": true,
    "options": [
      {
        "model": "ag/gemini-3.8-flash-high",
        "label": "Gemini 3.8 Flash High",
        "description": "Primario: raciocinio alto, 1M de contexto",
        "behavesAs": "claude-opus-4-8"
      },
      {
        "model": "ag/gemini-3.6-flash-high",
        "label": "Gemini 3.6 Flash High",
        "description": "Latencia minima, alta frequencia",
        "behavesAs": "claude-haiku-4-5-20251001"
      },
      {
        "model": "claudegravity-fallback",
        "label": "ClaudeGravity Resiliente (combo)",
        "description": "5 niveis. Use quando a cota de uma familia estourar",
        "behavesAs": "claude-opus-4-8"
      }
    ]
  }
}
```

Depois disso o leitor nunca mais vê "Opus 5" ou "Fable 5.1" no menu: vê "Gemini 3.8 Flash High",
"ClaudeGravity Resiliente (combo)" e as demais linhas que você declarou. O `behavesAs` fica nos
bastidores, apenas dizendo à CLI de qual modelo conhecido cada entrada tem porte  -  repare que ele
acompanha a capacidade real, e não o papel: a linha do 3.6 se descreve como Haiku porque é isso que
ela é.

> **Por que isso substitui o `modelOverrides`:** o override reage a um identificador que a CLI já
> escolheu; o picker define quais identificadores sequer existem. Com a lista nativa substituída e os
> quatro papéis declarados, nada mais no harness pede um nome da Anthropic  -  verificamos removendo
> o bloco por completo e reexecutando as tarefas, inclusive com subagente: **nenhuma falhou, e nenhum
> consumidor pediu um `claude-*`**. Por isso os arquivos deste artigo mantêm apenas as três entradas
> de pin da seção anterior, e nada além disso.

Valide com `claude doctor`  -  ele aceita ou recusa cada linha do picker sem abrir sessão.

---

## Referência Completa e Onde Cada Configuração Mora

Esta seção existe porque a pergunta mais frequente não é *o que* configurar, e sim **em qual arquivo**.
O Claude Code lê várias camadas, e o aplicativo de janela lê outra. Quem não conhece o mapa passa horas
editando o arquivo errado.

### As camadas de settings, da mais fraca para a mais forte

| Camada | Arquivo | Alcance | Observação |
| :--- | :--- | :--- | :--- |
| **Usuário** | `~/.claude/settings.json` | Toda sessão da sua máquina | O ponto de entrada mais amplo. É onde o aplicativo de janela encontra a configuração |
| **Projeto** | `<repo>/.claude/settings.json` | Só dentro daquele repositório | Versionável, compartilhável com o time |
| **Local** | `<repo>/.claude/settings.local.json` | Só na sua máquina, naquele repositório | **Tem precedência**, e fica fora do git |

A camada mais forte vence. Colocar o gateway em `~/.claude/settings.json` faz ele valer em tudo;
colocar em `.claude/settings.local.json` limita ao repositório e à sua máquina.

O que determina quais camadas entram na conta é o **diretório em que a sessão roda**. Uma sessão de
terminal aberta dentro de um repositório soma as três; uma janela de conversa do aplicativo, que não
tem repositório, enxerga só a de usuário. É a mesma regra, aplicada a contextos diferentes  -  e é o
que a seção [Configurando o Aplicativo de Janela e o Cowork](#configurando-o-aplicativo-de-janela-e-o-cowork)
detalha.

> **Um arquivo que não é camada de settings.** O `claude_desktop_config.json` do aplicativo (caminho
> na seção citada acima) guarda **servidores MCP e preferências da interface**. Ele não participa
> desta precedência, não aceita `model`, `env` nem `permissions`, e editá-lo esperando trocar de
> modelo não produz efeito nenhum.

### Todas as variáveis de ambiente que importam

Vão dentro do bloco `"env"` de qualquer camada de settings, ou exportadas no shell.

| Variável | Para que serve |
| :--- | :--- |
| `ANTHROPIC_BASE_URL` | Endereço do gateway. É a chave de tudo: aponta o harness para fora da API da Anthropic |
| `ANTHROPIC_API_KEY` | Credencial que o gateway exige. Gerada localmente, nunca a da Anthropic |
| `ANTHROPIC_AUTH_TOKEN` | Alternativa ao anterior, aceita pelos mesmos caminhos |
| `ANTHROPIC_MODEL` | Modelo do laço principal da sessão |
| `ANTHROPIC_DEFAULT_MODEL` | Modelo aplicado quando nada mais foi escolhido. Equivale ao `"model"` do `settings.json` |
| `ANTHROPIC_DEFAULT_FABLE_MODEL` | Papel Fable: o mais capaz, para o que a CLI considerar mais difícil |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Papel Opus: trabalho complexo e **todo subagente despachado** |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Papel Sonnet: a maior parte das tarefas |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Papel Haiku: alta frequência. Acionado em **toda sessão** |
| `ANTHROPIC_SMALL_FAST_MODEL` | Operações rápidas internas, quando declarado |
| `ANTHROPIC_CUSTOM_MODEL_OPTION` | Entrada extra no menu, com `_NAME` e `_DESCRIPTION` |
| `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT` | Desliga a checagem de janela por modelo. **Necessária** com modelos não-Anthropic |

Os quatro papéis aceitam ainda três sufixos, úteis justamente porque o modelo apontado é de gateway e
a CLI não tem como descrevê-lo sozinha:

| Sufixo | Efeito |
| :--- | :--- |
| `_NAME` | Rótulo exibido no lugar do nome do papel  -  por exemplo, `ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME="Gemini 3.6 Flash High"` |
| `_DESCRIPTION` | Texto de apoio ao lado do rótulo |
| `_SUPPORTED_CAPABILITIES` | Declara o que aquele modelo aceita, no mesmo papel que o `behavesAs` cumpre no `modelPicker` |

São o caminho equivalente ao `modelPicker` para quem prefere configurar por ambiente  -  em um
contêiner de CI, por exemplo  -  em vez de por arquivo.

> **Confira antes de adotar qualquer variável**, e confira com correspondência exata:
>
> ```bash
> strings -a "$(which claude)" | grep -oE '\bCLAUDE_CODE_[A-Z0-9_]+\b' | sort -u
> ```
>
> O `-oE` com `\b` é o que importa. Um `grep -c CLAUDE_CODE_EXPERIMENTAL` devolve 8 ocorrências e
> parece confirmar a variável, mas todas são de `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`  -  um nome
> maior que a contém. Caímos exatamente nessa armadilha: publicamos `CLAUDE_CODE_EXPERIMENTAL`,
> `CLAUDE_CODE_ENABLE_LOOPS`, `_ADVISOR` e `_GOAL` como se existissem. Nenhuma existe. Eram
> configuração decorativa, e o leitor não teria como perceber.

### Todas as chaves de `settings.json`

| Chave | Efeito |
| :--- | :--- |
| `model` | Modelo padrão da sessão |
| `advisorModel` | Modelo do revisor. Precisa ser **ao menos tão capaz** quanto o principal |
| `modelOverrides` | Traduz um identificador que a CLI pediu para um que o gateway serve |
| `modelPicker.options` | As linhas do menu `/model`: `{ model, label, description, behavesAs }` |
| `modelPicker.replaceBuiltInOptions` | `true` substitui a lista nativa; `false` soma a ela |
| `permissions.defaultMode` | `bypassPermissions` para autonomia total |
| `permissions.allow` | Ferramentas liberadas. Curinga solto (`*`, `mcp__*`) é **recusado** |
| `permissions.deny` | Bloqueios. Aceita curinga em qualquer posição, e vence sobre tudo |
| `skipDangerousModePermissionPrompt` | Remove a confirmação do modo irrestrito |
| `includeCoAuthoredBy` | `false` impede a assinatura de coautoria nos commits |
| `env` | O bloco de variáveis da tabela anterior |

Valide qualquer combinação com `claude doctor`, que aponta chave inválida sem abrir sessão.

---

## Configurando o Aplicativo de Janela e o Cowork

Tudo até aqui vale para o terminal. O aplicativo  -  e o **Cowork**, que roda dentro dele  -  tem uma
disposição própria, e a boa notícia é que o ponto de entrada é o mesmo.

### O aplicativo embute o mesmo Claude Code

Vale começar desfazendo uma suposição fácil de fazer  -  nós fizemos. O aplicativo não reimplementa o
harness: ele **empacota a mesma CLI**, numa pasta própria.

```bash
~/Library/Application Support/Claude/claude-code-vm/<versão>/claude
```

Na máquina em que este artigo foi escrito, a versão ali dentro e a do terminal eram idênticas
(`2.1.266`), e o binário embutido reconhece exatamente as mesmas chaves  -  `modelPicker`,
`replaceBuiltInOptions`, `behavesAs`, `advisorModel`, `modelOverrides`  -  além dos dois caminhos de
projeto, `.claude/settings.json` e `.claude/settings.local.json`.

A consequência é que **não existe um conjunto de regras diferente para o app**. O que muda é o
diretório em que cada sessão roda:

| Contexto | Camadas que valem |
| :--- | :--- |
| Terminal dentro de um repositório | Usuário + projeto + local |
| Janela de conversa do aplicativo | Só a de usuário  -  não há repositório |
| Tarefa do Cowork sobre uma pasta | Usuário + as camadas de projeto **daquela pasta** |

A terceira linha é a que costuma surpreender: ao apontar o Cowork para um repositório, o
`.claude/settings.local.json` dele volta a valer, com a precedência de sempre. As pastas liberadas
para esse modo ficam registradas em `preferences.localAgentModeTrustedFolders`.

### O que vai em cada lugar

```bash
~/.claude/settings.json                                    # modelo, papéis, env, permissões
~/Library/Application Support/Claude/claude_desktop_config.json   # servidores MCP e preferências
~/Library/Application Support/Claude/cowork-enabled-cli-ops.json  # conta dona das operações do Cowork
```

> **Fora do macOS.** Os caminhos acima são os do macOS. No Windows o diretório equivalente é
> `%APPDATA%\Claude\`, e no Linux, `~/.config/Claude/`. O `~/.claude/settings.json` é o mesmo nos três
> sistemas  -  e, por ser o arquivo que carrega modelo, papéis e `env`, é também o único que você
> precisa editar para apontar o app ao gateway.

Como a janela de conversa não tem repositório, a configuração vai no **arquivo de usuário**:

```json
{
  "model": "ag/gemini-3.8-flash-high",
  "advisorModel": "ag/gemini-pro-agent",
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:20128",
    "ANTHROPIC_API_KEY": "sk-sua-chave-do-9router",
    "ANTHROPIC_DEFAULT_FABLE_MODEL": "ag/gemini-pro-agent",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "ag/gemini-3.8-flash-high",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "ag/gemini-3.7-flash-high",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "ag/gemini-3.6-flash-high"
  }
}
```

### O seletor de modelo do aplicativo é outro

Uma diferença que só aparece ao inspecionar a janela: o aplicativo tem **seu próprio controle de
modelo**, na barra inferior, e ele não é o menu `/model` do terminal. A árvore de acessibilidade
mostra o elemento assim:

```text
AXPopUpButton (Modelo: Fable 5.1  Máx  3× ou mais de uso)
```

Abrindo esse controle, a hierarquia dos quatro papéis aparece escrita, com a descrição de cada um:

![Seletor de modelo do aplicativo, com os quatro papéis](../assets/13a_app_seletor_modelo.png)

> **Figura 13a:** O seletor de modelo do aplicativo. É a própria interface declarando para que serve
> cada papel  -  a referência mais direta na hora de decidir qual Gemini mapear para qual.

| Opção | Descrição no aplicativo |
| :--- | :--- |
| **Fable 5.1** | Para seus desafios mais difíceis |
| **Opus 5** | Para tarefas complexas |
| **Sonnet 5** | Mais eficiente para tarefas do dia a dia |
| **Haiku 4.5** | Mais rápido para respostas rápidas |
| **Esforço** | `Máx`, com submenu próprio |
| **Mais modelos** | Submenu com gerações anteriores da Anthropic |

É a mesma ordem que a CLI declara internamente (*Fable for the hardest problems, Opus for complex
work, Sonnet for most tasks, Haiku for quick questions*), agora confirmada na interface. Se você
estava em dúvida sobre qual papel mapear para qual Gemini, esta tela é a referência: ela diz, com
todas as letras, para que serve cada um.

Duas consequências práticas:

- **A escolha feita nesse controle vale para a janela**, e é independente do menu `/model` do
  terminal. Se mudou o modelo no app e continua vendo o comportamento antigo no terminal, os dois
  estão em camadas diferentes.
- **O multiplicador de consumo só aparece aqui.** O rótulo `3× ou mais de uso` avisa que aquele modelo
  gasta cota numa proporção que o `--model` na linha de comando não anuncia. Vale olhar antes de deixar
  uma tarefa longa rodando.

#### O seletor do aplicativo ignora o `modelPicker`

Esta parte nós medimos, porque a suposição natural  -  a de que o `modelPicker` do arquivo de usuário
alimentaria o submenu **Mais modelos**  -  está errada.

O teste: declaramos em `~/.claude/settings.json` um `modelPicker` com `replaceBuiltInOptions: true` e
uma única entrada, rotulada de forma inconfundível, apontando para um modelo do gateway. Reiniciamos
o aplicativo e abrimos o seletor.

![Submenu Mais modelos do aplicativo](../assets/13b_app_submenu_mais_modelos.png)

> **Figura 13b:** O submenu **Mais modelos** com o `modelPicker` declarado e `replaceBuiltInOptions`
> ligado. A entrada de teste não aparece, e a lista nativa continua intacta.

O resultado foi **nenhuma mudança**: os quatro papéis continuaram nativos, o submenu continuou
listando apenas gerações anteriores da Anthropic (Fable 5, Opus 4.8, 4.7, 4.6 e Sonnet 4.6), e a
entrada declarada não apareceu em lugar nenhum. O `replaceBuiltInOptions` não substituiu coisa
alguma.

A conclusão prática é direta:

| Caminho | Terminal | Aplicativo |
| :--- | :--- | :--- |
| `env` no arquivo de usuário | Funciona | **Funciona**  -  é o caminho para apontar o app ao gateway |
| Papéis `ANTHROPIC_DEFAULT_*_MODEL` | Funciona | **Funciona**, pelo mesmo bloco `env` |
| `modelPicker` / `replaceBuiltInOptions` | Funciona | **Ignorado pelo seletor da janela** |

Ou seja: no app você não escolhe o modelo do gateway pelo menu, você o **define** pelo `env`. O
seletor da janela continua exibindo os nomes da Anthropic, e o que responde do outro lado é o que
você mapeou nos papéis  -  o rótulo na tela deixa de corresponder ao modelo real, e vale ter isso em
mente antes de estranhar.


### Três cuidados específicos do app

1. **O gateway precisa estar de pé antes de abrir a janela.** O terminal falha com uma mensagem clara;
   o aplicativo tende a mostrar erro genérico. Suba o container primeiro.
2. **`localhost` precisa ser alcançável pelo app.** Como o `docker-compose.yml` publica em
   `127.0.0.1:20128`, e o app roda na mesma máquina, funciona. Se você mudar para outra interface,
   ajuste o `ANTHROPIC_BASE_URL` de acordo.
3. **Reinicie o aplicativo depois de editar.** Ele lê a configuração na inicialização, e não recarrega
   sozinho  -  o mesmo comportamento que o Antigravity IDE tem no [Artigo 0001](../../0001_antigravity_acesso_total_irrestrito/article/ARTICLE.md).

### O que o `claude_desktop_config.json` controla

Ele guarda `mcpServers` e um bloco `preferences`. Modelos e credenciais **não** moram ali: continuam
no arquivo de usuário. As chaves que importam para quem opera com gateway são as de autonomia e as do
Cowork:

| Chave em `preferences` | Efeito |
| :--- | :--- |
| `bypassPermissionsModeEnabled` | O equivalente, na janela, ao `--dangerously-skip-permissions` do terminal |
| `dispatchCodeTasksPermissionMode` | Modo de permissão aplicado às tarefas de código despachadas |
| `localAgentModeTrustedFolders` | As pastas que o Cowork pode operar  -  e, portanto, de onde ele lê settings de projeto |
| `coworkPreferredBrowser` · `coworkBrowserToolsEnabled` | Navegador usado pelas ferramentas de browser do Cowork |
| `coworkWebSearchEnabled` | Liga a busca na web durante as tarefas |
| `coworkScheduledTasksEnabled` | Habilita tarefas agendadas |
| `coworkModelAutoFallbackByAccount` | Troca automática de modelo por conta  -  vale conhecer, porque é um fallback do app que convive com o do gateway |

A última merece um parágrafo. Existem **duas camadas de fallback** quando você opera o app com
gateway: a do 9Router, que desce a cascata do combo, e a do próprio aplicativo. Elas não se enxergam.
Se uma tarefa trocar de modelo sem explicação aparente no log do gateway, é aqui que se procura.

---

## Isto Não É Sobre o Antigravity

Vale explicitar, porque o artigo inteiro usa um provedor como exemplo e isso pode dar a impressão
errada.

Nada do que foi montado aqui é específico do Google. A arquitetura tem três peças, e só a do meio
conhece o provedor:

| Peça | Depende do provedor? |
| :--- | :--- |
| **Harness** (Claude Code, terminal ou app) | Não. Ele só fala a Messages API |
| **Gateway** (9Router) | Sim. É ele que traduz protocolo e guarda credenciais |
| **Provedor** (Antigravity, Groq, Mistral, Ollama…) | É o que se troca |

O harness não sabe quem está do outro lado. Ele envia uma requisição no formato da Anthropic para o
endereço de `ANTHROPIC_BASE_URL` e recebe uma resposta no mesmo formato. Trocar de provedor é trocar
uma conexão no gateway e um identificador na configuração  -  nenhuma linha do harness muda.

É por isso que o [Artigo 0003](../../0003_fallback_modelos_gratuitos_9router/article/ARTICLE.md) mistura
cinco provedores diferentes na mesma cascata sem nenhuma adaptação: Antigravity, OpenRouter, Groq,
Mistral e um Ollama rodando na própria máquina convivem atrás do mesmo endereço.

O mesmo raciocínio vale para o futuro. Quando surgir um motor novo, o caminho é o mesmo: uma conexão
no gateway, um identificador na configuração, e o `behavesAs` dizendo à CLI de qual modelo conhecido
ele tem porte. O harness continua sem saber, e sem precisar saber.

---

## O Advisor, uma Segunda Opinião Durante a Sessão

O Claude Code expõe uma ferramenta de **advisor**, descrita internamente como *"an advisor tool
backed by a stronger reviewer model"*  -  um revisor acionado sob demanda para conferir decisões do
laço principal. A configuração é a chave `advisorModel` no `settings.json`.

A regra que a própria CLI impõe é a parte importante: **o advisor precisa ser pelo menos tão capaz
quanto o modelo principal**. Não faz sentido pedir segunda opinião a quem sabe menos. Nos arquivos
`.example` deste artigo o advisor aponta para o `ag/gemini-pro-agent`, o mesmo do papel Fable,
enquanto o principal fica no `ag/gemini-3.8-flash-high`.

> **Uma ressalva honesta sobre o advisor com modelo de gateway.** A CLI decide a capacidade relativa
> pelo campo `advisor_rank`, que existe apenas nas entradas do **catálogo dela**:
>
> ```text
> claude-haiku-4-5 … advisor_rank:1
> claude-sonnet-5  … advisor_rank:2
> claude-opus-4-0  … advisor_rank:3
> ```
>
> Um identificador `ag/*` não tem esse campo, então a comparação de capacidade não encontra referência.
> Por isso os `.example` também declaram `CLAUDE_CODE_ENABLE_EXPERIMENTAL_ADVISOR_TOOL=1`, que existe
> no binário e destrava a ferramenta. Confirmamos que a variável e o campo existem, e que a chave
> `advisorModel` é aceita sem reclamação  -  **não confirmamos** a ativação completa do advisor com um
> modelo de gateway, porque não encontramos um sinal observável que provasse a chamada. Trate esta
> parte como configuração preparada, não como comportamento medido.

```json
{
  "model": "ag/gemini-3.8-flash-high",
  "advisorModel": "ag/gemini-pro-agent"
}
```

Repare que essa regra de capacidade é verificável **entre modelos do catálogo da Anthropic**, onde o
`advisor_rank` existe e pode ser comparado. Com dois identificadores `ag/*` não há o que comparar, e a
CLI aceita a chave sem reclamar  -  inclusive numa combinação sem sentido, com o advisor mais fraco
que o principal. A responsabilidade de escolher um revisor à altura passa a ser sua: aponte o
`advisorModel` para o modelo mais denso que sua conta atende, que aqui é o `ag/gemini-pro-agent`.

---

## Tarefas Longas com `/goal`, `/loop` e Trabalho com Subagentes

Esta é a dúvida que mais aparece: recursos de longo prazo dependem de algo proprietário da Anthropic,
ou funcionam com qualquer modelo servido pelo gateway?

A resposta curta é que **a orquestração é local**. `/goal` e `/loop` são lógica da CLI: ela mantém a
condição, decide quando reentrar e agenda o próximo despertar. O modelo é chamado a cada iteração
como em qualquer outra requisição. Não há endpoint especial, nem recurso do servidor de inferência
que precise existir do outro lado.

O que **é** exigido do modelo é outra coisa, e essa sim elimina candidatos:

- **Uso de ferramenta confiável.** Uma tarefa longa é uma sequência de leituras, edições e comandos.
  Um modelo que responde texto solto em vez de chamar a ferramenta trava o ciclo sem levantar erro.
- **Aderência à instrução ao longo de muitos turnos.** Não basta acertar o primeiro passo.
- **Janela de contexto que aguente o acúmulo.** Os Gemini do Antigravity entregam 1M de tokens, o que
  cobre folgadamente esse ponto.

Foi exatamente aqui que o `arsenal-offline` do [Artigo 0003](../../0003_fallback_modelos_gratuitos_9router/article/ARTICLE.md)
reprovou: ele responde ao gateway, mas não opera o harness. Um modelo assim serve de rede de
segurança para a cascata não cair, e **nunca** deve ocupar um papel  -  numa tarefa longa ele falha
em silêncio, com `exit code 0`, e você só descobre no fim.

Para subagentes vale o mapa da seção sobre os quatro papéis: quem os atende é o **papel Opus**. Se a sua rotina
despacha subagentes com frequência, é esse papel que domina o consumo, e é nele que a escolha entre
uma Flash e uma Pro tem o maior impacto na cota.

---

## Executando o ClaudeGravity no Terminal

Com as configurações salvas, você pode operar em dois modos de trabalho:

### Modo 1 - ClaudeGravity Principal (Velocidade e Raciocínio Máximo com Gemini 3.8 Flash High)
Neste modo de medição direta, o Claude Code executa contra o motor Gemini 3.8 Flash High conectado via Antigravity Pro, desfrutando de 1 milhão de tokens de contexto e custo zero.

```bash
# macOS e Linux (bash / zsh)
export ANTHROPIC_BASE_URL="http://localhost:20128"
export ANTHROPIC_API_KEY="sk-sua-chave-do-9router"
claude --dangerously-skip-permissions --model ag/gemini-3.8-flash-high

# Windows (PowerShell)
$env:ANTHROPIC_BASE_URL="http://localhost:20128"
$env:ANTHROPIC_API_KEY="sk-sua-chave-do-9router"
claude --dangerously-skip-permissions --model ag/gemini-3.8-flash-high

# Ou via launcher Python automatizado (qualquer sistema operacional)
python3 src/claudegravity.py
```

> **Nota sobre o launcher:** o `claudegravity.py` sincroniza as credenciais do Antigravity, garante os dois combos no gateway e, antes de entregar o controle ao Claude Code, muda o diretório de trabalho para `examples/`. Isso mantém a sessão dentro do sandbox de testes do artigo, com as políticas de `examples/.claude/` já aplicadas. Para trabalhar no seu próprio repositório, chame o `claude` diretamente com as variáveis de ambiente acima.

### Modo 2 - ClaudeGravity com Fallback Gratuito (Alta Disponibilidade Ininterrupta)
Neste modo resiliente, você utiliza o combo virtual configurado no 9Router. Se o Gemini 3.8 atingir qualquer teto de cota momentâneo (HTTP 429), o gateway percorre a cascata até Gemini 3.7, 3.6, Sonnet 4.6 e GPT-OSS 120B sem interromper o raciocínio nem fechar a sessão. A troca não é instantânea: o gateway aplica até 3 retentativas com backoff exponencial antes de descer um nível  -  em nossos testes, o salto completo levou cerca de 3 segundos. O que importa é que a sessão do Claude Code não cai e o contexto é preservado.

![Combos Virtuais no 9Router](../assets/10_9router_combos.png)

> **Figura 10:** Visualização dos combos virtuais configurados no painel do 9Router.

```bash
# macOS e Linux (bash / zsh)
export ANTHROPIC_BASE_URL="http://localhost:20128"
export ANTHROPIC_API_KEY="sk-sua-chave-do-9router"
claude --dangerously-skip-permissions --model claudegravity-fallback

# Windows (PowerShell)
$env:ANTHROPIC_BASE_URL="http://localhost:20128"
$env:ANTHROPIC_API_KEY="sk-sua-chave-do-9router"
claude --dangerously-skip-permissions --model claudegravity-fallback

# Ou via launcher Python com a flag de modelo (qualquer sistema operacional)
python3 src/claudegravity.py --model claudegravity-fallback
```

Veja a evidência da execução dos testes de integração no terminal comprovando que o gateway responde com sucesso ao Gemini 3.8 e ao fallback resiliente:

![Validação de Inferência do ClaudeGravity no Terminal](../assets/11_claude_gravity_terminal.png)

> **Figura 11:** Validação da suíte de integração e inferência em tempo real no terminal através do script `test_gateway.py`, comprovando que o modelo Gemini 3.8 Flash High e o combo `claudegravity-fallback` respondem com status HTTP 200 e mensagem operacional.

---

## Comparativo entre Claude Nativo, DeepClaude e ClaudeGravity

Para posicionar claramente o valor de engenharia do ClaudeGravity em relação às abordagens existentes no mercado:

| Recurso | Claude Code Nativo | DeepClaude | ClaudeGravity (Este Artigo) |
| :--- | :--- | :--- | :--- |
| **Harness CLI** | Claude Code | Claude Code | **Claude Code** |
| **Modelo Principal** | Claude 3.7 / 3.5 Sonnet | DeepSeek R1 / V3 | **Gemini 3.8 Flash (High Reasoning)** |
| **Modelos Auxiliares** | Claude Haiku | Nenhum | **Gemini 3.7, 3.6, 3.1 Pro, GPT-OSS 120B** |
| **Janela de Contexto** | 200k tokens | 64k a 128k tokens | **1.000.000 tokens (1M)** |
| **Custo de Inferência** | Faturado por token ($3 a $15 / 1M) | API DeepSeek ou Router ($0.14 a $2.19 / 1M) | **$0 extra** (incluído na conta Google AI Pro) |
| **Dependência de API Paga** | Sim (Anthropic Console) | Sim (DeepSeek API Key) | **Não** (Gateway via OAuth Antigravity) |
| **Token Saver de Ferramentas**| Não | Depende do proxy | **Sim (RTK Token Saver nativo, ativo por padrão)** |
| **Multi-Conta & Fallback** | Manual | Manual | **Automático (Round-Robin no 9Router)** |
| **Renovação de Credenciais** | Manual (API Key estática) | Manual | **Automática via OAuth em segundo plano** |

---

## Segurança, Termos de Uso, Gestão de Risco e Arquitetura Multi-Usuário

Ao explorar integrações avançadas baseadas em sessões OAuth e gateways locais, uma das principais preocupações de qualquer desenvolvedor ou líder técnico é a **segurança da conta** e a **conformidade com os termos de serviço (ToS)** dos provedores de IA.

Nesta seção, analisamos com total transparência técnica o que há por trás dos avisos de risco, como o Google monitora essas conexões e como dimensionar a solução para uso individual ou em equipe.

### 1. Desmistificando o Aviso `RISK_NOTICE`

Ao navegar no painel do 9Router ou inspecionar o código do catálogo de provedores, você pode encontrar a seguinte mensagem:

> *"⚠️ Risk Notice: This provider uses a subscription/OAuth session not officially licensed for proxy/router use. Account may be restricted or banned. Use at your own risk."*

**O que significa tecnicamente?**
1. **Origem do aviso:** Essa mensagem **não é um alerta do Google nem da Anthropic**. Trata-se de uma cláusula padrão de isenção de responsabilidade jurídica (CYA, termo em inglês para proteção preventiva de responsabilidade) inserida pelos mantenedores do projeto open-source 9Router.
2. **Aplicada universalmente:** Esse mesmo aviso é exibido para **todos os seis provedores baseados em OAuth e assinaturas** suportados pelo gateway:
   * Google Antigravity
   * Claude Code / Anthropic OAuth
   * OpenAI Codex / ChatGPT Plus
   * Gemini CLI
   * GitHub Copilot
   * Kiro
3. **Objetivo:** Isentar os autores do software de qualquer mau uso por usuários que decidam revender acessos ou automatizar requisições massivas abusivas contra provedores em nuvem.

---

### 2. A Assinatura Técnica e Como o Google Enxerga o 9Router

O 9Router não executa nenhuma invasão, bypass criptográfico ou engenharia reversa destrutiva. Ele atua estritamente como um **emulador de protocolo local**:

* **Endpoint de Destino:** Conecta-se às rotas oficiais do Google Cloud Code em `cloudcode-pa.googleapis.com`  -  `/v1internal:loadCodeAssist` e `/v1internal:onboardUser` no handshake, `/v1internal:fetchAvailableModels` no catálogo e `/v1internal:generateContent` na inferência.
* **Client ID:** Utiliza o Client ID oficial do Google Antigravity (`1071006060591-...`).
* **Headers e Metadados:** Envia os cabeçalhos com `User-Agent: antigravity/ide/2.11.0 darwin/arm64`, `x-request-source: local` e flag de plataforma `ideType: 9`.
* **Fluxo de Tokens:** O token de acesso (`ya29...`) e o token de atualização (*refresh token*) são gerados pelos servidores de autorização padrão da Google (`oauth2.googleapis.com/token`).

Na prática, as requisições do ClaudeGravity carregam os mesmos metadados de um desenvolvedor operando o IDE Antigravity. Com uma ressalva honesta: **a plataforma no `User-Agent` está fixa como `darwin/arm64` no código do 9Router**. Se você roda Linux ou Windows, o cabeçalho declara macOS ARM  -  ou seja, a assinatura é consistente com o IDE, mas não reflete o seu sistema real.

---

### 3. Análise de Risco Real e o Que Acontece sob Estresse

| Cenário | O que observamos na prática | Mecanismo técnico e recuperação |
| :--- | :--- | :--- |
| **Rate Limiting Temporário (`HTTP 429 ResourceExhausted`)** | Ocorrência normal em rajadas de requisições com modelos pesados | A conta é pausada até a janela de taxa reabrir. O 9Router aplica até 3 retentativas com *backoff exponencial* e, em combos, desce para o próximo modelo da cascata. Recuperação automática. |
| **Revogação de Sessão OAuth (`HTTP 401 Unauthorized`)** | Observado quando o token expira ou a senha da conta Google muda | Reproduzimos esse cenário no laboratório do artigo 0003: o gateway barra a chamada e o combo salta para o próximo provedor. Recuperação com `agy login` ou reautenticação no dashboard. |
| **Suspensão da Cota de IA (Gemini Code Assist)** | Não observado em uso individual de desenvolvimento | É a cota de ferramenta de desenvolvedor, separada dos serviços civis da conta. O risco cresce ao expor a porta publicamente ou automatizar tráfego sintético contínuo. |
| **Ação sobre a conta Google** | Não observado | O Google opera com separação entre serviços de desenvolvedor e serviços pessoais, mas **não existe garantia pública sobre isso**  -  veja a ressalva abaixo. |

> **Ressalva honesta:** as linhas acima descrevem o que medimos no nosso ambiente, não uma promessa. Os termos de uso e as políticas de enforcement do Google são privados e podem mudar a qualquer momento, sem aviso. Ninguém  -  nem este artigo  -  pode garantir o comportamento futuro do provedor. A decisão de assumir esse risco é sua, e a recomendação de usar uma conta dedicada (regra 1 abaixo) existe justamente para limitar o impacto caso algo mude.

---

### 4. E Se Múltiplas Pessoas Usarem? (Arquitetura de Equipe e Servidor Central)

Uma dúvida arquitetural frequente em equipes de engenharia é:
*"Podemos hospedar uma instância única do 9Router em um servidor interno e apontar o Claude Code de vários desenvolvedores para o mesmo endpoint?"*

A resposta é **sim**, mas com considerações técnicas cruciais sobre como o Google gerencia cotas:

![Arquitetura para Equipes e Connection Pooling Multi-Contas](../assets/12_diagrama_arquitetura_equipes.png)

> **Figura 12:** Arquitetura centralizada de conexão multi-contas do 9Router, distribuindo requisições via Round-Robin entre credenciais distintas e isolando o contexto de cada desenvolvedor.


#### Como a Google Contabiliza os Limites?
A Google audita as cotas de consumo em duas camadas:
1. **Por Conta Google (Token OAuth):** Esta é a camada principal. O limite de requisições por minuto (RPM) e tokens por minuto (TPM) está atrelado à **assinatura do titular da conta**.
2. **Por IP de Origem:** Camada secundária para proteção contra ataques de negação de serviço (DDoS).

#### Dois Cenários de Uso em Equipe

**Cenário 1  -  Quantas contas Google alimentam o gateway.** É a decisão que define o teto de throughput da equipe:

* **Uma única conta:** o tráfego de todos concorre pela mesma janela de RPM. Em tarefas intensivas simultâneas, respostas `HTTP 429 (ResourceExhausted)` ficam frequentes  -  não há banimento, apenas pausas para resfriamento da cota.
* **Múltiplas contas (recomendado):** em **Providers → Antigravity** você conecta a conta de cada membro da equipe. O 9Router distribui as requisições por Round-Robin e, quando uma conta entra em *cool-down*, redireciona para a próxima  -  multiplicando o throughput total.

**Cenário 2  -  Isolamento entre desenvolvedores.** O 9Router identifica cada requisição por um `sessionId` próprio, de modo que prompts simultâneos sobre bases de código diferentes são tratados como conversas independentes. Vale dizer com precisão: esse é o mecanismo de roteamento do gateway, não uma fronteira de segurança auditada. Para times que lidam com código sob sigilo contratual, a recomendação continua sendo uma instância por equipe, em rede privada.

---

### 5. Combos de Fallback Inteligentes para Resiliência sem Paradas

No menu **Combos** do 9Router (`/dashboard/combos`), você pode criar um modelo virtual inteligente para eliminar qualquer possibilidade de interrupção por taxa de limite:

1. Crie um combo chamado `claudegravity-fallback`.
   > **Atenção:** No 9Router, o nome do combo **não pode conter barra (`/`)**. Qualquer string com barra é tratada internamente como `provedor/modelo`. Nomes limpos como `claudegravity-fallback` ou `arsenal-livre` são identificados instantaneamente como grupos de fallback.
2. Adicione os modelos na seguinte ordem hierárquica:
   * **1º:** `ag/gemini-3.8-flash-high` (Máximo raciocínio profundo)
   * **2º:** `ag/gemini-3.7-flash-high` (Fallback rápido se o 3.8 atingir 429)
   * **3º:** `ag/gemini-3.6-flash-high` (Fallback de ultra-baixa latência)
   * **4º:** `ag/claude-sonnet-4-6` (Instância Claude Sonnet 4.6 servida pelo Antigravity)
   * **5º:** `ag/gpt-oss-120b-medium` (Modelo open-weights como última camada)

   > Essa é exatamente a cascata que o script `src/sync_antigravity_token.py` provisiona automaticamente ao registrar a conta. Se você criar o combo pela interface, replique os cinco níveis para obter o mesmo comportamento.
3. Crie um segundo combo, `claudegravity-thinking`, que é o **modelo padrão entregue nos arquivos `.example`**:
   * **1º:** `ag/claude-opus-4-6-thinking` (raciocínio denso, e fora da cota do Gemini)
   * **2º:** `ag/claude-sonnet-4-6`
   * **3º:** `ag/gemini-3.8-flash-high`
   * **4º:** `ag/gpt-oss-120b-medium`

   > Ele existe justamente para o caso da seção anterior: quando a cota da família Gemini estoura, este combo continua respondendo pelo primeiro nível, sem gastar saltos. Rodar `python3 src/claudegravity.py` uma única vez provisiona os dois combos automaticamente, e é o caminho mais rápido.
4. Para ativar a resiliência por padrão, no `.claude/settings.json`, configure:
   ```json
   "model": "claudegravity-fallback"
   ```
   Ou chame via terminal mantendo `ag/gemini-3.8-flash-high` como padrão no JSON:
   ```bash
   claude --dangerously-skip-permissions --model claudegravity-fallback
   ```

Se o Gemini 3.8 Flash atingir o teto momentâneo de tokens por minuto durante uma refatoração em lote, o 9Router retenta e depois desce para o Gemini 3.7 Flash sem que o terminal do Claude Code acuse qualquer erro. O usuário percebe apenas uma resposta um pouco mais demorada  -  não uma sessão interrompida.

> **Ao estender a cascata com modelos gratuitos de terceiros**, lembre-se de que identificadores `:free` são cortesia do provedor, não contrato: podem ser descontinuados, saturados ou passar a exigir permissão sem aviso. O [Artigo 0003](../../0003_fallback_modelos_gratuitos_9router/article/ARTICLE.md) traz a lista do que está respondendo e a rotina de revalidação.

---

### 6. As Três Regras de Ouro para Blindagem e Tranquilidade

1. **Use uma conta Google dedicada a desenvolvimento**, nunca a conta pessoal onde vivem e-mails bancários e documentos essenciais. É o que limita o impacto caso a política do provedor mude.
2. **Mantenha o gateway em rede privada:** `localhost` para uso individual, VPN ou rede overlay (como Tailscale) para o time. Nunca exponha a porta `20128` na internet aberta.
3. **Respeite o padrão de uso humano:** programar com o Claude Code intercala inferência com leitura e revisão. Evite benchmarks sintéticos disparando requisições contínuas em loop infinito.
4. **Separe a saída de rede por conta.** Várias sessões na mesma conta não são o problema — os provedores aceitam isso. O que chama atenção é o inverso: **várias contas saindo pelo mesmo endereço**, que é o padrão natural de um gateway com todas as contas cadastradas. A seção abaixo mostra como o 9Router resolve isso.

---

### 7. Multi-sessão: por que o endereço de saída importa mais que o número de sessões

Existe uma confusão comum que vale desfazer, porque ela leva à decisão errada.

**O que não é problema:** manter mais de uma sessão ativa na mesma conta. OpenAI, Anthropic e Google convivem com isso — é o caso de quem usa o app no celular e a CLI no desktop ao mesmo tempo.

**O que é problema:** um gateway com cinco contas cadastradas faz as cinco saírem pelo mesmo IP. Para o provedor, cinco identidades distintas compartilhando um endereço é o formato de uma revenda de acesso — exatamente o comportamento que o `RISK_NOTICE` da seção 1 existe para desencorajar.

#### Tailscale resolve? Só metade do problema

A regra de ouro nº 2 recomenda Tailscale para manter o gateway fora da internet aberta, e essa recomendação continua válida. Mas é fácil concluir dela algo que não se sustenta: **um exit node do Tailscale dá endereço estável ao host, não a cada conta**. Com várias contas no mesmo gateway, todas continuam saindo pelo mesmo lugar — o problema volta intacto.

Vários exit nodes separam de verdade, mas só se cada conta estiver **vinculada** a um deles. E o vínculo não vem da tecnologia que produziu o endereço: vale igual para VPS, proxy residencial ou um segundo link. **O que separa contas é o vínculo por conta, nunca a tecnologia que gerou o IP.**

#### Como o 9Router modela isso

O gateway já tem a peça pronta, e ela não depende de nada externo:

| Onde | O que guarda |
| :--- | :--- |
| `proxyPools` | Os endereços de saída disponíveis |
| `providerSpecificData.proxyPoolId` | A qual pool **aquela conexão** está vinculada |
| `providerSpecificData.connectionProxyEnabled` | Se o roteamento está ativo para ela |

A propriedade que interessa: o vínculo é **por conexão**, não global. Cadastrar um pool por conta e apontar cada conexão para o seu fixa a saída daquela conta — sem rotação, sem sorteio. Duas contas nunca dividem endereço se cada uma tiver o próprio `proxyPoolId`.

> **Quem aplica o roteamento é o gateway, sempre.** O painel do [9RTKSync](https://github.com/pathbit/9RTKSync) exibe o vínculo de cada conta em modo **somente leitura**: *saída própria* quando ela tem o seu pool, *divide o endereço do gateway com N contas* quando não tem — e esse aviso só aparece a partir da segunda conta nessa situação, porque uma conta sozinha é a única dona daquele IP. É assim que você vê quais contas compartilham endereço antes que o provedor veja. A consulta que lista isso está em [Egress and Multi-Session](https://github.com/pathbit/9RTKSync/wiki/Egress-And-Multi-Session), com a versão equivalente para o OmniRoute no [OminiRTkSync](https://github.com/pathbit/OminiRTkSync/wiki/Egress-And-Multi-Session).

#### O mínimo que vale fazer

Se cadastrar uma conta só, nada disso se aplica. A partir da segunda:

1. Confira no painel do 9RTKSync quais contas aparecem como `compartilhada`.
2. Cadastre um endereço de saída por conta em `proxyPools` — exit node, VPS ou proxy, tanto faz.
3. Vincule cada conexão ao seu pool e ative `connectionProxyEnabled`.
4. Revalide no painel: o estado de cada conta deve passar a `vinculada`.

---

## Show-Me-The-Code

O artigo disponibiliza uma suíte completa de infraestrutura e ferramentas em Python que entrega:

- orquestração via Docker Compose do gateway 9Router, com healthcheck e acesso aos 20 modelos Antigravity;
- diagnóstico automatizado em Python que valida portas, endpoints HTTP, tokens OAuth e CLI do Claude Code;
- testes de inferência em tempo real para Gemini 3.8 Flash, Gemini 3.7 Flash, Gemini 3.6 Flash e Claude Sonnet;
- ambiente prático e isolado (`examples/`) com configurações prontas do Claude Code (`.claude/`) e script de teste (`sample_task.py`);
- launcher em Python com injeção automática de flags de permissão total e modo zero-interrupção.

**Opção 1** Execute a infraestrutura e o diagnóstico automatizado localmente pelo terminal.

[**Abrir README.md com instruções locais**](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0002_claude_gravity_utilizando_9router/README.md)

**Opção 2** Execute o código de testes e interaja com o Claude Code diretamente no ambiente prático isolado (`examples/`).

[**Abrir pasta de exemplos e testes práticos**](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0002_claude_gravity_utilizando_9router/examples/README.md)

### Pré-requisitos do Ambiente e Credenciais

Para reproduzir a infraestrutura do ClaudeGravity localmente, assegure que as seguintes ferramentas e credenciais estejam instaladas e prontas:

1. **Python 3.14.7 (Recomendado) ou Superior (mínimo 3.10):**
   - Recomendamos a versão oficial: [Python 3.14.7](https://www.python.org/ftp/python/3.14.7/python-3.14.7-macos11.pkg) (pacote instalador macOS).
   - Necessário para rodar os scripts de ciclo de vida (`src/manage_env.py`), sincronização de credenciais (`src/sync_antigravity_token.py`) e diagnóstico (`src/verify_setup.py`).
   - Se necessário, instale via pacote oficial [Python 3.14.7](https://www.python.org/ftp/python/3.14.7/python-3.14.7-macos11.pkg) ou `brew install python` (macOS), `sudo apt install python3 python3-venv python3-pip` (Linux) ou `winget install Python.Python.3.14` (Windows).

2. **Ambiente Virtual Dedicado:** Crie e ative o ambiente virtual para isolamento das dependências:
   ```bash
   # Criar o ambiente virtual na pasta do modulo
   python3 -m venv .venv

   # Ativar no macOS e Linux
   source .venv/bin/activate

   # Ativar no Windows (PowerShell)
   .venv\Scripts\Activate.ps1

   # Instalar dependencias minimas
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Docker e Docker Compose:**
   - O gateway `claudegravity-router` é orquestrado em container. Instale o Docker Desktop (macOS / Windows via winget / site oficial) ou Docker Engine (Linux via `curl -fsSL https://get.docker.com | sh`).
   - Valide que o serviço está ativo com `docker info` e `docker compose version`.

4. **Node.js e Claude Code CLI:**
   - O Claude Code requer Node.js 18+. Instale via `brew install node`, `sudo apt install nodejs npm` ou `winget install OpenJS.NodeJS`.
   - Instale o Claude Code globalmente com `npm install -g @anthropic-ai/claude-code` e valide com `claude --version`.

5. **Conta Google com Antigravity (Google AI Pro) e Sessão Ativa no Navegador:**
   - Possuir uma conta Google ativa com a assinatura Google AI Pro, Google One AI Premium ou Google Workspace com Gemini.
   - O login prévio no **Google Antigravity IDE** ou na CLI `agy` (`agy --version`) gera a credencial local em `~/.gemini/jetski-standalone-oauth-token` utilizada pelo utilitário de sincronização.
   - **Mandatório para o 9Router:** O dashboard em `http://localhost:20128/dashboard` deve ser aberto no navegador exatamente sob a conta Google detentora da licença Antigravity. Conectar o 9Router através de uma conta pessoal sem assinatura causará erros imediatos `HTTP 403 Forbidden` na chamada aos modelos Gemini.

6. **Variáveis de Ambiente (.env):** Inicialize o arquivo `.env` a partir de `.env.example` definindo `INITIAL_PASSWORD` e `JWT_SECRET` para proteger a interface administrativa do gateway.

### Executando os Scripts de Diagnóstico e Teste

```bash
# Diagnóstico completo de saúde do ambiente
python3 src/verify_setup.py

# Teste de inferência do gateway
python3 src/test_gateway.py

# Iniciar Claude Code conectado ao Antigravity
python3 src/claudegravity.py
```

---

## Próximos Passos e Otimizações

Agora que você tem o ClaudeGravity funcionando na sua máquina:

1. **Configure Combos de Fallback no 9Router:** Crie um combo no dashboard que tente primeiro o `ag/gemini-3.8-flash-high` e, caso o rate limit por minuto da Google seja atingido em tarefas brutas, comute automaticamente para `ag/gemini-3.7-flash-high` e `ag/gemini-3.6-flash-high`.
2. **Adicione Servidores MCP:** conecte servidores de PostgreSQL, GitHub e navegadores locais. Para liberá-los sem confirmação, acrescente ao `allow` uma entrada por servidor no formato `mcp__<servidor>__*`  -  o curinga solto `mcp__*` é recusado, porque uma regra de `allow` precisa nomear o servidor que amplia.
3. **Explore Projetos Extensos:** Graças à janela de 1M de tokens do Gemini combinada com o harness do Claude Code, submeta módulos inteiros de microsserviços para refatoração arquitetural em lote.
4. **Evolua para o Arsenal Ilimitado com Provedores Gratuitos:** No [Artigo 0003 - Claude Code sem Limites com Arsenal de Modelos Gratuitos e Fallback no 9Router](../../0003_fallback_modelos_gratuitos_9router/article/ARTICLE.md), mostramos como integrar Google AI Studio, Groq, OpenRouter e Ollama para nunca mais ficar sem tokens e programar continuamente com custo zero.

---

## Referências

- [Claude Code Settings & Permissions Guide](https://code.claude.com/docs/en/settings)
- [Claude Code Model Configuration Reference](https://code.claude.com/docs/en/model-config)
- [9Router GitHub Repository & Architecture](https://github.com/decolua/9router)
- [9RTKSync: 9Router Universal Token & Connection Synchronizer](https://github.com/pathbit/9RTKSync)
- [OminiRTKSync: OminiRoute Universal Token & Connection Synchronizer](https://github.com/pathbit/OminiRTkSync)
- [OmniRoute Gateway Repository](https://github.com/diegosouzapw/OmniRoute)
- [Google Antigravity Overview](https://antigravity.google)
- [DeepClaude Architecture Reference](https://github.com/aattaran/deepclaude)

---

## 📄 Licença

Distribuído sob a Licença MIT. O texto completo está em [LICENSE](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/LICENSE).

Na prática: use, copie, altere e redistribua à vontade, inclusive comercialmente, desde que o aviso de copyright e a licença acompanhem as cópias. O software é fornecido como está, sem garantias.

---

Desenvolvido com ❤️ pela [Pathbit](https://pathbit.co/)
