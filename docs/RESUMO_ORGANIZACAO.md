# 📋 Resumo da Organização do Repositório

Este documento detalha a topologia de diretórios do repositório **Pathbit AI for Devs**, a anatomia padrão de cada artigo e o processo para adicionar novos módulos ao catálogo.

---

## 📁 Estrutura de Pastas do Projeto

```text
pathbit-ai-for-devs/
├── 0001_antigravity_acesso_total_irrestrito/  # Artigo 0001: Permissões irrestritas no Antigravity
├── 0002_claude_gravity_utilizando_9router/              # Artigo 0002: ClaudeGravity e roteamento 9Router
├── 0003_fallback_modelos_gratuitos_9router/  # Artigo 0003: Arsenal multi-provedor e fallback
├── docs/                                     # Documentação técnica e padrões de engenharia
├── README.md                                 # Índice executivo do repositório
├── .editorconfig                             # Padronização de indentação e charset
└── .gitignore                                # Regras de proteção de segredos e temporários
```

---

## 🏛️ Anatomia Padrão de um Módulo de Artigo

Cada artigo do repositório é um pacote auto-contido que possui cinco componentes essenciais:

```text
000X_nome_do_artigo/
├── article/
│   └── ARTICLE.md                 # Artigo técnico completo ilustrado para publicação
├── assets/
│   ├── 00_cover_*.png             # Imagem de capa estilizada (1824 x 834)
│   ├── 01_diagrama_*.png          # Diagramas arquiteturais ou conceituais
│   └── 02_evidencia_*.png         # Prints e evidências reais numeradas em ordem
├── src/
│   ├── manage_env.py              # Gerenciador de ciclo de vida (start, status, stop, destroy)
│   ├── verify_*.py                # Script de auditoria e validação de saúde do ambiente
│   └── *.py                       # Scripts utilitários e testes de inferência em Python puro
├── examples/
│   ├── .claude/                   # Sandbox isolado para testes com Claude Code
│   │   ├── settings.json.example  # Configuração padrão versionada
│   │   └── settings.local.json.example
│   ├── README.md                  # Instruções de execução isolada do exemplo
│   └── sample_*.py                # Tarefa prática de demonstração
├── docker-compose.yml             # Manifesto de infraestrutura (quando aplicável)
├── .env.example                   # Modelo limpo de variáveis de ambiente
└── README.md                      # Guia rápido de execução do módulo
```

---

## 🔄 Checklist para Publicação de Novos Artigos

Ao criar um novo módulo (por exemplo, `0004_novo_artigo/`), siga este checklist de qualidade:

1. **Numeração Sequencial:** O prefixo da pasta deve seguir o formato `000X_nome_em_snake_case`.
2. **Imagens e Assets:**
   - Crie a capa com padrão escuro e dimensões adequadas (`00_cover_...`).
   - Nomeie todos os diagramas e prints de acordo com a ordem que aparecem no texto (`01_...`, `02_...`).
3. **Seção Show-Me-The-Code:**
   - Adicione no `ARTICLE.md` a seção `## Show-Me-The-Code` com a Opção 1 (via README) e Opção 2 (via sandbox `examples/`).
4. **Isolamento de Configurações:**
   - Garanta que `.claude/` esteja somente dentro de `examples/`.
   - Adicione arquivos `.example` para todas as configurações que utilizem caminhos ou chaves locais.
5. **Automação em Python:**
   - Todo script deve ser escrito em Python 3 puro sem dependências pesadas de terceiros.
   - Forneça scripts de verificação e testes com saída limpa no terminal.
6. **Integração Cruzada:**
- Acrescente a seção do artigo no `README.md` raiz seguindo o padrão dos existentes: título H3 com link para a pasta, linha `**Ano:** … | **Categoria:** …`, parágrafo de resumo e a linha de três links.
   - Adicione referências cruzadas entre artigos anteriores e futuros na seção de conclusão.
7. **Auditoria de Regras Editoriais:**
   - Verifique que não existam dois-pontos em títulos.
   - Verifique que não existam caracteres de travessão longo.
   - Utilize vocabulário direto e simples.
