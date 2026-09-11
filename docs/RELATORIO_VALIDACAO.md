# Relatório de Validação End-to-End dos Artigos

> Cada artigo foi validado em um **ciclo dedicado**, com o Docker completamente destruído
> (containers, volumes e redes) imediatamente antes de começar. Nenhum ciclo herda estado do anterior.

Este documento registra as evidências de que cada artigo funciona conforme publicado, executando
todas as ferramentas que ele apresenta ao leitor.

---

## Ciclo 1/3 - Artigo 0001 · Google Antigravity com Acesso Total Irrestrito e sem Interrupções

Ambiente zerado antes do ciclo: `containers: 0 · volumes: 0`. O artigo configura permissões locais
do Antigravity e não depende de Docker; a zeragem garante isolamento entre os ciclos.

| Ferramenta | Resultado |
| :--- | :--- |
| `src/test_permissions.py` | **35 testes, OK**, simula macOS, Linux e Windows com `HOME`/`APPDATA`/`USERPROFILE` redirecionados, sem tocar no ambiente real |
| `src/setup_permissions.py --dry-run` | 10 destinos simulados, nenhuma gravação |
| `src/verify_permissions.py` | `ESTADO PERFEITO: TODAS AS CONFIGURAÇÕES ESTÃO 100% APLICADAS` |
| `src/restore_permissions.py --list` | Backups da máquina listados em ordem, sem disparar restauração |
| `examples/sample_task.py` | `Status confirmado: OPERATIONAL` |

### Teste de detecção de falha

O diagnóstico foi validado por injeção deliberada de erro, não basta ele dizer que está tudo certo:

| Etapa | Resultado |
| :--- | :--- |
| 4 falhas injetadas na configuração real | `artifactReviewMode`, `enableTerminalSandbox`, `browserJsExecutionPolicy` e 5 dos 6 wildcards |
| `verify_permissions.py` | Acusou **exatamente as 4** |
| `setup_permissions.py` | Corrigiu tudo, com backup automático prévio |
| `restore_permissions.py --latest` | Restaurou o backup e o diagnóstico **voltou a acusar** as falhas, prova de que a restauração é real |

---

## Ciclo 2/3 - Artigo 0002 · ClaudeGravity e o Roteamento de Modelos Gemini

Ambiente zerado antes do ciclo: `containers: 0 · volumes: 0`.

```text
Container claudegravity-router   Up (healthy)   127.0.0.1:20128->20128/tcp
```

| Ferramenta | Resultado |
| :--- | :--- |
| `docker compose up -d` | Container saudável pelo healthcheck, porta apenas em loopback |
| `src/sync_antigravity_token.py` | Access token renovado e credenciais injetadas, **sem login manual no navegador** |
| `src/verify_setup.py` | `AMBIENTE 100% OPERACIONAL` · Claude Code 2.1.266 detectado |
| `src/test_gateway.py` (modo principal) | **HTTP 200 em 1.23s** · `PONG - ClaudeGravity Operacional` |
| `src/test_gateway.py` (modo resiliente) | **HTTP 200 em 1.13s** · `PONG - ClaudeGravity Operacional` |
| `src/claudegravity.py --list-models` | 9 modelos e combos listados |
| `src/manage_env.py status` | `Gateway HTTP Status: 200 OK` |

A reconexão OAuth ocorreu a partir do refresh token local, com o volume do gateway destruído
segundos antes.

---

## Ciclo 3/3 - Artigo 0003 · Claude Code sem Limites com Arsenal de Modelos Gratuitos e Fallback no 9Router

Ambiente zerado antes do ciclo: `containers: 0 · volumes: 0`.

```text
Container claudegravity-ollama  Healthy      ← depends_on aguardou o Ollama
Container claudegravity-router  Up (healthy) 127.0.0.1:20128->20128/tcp
```

### Provisionamento com 5 Provedores Integrados

