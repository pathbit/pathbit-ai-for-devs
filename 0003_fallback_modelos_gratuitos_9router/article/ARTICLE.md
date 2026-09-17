# Claude Code sem Limites com Arsenal de Modelos Gratuitos e Fallback no 9Router

![Capa do Artigo - Combos de Fallback e Modelos Gratuitos](../assets/00_cover_arsenal_fallback.png)

No desenvolvimento moderno de software assistido por agentes, poucas experiências são tão frustrantes quanto ver um fluxo cognitivo de refatoração ser abruptamente interrompido por uma parede de limite de taxa:

```text
HTTP Error 429: Too Many Requests (Rate limit exceeded)
```

Quando você opera o Claude Code em tarefas de engenharia complexas (executando testes, analisando dependências, iterando sobre arquivos e revisando código), o consumo de tokens e a frequência de requisições por minuto atingem picos elevados. Depender de um único provedor ou de uma única cota de API significa aceitar interrupções involuntárias no meio do seu raciocínio.

Neste artigo, apresentamos uma solução arquitetural definitiva: como transformar o **9Router** em uma central de alta disponibilidade para o **Claude Code**, mapeando **9 fontes de modelos de inteligência artificial gratuitas** e integrando 5 delas em **Combos de Fallback Inteligentes** prontos para uso. Quando uma cota atinge o teto temporário, o gateway comuta automaticamente para o próximo provedor da fila, sem que sua sessão no terminal sofra quedas ou perca o contexto de trabalho.

![Malha de Resiliência Multi-Provedores com Fallback Automático](../assets/01_diagrama_malha_multiprovedor.png)

> **Figura 1:** Malha de resiliência multi-provedores com o gateway 9Router orquestrando a comutação transparente entre os grupos de provedores que alimentam o Claude Code CLI.

Este trabalho é a evolução direta da infraestrutura apresentada no [Artigo 0002 - ClaudeGravity e o Roteamento de Modelos Gemini no Claude Code via 9Router](../../0002_claude_gravity_utilizando_9router/article/ARTICLE.md). Se lá consolidamos a ponte de alta fidelidade com o Google Antigravity, aqui expandimos essa base para um ecossistema multi-provedor resiliente que nunca para de programar.

---

## 9Router e OmniRoute na Prática

Com a proliferação de gateways locais para desenvolvedores, duas ferramentas ganharam destaque no ecossistema de código aberto: o **9Router** e o **OmniRoute**. Ambas resolvem o aprisionamento tecnológico em provedores proprietários, atendem aos mesmos contratos de API (Anthropic Messages e OpenAI Chat Completions) e padronizaram a porta local `20128`  -  mas com focos distintos.

O **9Router**, que usamos neste artigo, é um gateway enxuto de *set-and-forget*: container Node.js com SQLite embarcado, cascata de prioridade simples e compressão RTK nativa. O **OmniRoute** é um orquestrador mais abrangente, com matriz dinâmica de roteamento por latência, custo e taxa de sucesso  -  mais indicado para quem quer calibrar pesos do que para quem quer um gateway que simplesmente funcione.

Escolhemos o 9Router pela previsibilidade: menos peças móveis significa menos coisas que podem falhar no meio de uma refatoração.

---

## A Resolução da URL Base no Claude Code

Uma dúvida técnica recorrente gerada por tutoriais de gateways locais envolve a variável `ANTHROPIC_BASE_URL`: devemos declarar `http://localhost:20128` ou `http://localhost:20128/v1`?

A CLI da Anthropic monta o endereço final concatenando `baseUrl + "/v1/messages"`. Declarar a base já com `/v1` produz a rota duplicada `http://localhost:20128/v1/v1/messages` (que o 9Router tolera, ambas respondem HTTP 200), mas que quebra com **HTTP 404** em proxies estritos.

A regra de ouro, portanto, é declarar a base **sem** o sufixo:

```bash
ANTHROPIC_BASE_URL="http://localhost:20128"
```

---

## A Regra Crítica de Nomenclatura de Combos

Ao criar grupos de modelos virtuais no 9Router, há uma regra essencial no código-fonte que você precisa conhecer. No serviço de resolução de modelos (`open-sse/services/combo.js`):

```js
export function getComboModelsFromData(modelStr, combosData) {
  if (modelStr.includes("/")) return null;
  ...
}
```

Essa linha de validação estabelece que:
* Se o nome passado no campo `model` contiver uma barra (`/`), o gateway **rejeita a busca como combo** e assume que se trata de uma chamada a um provedor específico (`provedor/modelo`).
* Portanto, nomear um combo como `combo/arsenal-supremo` fará o gateway tentar autenticar o provedor fictício `combo`, resultando no erro `[AUTH] No credentials for combo`.
* O nome do combo deve ser **estritamente plano**, como `arsenal-supremo`, `arsenal-rapido` ou `arsenal-offline`.

Com essa nomenclatura, o 9Router identifica o grupo de modelos na hora, inicia a tentativa pelo primeiro item e aplica a transição automática em caso de limite.

---

## O Mapeamento das 9 Fontes de IA Gratuitas para Programação

Montar um arsenal que nunca para de programar exige diversificar as origens de tokens. Mapeamos as 9 principais fontes de modelos e tiers gratuitos com alta capacidade para tarefas de código.

> **Escopo desta implementação:** as 9 fontes abaixo compõem o mapa completo do ecossistema gratuito, mas os combos de referência deste artigo (`arsenal-supremo`, `arsenal-rapido` e `arsenal-offline`) e o provisionamento automatizado em `src/setup_combos.py` integram 5 delas: **Antigravity, OpenRouter, Groq, Mistral e Ollama Local**. Kiro, Cerebras, Cloudflare Workers AI e Google AI Studio ficam documentados como fontes adicionais (o AI Studio já entra como conexão opcional via `GEMINI_API_KEY`, e as demais podem ser plugadas na mesma cascata seguindo o padrão mostrado aqui).

### 1. Google Antigravity (Google AI Pro)
* **Modelos:** `ag/gemini-3.8-flash-high`, `ag/gemini-3.7-flash-high`, `ag/claude-sonnet-4-6`.
* **Vantagem:** Janela de contexto de até 1 milhão de tokens, raciocínio profundo de última geração e cota já incluída na assinatura do AI Pro sem cobrança por token adicional.

### 2. Kiro AWS Builder
* **Modelos:** Claude 3.5/3.7 Sonnet e GLM via tokens de desenvolvedor AWS.
* **Vantagem:** Créditos mensais generosos voltados a builders, com infraestrutura de baixíssima latência na nuvem da AWS.

### 3. Google AI Studio (Gemini Free Tier)
* **Modelos no catálogo do gateway:** `gemini/gemini-3.8-flash`, `gemini/gemini-3.7-flash`, `gemini/gemini-3.6-flash`, `gemini/gemini-3.5-flash-lite`, `gemini/gemini-3.1-pro-preview`.
* **Vantagem:** Chave de API direta e gratuita, sem necessidade de cartão de crédito. Os limites do tier gratuito (requisições e tokens por minuto) variam por modelo e são revisados periodicamente pelo Google  -  consulte a [tabela oficial de rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) antes de dimensionar sua cascata.

