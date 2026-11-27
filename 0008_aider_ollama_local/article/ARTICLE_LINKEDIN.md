# Uma correção Python com o modelo rodando no seu computador

O laboratório usa Aider e Ollama para ajustar uma função que aceita minutos fora do intervalo. O modelo recebe dois arquivos e o patch fica disponível para revisão antes do commit.

## Como as ferramentas conversam

| Componente | Responsabilidade |
| --- | --- |
| Ollama | Carrega o modelo e responde pela API de loopback |
| Aider | Monta a conversa com os arquivos selecionados e aplica edições |
| Git e `unittest` | Mostram o patch e executam o contrato revisado |

`OLLAMA_API_BASE` aponta o Aider para `http://127.0.0.1:11434`. Use o prefixo `ollama_chat/` no identificador do modelo para a integração de chat. O download do modelo exige rede e espaço em disco. A inferência do exercício usa o servidor local e dispensa credenciais de um provedor de modelos na nuvem. [Integração Aider com Ollama](https://aider.chat/docs/llms/ollama.html).

## Escolha o contexto antes de aumentar o modelo

O procedimento usa `qwen2.5-coder:7b` como exemplo disponível no catálogo do Ollama. O tamanho do arquivo baixado e a memória durante a geração são medidas diferentes. Se o computador tiver poucos recursos, comece por `qwen2.5-coder:3b` e ajuste a tag nos dois comandos. Reserve modelos menores para tarefas curtas e confira se a ferramenta consegue interpretar a edição. [Família Qwen 2.5 Coder no Ollama](https://ollama.com/library/qwen2.5-coder).

Passe `src/durations.py` e `tests/test_durations.py` ao iniciar o Aider. Declare no prompt que essa tarefa se limita a esses arquivos. Use `--no-auto-commits` para deixar a criação de commits sob seu controle e `--no-analytics` para desativar a telemetria do Aider na sessão. Revise também opções e configurações locais se estiver adotando a ferramenta para código de trabalho. [Opções do Aider](https://aider.chat/docs/config/options.html).

## Experimente no seu projeto de estudo

Indique o endpoint de loopback, use um modelo `ollama_chat/` e confira `59` e `60` minutos nos testes. Mantenha a conversão de `1h15` como controle.

O tamanho do modelo muda o custo de execução. O caso de teste continua sendo o mesmo.

[Guia, exemplo e comandos no GitHub](https://github.com/pathbit/pathbit-ai-for-devs/tree/master/0008_aider_ollama_local)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