```text
[+] Provedor configurado: groq · openrouter · gemini · ollama · mistral
[+] Ollama local pronto com: qwen2.5-coder:latest
[+] Combos: claudegravity-fallback (5) · arsenal-supremo (7) · arsenal-rapido (4) · arsenal-offline (1)
```

### Cascata validada nível a nível

A suíte testa cada nível isoladamente, pois a versão anterior aprovava a cascata exercitando apenas o
primeiro nível, e níveis mortos passavam despercebidos.

```text
[*] Cascata de 'arsenal-supremo' (7 níveis):
  [OK] 1º ag/gemini-3.8-flash-high                                  1.18s
  [OK] 2º ag/gemini-3.7-flash-high                                  1.09s
  [OK] 3º ag/gemini-3.6-flash-high                                  0.80s
  [OK] 4º openrouter/nvidia/nemotron-3.5-lightning:free            13.75s
  [OK] 5º groq/openai/gpt-oss-120b                                  1.87s
  [OK] 6º mistral/codestral-latest                                  0.88s
  [OK] 7º openai-compatible-chat-ollama-local/qwen2.5-coder:latest  1.43s

  Níveis testados: 12 · quebrados: 0
  Combos testados: 3 · com falha: 0
```

O volume do Ollama é destruído junto com o resto do ambiente, então o provisionamento acusa o modelo
local ausente e imprime os dois comandos que o recolocam. Seguidos à risca, o `setup_combos.py`
volta a registrar `Ollama local pronto com: qwen2.5-coder:latest`. É o mesmo procedimento do
**Problema 2** em [Problemas Comuns](./SOLUCAO_PROBLEMAS_COMUNS.md), executado a partir de um volume
vazio.

Teste de regressão do próprio validador: ao injetar um modelo morto na cascata, ele reprova com
exit code 1 mesmo com o combo respondendo pelo nível 1.

### Laboratório de Resiliência com 5 Cenários

```text
✅ PASSOU  · Cenário 1 · Estado nominal · HTTP 200 em 1.11s
✅ PASSOU  · Cenário 2 · Salto de fallback · HTTP 200 em 3.07s
✅ PASSOU  · Cenário 3 · Bloqueio sob token inválido · HTTP 503
✅ PASSOU  · Cenário 4 · Auto-cura · HTTP 200 em 1.83s
✅ PASSOU  · Cenário 5 · Claude Code CLI · 3.13s

Total: 5 aprovado(s), 0 falha(s), 0 pulado(s).
```

---

## Harness do Claude Code Modelo a Modelo

Responder à API não é o mesmo que operar o harness. O teste abaixo exige **uso de ferramenta**: a CLI
recebe a instrução de ler um arquivo do diretório e devolver o código que está dentro dele. Só passa
quem entende o protocolo de ferramentas, executa a leitura e responde com o valor certo.

Todos os identificadores declarados nos arquivos `.example` dos artigos foram submetidos ao mesmo teste:

| Modelo / combo | Operou o harness | Tempo |
| :--- | :--- | ---: |
| `ag/gemini-3.8-flash-high` | ✅ | 7,5s |
| `ag/gemini-3.7-flash-high` | ✅ | 5,2s |
| `ag/gemini-3.6-flash-high` | ✅ | 4,0s |
| `ag/gemini-pro-agent` | ✅ | 8,6s |
| `ag/gemini-3.1-pro-low` | ✅ | 13,3s |
| `ag/claude-sonnet-4-6` | ✅ | 8,3s |
| `ag/claude-opus-4-6-thinking` | ✅ | 14,9s |
| `ag/gpt-oss-120b-medium` | ✅ | 6,7s |
| `arsenal-supremo` | ✅ | 7,2s |
| `arsenal-rapido` | ✅ | 3,7s |
| `claudegravity-fallback` | ✅ | 6,8s |
| `arsenal-offline` | ❌ | 1,9s |
| `claude-opus-4-6` *(via override)* | ✅ | 10,9s |
| `claude-sonnet-4-6` *(via override)* | ✅ | 4,8s |
| `claude-haiku-4-5-20251001` *(via override)* | ✅ | 9,3s |

