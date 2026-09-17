# pathbit-ai-for-devs

## 0004_deep_claude_alternativa_claudegravity

![Capa - DeepClaude](assets/00_cover_deepclaude.png)

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
│   └── ARTICLE.md                             # Artigo completo: capa + 41 prints e análise técnica
├── assets/                                    # Imagens, telas e capas oficiais
│   ├── cover_linkedin.png                     # Capa para compartilhamento no LinkedIn
│   ├── 00_cover_deepclaude.png                # Capa oficial do artigo
│   └── ...                                    # 41 prints de evidência visual (01 a 42, sem o 08)
├── src/
│   └── verify_deepclaude.py                   # Verificador de consistência e inferência real
└── examples/
    ├── README.md                              # Instruções de execução prática
    └── .claude/
        ├── settings.local.json.deepseek.example     # DeepSeek Platform Oficial (pago por uso)
        └── settings.local.json.orcarouter.example   # OrcaRouter (DeepSeek V4 Flash gratuito)
```

Só os templates `.example` são versionados. A cópia ativa `examples/.claude/settings.local.json` — a que carrega o seu token real — fica fora do Git pelo `.gitignore`.

**Por que `settings.local.json` e não `settings.json`?** Porque o arquivo carrega uma credencial pessoal. O `.claude/settings.json` existe para configuração *compartilhada do time*, comitada no repositório; usá-lo aqui significaria impor o redirecionamento de provedor a qualquer pessoa que clonasse o projeto. O artigo detalha os cinco escopos de configuração da CLI e a precedência entre eles.

---

### Roteiro Prático de Reprodução

1. Crie a conta e gere a chave em uma das plataformas: [DeepSeek Platform](https://platform.deepseek.com/sign_in) ou [OrcaRouter](https://www.orcarouter.ai/login). Opcionalmente valide o modelo gratuito no [OrcaRouter Playground](https://www.orcarouter.ai/pt/playground?model=deepseek%2Fdeepseek-v4-flash-free).
2. Escolha o template desejado e gere o arquivo ativo `.claude/settings.local.json` ANTES de iniciar os testes:

   ```bash
   cd 0004_deep_claude_alternativa_claudegravity/examples

   # Opção A: DeepSeek Platform oficial
   cp .claude/settings.local.json.deepseek.example .claude/settings.local.json

   # Opção B: OrcaRouter gratuito
   # cp .claude/settings.local.json.orcarouter.example .claude/settings.local.json
   ```

   No arquivo gerado, preencha o valor de `ANTHROPIC_AUTH_TOKEN` com o seu token real `sk-...`.
3. Valide a integridade do JSON:

   ```bash
   python3 -c "import json; json.load(open('.claude/settings.local.json'))"
   ```
4. Inicie a sessão aplicando o arquivo com a flag `--settings`:

   ```bash
   claude --settings .claude/settings.local.json
   ```

   *Regra de Ouro:* Inicie **sempre** com `--settings .claude/settings.local.json`. É a única forma de o `modelPicker` ser honrado a partir de uma pasta de projeto (a CLI ignora esse bloco em checkouts locais) e de evitar a tela de login no primeiro uso.

   *Regra de Ouro nº 2:* No menu `/model`, use a tecla **`s`** (apenas esta sessão) ou `Esc`. **Nunca Enter** — Enter significa "salvar como padrão" e grava o modelo no seu `~/.claude/settings.json` global, fazendo o DeepSeek virar o padrão de toda nova sessão, inclusive nas que usam a sua conta Anthropic.
5. Teste rápido de inferência no terminal:

   ```bash
   claude --settings .claude/settings.local.json -p "Responda somente OK" --max-turns 1
   ```

---

### Verificação Automatizada

O módulo traz um verificador que confere a configuração e, opcionalmente, dispara uma inferência real contra o provedor ativo:

```bash
cd 0004_deep_claude_alternativa_claudegravity

python3 src/verify_deepclaude.py              # validação offline, sem rede
python3 src/verify_deepclaude.py --online     # inclui uma chamada real à API
python3 src/verify_deepclaude.py --fix-global # limpa um modelo vazado para o settings global
```

Ele valida a sintaxe dos JSON, exige `ANTHROPIC_AUTH_TOKEN` (e recusa `ANTHROPIC_API_KEY`), recusa o sufixo `[1m]` em qualquer identificador, detecta `ANTHROPIC_BASE_URL` terminada em `/v1`, garante que os templates versionados não carreguem credencial real e avisa se o seu `~/.claude/settings.json` global foi contaminado com um modelo de terceiros.

Para conferir a consistência entre os artigos e o repositório (JSON transcrito, imagens citadas, links e convenção de nomes), rode a partir da raiz:

```bash
make valida-consistencia
```

Para entender as regras arquiteturais detalhadas (`ANTHROPIC_AUTH_TOKEN`, desativação do Advisor, por que não usar `[1m]`, e a gestão de estado global da CLI), consulte o [Artigo Completo](./article/ARTICLE.md) e a documentação em [docs/CHECKLIST_SETTINGS_CLAUDE_CODE.md](../docs/CHECKLIST_SETTINGS_CLAUDE_CODE.md).
