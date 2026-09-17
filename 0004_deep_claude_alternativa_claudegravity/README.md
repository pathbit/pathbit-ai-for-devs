# pathbit-ai-for-devs

## 0004_deep_claude_alternativa_claudegravity

**Ano:** 2026  
**ID do Artigo:** 0004  
**Título:** DeepClaude: A Alternativa ao ClaudeGravity com DeepSeek e OrcaRouter no Claude Code  
**Autor:** Eliel Sousa  
**Categoria:** Engenharia de IA / Claude Code / Provedores Alternativos  
**Status:** Publicado / Validado  

---

### Resumo

Opera o **Claude Code CLI** diretamente com os modelos da família **DeepSeek** por dois caminhos complementares e compatíveis com a especificação Anthropic Messages API:
1. **DeepSeek Platform Direto (`https://api.deepseek.com/anthropic`):** API oficial paga por uso, com preços imbatíveis por milhão de tokens e modelos de alto raciocínio (`deepseek-v4-pro` e `deepseek-flash`).
2. **OrcaRouter (`https://api.orcarouter.ai`):** Gateway agregador que disponibiliza o modelo `deepseek/deepseek-v4-flash-free` com janela de 1 milhão de tokens a custo zero na data de publicação deste artigo.

Representa a alternativa universal ao ClaudeGravity do [Artigo 0002](../0002_claude_gravity_utilizando_9router/) para desenvolvedores que não possuem acesso ao Google Antigravity, funcionando também integrado à cascata de fallback do 9Router apresentada no [Artigo 0003](../0003_fallback_modelos_gratuitos_9router/).

---

### Estrutura de Arquivos do Módulo

```text
0004_deep_claude_alternativa_claudegravity/
├── README.md                                  # Este documento
├── article/
│   └── ARTICLE.md                             # Artigo completo com 42 prints e análise técnica
├── assets/                                    # 41 arquivos de evidência visual sequenciada (01 a 42)
└── examples/
    ├── README.md                              # Instruções de execução prática
    └── .claude/
        ├── settings.json.deepseek.example     # DeepSeek Platform Oficial (pago por uso)
        └── settings.json.orcarouter.example   # OrcaRouter (DeepSeek V4 Flash gratuito)
```

A cópia ativa `examples/.claude/settings.json` fica fora do controle de versão (`.gitignore`).

---

### Roteiro Prático de Reprodução

1. Crie a conta e gere a chave em uma das plataformas: [DeepSeek Platform](https://platform.deepseek.com/sign_in) ou [OrcaRouter](https://www.orcarouter.ai/login). Opcionalmente valide o modelo gratuito no [OrcaRouter Playground](https://www.orcarouter.ai/pt/playground?model=deepseek%2Fdeepseek-v4-flash-free).
2. Escolha o template desejado e gere o arquivo ativo `.claude/settings.json` ANTES de iniciar os testes:

   ```bash
   cd 0004_deep_claude_alternativa_claudegravity/examples

   # Opção A: DeepSeek Platform oficial
   cp .claude/settings.json.deepseek.example .claude/settings.json

   # Opção B: OrcaRouter gratuito
   # cp .claude/settings.json.orcarouter.example .claude/settings.json
   ```

   No arquivo gerado, preencha o valor de `ANTHROPIC_AUTH_TOKEN` com o seu token real `sk-...`.
3. Valide a integridade do JSON:

   ```bash
   python3 -c "import json; json.load(open('.claude/settings.json'))"
   ```
4. Inicie a sessão aplicando o arquivo com a flag `--settings`:

   ```bash
   claude --settings .claude/settings.json
   ```

   *Recomendação de Ouro:* Inicie **sempre** com `--settings .claude/settings.json`. Isso blinda a execução contra configurações residuais do arquivo de usuário global (`~/.claude/settings.json`), garante que o `modelPicker` substitua os modelos Anthropic no menu `/model` e evita assistentes de login.
5. Teste rápido de inferência no terminal:

   ```bash
   claude -p "Responda somente OK" --max-turns 1
   ```

Para entender as regras arquiteturais detalhadas (`ANTHROPIC_AUTH_TOKEN`, desativação do Advisor, por que não usar `[1m]`, e a gestão de estado global da CLI), consulte o [Artigo Completo](./article/ARTICLE.md) e a documentação em [docs/CHECKLIST_SETTINGS_CLAUDE_CODE.md](../docs/CHECKLIST_SETTINGS_CLAUDE_CODE.md).