**14 de 15 operam o harness.** As três últimas linhas são os `modelOverrides` exercitados pelo nome
que o Claude Code emite, e não pelo identificador do gateway: são a prova de que a tradução acontece.
A única reprovação é o `arsenal-offline`, e ela é esperada, o motivo está logo abaixo.

### Os `modelOverrides` medidos um a um

A primeira versão do bloco declarava 14 mapeamentos e a medição mostrou que **só 3 traduziam**. A
causa apareceu ao usar o menu `/model`: a CLI grava o identificador da geração corrente, e nenhum
deles estava no bloco. A reação inicial foi cobrir tudo, com 33 chaves incluindo o sufixo `[1m]`  -
e isso também estava errado.

O teste seguinte desfez o excesso. Declarando apenas `claude-opus-5`, o pedido `--model
claude-opus-5[1m]` **resolve normalmente**: a CLI normaliza o sufixo antes de consultar o mapa, e o
próprio binário trata a variante como opcional no padrão que usa para reconhecer modelos:

```text
(?:[-@]\d{8})?(?:-v\d+(?::\d+)?)?(?:\[[12]m\])?$
```

E um terceiro teste mostrou que quase nada precisa de override. Com o `modelPicker` substituindo a
lista nativa e os quatro papéis declarados, removemos o bloco inteiro e reexecutamos as tarefas,
inclusive com subagente: **nenhuma falhou, e nenhum consumidor pediu um `claude-*`**. Restou um único
cenário, o de um `settings.local.json` com pin antigo.

O bloco final tem **três entradas, uma por família**, cada uma apontando para o mesmo modelo do papel
correspondente  -  de modo que um pin esquecido resolve exatamente para onde o papel já apontava:

| Chave | Destino (0002 e 0003) | Papel equivalente |
| :--- | :--- | :--- |
| `claude-fable-5-1` | `ag/gemini-pro-agent` | Fable |
| `claude-opus-5` | `ag/gemini-3.8-flash-high` | Opus |
| `claude-sonnet-5` | `ag/gemini-3.7-flash-high` | Sonnet |

De 33 para 3, com o mesmo resultado nos testes.

### Configurações validadas com `claude doctor`

O `claude doctor` valida arquivos de settings sem abrir sessão e lista regras de permissão
descartadas. Foram submetidos os 12 arquivos de settings dos três artigos e, separadamente, os 6
blocos JSON transcritos no corpo dos artigos, que é o que o leitor copia:

```text
arquivos de settings ....... 12/12 aprovados
blocos publicados nos artigos 6/6 aprovados
```

O varredor encontrou e removeu `"*"` e `"mcp__*"` de `permissions.allow`: são recusados porque uma
regra de permissão precisa nomear o escopo que amplia. Curinga em `allow` só é aceito na posição da
ferramenta, após um prefixo literal `mcp__<servidor>__`.

### Volatilidade capturada durante a própria medição

O `ag/gpt-oss-120b-medium` **estourou o limite de 180s na primeira tentativa** e concluiu em 7,7s na
segunda, sem nenhuma mudança de configuração entre as duas. O modelo não saiu do catálogo nem passou
a recusar a chave: ele simplesmente ficou lento por alguns minutos.

É exatamente o cenário para o qual a cascata existe. Um modelo em papel fixo teria travado a sessão;
dentro de um combo, o gateway teria comutado para o nível seguinte. Vale como aviso a quem for
reproduzir: **um tempo ruim isolado não significa modelo morto**, repita antes de trocar o
identificador.

### O caso do `arsenal-offline`

O nível local **responde ao gateway**, `HTTP 200` em 0,08s, servido por `qwen2.5-coder:latest`. Dentro
do harness, porém, ele ignora a instrução e devolve texto solto, com **exit code 0**:

```text
$ claude -p "Leia o arquivo alvo.txt ... responda somente com o valor de codigo_de_verificacao"
      --model arsenal-offline
Dê-me tempo para explorar a minha base de código.
exit=0
```

