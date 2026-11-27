# OpenCode com 9Router e Ollama — Como saber para onde seu pedido foi

![Capa do artigo sobre seleção de modelos no OpenCode](../assets/00_capa.png)

← [0008 · Claude Code e Git Worktrees](../../0008_claude_code_worktrees/article/ARTICLE.md) · [Índice da série](../../README.md) · [0010 · Playwright MCP no Agregador](../../0010_playwright_mcp_agregador/article/ARTICLE.md) →

## O texto chegou. De onde ele veio?

Você configura o OpenCode para usar um combo do 9Router e conecta um modelo local do Ollama. Abre o Agregador e pede uma explicação da rota de favoritos. O terminal mostra uma resposta perfeitamente plausível. O trecho explica a mesma rota que você conhece. Ainda falta resolver a pergunta operacional: qual endpoint recebeu o arquivo?

Há três decisões diferentes. O OpenCode seleciona um provedor e um identificador de modelo. O 9Router pode aplicar uma política própria depois de receber a requisição. O Ollama carrega e executa o modelo da tag solicitada. Uma resposta em linguagem natural apresenta o conteúdo gerado. Quem operou o transporte precisa de outra coisa para identificar a rota.

O [artigo 0003](../../0003_fallback_modelos_gratuitos_9router/article/ARTICLE.md) entra na cascata de provedores. O foco aqui é a fronteira logo antes dela. Vamos configurar duas rotas no mesmo cliente, verificar o caminho HTTP e o identificador enviado a cada uma e só então ligar serviços reais. Dá para completar a primeira etapa com Python e OpenCode, sem comprar crédito de modelo nem disponibilizar um trecho do projeto.

## A diferença entre selecionar, rotear e executar

![Fluxo da seleção de modelo até o recibo HTTP](../assets/01_roteamento_modelos.png)

| Decisão | Onde acontece | Evidência prática |
| --- | --- | --- |
| Qual provedor recebeu a seleção | OpenCode lê `--model provedor/id` e a configuração do projeto | Enumeração da configuração e nome selecionado no comando |
| Qual URL recebeu o pedido | Cliente monta a URL em torno de `baseURL` | Log do serviço receptor ou sonda local |
| Qual identificador chegou | Corpo JSON do pedido de geração | Contrato da sonda ou log de requisição com o campo `model` |
| Qual membro do combo atendeu | Política e estado do 9Router | Telemetria da própria instância para aquele pedido |
| Qual peso foi carregado localmente | Ollama resolve a tag instalada | Catálogo, modelos carregados e informações de execução do Ollama |
| Qual resposta atende à tarefa | Avaliação do desenvolvedor, testes e métricas da tarefa | Diff revisado ou resposta comparada ao contrato do projeto |

O identificador `router/pathbit-code` significa que o OpenCode selecionou o provedor `router` e passou `pathbit-code` como modelo. Na instância real, esse identificador pode ser um combo com vários membros. O CLI só conhece o endereço e o identificador inicial. A trilha do gateway é onde se comprova eventual fallback.

`local/qwen2.5-coder:7b` seleciona outra entrada de configuração. O trecho com o dois-pontos faz parte da tag do Ollama. Uma instalação com `qwen2.5-coder:3b`, por exemplo, tem outra tag e precisa usar o mesmo valor na chamada e na configuração.

## O que uma API compatível resolve

O [arquivo de configuração](../examples/opencode.json.example) registra duas entradas em `providers`. As duas usam o adaptador `@opencode/ai/providers/openai-compatible`. Isso dá ao cliente uma forma compartilhada de montar pedidos de completions. Implantações reais ainda podem oferecer conjuntos diferentes de modelos, chamadas de ferramenta e comportamento de streaming.

| Entrada | Identificador de sessão | Base do laboratório | Da configuração ao serviço real |
| --- | --- | --- | --- |
| `router` | `router/pathbit-code` | `http://127.0.0.1:19809/router/v1` | `PATHBIT_ROUTER_BASE` aponta à API do seu gateway e `PATHBIT_ROUTER_KEY` vem da sessão |
| `local` | `local/qwen2.5-coder:7b` | `http://127.0.0.1:19809/local/v1` | `PATHBIT_OLLAMA_BASE` aponta à API loopback e o valor `ollama` é usado com o serviço local padrão |

