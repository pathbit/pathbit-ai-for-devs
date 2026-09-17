# Ambiente Prático de Execução e Testes - Antigravity

Este diretório funciona como o espaço isolado de testes e validação prática do **Google Antigravity** e de agentes autônomos para o Artigo 0001.

---

## Como Executar os Testes neste Diretório

### 1. Executar a Tarefa de Exemplo com o Script de Teste

Execute o script de teste para verificar a autonomia de geração de relatórios e manipulação de arquivos:

```bash
python3 sample_task.py
```

### 2. Executar o Agente Antigravity com Autonomia Total

Acione o agente CLI do Antigravity com permissão irrestrita no ambiente de desenvolvimento:

```bash
agy --dangerously-skip-permissions
```

> Nesse modo o agente recebe autoridade de terminal para execução ágil de ferramentas. Use em diretórios de trabalho isolados e leia a seção de Gestão de Risco do artigo.

---

## Arquivos Disponíveis

* **`sample_task.py`:** Código Python demonstrando geração de artefatos de telemetria e operação autônoma sem interrupções manuais.
* Se você deseja integrar essa autonomia de execução com o **Claude Code CLI**, consulte o [Artigo 0002](../../0002_claude_gravity_utilizando_9router/article/ARTICLE.md), onde o harness da Anthropic é configurado com políticas de permissão e roteamento via 9Router.