Nenhum erro é levantado. É por isso que `arsenal-offline` serve como rede de segurança da cascata e
garante que o combo sempre devolva alguma resposta, mas **nunca** deve ser atribuído a um papel de
modelo (`ANTHROPIC_DEFAULT_*_MODEL`): a tarefa daquele papel falharia sem sinal visível.

---

## Papéis de Modelo, Advisor e Tarefas Longas

O Claude Code expõe quatro papéis, e a ordem de capacidade vem da própria CLI: *Fable for the
hardest problems, Opus for complex work, Sonnet for most tasks, Haiku for quick questions*.

### Qual papel cada parte do harness aciona

Cada papel recebeu um Gemini **diferente** e tarefas comuns foram executadas. A CLI identifica o
consumidor pelo campo `query_source`, e o gateway registra o modelo servido:

| `query_source` | Papel acionado | Frequência observada |
| :--- | :--- | :--- |
| `sdk` | modelo principal | Toda requisição do laço principal |
| `generate_session_title` | **Haiku** | **Toda sessão**, sem exceção |
| `agent:builtin:Explore` | **Opus** | A cada subagente de exploração despachado |

Duas consequências para quem monta a configuração: o papel Haiku é chamado sempre, então um modelo
caro ali é desperdício garantido; e subagentes consomem o papel **Opus**, não o rápido.

### `modelOverrides` cobrindo os identificadores do seletor

O menu `/model` grava o identificador completo, **incluindo o sufixo de janela**: `claude-opus-5[1m]`,
`claude-fable-5-1[1m]`. Sem essas chaves no `modelOverrides`, a sessão morre com
`There's an issue with the selected model`. Os `.example` passaram a declarar 33 chaves, cobrindo
cada família com e sem `[1m]`, mais os aliases curtos.

Verificação após a correção, exatamente com os identificadores que falhavam:

```text
--model claude-fable-5-1[1m]   OK   5,5s
--model claude-opus-5[1m]      OK  25,9s
--model claude-sonnet-5[1m]    OK   5,8s
--model fable                  OK  11,3s
--model sonnet                 OK   3,8s
--model haiku                  OK   2,5s
```

### Latência por papel e o caso do alias `opus`

| Invocação | Tempo |
| :--- | ---: |
| `--model sonnet` | 3,8s |
| `--model fable` | 11,3s |
| `--model claude-opus-5[1m]` | 25,9s |
| `--model opus` | 62,2s |

O alias `opus` **não** é sinônimo de `claude-opus-5`: ele liga o **Opus Plan Mode**, que planeja
antes de responder e custa dezesseis vezes o tempo do `sonnet` na tarefa mais simples possível.

### Advisor

A CLI descreve a ferramenta como *"an advisor tool backed by a stronger reviewer model"* e impõe que
o advisor seja **ao menos tão capaz quanto o modelo principal**. Nos `.example` dos dois módulos,
`advisorModel` aponta para `ag/gemini-pro-agent`  -  o mesmo do papel Fable, e o modelo mais denso da
conta  -  enquanto o principal fica em `ag/gemini-3.8-flash-high`. Não há degrau de capacidade.

Essa checagem, porém, **só é verificável dentro do catálogo da Anthropic**: a comparação usa o campo
`advisor_rank`, que existe nas entradas `claude-*` e não nos identificadores de gateway. Com dois
`ag/*` a CLI aceita a chave sem conferir nada, inclusive numa combinação invertida. A escolha de um
revisor à altura é responsabilidade de quem configura.

### Processos órfãos que consomem cota

Um `claude -p` interrompido por timeout **não necessariamente morre**. Durante as medições,
processos de tentativas anteriores continuaram emitindo requisições por minutos e sobreviveram a
`pkill -9` no processo pai. Com alguns acumulados, o gateway registrou **79 requisições em 10
segundos com ninguém usando**, e toda medição nova saía lenta.

O efeito é enganoso: a primeira leitura sugeria que o alias `opus` provocava tempestade de
retentativas. Com o gateway limpo, o `opus` respondeu normalmente. **A lentidão era dos órfãos, não
do modelo.** Confira o gateway ocioso antes de culpar qualquer identificador.

