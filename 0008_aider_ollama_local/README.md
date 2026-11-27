# Aider com um modelo local no Ollama

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Use o Aider para propor uma pequena correção Python com o modelo de código rodando no seu computador. Revise os arquivos alterados e execute a suíte.

## Estrutura do módulo

- [Artigo completo](article/ARTICLE.md)
- [Artigo para LinkedIn](article/ARTICLE_LINKEDIN.md)
- [Post para LinkedIn](article/POST_LINKEDIN.md)
- [Exemplo prático e prompt](examples/README.md)

## Pré-requisitos

- [Ollama](https://ollama.com/download) e [Aider](https://aider.chat/docs/install.html).
- Git, Python 3.10 ou superior e espaço para o modelo. A tag `qwen2.5-coder:7b` ocupa cerca de 4,7 GB no catálogo.

## Início rápido

Inicie o Ollama pelo aplicativo ou por `ollama serve`, se ainda não estiver rodando. Confirme `ollama list`. Copie `examples` para um diretório descartável e entre nele antes dos comandos Git abaixo.

```bash
git init
git add src tests
git commit -m 'Add duration example baseline'
python3 -m unittest discover -s tests -v
ollama pull qwen2.5-coder:7b
OLLAMA_API_BASE=http://127.0.0.1:11434 aider --model ollama_chat/qwen2.5-coder:7b \
  --no-auto-commits --no-dirty-commits --no-analytics --no-check-update src/durations.py tests/test_durations.py
```

No PowerShell, defina `$env:OLLAMA_API_BASE = 'http://127.0.0.1:11434'` e execute o comando `aider` em uma linha. Use o [prompt do exercício](examples/README.md), encerre a sessão com `/exit`, examine `git diff` e rode os testes.

Developed with ❤️ by [Pathbit](https://pathbit.co/)