A configuração completa usa o nome do provedor como chave e lista somente o modelo que cada destino deve receber. Este é o mesmo conteúdo do exemplo versionado.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "providers": {
    "router": {
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": {
        "baseURL": "{env:PATHBIT_ROUTER_BASE}",
        "apiKey": "{env:PATHBIT_ROUTER_KEY}"
      },
      "models": {
        "pathbit-code": { "name": "Pathbit Code" }
      }
    },
    "local": {
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": {
        "baseURL": "{env:PATHBIT_OLLAMA_BASE}",
        "apiKey": "ollama"
      },
      "models": {
        "qwen2.5-coder:7b": { "name": "Qwen 2.5 Coder 7B" }
      }
    }
  }
}
```

Leia cada entrada de fora para dentro. Em `router/pathbit-code`, `router` resolve `providers.router` e `pathbit-code` resolve a chave em `models`. O nome de exibição `Pathbit Code` ajuda a reconhecer a opção na interface. Ele pode mudar sem transformar o ID aceito pelo endpoint. A interpolação `{env:PATHBIT_ROUTER_BASE}` deixa o endereço fora do arquivo versionado e `{env:PATHBIT_ROUTER_KEY}` faz o mesmo com a credencial.

Ao adaptar o exemplo para outro projeto, mantenha nomes distintos para os provedores e comece com uma tag em cada um. Se duas entradas chamarem destinos diferentes, escolha explicitamente com `--model provedor/id` durante o diagnóstico. O ID de uma delas pode coincidir com o de outra. A chave do provedor é que identifica a configuração de transporte.

A opção `--standalone` usada aqui mantém a execução no modo local do próprio CLI. Rode a partir do diretório que contém o `opencode.json`. Em um workspace que já configura plugins ou outras fontes de configuração, comece por reproduzir o erro no diretório temporário. Quando a sonda responde nesse diretório e falha no projeto, compare o modelo selecionado, o endereço resolvido e a configuração encontrada em cada ambiente.

O padrão de URI no laboratório deixa os destinatários distintos em uma única porta. O adaptador acrescenta a rota `/chat/completions`. Ao trocar pela instância real, a base normalmente termina em `/v1`. Guarde no exemplo somente os nomes das variáveis e deixe a chave real no ambiente da sessão. Se a instância Ollama tem um proxy autenticado, use a forma de autenticação que ele exige.

É tentador modificar o arquivo global para que o combo esteja em todos os projetos. Neste primeiro exercício, a configuração vive num diretório temporário. Dá para reproduzir as chamadas sem misturar plugins, configurações ou chaves do seu workspace habitual. Depois de validar os contratos, use a configuração de projeto onde fizer sentido e mantenha as credenciais fora do Git. [Documentação de provedores no OpenCode](https://opencode.ai/docs/providers/) · [Compatibilidade OpenAI no Ollama](https://docs.ollama.com/api/openai-compatibility)

## Passo 1 · Suba um destino com respostas conhecidas

Use Python 3.10+ e OpenCode 2.4.x. A reprodução nas capturas foi feita com OpenCode 2.4.1. Na raiz do repositório da série, inicie a sonda num terminal.

```bash
python3 0009_opencode_9router_ollama/examples/probe_server.py --port 19809
```

A sonda escuta em `127.0.0.1`. Ela conhece dois pares e rejeita combinações que não reconhece. Cada caminho tem um modelo de catálogo e um recibo fixo. Esse acoplamento é a parte importante do exemplo. Um servidor que simplesmente devolve `OK` a tudo daria um falso positivo quando o cliente enviou a tag errada à rota certa.

| Caminho recebido | Campo `model` esperado | Conteúdo devolvido |
| --- | --- | --- |
| `/router/v1/chat/completions` | `pathbit-code` | `PATHBIT_ROUTER_OK` |
| `/local/v1/chat/completions` | `qwen2.5-coder:7b` | `PATHBIT_LOCAL_OK` |

Fora desses caminhos a sonda devolve `404`. Um corpo inválido ou um modelo que não corresponde ao caminho resulta em `400`. A sonda implementa JSON e SSE para que o mesmo experimento aceite uma requisição sem stream ou aquela que pede respostas em eventos. Seu código cabe num arquivo e pode ser lido lado a lado com o terminal. [Código da sonda](../examples/probe_server.py)

## Passo 2 · Abra o cliente em um diretório de laboratório

Em outro terminal, a partir da raiz da série, crie a configuração de projeto. `lab-only` é uma credencial fictícia de demonstração. Os três endereços são locais e usam o servidor que acabamos de iniciar.

```bash
lab=$(mktemp -d)
cp 0009_opencode_9router_ollama/examples/opencode.json.example "$lab/opencode.json"
cd "$lab"
export PATHBIT_ROUTER_BASE=http://127.0.0.1:19809/router/v1
export PATHBIT_ROUTER_KEY=lab-only
export PATHBIT_OLLAMA_BASE=http://127.0.0.1:19809/local/v1
opencode --standalone run --model router/pathbit-code 'Return only a route receipt.'
opencode --standalone run --model local/qwen2.5-coder:7b 'Return only a route receipt.'
```

A primeira execução devolveu `PATHBIT_ROUTER_OK`. A segunda devolveu `PATHBIT_LOCAL_OK`. Observe que o prompt era o mesmo nas duas sessões. A diferença vem da seleção de provedor e da checagem no servidor. Na captura da sonda a porta foi escolhida dinamicamente para a execução e os caminhos continuam os mesmos.

![Exemplo do OpenCode com os recibos router e local](../assets/02_respostas_cli.png)

O log HTTP registra o caminho e o código de estado. Nesta versão do cliente foram observados dois `POST` para cada caminho. Isso descreve a execução capturada. Para validar sua configuração, procure a associação entre rota, ID e recibo, sem acoplar o teste ao número de chamadas internas que uma versão do cliente decide realizar.

![Rotas HTTP de exemplo esperadas em cada prefixo](../assets/03_trafego_sonda.png)

## Antes de mudar o destino, veja a sonda falhar

Os dois recibos demonstram os caminhos felizes. Uma checagem de controle ajuda a descobrir o que o laboratório realmente distingue. Com a sonda do passo 1 em execução, mande o modelo local ao caminho conhecido do roteador. O mesmo servidor também pode receber o identificador correto em um caminho propositalmente inexistente.

```bash
probe=http://127.0.0.1:19809
curl -sS -i -H 'Content-Type: application/json' \
  -d '{"model":"pathbit-code"}' "$probe/router/v1/chat/completions"
