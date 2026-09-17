# ARTICLE

Aqui estamos usando API key padrao, pode funcionar com qualquer router, provedor e etc que tenham compatibilidade com a Anthropic para seus endpoints de codigo e outros entendeu? Entao precisamos colocar este tipo de validacao nos artigos.

## Referencias

- Artigo de referencia: https://github.com/aattaran/deepclaude
- Criar conta deepseek, adicionar credito e obter token: https://platform.deepseek.com/sign_in
- Criar conta e obter token para usar deepseek free: https://www.orcarouter.ai/login (lógico até a escrita deste artigo)
- Preços do Deepseek no Orca Router: https://www.orcarouter.ai/pt/providers/deepseek

## Importante

- As imagens no assets ja estao na ordem que eu gostaria de fazer
- Na pastas examples eu já tenho exemplos de arquivos settings.json tanto para o deepseek e para o orca router.
- Estamos usando os arquivos de exemplos na pasta `.claude/settings.json.deepseek.example` e `.claude/settings.json.orcarouter.example`
- Seria interessante falar que é possivel usar com o 9router ou outro local tambem, referenciar o artigo anterior
- Importante lembrar que os modelos nao ficam free para sempre, estamos com este item agora sendo free no orca router
- Podemos referenciar o artigo 0002 e dizer que é possivel usar com o 9router tambem e trabalhar ate com diferentes modelos, nao somente com deepseek, podemos usar multiplos modelos, como podemos fazer isto no OrcaRouter tambem, somente adicionando mais modelos na chave de API ou deixando sem nenhum modelo pre-definido, desta forma, podemos usar todos os que tiverem disponiveis na plataforma: 

## Arquivos importantes

> Os arquivos abaixo neste artigo estao na pasta examples/.claude/

settings.json.deepseek.example

```json
{
    "model": "deepseek-v4-pro",
    "env": {
        "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
        "ANTHROPIC_AUTH_TOKEN": "sk-sua-chave-do-DEEPSEEK-PLATFORM",
        "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro",
        "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME": "DeepSeek V4 PRO (Opus)",
        "ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION": "Primario: raciocinio alto, 1M de contexto",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-flash",
        "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME": "DeepSeek Flash (Sonnet)",
        "ANTHROPIC_DEFAULT_SONNET_MODEL_DESCRIPTION": "Trabalho corrente: alta velocidade e baixa latencia",
        "ANTHROPIC_DEFAULT_FABLE_MODEL": "deepseek-v4-pro",
        "ANTHROPIC_DEFAULT_FABLE_MODEL_NAME": "DeepSeek V4 PRO (Fable)",
        "ANTHROPIC_DEFAULT_FABLE_MODEL_DESCRIPTION": "Tarefas longas e raciocinio profundo",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-flash",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME": "DeepSeek Flash (Haiku)",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL_DESCRIPTION": "Latencia minima e respostas rapidas",
        "ANTHROPIC_MODEL": "deepseek-flash",
        "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-flash",
        "CLAUDE_CODE_EFFORT_LEVEL": "max",
        "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "786432",
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
                "model": "deepseek-flash",
                "label": "DeepSeek Flash (Sonnet)",
                "description": "Trabalho corrente: alta velocidade e baixa latencia",
                "behavesAs": "claude-sonnet-4-6"
            },
            {
                "model": "deepseek-v4-pro",
                "label": "DeepSeek V4 PRO (Opus)",
                "description": "Primario: raciocinio alto, 1M de contexto",
                "behavesAs": "claude-sonnet-4-6"
            }
        ]
    },
    "modelOverrides": {
        "claude-fable-5-1": "deepseek-v4-pro[1m]",        
        "claude-opus-5": "deepseek-v4-pro",
        "claude-sonnet-5": "deepseek-flash"
    }
}
```

