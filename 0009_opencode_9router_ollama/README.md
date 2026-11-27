# OpenCode com 9Router e Ollama

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Aproveite o gateway dos primeiros artigos e adicione uma saída local ao cliente OpenCode. Comprove a rota e o identificador de cada sessão com uma sonda compatível com OpenAI.

## Início rápido

### Pré-requisitos

- OpenCode 2.4.x e Python 3.10+.
- Para a etapa real, 9Router configurado como nos artigos anteriores e Ollama com um modelo baixado. A sonda local funciona sem os dois serviços.

### Comprove o roteamento primeiro

Na raiz do repositório, mantenha a sonda em execução em um terminal.

```bash
python3 0009_opencode_9router_ollama/examples/probe_server.py --port 19809
```

Em outro terminal, ainda a partir da raiz, crie uma pasta independente.

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

Os resultados contêm `PATHBIT_ROUTER_OK` e `PATHBIT_LOCAL_OK`. No log da sonda, veja em quais caminhos as chamadas chegaram. Use [a etapa de serviços reais](examples/README.md) para trocar os endereços, escolher um combo existente e repetir a verificação com um pedido do Agregador.

## Material do módulo

- [Artigo completo](article/ARTICLE.md)
- [Arquivos e roteiro do exercício](examples/README.md)
- [Artigo para LinkedIn](article/ARTICLE_LINKEDIN.md)
- [Post para LinkedIn](article/POST_LINKEDIN.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