curl -sS -i -H 'Content-Type: application/json' \
  -d '{"model":"qwen2.5-coder:7b"}' "$probe/router/v1/chat/completions"
curl -sS -i -H 'Content-Type: application/json' \
  -d '{"model":"pathbit-code"}' "$probe/invalido/v1/chat/completions"
```

![Respostas HTTP esperadas dos casos aceito, modelo incorreto e rota inexistente](../assets/04_controles_sonda.png)

Essas três chamadas retornaram `200`, `400` com `Expected model pathbit-code` e `404` com `Unknown route`. O segundo erro diz que o caminho chegou ao handler correto, mas o corpo não cumpriu seu contrato. O terceiro erro interrompe a chamada antes de interpretar o modelo. Use essa diferença para decidir se deve abrir o arquivo de configuração na entrada `models` ou no endereço da URL.

### O que o recibo prova quando a resposta chega em pedaços

O cliente e o servidor podem negociar respostas em eventos. A sonda emite `text/event-stream` e encerra a sequência com `[DONE]` se o pedido traz `stream:true`. No modo JSON, devolve uma resposta de completions com uma única mensagem. A verificação do `model` ocorre antes de escolher a representação. É por isso que o código de erro serve às duas formas de chamada.

Em um serviço real, é possível receber `200` e ainda ficar sem texto se o adaptador não interpretar o último evento. Isso pede revisar a compatibilidade de streaming e o registro do cliente. Já um erro de modelo da sonda acontece antes de produzir os eventos. Manter cada controle pequeno ajuda a fechar um problema sem atribuir a causa à camada errada.

## Passo 3 · Mude um destino por vez

Assim que o circuito com a sonda funcionar, troque primeiro o gateway ou primeiro o Ollama. Deixe o outro na sonda até entender um novo resultado por vez. O [roteiro de serviços reais](../examples/README.md) reúne os comandos de consulta e exemplos de sessão.

### Ligar o 9Router

Use o endereço da instância que você administra e a chave com escopo para esse combo. No exemplo local, a API está em `http://127.0.0.1:20128/v1`. Consulte o catálogo antes de rodar a sessão. É possível conferir o ID sem procurar a chave em logs ou colá-la no projeto.

```bash
export PATHBIT_ROUTER_BASE=http://127.0.0.1:20128/v1
curl -fsS -H "Authorization: Bearer $PATHBIT_ROUTER_KEY" "$PATHBIT_ROUTER_BASE/models"
opencode --standalone run --model router/pathbit-code 'Responda apenas OK.'
```

Esses comandos pressupõem `PATHBIT_ROUTER_KEY` configurada para a sua instância. Substitua o valor de demonstração com o passo protegido do roteiro. Se o catálogo expõe outro ID de combo, altere a chave em `providers.router.models` e o identificador no `--model`. Uma execução bem-sucedida deixa você procurar a mesma transação na instância do gateway, inclusive para identificar qual membro do combo respondeu.

### Ligar o Ollama

O Ollama precisa estar em execução no endereço de loopback configurado. Verifique a existência da tag antes de pedir uma inferência. `ollama pull` baixa o modelo e tem seu próprio custo de tempo e armazenamento.

