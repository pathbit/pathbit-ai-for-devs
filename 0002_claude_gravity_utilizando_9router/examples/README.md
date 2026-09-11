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

### 2. Provisionar credenciais e combos

Os arquivos copiados acima usam `ag/gemini-3.8-flash-high` como modelo padrão e apontam os quatro
papéis para modelos individuais do Antigravity. Os dois combos ficam no menu `/model`, como rede de
segurança para quando a cota de uma família estourar  -  e precisam existir no gateway antes da
primeira sessão:

```bash
cd ..
python3 src/sync_antigravity_token.py   # credenciais e a chave do gateway no .env
python3 src/claudegravity.py            # provisiona os dois combos e abre a sessao
cd examples
```

> Sem este passo o gateway não conhece nenhum identificador `ag/*`, e a primeira mensagem falha.
> O `claudegravity.py` resolve credencial e combos de uma vez, por isso é o caminho recomendado.

### 3. Iniciar o Claude Code

Com o container do 9Router em execução na porta `20128` e os combos provisionados:

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
* **`sample_task.py`:** Código Python de exemplo para testar refatoração e planejamento agêntico com o modelo padrão do `settings.json`.
