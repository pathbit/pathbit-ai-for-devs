# pathbit-ai-for-devs

## 0004_deep_claude_alternativa_claudegravity

**Ano:** 2026
**ID do Artigo:** 0004
**Autor:** Eliel Sousa
**Categoria:** Engenharia de IA / Claude Code / Provedores Alternativos

> **Status:** artigo em elaboração. Os arquivos de configuração em `examples/.claude/` já estão validados e são a referência; o texto do `article/ARTICLE.md` ainda está em rascunho.

---

### Resumo

Usa o **Claude Code** com modelos **DeepSeek** por dois caminhos que expõem a API no formato Anthropic Messages: a plataforma oficial da DeepSeek (`https://api.deepseek.com/anthropic`, paga por uso) e o **OrcaRouter** (`https://api.orcarouter.ai`, com o `deepseek/deepseek-v4-flash-free` gratuito na data da escrita). É a alternativa ao ClaudeGravity do [Artigo 0002](../0002_claude_gravity_utilizando_9router/) para quem não tem o Antigravity, e funciona também atrás do 9Router.

---

### Estrutura de Arquivos do Módulo

```text
0004_deep_claude_alternativa_claudegravity/
├── README.md
├── article/
│   └── ARTICLE.md
├── assets/
└── examples/
    ├── README.md
    └── .claude/
        ├── settings.json.deepseek.example     # DeepSeek Platform (pago por uso)
        └── settings.json.orcarouter.example   # OrcaRouter (DeepSeek Flash gratuito)
```

A cópia ativa `examples/.claude/settings.json` fica fora do controle de versão.

---

### Roteiro Prático de Reprodução

1. Crie a conta e gere a chave em uma das plataformas: [DeepSeek Platform](https://platform.deepseek.com/sign_in) ou [OrcaRouter](https://www.orcarouter.ai/login).
2. Escolha o exemplo correspondente e substitua o placeholder da chave:

   ```bash
   cd 0004_deep_claude_alternativa_claudegravity/examples
   cp .claude/settings.json.deepseek.example .claude/settings.json     # ou settings.json.orcarouter.example
   ```

   No arquivo, troque o valor de `ANTHROPIC_AUTH_TOKEN` pela sua chave.
3. Na primeira execução, ou depois de um `/logout`, inicie com o arquivo aplicado antes do assistente de primeiro uso:

   ```bash
   claude --settings .claude/settings.json
   ```

   Depois disso, `claude` puro nesta pasta carrega o `settings.json` em toda sessão.
4. Teste sem abrir a interface:

   ```bash
   claude -p "Responda somente OK" --max-turns 1
   ```

As regras por trás desses arquivos (`ANTHROPIC_AUTH_TOKEN`, advisor desligado, estado global da CLI) estão em [docs/CHECKLIST_SETTINGS_CLAUDE_CODE.md](../docs/CHECKLIST_SETTINGS_CLAUDE_CODE.md).
