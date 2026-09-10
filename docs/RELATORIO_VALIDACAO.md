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
| `src/claudegravity.py --list-models` | 8 modelos e combos listados |
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
| `ag/gemini-3.8-flash-high` | ✅ | 6,7s |
| `ag/gemini-3.7-flash-high` | ✅ | 5,4s |
| `ag/gemini-3.6-flash-high` | ✅ | 4,9s |
| `ag/gemini-3.1-pro-low` | ✅ | 11,2s |
| `ag/claude-sonnet-4-6` | ✅ | 3,7s |
| `ag/claude-opus-4-6-thinking` | ✅ | 9,4s |
| `ag/gpt-oss-120b-medium` | ✅ | 7,1s |
| `arsenal-supremo` | ✅ | 4,8s |
| `arsenal-rapido` | ✅ | 2,7s |
| `claudegravity-fallback` | ✅ | 8,6s |
| `arsenal-offline` | ❌ | 4,0s |

**10 de 11 operam o harness.** A única reprovação é o `arsenal-offline`, e ela é esperada, o motivo
está logo abaixo.

### Os `modelOverrides` medidos um a um

O bloco declara 14 mapeamentos. Cada chave foi pedida à CLI para verificar se a tradução acontece:

| Resultado | Identificadores |
| :--- | :--- |
| **Traduzem** (3) | `claude-opus-4-6` · `claude-sonnet-4-6` · `claude-haiku-4-5-20251001` |
| **Inertes** (11) | `claude-3-opus` · `claude-5-opus` · `claude-3-7-sonnet` · `claude-5-sonnet` · `claude-5` · `claude-haiku` · `claude-3-5-haiku` · `fable` · `claude-fable` · `gpt-oss` · `gpt-oss-120b` |

A tradução dos três foi confirmada por eliminação: pedidos diretos ao gateway devolvem `404` para
esses nomes, e com o `modelOverrides` ativo a mesma chamada passa pela CLI. Os onze restantes falham
com `There's an issue with the selected model`  -  **resposta idêntica, e no mesmo tempo, à de um nome
inventado**, o que mostra que a CLI valida contra uma lista fechada antes de consultar o mapeamento.

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
