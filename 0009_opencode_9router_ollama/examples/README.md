# Da sonda local para o 9Router e o Ollama reais

Comece pela [sonda](../README.md) e confira os recibos antes de trocar os destinos. Use a chave da sua instância, com escopo apropriado. Digite no terminal e guarde no ambiente da sessão. O exemplo não versiona credenciais.

## Gateway

Use o endereço e a porta que sua stack expõe. Em Bash, os comandos abaixo consultam primeiro o catálogo. Substitua `pathbit-code` no arquivo [opencode.json.example](opencode.json.example) e no comando se o ID do seu combo for outro.

```bash
export PATHBIT_ROUTER_BASE=http://127.0.0.1:20128/v1
read -r -s -p 'Chave do 9Router: ' PATHBIT_ROUTER_KEY
printf '\n'
export PATHBIT_ROUTER_KEY
curl -fsS -H "Authorization: Bearer $PATHBIT_ROUTER_KEY" "$PATHBIT_ROUTER_BASE/models"
opencode --standalone run --model router/pathbit-code 'Responda apenas OK.'
```

## Ollama

O Ollama precisa ouvir em loopback. Se o aplicativo ainda não está rodando, inicie-o antes do `pull`. Confira a tag carregada na máquina.

```bash
export PATHBIT_OLLAMA_BASE=http://127.0.0.1:11434/v1
ollama pull qwen2.5-coder:7b
ollama list
opencode --standalone run --model local/qwen2.5-coder:7b 'Responda apenas OK.'
```

Use um cliente OpenCode aberto na pasta que contém a configuração. Para comparar os destinos com o Agregador, copie-a para a cópia descrita no [artigo 0006](../../0006_openspec_claude_code/README.md). Anexe `src/routes/favoritos.js` por `--file` apenas quando o destino for autorizado para os dados do projeto.