### O seletor do aplicativo de janela ignora o `modelPicker`

Medido diretamente na interface, com a árvore de acessibilidade do app.

Primeiro o que **é** verdade e costuma ser suposto ao contrário: o aplicativo não reimplementa o
harness. Ele empacota a mesma CLI, em `~/Library/Application Support/Claude/claude-code-vm/<versão>/claude`
 -  na máquina de teste, a mesma versão `2.1.266` do terminal  -  e o binário embutido reconhece
`modelPicker`, `replaceBuiltInOptions`, `behavesAs`, `advisorModel`, `modelOverrides` e os dois
caminhos de projeto. Não há regra de configuração diferente para o app; o que muda é o diretório em
que cada sessão roda.

O teste do seletor: declaramos em `~/.claude/settings.json` um `modelPicker` com
`replaceBuiltInOptions: true` e uma única entrada de rótulo inconfundível apontando para um modelo do
gateway, reiniciamos o aplicativo e abrimos o controle de modelo da janela.

| Observação | Resultado |
| :--- | :--- |
| Quatro papéis no seletor | Inalterados (Fable 5.1, Opus 5, Sonnet 5, Haiku 4.5) |
| Submenu **Mais modelos** | Inalterado: Fable 5, Opus 4.8, Opus 4.7, Opus 4.6, Sonnet 4.6 |
| Entrada declarada no `modelPicker` | **Não aparece em lugar nenhum** |
| `replaceBuiltInOptions: true` | Sem efeito sobre a lista nativa |

**O seletor da janela ignora o `modelPicker`.** O caminho confirmado para apontar o aplicativo ao
gateway continua sendo o bloco `env` do arquivo de usuário, com os quatro papéis. A consequência
editorial é que, no app, o rótulo exibido na tela deixa de corresponder ao modelo que de fato
responde  -  e o artigo 0002 passou a dizer isso explicitamente.

O `settings.json` do usuário foi restaurado a partir de backup e conferido byte a byte após o teste.

---

## Coerência entre artigo, código e gateway

As 4 cascatas definidas em `src/setup_combos.py` foram comparadas, modelo a modelo e em ordem, com
o que ficou gravado no gateway após o provisionamento e com o que os artigos descrevem:
**idênticas nas três fontes**. Todos os identificadores declarados nos arquivos `.example` existem
no catálogo do gateway.

---

## Modelos Gratuitos e Volatilidade Observada

O catálogo gratuito foi testado modelo a modelo. Os três modos de falha encontrados justificam a
arquitetura em cascata:

| Modo de falha | Resposta do provedor |
| :--- | :--- |
| Descontinuado ou migrado para a versão paga | `404` |
| Saturado no momento | `429` |
| Requer permissão adicional na conta | `403` |

Dois modelos que constavam das cascatas publicadas haviam saído do catálogo e foram substituídos
por identificadores verificados.

### Prova do salto sobre um nível quebrado

Combo de teste com um identificador inexistente no topo, registrado pelo log do gateway:

```text
[COMBO] Trying model 1/4: openrouter/exemplo/modelo-indisponivel:free
✗ ERROR 400 · "exemplo/modelo-indisponivel:free is not a valid model ID"
[COMBO] Model failed, trying next
[COMBO] Trying model 2/4: groq/openai/gpt-oss-120b
[COMBO] Model succeeded
```

Resposta entregue em **0,72 s**, sem queda de sessão. O Claude Code CLI também foi executado
apontando direto para modelos de custo zero, retornando corretamente em ambos.

---

## Execução Completa de Ponta a Ponta (11/09/2026)

Bateria final com o ambiente real no ar: 9Router `v0.5.75`, container `Up 15h (healthy)`, as duas
imagens em `:latest`, conexão Antigravity `active` via OAuth.

### Suítes dos próprios artigos