### 4. Groq Cloud
* **Modelo validado neste artigo:** `groq/openai/gpt-oss-120b`.
* **Vantagem:** Inferência acelerada por chips LPU (Language Processing Units), com as menores latências que medimos entre os provedores em nuvem  -  **0,34s a 0,55s** por resposta curta nos nossos testes. Excelente para testes unitários, linting e geração rápida de código.
* **Atenção ao catálogo:** os identificadores da Groq mudam com frequência. Confira o [catálogo vigente](https://console.groq.com/docs/models) e valide a cascata com `python3 src/test_arsenal.py` antes de confiar nela.

### 5. Cerebras Cloud
* **Modelos:** família Llama servida na infraestrutura Cerebras.
* **Vantagem:** Arquitetura Wafer-Scale Engine, orientada a latência de primeiro token (TTFT) muito baixa. Não integramos o Cerebras aos combos de referência, portanto não temos medição própria para comparar  -  trate os números divulgados pelo fornecedor como material de marketing até validar no seu ambiente.

### 6. OpenRouter Free Tier
* **Modelo validado neste artigo:** `openrouter/nvidia/nemotron-3.5-lightning:free` (contexto de 1M de tokens).
* **Vantagem:** Catálogo agregador que expõe versões gratuitas com sufixo `:free`. Na consulta que fizemos ao montar este artigo, 21 dos 430 modelos do catálogo tinham custo zero de prompt e de resposta; ao revalidar em 2026-09-13, eram **22 de 445**. O catálogo cresce e o subconjunto gratuito se mexe  -  reconte com o comando da seção [Modelos Gratuitos, Volatilidade e Catálogo Verificado](#modelos-gratuitos-volatilidade-e-catálogo-verificado).
* **Atenção à rotatividade:** o conjunto gratuito muda com frequência, e alguns identificadores citados em tutoriais antigos simplesmente deixam de existir. Tratamos esse ponto em detalhe, com a lista do que está respondendo, na seção [Modelos Gratuitos, Volatilidade e Catálogo Verificado](#modelos-gratuitos-volatilidade-e-catálogo-verificado).

### 7. Cloudflare Workers AI
* **Modelos:** catálogo de modelos abertos servidos na edge (`@cf/meta/...`).
* **Vantagem:** Execução em edge computing com cota diária gratuita medida em "neurônios". Não integramos o Workers AI aos combos deste artigo; consulte os [limites vigentes](https://developers.cloudflare.com/workers-ai/platform/pricing/) antes de posicioná-lo na cascata.

### 8. Mistral AI Developer Free Tier
* **Modelo integrado à cascata:** `mistral/codestral-latest`, o modelo de código do provedor ([documentação oficial](https://docs.mistral.ai/capabilities/code_generation/)).
* **Vantagem:** foi o provedor em nuvem **mais rápido de toda a nossa validação**. Medimos dez modelos da conta, e todos responderam entre **0,35s e 1,23s** por resposta curta  -  a tabela completa está na seção [O Catálogo da Mistral](#o-catálogo-da-mistral-e-o-que-a-api-não-mostra).
* **Atenção ao tier gratuito:** responder rápido não significa responder sempre. O tier de desenvolvedor tem limites de uso próprios, que não medimos; trate a Mistral como mais um nível da cascata, não como fonte ilimitada.

### 9. Ollama Local (A Rede de Segurança Definitiva)
* **Modelo validado neste artigo:** `openai-compatible-chat-ollama-local/qwen2.5-coder:latest`.
* **Sobre o prefixo:** o identificador não é `ollama/...` porque conectamos o Ollama pelo nó **OpenAI-compatible** do 9Router (`/v1/chat/completions`), e não pela rota proprietária `/api/chat`. Essa escolha garante streaming SSE nativo, como detalhamos na seção de Docker Compose.
* **Vantagem:** Execução 100% no hardware da sua máquina. Zero dependência de internet, zero risco de rate limit, privacidade absoluta para código confidencial e tokens verdadeiramente infinitos.

---

## Modelos Gratuitos, Volatilidade e Catálogo Verificado

> ⚠️ **Catálogos gratuitos mudam sem aviso.** Modelos com sufixo `:free` são cortesia do provedor, não um contrato. Qualquer lista de modelos gratuitos publicada em um artigo é um retrato do momento em que foi escrita  -  inclusive esta.
>
> Testando o catálogo gratuito pelo próprio gateway, três modos de falha aparecem com frequência:
>
> | Situação | Resposta do provedor | O que fazer |
> | :--- | :--- | :--- |
> | **Descontinuado ou migrado para a versão paga** | `404` | Substituir o identificador na cascata |
> | **Saturado no momento** | `429` | Nada  -  o gateway salta e tenta de novo depois |
> | **Requer permissão adicional na conta** | `403` | Habilitar o modelo no painel do provedor |
>
> **É exatamente por isso que a arquitetura aqui é uma cascata, e não um modelo único.** Quando um nível gratuito morre, o gateway salta para o próximo sem interromper sua sessão. Revalide periodicamente com `python3 src/test_arsenal.py`, que testa cada nível individualmente e acusa qualquer identificador quebrado.

### Modelos Gratuitos que Respondem

Até a data de escrita deste artigo, os modelos gratuitos abaixo estavam respondendo corretamente e servem para tarefas de código (use sempre com o prefixo `openrouter/`):

| Identificador | Contexto | Observação |
| :--- | ---: | :--- |
| `cohere/north-mini-code:free` | 256k | **Especializado em código** |
| `nvidia/nemotron-3.5-lightning:free` | 1M | **Melhor relação contexto/velocidade** |
| `nex-agi/nex-n2.5-mini:free` | 262k | O mais rápido entre os gratuitos |
| `nex-agi/nex-n2.5-pro:free` | 262k | Versão maior do anterior |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262k | 120B parâmetros |
| `dots-studio/dots-3-note-preview:free` | 512k | Contexto amplo |
| `poolside/laguna-xs-2.1:free` | 262k |  -  |
| `inclusionai/ling-3.0-flash-fin:free` | 262k | Ajustado para domínio financeiro |
| `inclusionai/ling-3.0-flash-sante:free` | 262k | Ajustado para domínio de saúde |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 1M | 550B, mais lento para uso interativo |

Revalidamos essa tabela em 2026-09-13 com o comando abaixo: **os dez identificadores continuavam no
catálogo gratuito**, dentro de um conjunto que passou de 21 para 22 modelos de custo zero, num
catálogo que cresceu de 430 para 445. É a rotatividade descrita acima acontecendo em escala pequena  -
e é a razão de a revalidação ser um comando, e não uma promessa.

Atenção a dois gratuitos que respondem, mas **não servem para programação**: `google/lyria-3-clip-preview` gera música (devolve marcações de tempo como `[4.0:8.0]` para um prompt de texto) e `nvidia/nemotron-3.5-content-safety:free` faz classificação de moderação.

Para listar os gratuitos vigentes no momento em que você ler isto, consulte o catálogo direto:

```bash
curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models \
  | python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin)['data'] if float(m['pricing']['prompt'])==0]"
```

### A cascata protegendo contra um nível quebrado

Para comprovar que a arquitetura absorve esse tipo de falha, montamos um combo de teste e colocamos deliberadamente um identificador inexistente no topo. O log do gateway registra o salto automático:

```text
[COMBO] Trying model 1/4: openrouter/exemplo/modelo-indisponivel:free
✗ ERROR 400 · "exemplo/modelo-indisponivel:free is not a valid model ID"
[COMBO] Model openrouter/exemplo/modelo-indisponivel:free failed, trying next {"status":503}
[COMBO] Trying model 2/4: groq/openai/gpt-oss-120b
[COMBO] Model groq/openai/gpt-oss-120b succeeded
```

A requisição foi respondida em **0,72s**, e o usuário do terminal não percebe nada além de uma resposta normal. O nível quebrado simplesmente deixa de ser usado  -  seja porque o identificador está errado, seja porque o modelo saiu do catálogo.

### Operando 100% gratuito

Os modelos gratuitos não são apenas rede de segurança: eles sustentam uma sessão inteira. Executamos a CLI oficial do Claude Code apontada diretamente para dois deles, sem nenhum modelo pago na rota:

```bash
claude -p "Responda apenas com o texto: ARSENAL_LIVRE_OK" \
  --model openrouter/cohere/north-mini-code:free --dangerously-skip-permissions
# ARSENAL_LIVRE_OK   (exit 0)

claude -p "Responda apenas com o texto: ARSENAL_LIVRE_OK" \
  --model openrouter/nvidia/nemotron-3.5-lightning:free --dangerously-skip-permissions
# ARSENAL_LIVRE_OK   (exit 0)
```

Se você não tem assinatura do Google AI Pro, monte sua cascata só com os identificadores da tabela acima mais o Ollama local  -  o custo de inferência é zero de ponta a ponta.

---

## O Catálogo da Mistral e o que a API Não Mostra

A Mistral entrou na cascata como o provedor em nuvem mais rápido que medimos. Testamos dez modelos da conta pelo próprio gateway, e **todos responderam**:

| Identificador | Latência medida | Perfil |
| :--- | ---: | :--- |
| `mistral/ministral-3b-latest` | 0,35s | O mais rápido entre os provedores em nuvem |
| `mistral/magistral-small-latest` | 0,38s | Raciocínio, porte pequeno |
| `mistral/ministral-8b-latest` | 0,39s | Pequeno e equilibrado |
| `mistral/mistral-vibe-cli-latest` | 0,43s | Voltado a uso em linha de comando |
| `mistral/magistral-medium-latest` | 0,45s | Raciocínio, porte médio |
| `mistral/codestral-latest` | 0,50s | **Código  -  é o que usamos na cascata** |
| `mistral/mistral-small-latest` | 0,52s | Uso geral |
| `mistral/mistral-large-latest` | 0,60s | Topo de linha |
| `mistral/mistral-medium-latest` | 0,66s | Uso geral |
| `mistral/mistral-code-latest` | 1,23s | Código, mais lento que o Codestral |

> **Latência não é cota.** Esses números medem o tempo de uma resposta curta, nada além disso. O tier gratuito de desenvolvedor da Mistral tem limites de uso próprios, que **não medimos**  -  um modelo rápido continua sujeito a `429` como qualquer outro. É por isso que ele entra como um nível da cascata, e não como fonte principal.

**Um detalhe que pode confundir:** o catálogo do gateway (`/v1/models`) lista apenas três modelos da Mistral  -  `codestral-latest`, `mistral-large-latest` e `mistral-medium-latest`  -  enquanto a API da Mistral expõe dezenas. Os demais **funcionam normalmente** mesmo sem aparecer na listagem: basta usar o identificador completo com o prefixo `mistral/`. Não se limite ao que o `/v1/models` mostra; se um modelo existe na sua conta, ele responde.

---

## Guia Prático para Obter as Chaves de API Gratuitas

Para que qualquer desenvolvedor possa reproduzir esta infraestrutura completa no seu computador, documentamos o procedimento passo a passo para obter as credenciais das cinco fontes gratuitas centrais do nosso arsenal.

### 1. Obtendo a Chave Gratuita no OpenRouter

O OpenRouter reúne centenas de modelos e mantém um subconjunto gratuito identificado pelo sufixo `:free`  -  na consulta que fizemos, 21 dos 430 modelos do catálogo tinham custo zero (22 de 445 na revalidação de 2026-09-13), entre eles o `nvidia/nemotron-3.5-lightning:free` que usamos na cascata.

1. Acesse o portal em [OpenRouter Keys](https://openrouter.ai/settings/keys).
2. Autentique-se com sua conta Google ou GitHub.
3. No painel de chaves, clique em **Create Key**.
4. Defina um nome identificador, como `claudegravity`.
5. No campo **Credit Limit (USD)**, configure o valor como `0.00`. Isso funciona como trava financeira: com limite zerado a chave não consegue consumir crédito, então só os modelos de custo zero respondem. O limite **não** garante que um modelo `:free` específico continue existindo  -  o catálogo gratuito é rotativo, e é por isso que validamos cada nível da cascata com `src/test_arsenal.py`.

![Painel de Chaves do OpenRouter com Limite Zerado](../assets/02_openrouter_dashboard_keys.png)

> **Figura 2:** Configuração da chave de API no OpenRouter com limite financeiro zerado ($0.00) para consumo exclusivo do catálogo gratuito.

6. Copie a chave gerada com o prefixo `sk-or-v1-`.

![Obtendo a Chave de API Gratuita no OpenRouter](../assets/03_openrouter_obter_api_key.png)

> **Figura 3:** Chave de API criada com sucesso no OpenRouter, pronta para conexão no 9Router.

### 2. Obtendo a Chave de Alta Velocidade no Groq Cloud

A Groq oferece inferência acelerada por chips LPU (Language Processing Units), e entregou **0,34s a 0,55s** por resposta curta com o `openai/gpt-oss-120b` no tier gratuito de desenvolvedor. Ficou logo atrás da Mistral na nossa medição, com diferença de centésimos.

1. Acesse o console da Groq em [Groq Console Keys](https://console.groq.com/keys).
2. Conecte-se com sua conta Google ou GitHub (sem necessidade de cartão de crédito).
3. Na seção **API Keys**, clique no botão **Create API Key**.
4. Atribua o nome identificador `9router-groq-lpu` e confirme.

![Criação da Chave no Groq Cloud](../assets/04_groq_dashboard_keys.png)

> **Figura 4:** Modal de criação de chave de API no console Groq Cloud.

5. Copie a chave exibida com o prefixo `gsk_` e guarde-a para a configuração do 9Router.

![Gerando a Chave de API no Groq Cloud](../assets/05_groq_obter_api_key.png)

> **Figura 5:** Chave de API da Groq Cloud revelada e copiada com sucesso.

### 3. Obtendo a Chave Direta do Gemini no Google AI Studio

O Google AI Studio fornece chaves de API diretas para a família Gemini, com cotas gratuitas que variam por modelo e são revisadas periodicamente  -  consulte os [limites vigentes](https://ai.google.dev/gemini-api/docs/rate-limits) antes de dimensionar seu uso.

1. Acesse a página de credenciais em [Google AI Studio](https://aistudio.google.com/apikey).
2. Clique no botão **Get API key** (ou **Create API key in new project**).
3. Selecione ou crie um projeto associado à sua conta Google (por exemplo, `meu-projeto-ia-001`).

![Dashboard do Google AI Studio](../assets/06_google_aistudio_dashboard.png)

> **Figura 6:** Seleção do projeto Google Cloud no painel do Google AI Studio para geração de chave.

4. Copie a chave gerada (com formato `AQ.` ou `AIzaSy`).

![Obtendo a Chave no Google AI Studio](../assets/07_google_aistudio_obter_api_key.png)

> **Figura 7:** Chave de API gratuita do Gemini no Google AI Studio exibindo a chave real gerada para o projeto.

### 4. Configurando o Ollama Local como Último Nível da Cascata

O Ollama é o componente local do arsenal. Ele roda no hardware da sua máquina ou via container Docker e cumpre um papel específico: garantir que a cascata **sempre devolva uma resposta**, mesmo com todos os provedores em nuvem indisponíveis. O gateway responde em vez de estourar erro, e a sessão não cai.

> **O que o nível local faz e o que não faz.** Testamos o harness do Claude Code contra quatro tamanhos do `qwen2.5-coder`, apontando a tag `latest` para cada um:
>
> | Modelo local | Responde ao gateway | Opera o Claude Code |
> | :--- | :--- | :--- |
> | `qwen2.5-coder:0.5b` | Sim | Não seguiu a instrução |
> | `qwen2.5-coder:1.5b` | Sim | Não seguiu a instrução |
> | `qwen2.5-coder:3b` | Sim | Não seguiu a instrução |
> | `qwen2.5-coder:7b` | Sim | Não seguiu a instrução |
>
> Todos respondem normalmente pela API (`/v1/messages`): o combo `arsenal-offline` devolve `PONG` em 0,04s. Mas o Claude Code envia um *system prompt* extenso com definições de ferramentas e exige obediência estrita a instruções mais *tool calling*, e nenhum desses modelos deu conta disso. Eles respondem qualquer coisa, não o que foi pedido.
>
> **Na prática:** o `arsenal-offline` serve para continuidade e para testar disponibilidade, não para conduzir uma sessão real de trabalho. Programar de fato sem internet exige modelo e hardware consideravelmente maiores, o que foge do escopo de uma contingência de 397 MB  -  que é exatamente o tamanho do `qwen2.5-coder:0.5b` que os comandos acima baixam (`docker exec claudegravity-ollama ollama list`, medido em 2026-09-13). Se você apontar a tag `latest` para o `1.5b`, são 986 MB pelo mesmo comando; e a primeira chamada depois de subir o container paga o carregamento na memória, como a seção do Compose mostra com número.

1. O Ollama já está declarado no `docker-compose.yml` deste módulo (seção "Execução Rápida do Gateway com Docker Compose"), então `docker compose up -d` sobe gateway e Ollama juntos. Use o comando avulso abaixo **apenas** se optar por não usar o Compose. Os dois caminhos são excludentes: disputam o mesmo nome de container e gravam em volumes distintos, porque o Compose prefixa o volume com o nome do projeto (`claudegravity_ollama_data`) enquanto o `docker run` cria um `ollama_data` sem prefixo.
   ```bash
   docker run -d --name claudegravity-ollama \
     -p 127.0.0.1:11434:11434 \
     -v ollama_data:/root/.ollama \
     ollama/ollama:latest
   ```
   A porta é publicada em `127.0.0.1` de propósito, igual ao Compose: um Ollama exposto em todas as interfaces aceita inferência de qualquer máquina da rede local, sem autenticação.
2. No seu terminal, baixe o modelo especialista em código e configure a tag padrão:
   ```bash
   docker exec -it claudegravity-ollama ollama pull qwen2.5-coder:0.5b
   docker exec claudegravity-ollama ollama cp qwen2.5-coder:0.5b qwen2.5-coder:latest
   ```
3. Valide que o serviço local está ativo e respondendo na porta `11434`:
   ```bash
   curl -s http://localhost:11434/api/tags
   ```

![Configurando o Ollama Local como Rede de Segurança](../assets/08_ollama_setup_local.png)

> **Figura 8:** Terminal demonstrando a execução do container Docker do Ollama, download e ativação do modelo Qwen 2.5 Coder.

Caso opte por utilizar também o endpoint cloud do Ollama no 9Router, obtenha sua chave de autenticação no portal [Ollama Keys](https://ollama.com/settings/keys):

![Painel de Chaves do Ollama](../assets/09_ollama_dashboard_keys.png)

> **Figura 9:** Painel de gerenciamento de chaves de API no portal do Ollama.

![Obtendo a Chave de API no Ollama](../assets/10_ollama_obter_api_key.png)

> **Figura 10:** Chave de API gerada no portal do Ollama para autenticação remota.

### 5. Obtendo a Chave da Mistral

A Mistral entra na cascata pelo `codestral-latest`, o modelo de código do provedor  -  e foi o provedor em nuvem mais rápido que medimos.

1. Acesse o console da Mistral em [console.mistral.ai](https://console.mistral.ai/) e autentique-se.
2. Na seção de chaves de API, crie uma nova chave e dê a ela um nome identificador.
3. Copie o valor gerado  -  como nos demais provedores, ele só é exibido no momento da criação.
4. Registre a chave no `.env` do módulo:
   ```bash
   MISTRAL_API_KEY=sua_chave_aqui
   ```

O `src/setup_combos.py` lê essa variável automaticamente. Se ela não existir, o script informa que o provedor foi pulado e segue provisionando os demais  -  a cascata continua funcionando, apenas sem o nível da Mistral.

---

## Configuração Visual dos Provedores e Combos no 9Router

Com as credenciais prontas, a integração no 9Router é simples e pode ser feita pelo painel gráfico (`http://localhost:20128`).

### 1. Conectando os Provedores no Painel do 9Router

No menu lateral do 9Router, clique em **Providers** (`http://localhost:20128/dashboard/providers`):

* **OpenRouter:** Clique no card do OpenRouter, visualize a cota gratuita destacada e clique em **+ Add Connection**. No modal, informe o nome e cole a chave `sk-or-v1-...`.

![Visão do Provedor OpenRouter no 9Router](../assets/11_9router_provider_openrouter.png)

> **Figura 11:** Tela de gerenciamento do provedor OpenRouter no 9Router com destaque para a cota gratuita.

![Modal para Inserção da Chave de API no 9Router](../assets/12_9router_add_connection_modal.png)

> **Figura 12:** Modal do 9Router para cadastro seguro da chave de API do provedor OpenRouter.

* **Groq Cloud:** Selecione o card da **Groq**, clique em **+ Add Connection**, insira a chave `gsk_...` e confirme. O modelo `groq/openai/gpt-oss-120b` ficará imediatamente ativo.

![Visão do Provedor Groq no 9Router](../assets/13_9router_provider_groq.png)

> **Figura 13:** Painel do provedor Groq no 9Router pronto para conexão.

* **Ollama Local:** Acesse o card do **Ollama** para verificar os modelos locais disponíveis e a conexão com a porta local `11434`.

![Visão do Provedor Ollama no 9Router](../assets/14_9router_provider_ollama.png)

> **Figura 14:** Painel de gestão do provedor local Ollama no 9Router.

* **Mistral:** Localize o card da **Mistral**, clique em **+ Add Connection** e cole a chave do console. O `mistral/codestral-latest` fica disponível em seguida.

---

### 2. Criando o Combo de Fallback no 9Router

O mecanismo central de alta disponibilidade é o **Combo com estratégia Fallback**:

1. No menu lateral, acesse **Combo & Vision Adapter** (`http://localhost:20128/dashboard/combos`).
2. Clique no botão superior **+ Create Combo**.

![Modal de Criação de Combo no 9Router](../assets/15_9router_create_combo_modal.png)

> **Figura 15:** Modal inicial para criação de novo combo virtual no 9Router.

3. Preencha os campos obrigatórios:
   * **Combo Name:** Defina o nome como `arsenal-supremo` (sem barras).
   * **Strategy:** Selecione **Fallback (tries models in order: next on failure)**.
   * **Adicionar Modelos:** Clique em **+ Add Model** e insira os modelos na ordem hierárquica da cascata.

4. Estrutura ordenada da cascata de resiliência:
   * **Nível 1:** `ag/gemini-3.8-flash-high` (Modelo primário de alto raciocínio via Antigravity)
   * **Nível 2:** `ag/gemini-3.7-flash-high` (Modelo secundário veloz)
   * **Nível 3:** `ag/gemini-3.6-flash-high` (Modelo de apoio)
   * **Nível 4:** `openrouter/cohere/north-mini-code:free` (Fallback gratuito especializado em código no OpenRouter)
   * **Nível 5:** `groq/openai/gpt-oss-120b` (Fallback de baixa latência em LPU)
   * **Nível 6:** `mistral/codestral-latest` (Fallback especializado em código)
   * **Nível 7:** `openai-compatible-chat-ollama-local/qwen2.5-coder:latest` (Continuidade local: garante resposta, não conduz a sessão)

![Estrutura da Cascata de Fallback no 9Router](../assets/16_9router_edit_combo_cascade.png)

> **Figura 16:** Painel de edição do combo `arsenal-supremo` exibindo a ordem dos modelos na cascata de transição automática.

5. Clique em **Save**. O combo ficará ativo imediatamente no dashboard.

---

## Arquitetura dos Combos de Fallback

No 9Router, agrupamos os provedores em três perfis complementares, além do `claudegravity-fallback` herdado do Artigo 0002:

![Cascata de Fallback Automático do Combo arsenal-supremo](../assets/17_diagrama_cascata_fallback.png)

> **Figura 17:** Sequência de execução e comutação automática em cascata do combo `arsenal-supremo`, exatamente na ordem provisionada por `src/setup_combos.py`: Gemini 3.8 Flash High -> Gemini 3.7 Flash High -> Gemini 3.6 Flash High -> Cohere North Mini Code (OpenRouter) -> GPT-OSS 120B (Groq LPU) -> Codestral (Mistral) -> Ollama Local.


### Combo 1 - `arsenal-supremo` (Resiliência Máxima)

A cadeia principal para trabalho pesado diário, com os sete níveis listados acima. As latências abaixo foram medidas por `src/test_arsenal.py` contra cada nível isoladamente, em um ambiente recriado do zero:

| Nível | Modelo | Papel | Latência medida |
| :---: | :--- | :--- | ---: |
| 1 | `ag/gemini-3.8-flash-high` | Máxima capacidade analítica | 1,30s |
| 2 | `ag/gemini-3.7-flash-high` | Raciocínio balanceado | 1,15s |
| 3 | `ag/gemini-3.6-flash-high` | Baixa latência | 0,70s |
| 4 | `openrouter/cohere/north-mini-code:free` | Fallback gratuito especialista em código | 0,93s |
| 5 | `groq/openai/gpt-oss-120b` | Velocidade bruta em LPU | 0,34s |
| 6 | `mistral/codestral-latest` | Especialista em código | 1,29s |
| 7 | `openai-compatible-chat-ollama-local/qwen2.5-coder:latest` | Continuidade local | 8,77s a frio · 0,05s a quente |

> **Fonte:** `src/test_arsenal.py`, executado em 2026-09-13. A saída completa está na seção
> [Validação de Inferência dos Combos](#validação-de-inferência-dos-combos).

> **Estes números são um retrato, não uma constante.** São latências de uma resposta curta, colhidas
> numa execução, contra provedores em nuvem cuja carga varia ao longo do dia  -  o `codestral-latest`,
> por exemplo, mediu 0,54s na cascata do `arsenal-rapido` e 1,29s na do `arsenal-supremo`, na mesma
> execução. Sirva-se deles para ordem de grandeza; para decidir ordem de cascata, meça no seu ambiente
> com o mesmo comando.

Repare que os níveis não estão em ordem de velocidade, e isso é proposital: a cascata é ordenada por **capacidade**, não por latência. O Cohere North Mini Code no nível 4 entrega especialização de sintaxe e código sem custo; os mais rápidos em nuvem ficam abaixo porque servem melhor como rede de contenção rápida do que como motor principal.

### Combo 2 - `arsenal-rapido` (Iteração e Testes Ágeis)
Projetado para ciclos curtos de teste e revisão de sintaxe, priorizando baixa latência **sem abrir mão de capacidade**:
1. `groq/openai/gpt-oss-120b`
2. `mistral/codestral-latest`
3. `ag/gemini-3.7-flash-high`
4. `ag/gemini-3.6-flash-high`

> **Por que não colocar o modelo mais rápido no topo?** O `mistral/ministral-3b-latest` foi o mais veloz da rodada em que medimos o catálogo da Mistral (0,35s, contra 0,44s do GPT-OSS 120B naquela mesma rodada). A diferença é de centésimos, e some no ruído: na revalidação de 2026-09-13 o próprio GPT-OSS 120B mediu **0,34s**, abaixo daquele 0,35s. Centésimos são imperceptíveis em um ciclo agêntico  -  o tempo real é dominado pela geração da resposta, não pelo primeiro byte. Um modelo de 3B no topo de um combo que alimenta o Claude Code troca uma diferença invisível por uma perda enorme de capacidade de raciocínio e de chamada de ferramentas. Velocidade só vale quando o resultado presta.

### Combo 3 - `arsenal-offline` (Continuidade Local)
Para manter o gateway respondendo em conexões instáveis ou ambientes sem tráfego externo:
1. `openai-compatible-chat-ollama-local/qwen2.5-coder:latest`

Use-o para continuidade e verificação de disponibilidade. Como mostramos na seção do Ollama, um modelo local pequeno responde à requisição mas não conduz uma sessão de trabalho do Claude Code.

![Dashboard de Combos no 9Router](../assets/18_9router_combos.png)

> **Figura 18:** Gestão de combos cadastrados (claudegravity-fallback, arsenal-supremo, arsenal-rapido e arsenal-offline) no painel web do 9Router em `http://localhost:20128/dashboard/combos`.

![Dashboard de Endpoints no 9Router](../assets/19_9router_dashboard_endpoint.png)

> **Figura 19:** Painel de chaves de API e porta local do 9Router em `http://localhost:20128/dashboard`.

---

## Execução Rápida do Gateway com Docker Compose

O módulo inclui um manifesto unificado pronto para provisionamento do gateway e da instância local de LLM:

```yaml
name: claudegravity

services:
  # Servico, container e hostname com o MESMO nome. Nao e estetica: o nome do
  # servico e o que outra stack usa para alcancar este container pela rede, e
  # quando os tres divergem voce le `9router` no compose, `claudegravity-router`
  # no `docker ps` e um terceiro nome no erro de DNS. E o padrao dos projetos
  # 9RTKSync / OminiRTkSync / LiteLlmRTKSync.
  claudegravity-router:
    # 9Router: Gateway oficial de conexões e modelos (https://github.com/decolua/9router)
    image: decolua/9router:latest
    container_name: claudegravity-router
    hostname: claudegravity-router
    restart: unless-stopped
    ports:
      # Apenas localhost: o gateway carrega credenciais reais e nao deve ficar acessivel na rede local.
      - "127.0.0.1:20128:20128"
    environment:
      - DATA_DIR=/app/data
      - PORT=20128
      - HOSTNAME=0.0.0.0
      - NEXT_PUBLIC_BASE_URL=http://localhost:20128
      - NODE_ENV=production
      - INITIAL_PASSWORD=${INITIAL_PASSWORD:?defina INITIAL_PASSWORD no .env}
      - JWT_SECRET=${JWT_SECRET:?defina JWT_SECRET no .env}
      - REQUIRE_API_KEY=${REQUIRE_API_KEY:-false}
      - REQUIRE_LOGIN=${REQUIRE_LOGIN:-false}
    command: ["/bin/sh", "-c", "cp /app/open-sse/providers/shared.js /app/data/shared.js 2>/dev/null || true; exec node server.js"]
    volumes:
      - 9router_data:/app/data
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      claudegravity-ollama:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "node -e \"require('http').get('http://127.0.0.1:20128/dashboard',r=>process.exit(r.statusCode<500?0:1)).on('error',()=>process.exit(1))\""]
      interval: 15s
      timeout: 5s
      retries: 5
      start_period: 20s

  claudegravity-ollama:
    image: ollama/ollama:latest
    container_name: claudegravity-ollama
    hostname: claudegravity-ollama
    restart: unless-stopped
    ports:
      - "127.0.0.1:11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    healthcheck:
      test: ["CMD-SHELL", "ollama list >/dev/null 2>&1 || exit 1"]
      interval: 15s
      timeout: 5s
      retries: 5

  router-sync:
    # 9RTKSync: 9Router Universal Token & Connection Synchronizer (https://github.com/pathbit/9RTKSync)
    image: ghcr.io/pathbit/9rtksync:latest
    container_name: router-sync
    hostname: router-sync
    restart: unless-stopped
    # NAO acrescente `user: "1000:1000"` aqui copiando do compose de exemplo do
    # 9RTKSync. `${HOME}` entra em /root/host, e /root e 0700 root: com uid 1000
    # o `ls /root/host` devolve "Permission denied" e a descoberta de credencial
    # do host morre em silencio -- o /healthz continua 200, porque so testa o
    # servidor web. A corrida de permissao no volume que motivou aquele `user:`
    # nao existe aqui: o `condition: service_healthy` abaixo faz o gateway criar
    # db/ e logs/ com o dono certo antes de este servico tocar no volume.
    ports:
      # 9090 dentro do container; 9190 no host. A faixa 909x fica para as
      # stacks dos repositorios (9091/9092/9093) -- assim a stack do artigo
      # e as dos tres sincronizadores sobem juntas sem disputar porta.
      - "127.0.0.1:9190:9090"
    volumes:
      - 9router_data:/app/data
      - ${HOME}:/root/host:ro
    environment:
      - PYTHONUNBUFFERED=1
      - HOST_HOME=/root/host
      - DB_PATH=/app/data/db/data.sqlite
      # Resolve pelo nome do servico, que aqui e igual ao do container.
      - ROUTER_URL=http://claudegravity-router:20128
      - SYNC_INTERVAL=300
      - REFRESH_MARGIN=900
      - MODULE=0003
      - ENABLE_WEB_DASHBOARD=1
      - WEB_PORT=9090
      # O painel exige autenticacao. Sem estas duas variaveis a stack sobe, mas
      # o navegador responde 401 e nao ha senha documentada para informar.
      # Sem valor de fallback de proposito: uma senha publicada em arquivo de
      # exemplo vira a senha real de toda implantacao que so copiou e colou.
      - DASHBOARD_USER=${DASHBOARD_USER:-admin}
      - DASHBOARD_PASSWORD=${DASHBOARD_PASSWORD:?defina DASHBOARD_PASSWORD no .env}
    depends_on:
      claudegravity-router:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "/opt/venv/bin/python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:9090/healthz', timeout=3)"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 10s

volumes:
  9router_data:
  ollama_data:
```

Seis detalhes de arquitetura essenciais foram incorporados neste manifesto:
1. **Serviço, `container_name` e `hostname` com o mesmo nome:** o nome do **serviço** é o que o DNS interno do Compose resolve; o `container_name` é o que aparece no `docker ps`. Quando divergem, você lê um nome no manifesto e outro no terminal, e perde tempo até perceber que são a mesma coisa. É o padrão dos projetos [9RTKSync](https://github.com/pathbit/9RTKSync), [OminiRTkSync](https://github.com/pathbit/OminiRTkSync) e [LiteLlmRTKSync](https://github.com/pathbit/LiteLlmRTKSync), e é por isso que o `ROUTER_URL` do sidecar aponta para `http://claudegravity-router:20128`. O [Artigo 0002](../../0002_claude_gravity_utilizando_9router/article/ARTICLE.md) detalha a mesma decisão.
2. **Compatibilidade Multiplataforma (`extra_hosts`):** A diretiva `host.docker.internal:host-gateway` garante que sistemas Linux mapeiem corretamente o gateway de rede para o host, assegurando paridade idêntica entre Linux, macOS e Windows WSL2.
3. **Streaming Nativo SSE com Ollama Local:** O 9Router consome a API compatível da OpenAI exposta pelo Ollama em `http://host.docker.internal:11434/v1` via nós `openai-compatible-*`. Ao contrário da rota proprietária `/api/chat` (que emite `application/x-ndjson`), a rota `/v1/chat/completions` entrega Server-Sent Events (`text/event-stream`), garantindo streaming nativo na inferência local. A diferença entre chamada fria e quente é grande, e aparece na mesma execução do validador: o nível local respondeu em **8,77s** na primeira chamada  -  que carrega o modelo na memória  -  e em **0,05s** na chamada seguinte, alguns segundos depois `[FONTE: src/test_arsenal.py, executado em 2026-09-13; as duas linhas estão no bloco de saída mais adiante]`. Se você medir uma latência alta no nível 7, meça de novo antes de concluir que algo está errado.
4. **Segredos fora do manifesto e ordem de subida:** `INITIAL_PASSWORD` e `JWT_SECRET` são lidos do `.env` (a sintaxe `${VAR:?mensagem}` aborta o `up` com um erro claro se a variável faltar), e os `healthcheck` combinados ao `depends_on: service_healthy` garantem que o 9Router só suba depois que o Ollama estiver respondendo  -  eliminando a corrida que obrigava a inserir esperas manuais nos scripts.
5. **O sidecar roda como root, e isso é deliberado:** o `${HOME}` da sua máquina entra no container em `/root/host`, e `/root` é `0700 root` na imagem. Com `user: "1000:1000"` o `ls /root/host` devolve `Permission denied` e a descoberta de credencial do host morre **em silêncio**, porque o `/healthz` continua respondendo `200` (ele só testa o servidor web). O compose de exemplo do próprio 9RTKSync traz esse `user:` para resolver uma corrida de permissão no volume compartilhado  -  corrida que aqui não existe, porque o `condition: service_healthy` faz o gateway criar `db/` e `logs/` com o dono certo antes de o sidecar tocar no volume. Não copie aquela linha para cá sem antes mover o mount para fora de `/root`.
6. **Guardião de Conexões sem Quedas (`router-sync`):** O container oficial [9RTKSync](https://github.com/pathbit/9RTKSync) (*9Router Universal Token & Connection Synchronizer*) roda isolado em virtual environment dedicado (`/opt/venv`) e garante a longevidade dos tokens Google Antigravity e combos multi-provedor. A cada 5 minutos ele valida a credencial no SQLite compartilhado, auto-cura divergências de datas e efetua a renovação preventiva via Google OAuth antes que ocorram erros 503 ou expiração de 1 hora. O consumo medido nesta máquina foi de **27,53 MiB de RAM** (`docker stats --no-stream router-sync`, em 2026-09-13)  -  barato, mas não desprezível: o Ollama ao lado ocupa 1,3 GiB.

Para subir a infraestrutura completa em segundo plano:

> **Se você já tinha uma stack anterior de pé, derrube antes.** Os serviços foram renomeados para
> bater com o nome do container (`9router` → `claudegravity-router`, `9rtksync` → `router-sync`,
> `ollama` → `claudegravity-ollama`). Para o Compose, serviço renomeado é serviço **novo**: ele não
> atualiza o container existente, tenta criar outro com o mesmo nome, e o `--dry-run` mostra
> `Creating` mais um aviso de `orphan containers`. Rode `docker compose down` antes deste `up`. Nada
> se perde: `9router_data` e `ollama_data` são volumes nomeados, então o SQLite do gateway e o modelo
> baixado no Ollama sobrevivem ao ciclo.

```bash
docker compose up -d

# Conferir status dos 3 containers (gateway, ollama e sidecar de tokens)
docker compose ps --format 'table {{.Name}}\t{{.Status}}'

# Acompanhar logs da auto-renovacao preventiva de tokens
docker logs -f router-sync
```

Saída real desta máquina, com a stack de pé:

```text
NAME                   STATUS
claudegravity-ollama   Up 32 hours (healthy)
claudegravity-router   Up 32 hours (healthy)
router-sync            Up 27 hours (healthy)
```

> **Não use `docker ps --filter "name=claudegravity"` aqui.** O sidecar chama-se `router-sync`, sem o
> prefixo, e o filtro por nome devolve **dois** containers em vez de três  -  escondendo justamente o
> que você quer vigiar. O `docker compose ps` lista pelo projeto e não depende de convenção de nome.

Para efetuar o download do modelo leve de contingência no Ollama:

```bash
docker exec -it claudegravity-ollama ollama pull qwen2.5-coder:0.5b
docker exec claudegravity-ollama ollama cp qwen2.5-coder:0.5b qwen2.5-coder:latest
```

> **Quando outro proxy precisa alcançar este gateway.** Esta stack sobe numa rede só, a
> `claudegravity_default` que o Compose cria sozinho, e isso basta enquanto o cliente do gateway é o
> Claude Code rodando no host. Ao empilhar um segundo proxy em contêiner na frente dele  -  o caso do
> LiteLLM, na [Conclusão](#conclusão-e-artigos-relacionados)  -  as duas stacks isoladas não se
> enxergam. A resposta dos projetos RTKSync é uma rede de inferência compartilhada, criada fora do
> ciclo de vida de qualquer stack:
>
> ```bash
> docker network create rtk-inference-net
> docker network connect rtk-inference-net claudegravity-router
> ```
>
> Só gateways entram nela; os sincronizadores ficam de fora, na rede de gestão. A rede **não** é
> declarada neste `docker-compose.yml` de propósito: como `external: true` ela viraria pré-requisito
> obrigatório e faria `docker compose up -d` falhar para quem nunca vai encadear proxy. O
> [Artigo 0002](../../0002_claude_gravity_utilizando_9router/article/ARTICLE.md) detalha o raciocínio.

> **Os dois comandos são necessários.** A cascata referencia a tag `qwen2.5-coder:latest`, e o `pull` grava apenas `qwen2.5-coder:0.5b`. Sem o `cp`, o `setup_combos.py` acusa `Modelos ausentes no Ollama local` e o último nível do `arsenal-supremo` fica sem servir. Como o modelo mora no volume do container, o passo se repete toda vez que você destrói o ambiente.

![Container Docker do 9Router em Execução](../assets/20_docker_container.png)

> **Figura 20:** Containers Docker `claudegravity-router`, `claudegravity-ollama` e o sidecar `router-sync` ativos e testes de provisionamento dos combos executados com sucesso.

---

## Provisionamento Automatizado de Combos via Python

Para desenvolvedores que preferem evitar cliques manuais na interface gráfica, disponibilizamos o script `src/setup_combos.py`. Ele injeta as definições dos quatro combos diretamente na base SQLite do 9Router:

```bash
python3 src/setup_combos.py
```

Trecho final da saída:

```text
[*] Provisionando combos no container claudegravity-router...
  [+] Combo cadastrado: claudegravity-fallback (5 modelos)
  [+] Combo cadastrado: arsenal-supremo (7 modelos)
  [+] Combo cadastrado: arsenal-rapido (4 modelos)
  [+] Combo cadastrado: arsenal-offline (1 modelos)
[*] Provisionamento concluído com sucesso!
```

---

## Validação de Inferência dos Combos

Antes de iniciar sua jornada de código, execute o teste de ponta a ponta com `src/test_arsenal.py`:

```bash
python3 src/test_arsenal.py
```

O script exercita **cada nível isoladamente** antes de testar o combo. É essa separação que
importa: um combo pode responder pelo primeiro nível e esconder que os seis seguintes estão mortos.

```text
=== Validador do Arsenal de Fallback do 9Router ===
    Gateway: http://claudegravity-router:20128

[*] Cascata de 'arsenal-supremo' - 7 nível(is):
  [OK   ] 1º ag/gemini-3.8-flash-high - 1.30s · 'PONG'
  [OK   ] 2º ag/gemini-3.7-flash-high - 1.15s · 'PONG'
  [OK   ] 3º ag/gemini-3.6-flash-high - 0.70s · 'PONG'
  [OK   ] 4º openrouter/cohere/north-mini-code:free - 0.93s · 'PONG'
  [OK   ] 5º groq/openai/gpt-oss-120b - 0.34s · 'PONG'
  [OK   ] 6º mistral/codestral-latest - 1.29s · 'PONG'
  [OK   ] 7º openai-compatible-chat-ollama-local/qwen2.5-coder:latest - 8.77s · 'PONG'
  [OK   ] combo 'arsenal-supremo' - 3.54s · 'PONG'

[*] Cascata de 'arsenal-rapido' - 4 nível(is):
  [OK   ] 1º groq/openai/gpt-oss-120b - 0.40s · 'PONG'
  [OK   ] 2º mistral/codestral-latest - 0.54s · 'PONG'
  [OK   ] 3º ag/gemini-3.7-flash-high - 1.25s · 'PONG'
  [OK   ] 4º ag/gemini-3.6-flash-high - 0.68s · 'PONG'
  [OK   ] combo 'arsenal-rapido' - 0.39s · 'PONG'

[*] Cascata de 'arsenal-offline' - 1 nível(is):
  [OK   ] 1º openai-compatible-chat-ollama-local/qwen2.5-coder:latest - 0.05s · 'PONG'
  [OK   ] combo 'arsenal-offline' - 0.05s · 'PONG'

======================================================================
RESUMO
======================================================================
  Níveis testados: 12 · quebrados: 0
  Combos testados: 3 · com falha: 0

[*] Todos os níveis e todos os combos responderam corretamente.
```

> **Fonte:** `src/test_arsenal.py`, executado em 2026-09-13 contra a stack deste artigo, pelo
> container de testes  -  daí a linha `Gateway:` mostrar o nome do serviço em vez de `localhost`.
> Rodando no host com `python3 src/test_arsenal.py`, ela exibe `http://localhost:20128`.

**Repare no nível 7: 8,77 s, e no mesmo modelo 0,05 s poucos segundos depois.** Não é instabilidade, e
não é defeito: a primeira chamada carrega o modelo na memória, as seguintes não. É a única latência da
tabela que muda por duas ordens de grandeza entre duas execuções seguidas, e é exatamente o tipo de
coisa que o teste nível a nível revela e o teste do combo esconde  -  o combo responde pelo primeiro
nível e nunca chega no sétimo.

O restante da cascata ficou entre 0,34 s e 1,30 s, sem nenhum nível quebrado. Vale contrastar com o
que este mesmo teste pega quando algo sai do catálogo: o nível não fica lento, ele **falha**, e o
script marca a linha. Um combo que responde não prova nada sobre os níveis abaixo do primeiro; por
isso o passo 2 da validação é o que dá segurança de verdade.

> **Uma observação sobre a obediência do modelo local.** Nesta execução os três combos devolveram
> `'PONG'` limpo, mas em execuções anteriores o mesmo nível local devolveu `'PONG.'` e `'**PONG**'`  -
> o modelo pequeno responde por perto, não exatamente. Com o validador isso é ruído; dentro do harness
> do Claude Code, que exige obediência estrita mais chamada de ferramenta, é o que reprova o
> `arsenal-offline` para qualquer papel fixo.

---

## Laboratório de Simulação de Fallback e Resiliência Multi-Cenários

Para garantir que a arquitetura opere de forma previsível em situações adversas de produção, desenvolvemos um laboratório completo de testes automatizados no script `src/simulate_fallback.py`. Ele simula falhas reais de infraestrutura, incluindo saturação de taxa e desautenticação do provedor primário, comprovando que o Claude Code segue operando com estabilidade.

O simulador avalia cinco cenários operacionais e encerra com um resumo explícito de aprovados, falhos e pulados. O código de saída só é zero quando todos os cenários executados passam.

### 1. Cenário Nominal (Antigravity Autenticado)
Valida a comunicação direta e via combo no modelo primário `ag/gemini-3.8-flash-high`. O 9Router registra a tentativa inicial e o retorno imediato com status HTTP 200 e latência próxima a 1 segundo.

### 2. Cenário de Rate Limit e Salto Automático (Hop)
Cria um combo de teste temporário no qual o primeiro modelo é apontado para um identificador saturado que responde com erro 429 ou 404. O motor de roteamento do 9Router intercepta o erro através da função `checkFallbackError`, aplica a regra de contingência e comuta para o modelo subsequente da cadeia, entregando a resposta com sucesso HTTP 200 sem interromper a sessão do usuário. A comutação não é instantânea: o gateway ainda aplica sua política de retentativa com espera progressiva antes de desistir de um nível. A requisição que precisou saltar de nível respondeu em **2,01s** de ponta a ponta na execução de 2026-09-13 (3,25s numa execução anterior)  -  o que o leitor percebe é uma resposta um pouco mais lenta, nunca uma sessão interrompida.

### 3. Cenário de Logout e Token Inválido no Antigravity
Simula a situação em que a conta Google é desconectada ou o token OAuth expira. O script altera temporariamente o token no banco SQLite para uma credencial inválida. Ao tentar acessar diretamente o modelo deslogado, o gateway barra a chamada com o status esperado HTTP 503 / 401 (`[AUTH] HTTP 401`). Em combos com rotas alternativas, o 9Router salta para o próximo provedor disponível da lista.

### 4. Cenário de Auto-Cura e Restauração

> Para sessões longas e contínuas, o container oficial `router-sync` (já embutido no `docker-compose.yml` e rodando a imagem oficial `ghcr.io/pathbit/9rtksync:latest` em virtual environment dedicado) gerencia de ponta a ponta as conexões e combos do [9Router](https://github.com/decolua/9router) a cada 5 minutos, inspecionando o SQLite e auto-renovando as credenciais 15 minutos antes da expiração. O projeto oficial [9RTKSync](https://github.com/pathbit/9RTKSync) (*9Router Universal Token & Connection Synchronizer*) elimina travamentos e mantém um dashboard web em tempo real em `http://localhost:9190`. O [Artigo 0002](../../0002_claude_gravity_utilizando_9router/article/ARTICLE.md) detalha a causa raiz da expiração e da normalização de formatos.

Aciona o utilitário `sync_antigravity_token.py`, que renova o access token via Google OAuth e restabelece a conexão primária. O script limpa quaisquer travas residuais de rate limit e dispara uma nova requisição, confirmando que o canal com o Gemini 3.8 Flash High volta a responder instantaneamente.

### 5. Cenário de Execução Real no Claude Code CLI
Executa uma chamada direta através do binário oficial da CLI (`claude -p ... --model arsenal-supremo --dangerously-skip-permissions`), provando que a integração com o terminal de desenvolvimento do engenheiro está 100% funcional. Quando o binário `claude` não está instalado na máquina, o cenário é registrado como **pulado**, e não como aprovado.

Ao final, o script restaura as credenciais originais do Antigravity e confere se a restauração realmente foi aplicada, avisando explicitamente caso o estado divirja do backup.

Para executar a suíte de simulação:

```bash
python3 src/simulate_fallback.py
```

> **O cenário 3 mexe no banco.** Ele grava um token inválido na tabela `providerConnections` para
> provar que o gateway barra a chamada, e restaura no fim  -  o próprio script confere a restauração e
> avisa se o estado divergir do backup. Não rode com uma sessão longa em andamento na mesma stack: a
> janela é de segundos, mas existe. Se algo interromper o script no meio, `python3
> ../0002_claude_gravity_utilizando_9router/src/sync_antigravity_token.py` restabelece a credencial.

O resumo final de uma execução completa nesta máquina:

```text
======================================================================
🔬 RESULTADO FINAL DA SUÍTE DE RESILIÊNCIA
======================================================================
  ✅ PASSOU  · Cenário 1 · Estado nominal - HTTP 200 em 1.42s
  ✅ PASSOU  · Cenário 2 · Salto de fallback - HTTP 200 em 2.01s
  ✅ PASSOU  · Cenário 3 · Bloqueio sob token inválido - HTTP 503
  ✅ PASSOU  · Cenário 4 · Auto-cura - HTTP 200 em 1.24s
  ✅ PASSOU  · Cenário 5 · Claude Code CLI - 5.70s

  Total: 5 aprovado(s), 0 falha(s), 0 pulado(s).

[*] Todos os cenários executados foram aprovados.
```

`[FONTE: src/simulate_fallback.py, executado em 2026-09-13 contra a stack deste artigo]`

O cenário 3 merece ver a evidência, porque é o único em que o sucesso **é** um erro. O gateway
devolveu o bloqueio com a causa nomeada, e o log do 9Router registrou a recusa do upstream:

```text
  ✅ Comportamento esperado confirmado: gateway barrou a chamada com HTTP 503!
     Motivo retornado: {"error":{"message":"[antigravity/gemini-3.8-flash-high] [401]: HTTP 401 (reset after 2m)"}}

  📋 Evidência do log do 9Router registrando a desautenticação:
     [01:31:48] 🔴 ✗ ERROR 401 · antigravity/gemini-3.8-flash-high · 3427ms
```

E o cenário 4 mostra a auto-cura fechando o ciclo, com o caminho da credencial que ela leu:

```text
[*] Credencial detectada em: /Users/elielsousa/.gemini/jetski-standalone-oauth-token
[+] Access token renovado com sucesso (validade: 3599s)
[+] Credenciais Antigravity injetadas no container claudegravity-router com sucesso!
  ✅ Canal primário restabelecido com sucesso (HTTP 200) em 1.24s
```

![Laboratório de Simulação de Fallback e Resiliência Multi-Cenários](../assets/21_simulacao_fallback_laboratorio.png)

> **Figura 21:** Execução da suíte automatizada de testes `simulate_fallback.py` comprovando comutação de modelos, proteção contra desautenticação e retorno íntegro no Claude Code CLI.

---

## Configuração do Claude Code com Autonomia Completa

Para que o Claude Code use os modelos do Antigravity como padrão e deixe os combos `arsenal-*` a um `/model` de distância, estruturamos modelos de configuração exclusivamente dentro da pasta de testes do artigo (`examples/.claude/`). Para inicializar suas configurações locais:

```bash
cp examples/.claude/settings.json.example examples/.claude/settings.json
cp .env.example .env
```

> **Sobre a chave `sk-sua-chave-do-9router` nos exemplos.** É um placeholder. A chave real é **gerada localmente** na primeira execução de `sync_antigravity_token.py` (artigo 0002): um valor aleatório exclusivo da sua máquina, registrado no gateway e gravado no `.env` do módulo, que não é versionado. Substitua o placeholder pela chave que o script imprimir. Os utilitários deste artigo (`test_arsenal.py`, `arsenal_launcher.py`, `simulate_fallback.py`) interrompem a execução com instruções caso a variável `ANTHROPIC_API_KEY` não esteja definida  -  de propósito, para que nenhuma chave publicada funcione como padrão silencioso.

### O que preencher no `.env`

O `.env.example` traz dezenas de variáveis, mas a maioria já vem com valor que funciona. Só estas exigem sua atenção:

| Variável | Obrigatória? | O que colocar |
| :--- | :--- | :--- |
| `INITIAL_PASSWORD` | **Sim** | Senha do painel do 9Router. O `docker compose` recusa subir sem ela. |
| `JWT_SECRET` | **Sim** | Valor longo e aleatório para assinar as sessões do painel. Gere com `openssl rand -hex 32`. |
| `ANTHROPIC_API_KEY` | **Sim** | Não invente: é impressa pelo `sync_antigravity_token.py` na primeira execução e gravada aqui. No `.env` ela alimenta os scripts Python; no `settings.json` o mesmo valor entra como `ANTHROPIC_AUTH_TOKEN`. |
| `MISTRAL_API_KEY` | Sim, para a cascata completa | Console da Mistral. Alimenta o nível 6 do `arsenal-supremo` e o nível 2 do `arsenal-rapido`. |
| `GROQ_API_KEY` | Sim, para a cascata completa | `console.groq.com/keys`. Alimenta o nível 5 do `arsenal-supremo`. |
| `OPENROUTER_API_KEY` | Sim, para a cascata completa | `openrouter.ai/settings/keys`, com limite `$0.00`. Alimenta o nível 4. |
| `GEMINI_API_KEY` | Opcional | Conexão direta com o Google AI Studio, fora dos combos de referência. |
| `CEREBRAS_API_KEY` | Não | Documentada como fonte adicional; nenhum combo deste artigo a utiliza. |

Sem as chaves de provedor, o `setup_combos.py` pula a conexão correspondente e informa o motivo  -  a cascata continua funcionando com os níveis restantes, apenas mais curta.

> **Cuidado com os papéis de modelo.** As variáveis `ANTHROPIC_DEFAULT_FABLE_MODEL`, `_OPUS_MODEL`, `_SONNET_MODEL` e `_HAIKU_MODEL` dizem ao Claude Code qual modelo usar em cada classe de tarefa. Nos arquivos deste artigo elas apontam para modelos individuais do Antigravity, e os combos continuam acessíveis por `/model arsenal-supremo` (o menu customizado tem a ressalva da seção seguinte)  -  a comparação entre os dois arranjos está no [Artigo 0002](../../0002_claude_gravity_utilizando_9router/article/ARTICLE.md#modelo-individual-ou-combo-e-a-escolha-do-padrão). **Não coloque `arsenal-offline` em nenhuma delas, nem como padrão:** o modelo local responde ao gateway, mas não segue instruções dentro do harness, e as tarefas daquele papel falhariam sem erro visível.

### O arquivo de configuração do Claude Code

Ele fica em `examples/.claude/settings.json`, isolado do restante do repositório  -  por isso não interfere no projeto em que você estiver trabalhando. É versionado apenas na forma `.example`; a cópia ativa fica fora do controle de versão.

É a configuração do projeto, compartilhável com o time: modelo padrão, papéis de modelo, `modelPicker`, `modelOverrides`, permissões e variáveis de ambiente.

**Por que não há um `settings.local.json` aqui.** O Claude Code lê também `.claude/settings.local.json`, com precedência sobre o `settings.json`, mas a função dele é guardar o que é específico da sua máquina e não pode ir para o git (uma chave pessoal, um caminho local). Neste artigo não existe nada nessa categoria: tudo o que a configuração precisa está no arquivo único acima, e a cópia ativa já fica fora do controle de versão. Uma cópia idêntica no arquivo local só criaria dois lugares para manter a mesma coisa. E o bloco `modelPicker` não seria motivo para tê-lo: a CLI só honra esse bloco em `~/.claude/settings.json`, em settings gerenciadas ou via `--settings`; em um checkout de projeto ele é ignorado tanto no `settings.json` quanto no `settings.local.json`. Para ter o menu `/model` customizado, copie o bloco `modelPicker` para o arquivo de usuário.

### O que fica no estado global do Claude Code (e como não depender dele)

Tudo o que este artigo configura mora em `examples/.claude/settings.json`. Mas o Claude Code guarda **fora do projeto**, em `~/.claude.json`, um estado que nenhuma chave de `settings.json` altera, por desenho:

| O que | Onde fica | O que zera |
| :--- | :--- | :--- |
| Assistente de primeiro uso concluído (tema, notas de segurança) | `~/.claude.json` | `/logout`, ou uma instalação nova |
| Login na conta Anthropic | `~/.claude.json` + chaveiro do sistema | `/logout` |
| Aprovação de uma `ANTHROPIC_API_KEY` vinda do `env` (pergunta *"Do you want to use this API key?"*) | `~/.claude.json` | `/logout` |
| Confiança na pasta (*"Do you trust the files in this folder?"*) | `~/.claude.json`, por caminho absoluto | Renomear ou mover a pasta |

Verificamos no binário da versão 2.1.268 (17 de setembro de 2026): o `/logout` marca o assistente como não concluído e apaga a lista de chaves aprovadas. Foi exatamente isso que produziu o sintoma "entro na pasta e ele fica pedindo login": o assistente reaparece, e **enquanto ele roda, o `settings.json` do projeto ainda não foi carregado**. Medimos com uma configuração global zerada: mesmo com a pasta já confiável e o arquivo completo, o assistente mostrou a tela *"Select login method"*. O arquivo do projeto só entra depois do assistente e da confirmação de confiança.

Duas decisões deixam este projeto imune a esse estado:

1. **`ANTHROPIC_AUTH_TOKEN` no lugar de `ANTHROPIC_API_KEY`.** As duas autenticam no 9Router (o middleware lê `Authorization: Bearer` antes de `x-api-key`); a diferença é o que a CLI faz com cada uma. `ANTHROPIC_API_KEY` exige uma aprovação interativa única, guardada em `~/.claude.json` e apagada pelo `/logout` (medimos: com a chave não aprovada, pasta confiável e assistente concluído, a pergunta reaparece). `ANTHROPIC_AUTH_TOKEN` vai direto para o cabeçalho `Authorization: Bearer`, sem aprovação nem estado global. É [documentada](https://code.claude.com/docs/en/env-vars) para exatamente isso. Confirmamos que o 9Router lê esse cabeçalho.
2. **Na primeira execução, ou depois de um `/logout`, inicie com `--settings`:**

   ```bash
   claude --settings .claude/settings.json
   ```

   A flag é [documentada](https://code.claude.com/docs/en/settings#change-a-setting-for-one-session) e aplica o arquivo **antes** do assistente. Medimos com configuração global zerada: a sequência foi tema, notas de segurança, confiança na pasta e o prompt, sem nenhuma tela de login. Depois disso a pasta fica confiável, e o `claude` puro passa a carregar o `settings.json` do projeto em toda sessão. Um efeito colateral bem-vindo: com `--settings`, a CLI também honra o bloco `modelPicker`, que ela ignora quando vem do checkout do projeto.

O que **não** dá para evitar por configuração de projeto: a escolha de tema e as notas de segurança na primeira execução, e a pergunta de confiança em cada pasta nova. São telas de um `Enter` cada, nunca pedem login, e é assim que a CLI protege quem abre um repositório desconhecido.

> **Se o Claude Code pedir login nesta pasta**, a ordem de verificação é: (1) o JSON do `settings.json` é válido? Uma vírgula sobrando faz a CLI descartar o arquivo em silêncio; (2) o assistente de primeiro uso está aparecendo? Saia dele com `claude --settings .claude/settings.json`; (3) a pasta foi renomeada? Aceite a confiança de novo.

### Estrutura do `settings.json.example`

```json
{
  "model": "ag/gemini-3.8-flash-high",
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:20128",
    "ANTHROPIC_AUTH_TOKEN": "sk-sua-chave-do-9router",
    "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "ag/gemini-3.8-flash-high",
    "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME": "Gemini 3.8 Flash High (Opus)",
    "ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION": "Primario: raciocinio alto, 1M de contexto",
    "ANTHROPIC_DEFAULT_FABLE_MODEL": "ag/gemini-pro-agent",
    "ANTHROPIC_DEFAULT_FABLE_MODEL_NAME": "Gemini 3.1 Pro High (Fable)",
    "ANTHROPIC_DEFAULT_FABLE_MODEL_DESCRIPTION": "O mais denso da conta: use com parcimonia",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "ag/gemini-3.7-flash-high",
    "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME": "Gemini 3.7 Flash High (Sonnet)",
    "ANTHROPIC_DEFAULT_SONNET_MODEL_DESCRIPTION": "Trabalho corrente",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "ag/gemini-3.6-flash-high",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME": "Gemini 3.6 Flash High (Haiku)",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_DESCRIPTION": "Latencia minima, alta frequencia",
    "ANTHROPIC_MODEL": "ag/gemini-3.8-flash-high",
    "CLAUDE_CODE_DISABLE_ADVISOR_TOOL": "1"
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
  "modelPicker": {
    "replaceBuiltInOptions": true,
    "options": [
      {
        "model": "ag/gemini-3.8-flash-high",
        "label": "Gemini 3.8 Flash High",
        "description": "Primario do Antigravity",
        "behavesAs": "claude-sonnet-4-6"
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
        "description": "Latencia minima",
        "behavesAs": "claude-haiku-4-5-20251001"
      },
      {
        "model": "groq/openai/gpt-oss-120b",
        "label": "GPT-OSS 120B (Groq)",
        "description": "LPU, resposta em fracao de segundo",
        "behavesAs": "claude-sonnet-4-6"
      },
      {
        "model": "mistral/codestral-latest",
        "label": "Codestral (Mistral)",
        "description": "Especialista em codigo",
        "behavesAs": "claude-sonnet-4-6"
      },
      {
        "model": "arsenal-supremo",
        "label": "Arsenal Supremo (combo)",
        "description": "7 niveis, do Gemini ao Ollama local",
        "behavesAs": "claude-sonnet-4-6"
      },
      {
        "model": "arsenal-rapido",
        "label": "Arsenal Rapido (combo)",
        "description": "4 niveis, otimizado para latencia",
        "behavesAs": "claude-sonnet-4-6"
      },
      {
        "model": "arsenal-offline",
        "label": "Arsenal Offline (combo)",
        "description": "So Ollama local. Responde sempre, nao opera o harness",
        "behavesAs": "claude-haiku-4-5-20251001"
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

> [!IMPORTANT]
> ### Por que o Advisor fica desligado (`"CLAUDE_CODE_DISABLE_ADVISOR_TOOL": "1"`)
>
> Não é economia nem esquecimento: **o advisor não funciona com nenhum modelo servido fora da API da Anthropic, e ligá-lo derruba a sessão.** Ele é uma *server tool* executada pelo servidor da Anthropic; um gateway ou provedor alternativo recebe um tipo de ferramenta que não conhece e rejeita a requisição inteira. Nenhuma outra chave (`advisorModel`, `modelOverrides`, papéis `ANTHROPIC_DEFAULT_*_MODEL`) contorna isso: elas só escolhem **qual** modelo entra na ferramenta, não **quem** a executa. Por isso `"CLAUDE_CODE_DISABLE_ADVISOR_TOOL": "1"` está em **todos** os arquivos deste artigo. O mecanismo, o erro exato devolvido pelo DeepSeek e o motivo do menu `/advisor` duplicar linhas estão no aviso `[!CAUTION]` da seção [Três blocos que merecem explicação](#três-blocos-que-merecem-explicação-modelpicker-behavesas-e-o-advisor), mais abaixo.

O bloco `modelOverrides` tem **três entradas, uma por família**. Ele cobre um caso específico: um
`~/.claude/settings.json` (onde o menu `/model` grava a escolha) que ficou apontando para um modelo escolhido antes de você
trocar a configuração. Não é preciso duplicar com o sufixo de janela (`[1m]`): a CLI normaliza o
identificador antes de consultar o mapa. O [Artigo 0002](../../0002_claude_gravity_utilizando_9router/article/ARTICLE.md)
detalha a medição que levou a esse formato enxuto.

#### Os quatro papéis e para onde eles apontam

O Claude Code escolhe sozinho qual modelo usar em cada situação, através de quatro papéis. A ordem
de capacidade vem da própria CLI: *Fable for the hardest problems, Opus for complex work, Sonnet for
most tasks, Haiku for quick questions*. Cada papel tem sua variável:

| Papel | Variável | Aponta para | Quando é acionado |
| :--- | :--- | :--- | :--- |
| Fable | `ANTHROPIC_DEFAULT_FABLE_MODEL` | `ag/gemini-pro-agent` | O que a CLI considerar mais difícil |
| Opus | `ANTHROPIC_DEFAULT_OPUS_MODEL` | `ag/gemini-3.8-flash-high` | Trabalho complexo e **todo subagente despachado** |
| Sonnet | `ANTHROPIC_DEFAULT_SONNET_MODEL` | `ag/gemini-3.7-flash-high` | A maior parte das tarefas |
| Haiku | `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `ag/gemini-3.6-flash-high` | Alta frequência: **toda sessão**, para nomear a conversa |

São modelos individuais, e não os combos  -  a mesma escolha do [Artigo 0002](../../0002_claude_gravity_utilizando_9router/article/ARTICLE.md#modelo-individual-ou-combo-e-a-escolha-do-padrão),
pelo mesmo motivo: consumo previsível. Os combos `arsenal-*` continuam a um `/model arsenal-supremo` de distância (ver a ressalva sobre `modelPicker` adiante),
e nada impede apontar um papel para eles se você preferir resiliência a previsibilidade.

Descobrir qual papel atende o quê não exige adivinhação. Aponte cada papel para um modelo diferente e
leia o log do gateway: ele registra `modelo pedido → modelo servido`. A CLI ainda ajuda, emitindo uma
linha de diagnóstico com o campo `query_source`, que nomeia quem fez o pedido:

| `query_source` | Papel acionado |
| :--- | :--- |
| `sdk` | modelo principal |
| `generate_session_title` | **Haiku**, em toda sessão |
| `agent:builtin:Explore` | **Opus** |

A segunda linha surpreende: **subagentes não usam o papel rápido, usam o de trabalho complexo.** Se
sua rotina despacha subagentes, é o Opus que domina o seu consumo, não o modelo principal.

### Três blocos que merecem explicação: `modelPicker`, `behavesAs` e o advisor

Os três estão no `settings.json` acima. Nenhum deles exige um `settings.local.json`; a razão está na seção
[O arquivo de configuração do Claude Code](#o-arquivo-de-configuração-do-claude-code).

- **`modelPicker`** popula o menu `/model`. Com **`replaceBuiltInOptions` em `true`**, suas entradas
  **substituem** a lista nativa em vez de somar a ela: o menu passa a oferecer apenas os seus combos,
  e não há como selecionar por engano um modelo que o seu gateway não serve. Vale a ressalva da seção
  [O arquivo de configuração do Claude Code](#o-arquivo-de-configuração-do-claude-code): no checkout do projeto o bloco é ignorado; ele só vale em `~/.claude/settings.json` ou via `--settings`.
- **`behavesAs`** em cada linha diz à CLI qual modelo conhecido serve de referência de capacidade
  para aquele combo. Mapeamos com `"claude-sonnet-4-6"` para evitar que a verificação de direitos de conta (`Lbn`)
  da CLI filtre ou oculte os modelos caso sua conta local Anthropic não possua assinatura com cota de Opus liberada.
- **Advisor desligado** com `"CLAUDE_CODE_DISABLE_ADVISOR_TOOL": "1"` no bloco `env`. O advisor é uma
  *server tool* executada pela API da Anthropic, e nenhum gateway a implementa; o detalhe está no aviso abaixo.

> [!CAUTION]
> ### O Advisor (`/advisor`) não funciona com modelos de terceiros
>
> O advisor **não é uma chamada extra feita pela CLI**. Ele é uma *server tool* da API da Anthropic: a cada requisição, o Claude Code acrescenta ao array `tools` um bloco `{"type": "advisor_20260301", "name": "advisor", "model": "<modelo escolhido>"}`, e é o **servidor da Anthropic** que decide quando consultar o modelo revisor, executa a consulta e devolve o resultado em blocos `advisor_result`. A [documentação oficial](https://code.claude.com/docs/en/advisor) é explícita: *"the advisor runs server-side on Anthropic's infrastructure as a server tool"* e *"requires the Anthropic API"*.
>
> Consequências com `ANTHROPIC_BASE_URL` apontando para um gateway ou provedor alternativo:
>
> 1. **O provedor recebe um tipo de ferramenta que não conhece.** A API do DeepSeek, por exemplo, responde `400 invalid_request_error: tools[0]: unknown variant advisor_20260301, expected web_search_20250305 or web_search_20260209`, e a requisição inteira falha, não só o advisor. Um gateway local que traduz para outro provedor tem o mesmo problema: ninguém fora da Anthropic executa esse bloco.
> 2. **Nenhuma configuração muda isso.** `advisorModel`, `modelOverrides` e os papéis `ANTHROPIC_DEFAULT_*_MODEL` só escolhem **qual** modelo vai dentro do bloco; quem executa continua sendo a Anthropic. Não é uma questão de `WebSearch`: o DeepSeek até aceita as *server tools* `web_search_*`; o que ele não tem é o advisor.
> 3. **O menu `/advisor` engana.** Ele lista apenas os aliases `fable`, `opus` e `sonnet` e nomeia cada linha pelo modelo em que o alias resolve. Se dois papéis, ou duas entradas de `modelOverrides`, apontam para o mesmo modelo do provedor, o menu mostra duas linhas com o mesmo nome (o "Fable" duplicado, sem nenhum "Opus"). É sintoma da mesma limitação: nada ali funcionaria de qualquer forma.
>
> **Como desligar de verdade:** no bloco `env` dos arquivos de configuração use `"CLAUDE_CODE_DISABLE_ADVISOR_TOOL": "1"`. Essa é a chave de desligamento documentada: remove o comando `/advisor` e impede que o bloco seja anexado, mesmo que exista um `advisorModel` salvo em `~/.claude/settings.json` de uma sessão antiga. Não use `CLAUDE_CODE_ENABLE_EXPERIMENTAL_ADVISOR_TOOL: "0"`: a CLI trata a variável como booleano, e `"0"` equivale a não defini-la; ela só serve, com `"1"`, para **liberar** o modo experimental. Tampouco é preciso `"advisorModel": ""`; com o recurso desligado a chave é ignorada.

Com essa estrutura, quando o Claude Code solicita o modelo padrão de raciocínio, o 9Router recebe a requisição com o identificador `arsenal-supremo`. Ele envia o prompt para o Gemini 3.8 Flash; caso o rate limit por minuto seja alcançado, o gateway salta automaticamente para o Gemini 3.7 Flash e, sucessivamente, até o último nível local.

### Validando a configuração

Três comandos, em ordem, confirmam que tudo está de pé antes de você começar a trabalhar:

```bash
# 1. Provisiona provedores e combos a partir das chaves do .env
python3 src/setup_combos.py

# 2. Testa cada nível de cada cascata isoladamente e acusa identificador quebrado
python3 src/test_arsenal.py

# 3. Exercita o harness real do Claude Code contra o combo padrão
claude -p "Responda apenas: OK" --model arsenal-supremo --dangerously-skip-permissions
```

O passo 2 é o que dá segurança de verdade: ele não se contenta em ver o combo responder, porque um combo responde pelo primeiro nível mesmo com todos os outros quebrados. Ao testar nível a nível, ele acusa exatamente qual identificador saiu do catálogo.

---

## Show-Me-The-Code

O artigo disponibiliza uma malha resiliente completa de infraestrutura e execução que entrega:

- orquestração unificada via Docker Compose com 9Router e Ollama para contingência offline;
- provisionamento automatizado de combos no banco de dados SQLite sem necessidade de cliques manuais;
- suíte de testes de resiliência com 5 cenários reais (operação nominal, salto de rate limit, erro 401, auto-cura e execução no CLI);
- ambiente prático e isolado (`examples/`) com configurações prontas do Claude Code (`.claude/`) e script de teste (`sample_task.py`);
- launcher dedicado em Python (`arsenal_launcher.py`) para execução direta do Claude Code no sandbox de exemplos.

**Opção 1** Execute o ambiente e a suíte de testes de resiliência localmente pelo terminal.

[**Abrir README.md com instruções locais**](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0003_fallback_modelos_gratuitos_9router/README.md)

**Opção 2** Execute o código de testes e interaja com o Claude Code diretamente no ambiente prático isolado (`examples/`).

[**Abrir pasta de exemplos e testes práticos**](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0003_fallback_modelos_gratuitos_9router/examples/README.md)

### Pré-requisitos do Ambiente e Credenciais

Antes de rodar os scripts de provisionamento e iniciar a cascata com o Claude Code, configure os seguintes componentes na sua máquina:

1. **Python 3.14.7 (Recomendado) ou Superior (mínimo 3.10):**
   - Recomendamos a versão oficial: [Python 3.14.7](https://www.python.org/ftp/python/3.14.7/python-3.14.7-macos11.pkg) (pacote instalador macOS).
   - Verifique com `python3 --version`. Se necessário, instale via pacote oficial [Python 3.14.7](https://www.python.org/ftp/python/3.14.7/python-3.14.7-macos11.pkg) ou `brew install python` (macOS), `sudo apt install python3 python3-venv python3-pip` (Linux) ou `winget install Python.Python.3.14` (Windows).
   - Crie o ambiente virtual e instale o ambiente (o módulo roda só com a biblioteca padrão do Python):
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate  # No Windows: .venv\Scripts\Activate.ps1
     pip install -r requirements.txt
     ```

2. **Docker e Docker Compose:**
   - Necessário para executar os serviços do 9Router e do Ollama local em containers. Instale via Docker Desktop (macOS/Windows) ou script oficial no Linux (`curl -fsSL https://get.docker.com | sh`).
   - Garanta que os containers estejam em execução com `docker compose up -d`.

3. **Node.js e Claude Code CLI:**
   - Instale Node.js 18+ e a ferramenta oficial da Anthropic globalmente:
     ```bash
     npm install -g @anthropic-ai/claude-code
     ```
   - Verifique com `claude --version`.

4. **Credenciais e Chaves Gratuitas:**
   - **OpenRouter:** Obtenha sua API Key em [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys) e configure limite financeiro de `$0.00` para restringir chamadas apenas aos modelos gratuitos (`:free`).
   - **Groq Cloud:** Obtenha sua chave gratuita com prefixo `gsk_...` em [console.groq.com/keys](https://console.groq.com/keys).
   - **Google AI Studio:** Obtenha sua chave gratuita em [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
   - **Mistral AI:** Obtenha sua chave gratuita em [console.mistral.ai/api-keys](https://console.mistral.ai/api-keys).
   - **Ollama Local:** Não exige chave externa, sendo executado diretamente no container local via Docker Compose.

### Executando os Scripts de Provisionamento e Teste

```bash
# 1. Provisionar combos no gateway
python3 src/setup_combos.py

# 2. Testar inferência dos combos
python3 src/test_arsenal.py

# 3. Executar o laboratório completo de simulação de falhas
python3 src/simulate_fallback.py

# 4. Iniciar o Claude Code conectado ao Arsenal Supremo
python3 src/arsenal_launcher.py
```

Ou diretamente pelo terminal:

```bash
# macOS e Linux (bash / zsh)
export ANTHROPIC_BASE_URL="http://localhost:20128"
export ANTHROPIC_AUTH_TOKEN="sk-sua-chave-do-9router"

claude --dangerously-skip-permissions --model arsenal-supremo

# Windows (PowerShell)
$env:ANTHROPIC_BASE_URL="http://localhost:20128"
$env:ANTHROPIC_AUTH_TOKEN="sk-sua-chave-do-9router"

claude --dangerously-skip-permissions --model arsenal-supremo
```

![Claude Code Operando com Combo Arsenal Supremo](../assets/22_claude_arsenal_terminal.png)

> **Figura 22:** Sessão autônoma do Claude Code operando sob o combo `arsenal-supremo`, roteando via 9Router com latência reduzida e zero custo de inferência.

---

## Boas Práticas para Operação Perpétua sem Custos

Para garantir estabilidade contínua ao longo de semanas de trabalho:

1. **Priorize Modelos de Raciocínio no Topo do Combo:** Modelos como o Gemini 3.8 Flash High devem ficar nas primeiras posições porque mantêm a capacidade de planejamento agêntico do Claude Code em alto nível. Reserve os níveis gratuitos de contexto amplo, como o `nemotron-3.5-lightning:free`, para o meio da cascata.
2. **Revalide a Cascata Periodicamente:** modelos gratuitos são descontinuados sem aviso, e um nível quebrado no meio da cascata só aparece quando os anteriores também falham. Rode `python3 src/test_arsenal.py` de tempos em tempos: ele testa cada nível isoladamente e acusa qualquer identificador que tenha saído do catálogo.
3. **Utilize o Ollama como Última Barreira de Proteção:** ter o `openai-compatible-chat-ollama-local/qwen2.5-coder:latest` como nível final assegura que a cascata nunca termine em erro, mesmo com todos os provedores em nuvem fora do ar. Trate-o como garantia de continuidade, não como substituto: um modelo local pequeno não sustenta uma sessão de trabalho do Claude Code.
4. **Mantenha Chaves de Provedores Distintas:** Crie contas específicas para desenvolvimento na Groq, OpenRouter e Google AI Studio para manter as cotas gratuitas isoladas e com monitoramento independente no dashboard do 9Router.
5. **Separe a Saída de Rede por Conta:** a prática nº 4 multiplica as contas — e é aí que aparece um risco que não vem da cascata, mas do gateway. Várias sessões na **mesma** conta são aceitas pelos provedores; o que destoa é o inverso: **várias contas saindo pelo mesmo IP**, que é o comportamento natural de um gateway com todas elas cadastradas. Para o provedor, isso tem o formato de uma revenda de acesso.

   Uma armadilha comum: **Tailscale não resolve isso sozinho**. Um exit node dá endereço estável ao *host*, não a cada conta — com cinco contas no mesmo gateway, as cinco continuam saindo pelo mesmo lugar. O que separa contas é o **vínculo por conta**, e não a tecnologia que gerou o endereço (VPS, proxy residencial ou segundo link servem igual).

   O 9Router já modela isso: os endereços ficam em `proxyPools` e o vínculo vive **dentro de cada conexão**, em `providerSpecificData.proxyPoolId` + `connectionProxyEnabled`. Um pool por conta fixa a saída daquela conta, sem rotação. O painel do [9RTKSync](https://github.com/pathbit/9RTKSync) mostra o vínculo em modo somente leitura — *saída própria* ou *divide o endereço do gateway com N contas*, este último só a partir da segunda conta nessa situação —, para você enxergar quais contas dividem endereço antes que vire problema — a consulta está em [Egress and Multi-Session](https://github.com/pathbit/9RTKSync/wiki/Egress-And-Multi-Session). O [Artigo 0002](../../0002_claude_gravity_utilizando_9router/article/ARTICLE.md) detalha o mecanismo e o passo a passo.
6. **Beneficie-se da Compressão RTK:** O 9Router traz filtros dedicados para saídas de `git diff`, `git status`, `git log`, `grep`, `tree`, `ls`, `find` e builds, ativos por padrão. Eles cortam o ruído repetitivo que o agente reenvia a cada turno e prolongam a vida útil de qualquer limite de taxa. A economia depende do tipo de saída que suas tarefas produzem  -  não medimos um percentual próprio, então trate qualquer número divulgado como estimativa até validar no seu fluxo.
7. **Dimensione pela trava, não pelo palpite:** a cascata multi-provedor é, em termos de dimensionamento, a alavanca mais barata que existe  -  ela multiplica a capacidade efetiva **sem comprar conta nova**, porque a cota é contabilizada por conta e, no Antigravity, por **família de modelo**. É a mesma propriedade que faz o nível 4 continuar respondendo quando os três primeiros caem. O que ela não faz é dizer se o número de contas acertou.

   E aqui vale repetir o padrão da casa: os tetos dos tiers gratuitos deste artigo **não foram medidos**  -  a seção do [catálogo da Mistral](#o-catálogo-da-mistral-e-o-que-a-api-não-mostra) já registra que latência não é cota, e nenhum dos provedores gratuitos publica capacidade absoluta. Então a unidade honesta não é requisição por minuto: é a **trava** que o gateway grava quando o teto chega, em `rateLimitedUntil` (conta inteira) e `modelLock_*` (por família). Com a stack de pé, a leitura sai em um comando  -  o gateway é o mesmo para os dois módulos:

   ```bash
   # a partir da pasta do modulo 0002, que versiona o script
   python3 src/quota_locks.py
   ```

   Conte as travas por conta por dia durante uma semana: nível que trava todo dia precisa de reforço acima dele na cascata, e conta que nunca trava é folga. A fórmula completa, com as variáveis, a medição do consumo real e o que fica em aberto por não ser publicado, está em [Quantas Contas para Quantos Desenvolvedores](../../0002_claude_gravity_utilizando_9router/article/ARTICLE.md#5-quantas-contas-para-quantos-desenvolvedores), no Artigo 0002.

---

## Conclusão e Artigos Relacionados

Ao desacoplar a camada de execução (Claude Code CLI) da camada de inferência e conectá-la a uma malha de múltiplos provedores orquestrada pelo 9Router, você elimina a maior barreira operacional da programação assistida por inteligência artificial: a vulnerabilidade a limites de cota e interrupções de serviço.

Para aprofundar na infraestrutura de permissões irrestritas do Google Antigravity, acesse o [Artigo 0001 - Google Antigravity com Acesso Total Irrestrito e sem Interrupções](../../0001_antigravity_acesso_total_irrestrito/article/ARTICLE.md).

Para aprofundar na configuração específica do Google Antigravity e na engenharia de tradução de chamadas do Claude Code, acesse o [Artigo 0002 - ClaudeGravity e o Roteamento de Modelos Gemini no Claude Code via 9Router](../../0002_claude_gravity_utilizando_9router/article/ARTICLE.md).

**Onde a cascata deste artigo encontra o seu limite.** Tudo o que foi montado aqui responde à pergunta "de onde sai o próximo token quando esta conta acabar". Nenhuma linha responde a outra, que aparece assim que mais de uma pessoa usa a mesma montagem: *quem* consumiu o quê, e como impedir que uma pessoa sozinha esgote a cota do time antes do almoço. O 9Router escolhe a conta; ele não reparte a cota entre pessoas.

Quem precisa disso põe um segundo proxy na frente — o LiteLLM trata o 9Router como se fosse um provedor comum, porque a API dele é compatível com OpenAI, e acrescenta por cima chave virtual por pessoa, orçamento por chave e teto de requisições por minuto. A cascata continua igual, embaixo; o que muda é que passa a existir um lugar onde se responde "quem paga a conta". O passo a passo está em [Chaining Gateways](https://github.com/pathbit/LiteLlmRTKSync/wiki/Chaining-Gateways).

---

## Referências Técnicas

- [9Router GitHub Repository](https://github.com/decolua/9router)
- [9RTKSync: 9Router Universal Token & Connection Synchronizer](https://github.com/pathbit/9RTKSync)
- [OminiRTKSync: OminiRoute Universal Token & Connection Synchronizer](https://github.com/pathbit/OminiRTkSync)
- [OmniRoute Gateway Repository](https://github.com/diegosouzapw/OmniRoute)
- [Claude Code Settings & Permissions Official Guide](https://code.claude.com/docs/en/settings)
- [Anthropic Messages API Reference](https://docs.anthropic.com/en/api/messages)
- [Groq Cloud Documentation](https://console.groq.com/docs)
- [Google AI Studio Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [OpenRouter Models Catalog](https://openrouter.ai/models)
- [Ollama Open Source LLM Runner](https://ollama.com)

---

## 📄 Licença

Distribuído sob a Licença MIT. O texto completo está em [LICENSE](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/LICENSE).

Na prática: use, copie, altere e redistribua à vontade, inclusive comercialmente, desde que o aviso de copyright e a licença acompanhem as cópias. O software é fornecido como está, sem garantias.

---

Desenvolvido com ❤️ pela [Pathbit](https://pathbit.co/)
