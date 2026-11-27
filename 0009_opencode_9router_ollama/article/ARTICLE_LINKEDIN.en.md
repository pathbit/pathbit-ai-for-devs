# Route OpenCode through 9Router and a local Ollama model

The gateway from articles 0002 and 0003 already manages model routing. This lab connects OpenCode to that gateway and keeps a second local route for Ollama. The observed destination and model ID matter as much as the answer returned to the terminal.

## Map the client selectors to upstream models

OpenCode chooses `router/pathbit-code` or `local/qwen2.5-coder:7b`. The prefix selects the configured provider. The gateway receives `pathbit-code` and Ollama receives `qwen2.5-coder:7b`. A gateway bound to loopback can still delegate to an external model. Check the upstream and data policy before attaching source files.

## Use the OpenCode 2.4 configuration format

The sample uses `providers`, `package`, and `settings` and loads environment values. Point `baseURL` to `/v1`. The compatible runtime adds `/chat/completions`. Keep a real gateway key out of the JSON file and use the model names recognized by your services.

## Observe a real CLI request against the local probe

Start `probe_server.py` and point the two provider URLs at its `/router/v1` and `/local/v1` routes. Run OpenCode twice with `--model`. Verify `PATHBIT_ROUTER_OK` and `PATHBIT_LOCAL_OK`, then confirm the path and model match at the probe. This verifies transport and selection with deterministic responses.

## Switch to real services one at a time

Inspect the gateway's model catalogue, select the combo you use, and send a small request. Start Ollama and pull the listed model tag before trying the second route. Start with a short request. For a task tied to the aggregator, attach only the favorites router and ask for the filter and limit.

## Distinguish switching from fallback

The gateway may fall back within the configured combo. The example selects between the gateway and the local route explicitly. Diagnose a `401` by checking the credential and a `404` by checking the model ID and path. A text prompt does not establish tool-call compatibility for a long agent task.

[Read the full article](https://github.com/pathbit/pathbit-ai-for-devs/tree/master/0009_opencode_9router_ollama/article/ARTICLE.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