| Módulo | Suíte | Resultado |
| :--- | :--- | :--- |
| 0001 | `verify_permissions.py` | 5/5 seções verdes (IDE, projetos, CLI `agy`, pastas confiáveis, VS Code) |
| 0001 | `test_permissions.py` | **35/35** testes, cobrindo macOS, Linux e Windows |
| 0002 | `verify_setup.py` | 5/5 (Docker, HTTP, 20 modelos, 5 combos, CLI 2.1.266) |
| 0002 | `test_gateway.py` | **4/4** com inferência real: direto 2,64 s · combo 1,34 s |
| 0003 | `test_arsenal.py` | **12/12 níveis · 3/3 combos**, zero quebrados |
| 0003 | `simulate_fallback.py` | **5/5 cenários**, incluindo auto-cura e Claude Code CLI real |

### Cascatas: documentado vs. servido

Lidas do banco do container e comparadas linha a linha com as tabelas publicadas. **Batem na ordem
exata**, sem exceção:

| Combo | Cascata servida |
| :--- | :--- |
| `claudegravity-fallback` | Gemini 3.8 → 3.7 → 3.6 → Sonnet 4.6 → GPT-OSS |
| `claudegravity-thinking` | Opus 4.6 Thinking → Sonnet 4.6 → Gemini 3.8 → GPT-OSS |
| `arsenal-supremo` | Gemini 3.8 → 3.7 → 3.6 → OpenRouter → Groq → Mistral → Ollama |
| `arsenal-rapido` | Groq → Mistral → Gemini 3.7 → 3.6 |
| `arsenal-offline` | Ollama `qwen2.5-coder:latest` |

### Papel de modelo confirmado em sessão real

Uma sessão `claude -p` rodando sobre `examples/.claude/` emitiu a telemetria da própria CLI:

```text
[claude-code:unrecognized_model] {"model":"ag/gemini-3.6-flash-high","query_source":"generate_session_title"}
```

`generate_session_title` é o papel **Haiku**, e `ag/gemini-3.6-flash-high` é exatamente o que os
`.example` mapeiam em `ANTHROPIC_DEFAULT_HAIKU_MODEL`. A tabela de papéis do artigo está provada em
execução, não apenas por leitura de binário.

### Tráfego real do dia

240 requisições atendidas, com **todos os cinco provedores** exercitados e todo modelo documentado
servindo tráfego:

| Provedor | Requisições | Modelos |
| :--- | ---: | :--- |
| Antigravity | 192 | `3.8-flash-high` 106 · `3.6-flash-high` 41 · `opus-4-6-thinking` 28 · `3.7-flash-high` 10 · `pro-agent` 6 · `sonnet-4-6` 1 |
| Groq | 18 | `openai/gpt-oss-120b` |
| Ollama local | 15 | `qwen2.5-coder:latest` |
| Mistral | 11 | `codestral-latest` |
| OpenRouter | 4 | `nvidia/nemotron-3.5-lightning:free` |

### A família 3.5, verificada literalmente

O artigo 0002 afirma que o `-high` responde 404 e que as variantes `-low` devolvem a mensagem do
Google. Ambas se confirmaram:

```text
ag/gemini-3.5-flash-high → HTTP 503 encapsulando [404] "Requested entity was not found."
ag/gemini-3.5-flash-low  → HTTP 200 com o texto:
   "Gemini 3.5 Flash is no longer available. Please switch to Gemini 3.7 Flash
    in the latest version of Antigravity."
```

### Não existe desconexão: o que parece logout é cota

O histórico completo do gateway desmente a hipótese de sessão caindo:

| Evento | Ocorrências |
| :--- | ---: |
| `Successfully refreshed Google token` | **21** |
| Falhas de refresh | **0** |
| `401` / `invalid_grant` / reauth | **0** espontâneas |
| `ERROR 404` em modelo servido | **1**, e apenas no descontinuado `gemini-3.5-flash-high` |
| `all 1 accounts locked` | **36**, todas por cota de família |

