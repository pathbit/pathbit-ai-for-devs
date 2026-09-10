# Ambiente Prático de Execução e Testes - Arsenal de Fallback

Este diretório funciona como o espaço de testes e execução prática do **Claude Code** para o Artigo 0003.

A pasta de configuração do Claude Code (`.claude/`) fica isolada aqui dentro, mantendo a raiz do módulo e do repositório completamente limpas.

---

## Como Executar os Testes neste Diretório

### 1. Inicializar as Configurações

Gere os arquivos ativos a partir dos modelos `.example`:

```bash
cp .claude/settings.json.example .claude/settings.json
cp .claude/settings.local.json.example .claude/settings.local.json
```

### 2. Iniciar o Claude Code Conectado ao Combo

Com o 9Router ativo na porta `20128`:

```bash
claude --model arsenal-supremo
```

Ou execute um prompt de teste diretamente:

```bash
claude -p "Explique a lógica do script sample_task.py" --model arsenal-supremo
```

---

## Arquivos Disponíveis

* **`.claude/`:** Contém o mapeamento do combo `arsenal-supremo`, permissões totais e menu interativo `/model`.
* **`sample_task.py`:** Código Python de exemplo para testar inferência resiliente e fallback automático.
