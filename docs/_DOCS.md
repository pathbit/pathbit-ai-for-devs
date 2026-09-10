# 📚 Documentação Técnica do Pathbit AI for Devs

Esta pasta centraliza toda a documentação técnica, padrões de engenharia, guias operacionais e soluções de problemas do projeto **Pathbit AI for Devs**.

---

## 📋 Índice de Documentos

### 🚀 Guias de Uso e Operação

| Documento | Descrição | Quando Usar |
| :--- | :--- | :--- |
| **[GUIA_CICLO_DE_VIDA_AMBIENTES.md](./GUIA_CICLO_DE_VIDA_AMBIENTES.md)** | Manual de criação, monitoramento, pausa e destruição completa de ambientes (`start`, `status`, `stop`, `destroy`) | Ao subir novas stacks locais ou limpar containers e volumes |
| **[GUIA_INTEGRACAO_CLAUDE_CODE.md](./GUIA_INTEGRACAO_CLAUDE_CODE.md)** | Guia prático de conexão do Claude Code CLI ao 9Router via API Anthropic Messages | Ao rodar o Claude Code com modelos Gemini ou combos de contingência |
| **[GUIA_PERMISSOES_ANTIGRAVITY.md](./GUIA_PERMISSOES_ANTIGRAVITY.md)** | Configuração de acesso irrestrito e autonomia total no ecossistema Google Antigravity | Ao configurar permissões automáticas na IDE, CLI e Agent 2.0 |

---

### 🔧 Soluções para Problemas Técnicos

| Documento | Descrição | Quando Usar |
| :--- | :--- | :--- |
| **[SOLUCAO_PROBLEMAS_COMUNS.md](./SOLUCAO_PROBLEMAS_COMUNS.md)** | Resolução de portas ocupadas, download de modelos locais e bloqueios de SQLite | Ao encontrar erros de conexão, portas ou serviços offline |
| **[SOLUCAO_TOKEN_EXPIRADO_ANTIGRAVITY.md](./SOLUCAO_TOKEN_EXPIRADO_ANTIGRAVITY.md)** | Procedimento de auto-cura para renovação e injeção do token OAuth do Antigravity | Ao receber erro HTTP 401 ou 503 no gateway 9Router |

---

### 📋 Padrões de Engenharia e Arquitetura

| Documento | Descrição | Quando Usar |
| :--- | :--- | :--- |
| **[PADROES_ENGENHARIA_IA.md](./PADROES_ENGENHARIA_IA.md)** | Diretrizes de desenvolvimento de scripts Python, isolamento de segredos e regras editoriais | Antes de criar novos scripts, artigos ou automações |
| **[RESUMO_ORGANIZACAO.md](./RESUMO_ORGANIZACAO.md)** | Topologia de diretórios, anatomia dos módulos de artigos e checklist de publicação | Para entender a estrutura do projeto ou criar novos artigos |
| **[RELATORIO_VALIDACAO.md](./RELATORIO_VALIDACAO.md)** | Evidências de execução end-to-end dos três artigos a partir de um Docker completamente zerado | Para conferir que os artigos publicados foram reproduzidos e comprovados |

---

## 🧭 Como Navegar na Documentação

1. **Identifique a sua necessidade técnica imediata** (operação de containers, integração de CLI ou resolução de falhas).
2. **Consulte as tabelas acima** para abrir o documento específico.
3. **Execute os comandos fornecidos** copiando diretamente os blocos de terminal.
4. **Verifique o resultado** utilizando os utilitários de diagnóstico em Python disponíveis em cada módulo.

---

## 🏷️ Convenções Visuais Utilizadas

* 🚀 = Guias operacionais e passos de execução
* 🔧 = Resolução de problemas e troubleshooting
* 📋 = Normas técnicas e organização
* 🔒 = Segurança, segredos e controle de acesso
* ⚠️ = Avisos importantes e pontos de atenção
* ✅ = Confirmação de status funcional e testes aprovados
* ❌ = Sintoma de erro ou bloqueio

---

## 🤝 Contribuindo com a Documentação

Para adicionar novos guias ou registrar soluções de novos cenários técnicos:

1. Mantenha os arquivos no formato Markdown limpo.
2. Não utilize dois-pontos (`:`) em títulos e subtítulos (`#`, `##`, `###`).
3. Não utilize caracteres de travessão longo; prefira hifens normais (` - `) ou parênteses.
4. Utilize vocabulário direto, simples e técnico, sem palavras rebuscadas.
5. Adicione o novo documento nas tabelas deste índice [`_DOCS.md`](./_DOCS.md).