> [!IMPORTANT]
> ### Por que o Advisor fica desligado (`"CLAUDE_CODE_DISABLE_ADVISOR_TOOL": "1"`)
>
> Não é economia nem esquecimento: **o advisor não funciona com nenhum modelo servido fora da API da Anthropic, e ligá-lo derruba a sessão.** Ele é uma *server tool* executada pelo servidor da Anthropic; um gateway ou provedor alternativo recebe um tipo de ferramenta que não conhece e rejeita a requisição inteira. Nenhuma outra chave (`advisorModel`, `modelOverrides`, papéis `ANTHROPIC_DEFAULT_*_MODEL`) contorna isso: elas só escolhem **qual** modelo entra na ferramenta, não **quem** a executa. Por isso `"CLAUDE_CODE_DISABLE_ADVISOR_TOOL": "1"` está em **todos** os arquivos deste artigo. O mecanismo, o erro exato devolvido pelo DeepSeek e o motivo do menu `/advisor` duplicar linhas estão no aviso `[!CAUTION]` ao final deste documento. O mesmo vale para o exemplo do OrcaRouter, logo abaixo.

settings.json.orcarouter.example

```json
{
    "model": "deepseek/deepseek-v4-flash-free",
    "env": {
        "ANTHROPIC_BASE_URL": "https://api.orcarouter.ai",
        "ANTHROPIC_AUTH_TOKEN": "sk-sua-chave-do-ORCA-ROUTER",
        "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek/deepseek-v4-flash-free",
        "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME": "DeepSeek V4 Flash FREE (Opus)",
        "ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION": "OrcaRouter Free: 1M contexto",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek/deepseek-v4-flash-free",
        "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME": "DeepSeek V4 Flash FREE (Sonnet)",
        "ANTHROPIC_DEFAULT_SONNET_MODEL_DESCRIPTION": "OrcaRouter Free: alta velocidade",
        "ANTHROPIC_DEFAULT_FABLE_MODEL": "deepseek/deepseek-v4-flash-free",
        "ANTHROPIC_DEFAULT_FABLE_MODEL_NAME": "DeepSeek V4 Flash FREE (Fable)",
        "ANTHROPIC_DEFAULT_FABLE_MODEL_DESCRIPTION": "OrcaRouter Free: tarefas analiticas",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek/deepseek-v4-flash-free",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME": "DeepSeek V4 Flash FREE (Haiku)",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL_DESCRIPTION": "OrcaRouter Free: respostas rapidas",
        "ANTHROPIC_MODEL": "deepseek/deepseek-v4-flash-free",
        "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-flash",
        "CLAUDE_CODE_EFFORT_LEVEL": "max",
        "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "786432",
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
                "model": "deepseek/deepseek-v4-flash-free",
                "label": "DeepSeek V4 Flash FREE (Sonnet)",
                "description": "Gratuito no OrcaRouter: alta velocidade e 1M de contexto",
                "behavesAs": "claude-sonnet-4-6"
            }
        ]
    },
    "modelOverrides": {
        "claude-fable-5-1": "deepseek-v4-pro[1m]",        
        "claude-opus-5": "deepseek/deepseek-v4-flash-free",
        "claude-sonnet-5": "deepseek/deepseek-v4-flash-free"
    }
}
```

---

## O que fica no estado global do Claude Code (e como não depender dele)

Tudo o que este artigo configura mora em `.claude/settings.json`. Mas o Claude Code guarda **fora do projeto**, em `~/.claude.json`, um estado que nenhuma chave de `settings.json` altera, por desenho:

| O que | Onde fica | O que zera |
| :--- | :--- | :--- |
| Assistente de primeiro uso concluído (tema, notas de segurança) | `~/.claude.json` | `/logout`, ou uma instalação nova |
| Login na conta Anthropic | `~/.claude.json` + chaveiro do sistema | `/logout` |
| Aprovação de uma `ANTHROPIC_API_KEY` vinda do `env` (pergunta *"Do you want to use this API key?"*) | `~/.claude.json` | `/logout` |
| Confiança na pasta (*"Do you trust the files in this folder?"*) | `~/.claude.json`, por caminho absoluto | Renomear ou mover a pasta |

