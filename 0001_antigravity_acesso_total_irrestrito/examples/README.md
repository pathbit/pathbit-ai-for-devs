# Ambiente Prático de Execução e Testes - Antigravity

Este diretório funciona como o espaço isolado de testes e validação prática do **Google Antigravity** e de agentes autônomos para o Artigo 0001.

As configurações de permissão ficam isoladas dentro de `.claude/` neste diretório, mantendo a raiz do módulo e do repositório completamente limpas.

---

## Como Executar os Testes neste Diretório

### 1. Inicializar as Configurações

Gere os arquivos ativos a partir dos modelos `.example`:

```bash
cp .claude/settings.json.example .claude/settings.json
cp .claude/settings.local.json.example .claude/settings.local.json
```

### 2. Executar a Tarefa de Exemplo com o Agente

Inicie a sessão com o script de teste para verificar a autonomia de leitura e escrita:

```bash
python3 sample_task.py
```

Ou acione o agente CLI com permissão irrestrita:

```bash
agy --dangerously-skip-permissions
```

---

## Arquivos Disponíveis

* **`.claude/`:** Contém modelos de políticas de permissão total (`bypassPermissions`) para testes.
* **`sample_task.py`:** Código Python demonstrando manipulação autônoma de arquivos e geração de relatórios sem interrupções manuais.
