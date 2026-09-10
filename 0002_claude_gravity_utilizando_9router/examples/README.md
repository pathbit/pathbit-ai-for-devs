# Ambiente Prático de Execução e Testes - ClaudeGravity

Este diretório funciona como o espaço de testes e execução prática do **Claude Code** para o Artigo 0002.

A pasta de configuração do Claude Code (`.claude/`) fica isolada aqui dentro, garantindo que a raiz do artigo e do projeto permaneçam limpas e organizadas.

---

## Como Executar os Testes neste Diretório

### 1. Inicializar as Configurações

Se ainda não o fez, gere os arquivos ativos a partir dos modelos `.example`:

```bash
cp .claude/settings.json.example .claude/settings.json
cp .claude/settings.local.json.example .claude/settings.local.json
```

### 2. Iniciar o Claude Code

Com o container do 9Router em execução na porta `20128`:

```bash
claude
```

Ou execute uma instrução direta no terminal:

```bash
claude -p "Analise o arquivo sample_task.py e sugira melhorias de desempenho"
```

---

## Arquivos Disponíveis

* **`.claude/`:** Contém os arquivos de política de permissões e menu interativo `/model`.
* **`sample_task.py`:** Código Python de exemplo para testar refatoração e planejamento agêntico com o Gemini 3.8 Flash High.
