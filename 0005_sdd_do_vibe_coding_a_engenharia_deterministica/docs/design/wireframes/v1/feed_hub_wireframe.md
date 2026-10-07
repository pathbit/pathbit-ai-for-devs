# Especificação Canônica de Wireframe v1: Pathbit SDD Feed Hub

> **Versão:** v1.0  
> **Status:** Homologado para Auditoria Visual  
> **Destino de Evidências:** `./tmp/evidencias/specs/01-feed-artigos/`

---

## 🎨 Layout e Componentes Obrigatórios (Design System Pathbit)

### 1. Header Global
- **Logo / Identidade:** `Pathbit SDD Feed Hub` com destaque no subtítulo.
- **Badges de Harness:**
  - Status do Gateway: `9Router :20128` (badge verde esmeralda `#00B050`).
  - Modelo Ativo: `Gemini 3.8 Flash High` (badge roxo `#C3B6FD`).
  - Banco de Dados: `SQLite WAL Mode` (badge cinza neutro).

### 2. Barra de Importação e Controles
- **Input de URL:** Campo de texto com placeholder `https://exemplo.com/feed.xml`.
- **Presets Rápidos:** Botões estilizados para `TechCrunch` e `BBC Tech`.
- **Botão de Ação:** `Importar Feed` com estados:
  - Repouso: roxo gradiente com hover effect.
  - Carregando: spinner animado e texto `Importando...`.
  - Sucesso/Erro: toast ou banner visual descritivo (HTTP 422 em erro).

### 3. Barra de Busca e Filtragem
- **Campo de Busca:** Input amplo `Buscar artigos por título, fonte ou conteúdo...`.
- **Contador Dinâmico:** Exibição em tempo real: `X artigos encontrados`.

### 4. Grid de Artigos Responsivo
- **Layout:** CSS Grid responsivo com colunas mínimas de `320px`.
- **Card de Artigo:**
  - Background dark com efeito glassmorphism (`backdrop-filter: blur(12px)`).
  - Badge de Fonte (categoria/fonte da notícia).
  - Data de Publicação formatada (`YYYY-MM-DD`).
  - Título em destaque com tipografia `Exo 2`.
  - Resumo/Conteúdo com tipografia `Roboto`.
  - Botão/Link `Ler artigo original →`.

### 5. Rodapé Institucional
- Indicação de conformidade: `Desenvolvido sob disciplina Spec-Driven Development (SDD)`.
- Indicador de persistência local atômica e autoria estritamente humana.
