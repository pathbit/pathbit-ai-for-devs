# Route OpenCode through 9Router and a local Ollama model

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

OpenCode 2.4.x and Python 3.10+. Add your 9Router instance and a local Ollama model for the optional real-service exercise.

## Quick start

Start the probe from the repository root and leave it running.

```bash
python3 0009_opencode_9router_ollama/examples/probe_server.py --port 19809
```

Open a second terminal in the repository root and run the client commands.

```bash
lab=$(mktemp -d)
cp 0009_opencode_9router_ollama/examples/opencode.json.example "$lab/opencode.json"
cd "$lab"
export PATHBIT_ROUTER_BASE=http://127.0.0.1:19809/router/v1
export PATHBIT_ROUTER_KEY=lab-only
export PATHBIT_OLLAMA_BASE=http://127.0.0.1:19809/local/v1
opencode --standalone run --model router/pathbit-code 'Return only a route receipt.'
opencode --standalone run --model local/qwen2.5-coder:7b 'Return only a route receipt.'
```

The sample uses a test key for the local probe. Supply your authorized gateway key only when you switch to your 9Router. Check the model ID and use the exact same Ollama tag in the configuration.

Expected outcome: the two receipts and the two distinct OpenAI-compatible request paths in the probe output.

## Module files

- [Full article](article/ARTICLE.en.md)
- [Practical example](examples/README.en.md)
- [LinkedIn article](article/ARTICLE_LINKEDIN.en.md)
- [LinkedIn post](article/POST_LINKEDIN.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