Verificamos no binário da versão 2.1.268 (17 de setembro de 2026): o `/logout` marca o assistente como não concluído e apaga a lista de chaves aprovadas. Foi exatamente isso que produziu o sintoma "entro na pasta e ele fica pedindo login": o assistente reaparece, e **enquanto ele roda, o `settings.json` do projeto ainda não foi carregado**. Medimos com uma configuração global zerada: mesmo com a pasta já confiável e o arquivo completo, o assistente mostrou a tela *"Select login method"*. O arquivo do projeto só entra depois do assistente e da confirmação de confiança.

Duas decisões deixam este projeto imune a esse estado:

1. **`ANTHROPIC_AUTH_TOKEN` no lugar de `ANTHROPIC_API_KEY`.** As duas autenticam no DeepSeek e no OrcaRouter; a diferença é o que a CLI faz com cada uma. `ANTHROPIC_API_KEY` exige uma aprovação interativa única, guardada em `~/.claude.json` e apagada pelo `/logout` (medimos: com a chave não aprovada, pasta confiável e assistente concluído, a pergunta reaparece). `ANTHROPIC_AUTH_TOKEN` vai direto para o cabeçalho `Authorization: Bearer`, sem aprovação nem estado global. É [documentada](https://code.claude.com/docs/en/env-vars) para exatamente isso. Confirmamos que os dois leem esse cabeçalho.
2. **Na primeira execução, ou depois de um `/logout`, inicie com `--settings`:**

   ```bash
   claude --settings .claude/settings.json
   ```

   A flag é [documentada](https://code.claude.com/docs/en/settings#change-a-setting-for-one-session) e aplica o arquivo **antes** do assistente. Medimos com configuração global zerada: a sequência foi tema, notas de segurança, confiança na pasta e o prompt, sem nenhuma tela de login. Depois disso a pasta fica confiável, e o `claude` puro passa a carregar o `settings.json` do projeto em toda sessão. Um efeito colateral bem-vindo: com `--settings`, a CLI também honra o bloco `modelPicker`, que ela ignora quando vem do checkout do projeto.

O que **não** dá para evitar por configuração de projeto: a escolha de tema e as notas de segurança na primeira execução, e a pergunta de confiança em cada pasta nova. São telas de um `Enter` cada, nunca pedem login, e é assim que a CLI protege quem abre um repositório desconhecido.

> **Se o Claude Code pedir login nesta pasta**, a ordem de verificação é: (1) o JSON do `settings.json` é válido? Uma vírgula sobrando faz a CLI descartar o arquivo em silêncio; (2) o assistente de primeiro uso está aparecendo? Saia dele com `claude --settings .claude/settings.json`; (3) a pasta foi renomeada? Aceite a confiança de novo.

---

## Como o Claude Code monta o menu `/model` e Precedência do `modelPicker`

Uma particularidade do Claude Code na versão 2.1.x:

1. **Escopo do `modelPicker`:**
   A CLI do Claude Code só carrega o bloco `modelPicker` quando ele está em:
   - Configurações de usuário: `~/.claude/settings.json`
   - Parâmetro de linha de comando: `claude --settings <arquivo>`
   - Políticas corporativas (*managed settings*)
   
   Em um checkout local de projeto (`.claude/settings.json`), o `modelPicker` é **ignorado**.

2. **Como o `/model` exibe os modelos no projeto:**
   Como o `modelPicker` do projeto é ignorado, a CLI monta as opções a partir das variáveis de ambiente dos 4 papéis (`OPUS`, `SONNET`, `FABLE`, `HAIKU`).
   
   Para evitar que o menu mostre nomes genéricos da Anthropic (como *"Fable 5.1"* ou *"Sonnet 5"*) ou rótulos duplicados:
   - Configure **`ANTHROPIC_DEFAULT_*_MODEL_NAME`** e **`ANTHROPIC_DEFAULT_*_MODEL_DESCRIPTION`** para cada papel dentro de `env`.
   - Se desejar que o comando `/model` mostre **apenas** a lista limpa do `modelPicker` sem nenhum papel nativo, copie o bloco `modelPicker` para o seu `~/.claude/settings.json` global, ou inicie a sessão com `claude --settings .claude/settings.json`, que também honra o bloco.

3. **Advisor e Provedores Alternativos:**

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