Os bloqueios por cota concentraram-se num único episódio (10/09, 22:06–22:08) sobre `gemini-3.8`,
`3.7` e `3.6`, mais `openai`. **É a Falha 1 do artigo**, e a resposta correta é a cascata, não
reautenticar.

### `expiresAt`: corrupção confirmada ao vivo e automatizada

A regravação como string ISO **voltou a acontecer durante esta bateria**, e o `keep_connected.py` a
identificou pelo nome:

```text
[*] Renovando: expiresAt gravado como texto pelo gateway.
[+] Credencial renovada. Válida por mais 59 min.
```

O log do gateway mostra que ele renova sozinho a cada 30 min com sucesso
(`hasNewAccessToken:true, expiresIn:3599`) e, ao gravar, corrompe o campo. Um teste de injeção
confirmou o mecanismo: com `expiresAt` em texto, `Number(...)` é `NaN` e a comparação de validade
falha  -  embora a inferência ainda responda `200` enquanto o token em si continua válido. O dano é
na contabilidade, e aparece quando o token de fato vence.

Para que a correção deixe de depender de alguém lembrar de rodar o script, a renovação foi promovida
a serviço do sistema, em `~/Library/LaunchAgents/co.pathbit.claudegravity.keepconnected.plist`:
roda ao entrar na sessão e a cada 5 minutos, com margem de 25 min.

### Cadeia de continuidade, verificada elo a elo

Renovar a credencial resolve um elo só. A pergunta que importa é outra: **depois de um reboot, ou de
uma queda do container, o ambiente volta sozinho?** Cada elo foi conferido:

| Elo | Estado | Como foi verificado |
| :--- | :--- | :--- |
| Docker Desktop abre no login | `AutoStart = True` | `settings-store.json` do Docker |
| Containers voltam com o Docker | `unless-stopped` nos 3 serviços | `docker inspect` da política efetiva |
| Gateway volta a servir | **2,6 s** após `docker restart` | medido com sondagem a cada 2 s |
| Credencial sobrevive ao restart | `expiresAt` numérico, `isActive: 1` | lida do banco depois do restart |
| Inferência volta | modelo direto e combo responderam | chamada real pós-restart |
| Renovação roda sozinha | LaunchAgent a cada 5 min | `launchctl print`, exit 0 |

O elo que faltava era a **visibilidade da falha**: o agente escrevia num log que ninguém lê. Foi
adicionado um guardião em `~/.claudegravity/guard.sh`, chamado pelo LaunchAgent, que faz o ciclo
completo e **avisa na tela** quando algo quebra:

1. Docker parado → notifica e sai
2. Container caído → **tenta subir sozinho** e só notifica se não conseguir
3. Renova a credencial
4. Confere o estado **gravado** (numérico, não vencido)  -  renovar sem conferir não prova nada
5. Confirma que `/v1/models` devolve `200`
6. Notifica a recuperação quando o problema passa, e não repete o mesmo alerta a cada 5 min

Os quatro caminhos foram exercitados: cenário saudável (`OK - credencial valida por 57 min, gateway
HTTP 200`), container parado à força (**religou sozinho em 8 s** e validou), gateway inalcançável
(`FALHA: Gateway nao responde - HTTP 000`) e credencial de origem ausente (mensagem clara apontando
`~/.gemini/`).

---

## Observações para quem for reproduzir

1. **Pré-requisito entre artigos:** o 0003 usa `sync_antigravity_token.py`, que pertence ao 0002.
2. **Arquivo `.env` obrigatório:** os compose leem `INITIAL_PASSWORD` e `JWT_SECRET` do ambiente e
   falham de propósito se faltarem. Copie `.env.example` para `.env` antes de subir.
3. **Chave do gateway:** é gerada na primeira execução do sincronizador e gravada no `.env`, que
   não é versionado. Nenhuma chave publicada funciona como padrão.
4. **Portas em loopback:** o gateway carrega credenciais reais e por isso publica apenas em
   `127.0.0.1`.
5. **Catálogos gratuitos mudam.** Revalide com `python3 src/test_arsenal.py`, que acusa qualquer
   nível quebrado.
