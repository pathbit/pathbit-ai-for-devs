# Practical example — Route OpenCode through 9Router and a local Ollama model

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

[Quick start](../README.en.md)

Follow the quick start first. Run the commands in the same lab terminals and use only the disposable data for this exercise.

```bash
export PATHBIT_ROUTER_BASE=http://127.0.0.1:20128/v1
read -r -s -p 'Chave do 9Router: ' PATHBIT_ROUTER_KEY
printf '\n'
export PATHBIT_ROUTER_KEY
curl -fsS -H "Authorization: Bearer $PATHBIT_ROUTER_KEY" "$PATHBIT_ROUTER_BASE/models"
opencode --standalone run --model router/pathbit-code 'Responda apenas OK.'
```

```bash
export PATHBIT_OLLAMA_BASE=http://127.0.0.1:11434/v1
ollama pull qwen2.5-coder:7b
ollama list
opencode --standalone run --model local/qwen2.5-coder:7b 'Responda apenas OK.'
```

The sample uses a test key for the local probe. Supply your authorized gateway key only when you switch to your 9Router. Check the model ID and use the exact same Ollama tag in the configuration.

- [OpenCode configuration](opencode.json.example)
- [Routing probe](probe_server.py)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
