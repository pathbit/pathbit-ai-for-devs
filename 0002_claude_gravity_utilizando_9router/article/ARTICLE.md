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
    image: decolua/9router:0.5.69
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
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://127.0.0.1:20128/dashboard"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s

volumes:
  9router_data:
```

Três decisões de engenharia neste manifesto:

* **`extra_hosts: ["host.docker.internal:host-gateway"]`** garante compatibilidade entre plataformas (macOS, Linux e Windows WSL2), permitindo que o container resolva o endereço do host local de forma idêntica em qualquer distribuição.
* **Senha e segredo JWT vêm do `.env`**, nunca literais no arquivo versionado. A sintaxe `${VAR:?mensagem}` interrompe a subida com um erro claro caso a variável não exista, em vez de silenciosamente aplicar um padrão fraco.
* **`healthcheck` ativo:** sem ele, a diretiva `restart: unless-stopped` só reage quando o processo morre  -  um container travado, mas vivo, permaneceria roteando para o vazio. A sonda HTTP a cada 30 segundos marca o container como `unhealthy` e torna o problema visível no `docker ps`.
* **Porta publicada apenas em `127.0.0.1`:** o gateway guarda o token OAuth da sua conta Google e as chaves dos provedores. Publicar como `"20128:20128"` o exporia em todas as interfaces de rede, permitindo que qualquer máquina da mesma rede consumisse sua cota. O prefixo de loopback restringe o acesso à própria máquina.

> **Sobre a versão fixada:** o manifesto usa `decolua/9router:0.5.69`, e não `:latest`, de propósito. Os scripts deste artigo dependem de um endpoint interno (`/api/auth/status`) e do schema SQLite do gateway (tabelas `providerConnections` e `combos`); uma atualização silenciosa da imagem pode alterar qualquer um dos dois e quebrar tudo sem aviso. Ao migrar para uma versão nova, troque a tag deliberadamente e revalide com `python3 src/verify_setup.py`.

### 2. Inicializando o serviço

Primeiro crie o arquivo `.env` a partir do modelo, definindo a senha do dashboard e o segredo JWT:

```bash
cp .env.example .env
```

Em seguida suba o serviço:

```bash
docker compose up -d
```

Verifique a saúde do container:

```bash
docker ps --filter "name=claudegravity-router"
```

![Container Docker Rodando](../assets/02_docker_container_running.png)

> **Figura 2:** Evidência do container `claudegravity-router` em execução e saudável na porta local `20128`.

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

Para que todas as sessões do Claude Code iniciem com permissões completas, loops, advisors e os modelos Gemini pré-configurados, disponibilizamos modelos `.example` exclusivamente dentro da pasta de testes do artigo (`examples/.claude/`). Para inicializar sua configuração local:

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
| `settings.json` | Políticas compartilhadas do projeto | Modelo padrão, mapeamento `modelOverrides`, permissões e variáveis de ambiente |
| `settings.local.json` | Preferências da sua máquina | O menu interativo `/model` e ajustes pessoais. **Tem precedência** sobre o anterior |

Os dois são versionados apenas na forma `.example`; as cópias ativas ficam fora do controle de versão.

#### Estrutura do `settings.json.example`

```json
{
  "model": "ag/gemini-3.8-flash-high",
  "modelOverrides": {
    "claude-opus-4-6": "ag/gemini-3.1-pro-low",
    "claude-3-opus": "ag/gemini-3.1-pro-low",
    "claude-5-opus": "ag/gemini-3.1-pro-low",
    "claude-sonnet-4-6": "ag/gemini-3.7-flash-high",
    "claude-3-7-sonnet": "ag/gemini-3.7-flash-high",
    "claude-5-sonnet": "ag/gemini-3.7-flash-high",
    "claude-5": "ag/gemini-3.7-flash-high",
    "claude-haiku-4-5-20251001": "ag/gemini-3.6-flash-high",
    "claude-haiku": "ag/gemini-3.6-flash-high",
    "claude-3-5-haiku": "ag/gemini-3.6-flash-high",
    "fable": "ag/gemini-3.6-flash-high",
    "claude-fable": "ag/gemini-3.6-flash-high",
    "gpt-oss": "ag/gpt-oss-120b-medium",
    "gpt-oss-120b": "ag/gpt-oss-120b-medium"
  },
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:20128",
    "ANTHROPIC_API_KEY": "sk-sua-chave-do-9router",
    "CLAUDE_CODE_EXPERIMENTAL": "1",
    "CLAUDE_CODE_ENABLE_LOOPS": "1",
    "CLAUDE_CODE_ENABLE_ADVISOR": "1",
    "CLAUDE_CODE_ENABLE_GOAL": "1",
    "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1"
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
  "includeCoAuthoredBy": false
}
```

#### Estrutura do `settings.local.json.example` (Menu `/model`)

```json
{
  "model": "ag/gemini-3.8-flash-high",
  "advisorModel": "ag/gemini-3.8-flash-high",
  "modelOverrides": {
    "claude-opus-4-6": "ag/gemini-3.1-pro-low",
    "claude-3-opus": "ag/gemini-3.1-pro-low",
    "claude-5-opus": "ag/gemini-3.1-pro-low",
    "claude-sonnet-4-6": "ag/gemini-3.7-flash-high",
    "claude-3-7-sonnet": "ag/gemini-3.7-flash-high",
    "claude-5-sonnet": "ag/gemini-3.7-flash-high",
    "claude-5": "ag/gemini-3.7-flash-high",
    "claude-haiku-4-5-20251001": "ag/gemini-3.6-flash-high",
    "claude-haiku": "ag/gemini-3.6-flash-high",
    "claude-3-5-haiku": "ag/gemini-3.6-flash-high",
    "fable": "ag/gemini-3.6-flash-high",
    "claude-fable": "ag/gemini-3.6-flash-high",
    "gpt-oss": "ag/gpt-oss-120b-medium",
    "gpt-oss-120b": "ag/gpt-oss-120b-medium"
  },
  "modelPicker": {
    "replaceBuiltInOptions": false,
    "options": [
      {
        "model": "ag/gemini-3.8-flash-high",
        "label": "ClaudeGravity Principal (Gemini 3.8 Flash High)",
        "description": "Modelo primário ClaudeGravity via Antigravity AI Pro"
      },
      {
        "model": "claudegravity-fallback",
        "label": "ClaudeGravity Resiliente (Fallback Gratuito)",
        "description": "Combo resiliente com fallback automático para modelos gratuitos"
      },
      {
        "model": "ag/gemini-3.7-flash-high",
        "label": "Gemini 3.7 Flash (High Reasoning)",
        "description": "Raciocínio balanceado e alta velocidade"
      },
      {
        "model": "ag/gemini-3.6-flash-high",
        "label": "Gemini 3.6 Flash (Low Latency)",
        "description": "Latência mínima para tarefas rápidas"
      },
      {
        "model": "ag/gemini-3.1-pro-low",
        "label": "Gemini 3.1 Pro (Deep Complex)",
        "description": "Planejamento arquitetural complexo e agentes profundos"
      },
      {
        "model": "ag/claude-sonnet-4-6",
        "label": "Claude Sonnet 4.6 (Thinking)",
        "description": "Sonnet 4.6 Thinking roteado via Antigravity"
      },
      {
        "model": "ag/claude-opus-4-6-thinking",
        "label": "Claude Opus 4.6 (Thinking)",
        "description": "Opus 4.6 Thinking roteado via Antigravity"
      },
      {
        "model": "ag/gpt-oss-120b-medium",
        "label": "GPT-OSS 120B (Medium)",
        "description": "Modelo open-weights via Antigravity"
      }
    ]
  },
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:20128",
    "ANTHROPIC_API_KEY": "sk-sua-chave-do-9router",
    "CLAUDE_CODE_EXPERIMENTAL": "1",
    "CLAUDE_CODE_ENABLE_LOOPS": "1",
    "CLAUDE_CODE_ENABLE_ADVISOR": "1",
    "CLAUDE_CODE_ENABLE_GOAL": "1",
    "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1"
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
  "includeCoAuthoredBy": false
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
| `CLAUDE_CODE_EXPERIMENTAL=1` | Ativa recursos experimentais do motor de execução da CLI da Anthropic. | Desbloqueia novas capacidades do motor agêntico. |
| `CLAUDE_CODE_ENABLE_LOOPS=1` | Habilita a execução contínua de loops de feedback e tentativa e erro pelo agente. | Permite que o Gemini 3.8 rode testes, capture erros e tente novamente até o código passar. |
| `CLAUDE_CODE_ENABLE_ADVISOR=1` | Permite que um modelo secundário atue como conselheiro (*Advisor*) do modelo primário. | Permite usar o `ag/gemini-3.8-flash-high` como revisor arquitetural em segundo plano. |
| `CLAUDE_CODE_ENABLE_GOAL=1` | Ativa o modo de metas de longo prazo (`/goal`) no Claude Code. | Ideal para tarefas noturnas ou refatorações extensas que duram horas. |
| `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1` | Desativa a restrição rígida de contagem de janela de contexto baseada exclusivamente nos modelos proprietários da Anthropic. | Permite que o Claude Code utilize os identificadores `ag/gemini-*` sem reclamar de tamanho de janela desconhecido. |

---

### Mapeamento de Modelos Primários, Secundários e Subagentes

O `modelOverrides` intercepta o identificador que o Claude Code pede e o substitui por um modelo do Antigravity. Ele não age quando você escolhe o modelo: age quando **a própria CLI** decide qual usar, como ao despachar um subagente ou ao acionar o modelo rápido de triagem.

Três mapeamentos respondem hoje, e são exatamente os identificadores que a CLI emite:

| Quando o Claude Code pede | Passa a ser servido por | Papel |
| :--- | :--- | :--- |
| `claude-opus-4-6` | `ag/gemini-3.1-pro-low` | Raciocínio denso: planejamento arquitetural e refatoração pesada |
| `claude-sonnet-4-6` | `ag/gemini-3.7-flash-high` | Cavalo de batalha do dia a dia, raciocínio híbrido |
| `claude-haiku-4-5-20251001` | `ag/gemini-3.6-flash-high` | Latência mínima para subagentes, varreduras e triagem |

As outras onze entradas do bloco (`claude-3-opus`, `claude-5-opus`, `claude-3-7-sonnet`, `claude-5-sonnet`, `claude-5`, `claude-haiku`, `claude-3-5-haiku`, `fable`, `claude-fable`, `gpt-oss` e `gpt-oss-120b`) ficam declaradas como reserva, para o caso de uma versão futura da CLI passar a emitir esses nomes. **Hoje elas não têm efeito**: a CLI valida o identificador contra uma lista fechada antes de consultar o `modelOverrides`, e recusa qualquer nome fora dela com `There's an issue with the selected model`  -  o mesmo erro que devolveria para um nome inventado. Mantê-las é inofensivo, mas não conte com elas.

Vale a distinção, porque é onde a maioria se perde: passar `--model claude-5-sonnet` **não** funciona, enquanto `--model ag/gemini-3.7-flash-high` funciona. O `modelOverrides` traduz o que a CLI pede por conta própria, não o que você digita.

O modelo principal declarado em `"model"` (`ag/gemini-3.8-flash-high`) segue sendo o motor primário da sessão. E, com o `modelPicker` no `settings.local.json`, você digita `/model` no terminal e alterna entre as variantes catalogadas sem sair da sessão  -  ali os identificadores são os `ag/*` diretos, que a CLI aceita sem intermediação.

---

## Executando o ClaudeGravity no Terminal

Com as configurações salvas, você pode operar em dois modos de trabalho:

### Modo 1 - ClaudeGravity Principal (Velocidade e Raciocínio Máximo com Gemini 3.8 Flash High)
Neste modo padrão, o Claude Code executa diretamente contra o motor Gemini 3.8 Flash High conectado via Antigravity Pro, desfrutando de 1 milhão de tokens de contexto e custo zero.

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

> **Nota sobre o launcher:** o `claudegravity.py` sincroniza as credenciais do Antigravity, garante o combo de fallback no gateway e, antes de entregar o controle ao Claude Code, muda o diretório de trabalho para `examples/`. Isso mantém a sessão dentro do sandbox de testes do artigo, com as políticas de `examples/.claude/` já aplicadas. Para trabalhar no seu próprio repositório, chame o `claude` diretamente com as variáveis de ambiente acima.

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
3. Para ativar a resiliência por padrão, no `.claude/settings.json`, configure:
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

1. **Python 3.10 ou Superior:**
   - Necessário para rodar os scripts de ciclo de vida (`src/manage_env.py`), sincronização de credenciais (`src/sync_antigravity_token.py`) e diagnóstico (`src/verify_setup.py`).
   - Se necessário, instale via `brew install python` (macOS), `sudo apt install python3 python3-venv python3-pip` (Linux) ou `winget install Python.Python.3.12` (Windows).

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
2. **Adicione Servidores MCP:** Como o `.claude/settings.local.json` já libera permissões para ferramentas `mcp__*`, conecte servidores MCP de PostgreSQL, GitHub e navegadores locais sem atrito.
3. **Explore Projetos Extensos:** Graças à janela de 1M de tokens do Gemini combinada com o harness do Claude Code, submeta módulos inteiros de microsserviços para refatoração arquitetural em lote.
4. **Evolua para o Arsenal Ilimitado com Provedores Gratuitos:** No [Artigo 0003 - Claude Code sem Limites com Arsenal de Modelos Gratuitos e Fallback no 9Router](../../0003_fallback_modelos_gratuitos_9router/article/ARTICLE.md), mostramos como integrar Google AI Studio, Groq, OpenRouter e Ollama para nunca mais ficar sem tokens e programar continuamente com custo zero.

---

## Referências

- [Claude Code Settings & Permissions Guide](https://code.claude.com/docs/en/settings)
- [Claude Code Model Configuration Reference](https://code.claude.com/docs/en/model-config)
- [9Router GitHub Repository & Architecture](https://github.com/decolua/9router)
- [Google Antigravity Overview](https://antigravity.google)
- [DeepClaude Architecture Reference](https://github.com/aattaran/deepclaude)
