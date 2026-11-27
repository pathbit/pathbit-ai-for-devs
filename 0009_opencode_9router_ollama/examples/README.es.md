# Ejemplo práctico — Enruta OpenCode por 9Router y un modelo local en Ollama

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

[Inicio rápido](../README.es.md)

Sigue primero el inicio rápido. Ejecuta los comandos en las terminales del laboratorio y usa solo los datos descartables del ejercicio.

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

La sonda usa una clave ficticia. Configura tu clave autorizada solo al cambiar a tu 9Router. Comprueba el modelo y usa la misma etiqueta de Ollama en el archivo y el comando.

- [OpenCode configuration](opencode.json.example)
- [Routing probe](probe_server.py)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