```bash
export PATHBIT_OLLAMA_BASE=http://127.0.0.1:11434/v1
ollama pull qwen2.5-coder:7b
ollama list
opencode --standalone run --model local/qwen2.5-coder:7b 'Responda apenas OK.'
```

A qualidade, a velocidade, o volume de memória e a aceitação de ferramentas podem variar com modelo, hardware e cliente. Faça um pedido simples antes de abrir código ou ativar ferramentas. Se a máquina alterna entre projetos, verifique qual modelo está carregado. Uma falha de memória ao iniciar pesa de modo diferente de uma tag ausente no catálogo.

## Passo 4 · Faça a mesma pergunta sobre código em dois destinos

Quando ambos os destinos autorizados funcionarem, prepare uma [cópia de laboratório do Agregador](../../0006_openspec_claude_code/README.md). Copie o `opencode.json` para essa cópia. Use a mesma pergunta, um arquivo permitido e um critério que pode ser conferido no código.

```bash
opencode --standalone run --model router/pathbit-code \
  'Quais métodos e formatos o módulo de favoritos expõe? Cite a informação que confirma cada um.' \
  --file src/routes/favoritos.js
opencode --standalone run --model local/qwen2.5-coder:7b \
  'Quais métodos e formatos o módulo de favoritos expõe? Cite a informação que confirma cada um.' \
  --file src/routes/favoritos.js
```

Rode `--file` somente para um destino autorizado a receber aquele arquivo. Um proxy em `127.0.0.1` pode encaminhar pedidos a outro serviço. O caminho de rede e a política do gateway indicam quais dados saem da máquina. Faça essas duas sessões em separado para atrelar cada resultado à sua configuração e evitar misturar a comparação com histórico de conversa.

| Critério | Como avaliar no Agregador |
| --- | --- |
| Correção | Compare métodos e formatos citados com as rotas registradas e as respostas efetivas |
| Especificidade | Procure arquivos, handlers e condições que a pessoa revisora possa abrir |
| Custo e latência | Meça as duas sessões nas mesmas condições e registre o método antes de concluir |
| Contexto enviado | Use o destino autorizado e explique quais arquivos e ferramentas receberam permissão |
| Disponibilidade | Observe se a instância que recebeu o pedido estava íntegra e, no gateway, se houve fallback |

O laboratório da sonda comprovou os dois endereços e os dois IDs com respostas determinísticas. A etapa acima é a avaliação proposta para as suas próprias instâncias e modelos. Separar as duas etapas evita atribuir qualidade de resposta a um teste de transporte.

## Diagnóstico sem adivinhar pelo texto da resposta

| Sintoma | Olhe primeiro | O que a observação separa |
| --- | --- | --- |
| `model not found` antes de aparecer tráfego na sonda | Nome do provedor, ID e diretório que contém `opencode.json` | Validação do cliente e resolução de configuração |
| `404` na sonda | URL recebida e `baseURL` com `/v1` | Prefixo incorreto ou rota HTTP ausente |
| `400` com `Expected model` na sonda | Caminho e valor enviado em `model` | O cliente chegou ao servidor, mas selecionou o ID errado |
| `401` ou `403` no gateway real | Chave, escopo e instância configurada | Permissão da API ou do combo |
| Resposta de modelo sem ferramenta esperada | Recurso anunciado pelo modelo e por seu adaptador | Limitação de capacidade depois do transporte |
| A sessão local demora ou termina ao carregar | `ollama list`, `ollama ps` e recurso disponível na máquina | Modelo disponível x modelo em execução |
| Gateway responde, mas fallback causa dúvida | Trace da transação dentro do 9Router | O HTTP recebido pelo gateway termina antes da escolha de upstream |

As duas rotas atendem necessidades que podem conviver. O gateway concentra política, observação e seleção de provedores. O endpoint local permite escolher diretamente um modelo instalado, com custo de recursos e compatibilidade do equipamento sob sua responsabilidade. Com o caminho verificado você pode trocar a escolha por tarefa e revisar o resultado com base no código. No [artigo 0010](../../0010_playwright_mcp_agregador/article/ARTICLE.md), a mesma disciplina de confirmar fronteiras passa do transporte à interface e ao estado do servidor.

## Referências

- [Provedores no OpenCode](https://opencode.ai/docs/providers/)
- [Compatibilidade com OpenAI no Ollama](https://docs.ollama.com/api/openai-compatibility)
- [Sonda em Python](../examples/probe_server.py) · [Configuração do OpenCode](../examples/opencode.json.example) · [Figuras do exercício](../assets/figuras.md)

Developed with ❤️ by [Pathbit](https://www.pathbit.com.br/)
