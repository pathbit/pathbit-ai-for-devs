# Como trabalhar em paralelo com Claude Code e Git Worktrees no mesmo projeto

![Duas mudanças e uma integração](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0008_claude_code_worktrees/assets/00_capa.png)


A primeira sessão do Claude Code começou a alterar `src/server.js`. A segunda precisa ajustar a apresentação do dashboard. As duas mudanças são independentes, mas ambas as sessões veem a mesma pasta, os mesmos arquivos não commitados e a mesma base SQLite. Quando uma dispara `git status`, o diff mistura os dois trabalhos. Se as duas rodarem o servidor na mesma porta, podem até conferir o aplicativo errado.

No [artigo 0007](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0007_skills_claude_code/article/ARTICLE.md), empacotamos o roteiro de leitura e planejamento em uma Skill. Agora as propostas viram duas tarefas do Agregador. Cada uma pode ser desenvolvida em uma sessão do Claude Code com seu próprio diretório e branch. No fim, uma terceira pasta recebe os commits e executa a validação integrada.

## Branch, pasta e sessão são três objetos diferentes

A branch aponta para uma sequência de commits. A worktree fornece uma pasta e um índice Git próprios para uma branch, compartilhando os objetos e as referências do mesmo repositório. A sessão do agente tem contexto de conversa e um diretório de trabalho. Você consegue fechar a sessão e preservar um commit na worktree. Também pode ter duas sessões em pastas diferentes que consultam o mesmo servidor externo. É por isso que código, processos e dados precisam de decisões separadas.

| Recurso | Compartilhado | Selecionado por tarefa |
| --- | --- | --- |
| Objetos Git e referências | Sim | Cada pasta faz checkout de uma branch diferente |
| Arquivos editados e índice | Por pasta | A sessão abre a raiz da worktree |
| Dependências geradas e banco local | Conforme a configuração | Instale dependências e use base própria por execução |
| Portas e serviços externos | Dependem do ambiente | Use portas distintas e confira o destino antes de testar |
| Conversa do Claude Code | Por sessão | Nomeie a tarefa e valide o diretório informado pelo CLI |

Um `git worktree add` não copia `.env`, `node_modules` ou bancos ignorados. Pode haver outras regras na ferramenta que cria o checkout, então confirme o estado real. Neste laboratório usamos bancos em diretórios locais e o Agregador instala o SQLite nativo em cada pasta que precisa rodar o aplicativo. Reutilizar um servidor de desenvolvimento torna a evidência ambígua, pois a requisição pode chegar à versão anterior do código. [Documentação de Git Worktree](https://git-scm.com/docs/git-worktree).

## Divida o Agregador por uma fronteira que o código já tem

Primeira tarefa: adicionar `GET /health` com `200` e `{"status":"ok"}`. O endpoint responde se o processo recebeu uma requisição. Os testes protegem `/`, `/artigos` e os outros contratos do estudo de caso. Segunda tarefa: alterar o `h1` do dashboard para `Meu Agregador de Notícias`. O texto muda, enquanto a busca, as categorias e os favoritos continuam cobertos pelo roteiro.

Na divisão proposta, a primeira sessão mexe no servidor e nos testes de API. A segunda mexe apenas no arquivo estático. Elas não disputam o schema de SQLite, o lockfile ou a arquitetura do aplicativo. Escolha fronteiras desse tipo antes de abrir vários agentes. Se duas entregas precisarem mudar a mesma interface pública, escreva e aprove o contrato comum primeiro.

## Caminho 1 com as worktrees do Claude Code

Na cópia inicializada conforme o [guia](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0008_claude_code_worktrees/README.md), execute em dois terminais. O `--worktree` aceita um nome de tarefa. Cada sessão trabalha em uma pasta criada para ela. Depois que abrir, peça `git status --short --branch` e `git rev-parse --show-toplevel` para verificar o ponto de partida. Leia as permissões exibidas pelo cliente antes de rodar comandos.

```bash
claude --worktree api-health
claude --worktree dashboard-title
```

A criação padrão do Claude Code parte da branch padrão remota quando está disponível. Em um repositório de demonstração sem remoto, ele pode partir do `HEAD` local. A configuração `worktree.baseRef` pode selecionar `head` quando você quer começar a partir dos seus commits locais. Se você precisa partir de um commit ou branch específica fora dessas opções, crie a worktree pelo Git. [Worktrees no Claude Code](https://code.claude.com/docs/en/worktrees).

Cada sessão recebe apenas o [pedido da sua tarefa](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0008_claude_code_worktrees/examples/prompts.md). Faça o agente explicar como verificou o diretório e que comandos deve executar. Antes de salvar cada commit, o mantenedor lê `git diff` dentro da própria worktree. Uma sessão não precisa copiar mudanças da outra para provar que alterou o arquivo certo.

## Caminho 2 com Git direto e decisões explícitas

Para escolher nome de branch, destino e base sem depender do padrão do cliente, crie as worktrees com Git. Na cópia do laboratório, atribua `base=$(git rev-parse HEAD)` antes de editar. Use `git worktree add -b lab/api-health ../api-health "$base"` e `git worktree add -b lab/dashboard-title ../dashboard-title "$base"`. Depois entre em cada pasta e inicie `claude`.

A [referência pronta](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0008_claude_code_worktrees/examples/README.md) fornece patches para reproduzir os dois resultados. Comece com os patches se você quer entender isolamento e integração antes de testar a qualidade das sugestões do modelo. Você vai observar o mesmo processo Git e a mesma aplicação.

## Integre no checkout que serve como referência

Quando a tarefa de API estiver pronta, `git diff "$base"..lab/api-health` deve mostrar a rota e o teste. O diff equivalente da segunda branch deve mostrar o texto do dashboard. No checkout de integração, incorpore o commit de cada tarefa pelo procedimento adotado no seu projeto. O exemplo usa `git cherry-pick` em um repositório local descartável. Faça isso em ordem e rode a suíte depois de aplicar ambos.

| Verificação | Na branch de API | Na branch de dashboard | Após integrar |
| --- | --- | --- | --- |
| `GET /health` | `200` com JSON | Rota ausente | `200` com JSON |
| Texto do `h1` | Título original | `Meu Agregador de Notícias` | `Meu Agregador de Notícias` |
| Fluxos existentes do Agregador | Suíte da aplicação | Suíte da aplicação | Suíte executada no conjunto |

Em caso de conflito, pare de iniciar novas sessões sobre o mesmo arquivo. Compare as duas mudanças com a base, preserve os critérios de ambas e confira o resultado na árvore integrada. Se uma branch ficou para trás porque a interface comum mudou, decida em que branch o ajuste pertence e revise-a como uma mudança explícita.

## Show-Me-The-Code

1. Prepare o Agregador e registre o estado inicial com o [guia](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0008_claude_code_worktrees/README.md).
2. Abra as duas worktrees e escolha um dos dois caminhos de execução.
3. Verifique os commits por tarefa e integre em um terceiro checkout local.
4. Faça `npm test` na árvore integrada. Suba um único servidor em `127.0.0.1:19808` para observar a resposta de `/health` e o título servido.
5. Examine `git worktree list` antes de limpar. Preserve sessões e arquivos que ainda estejam em uso. Para uma worktree Git já integrada e sem trabalho pendente, `git worktree remove <caminho>` pode retirar o checkout associado.

## Diagnóstico quando as sessões se confundem

Se o agente reportar um arquivo da outra tarefa, compare `pwd`, `git branch --show-current` e `git log -1` dentro da sessão. Se o código correto devolve uma resposta inesperada, confira a porta e o caminho da base passados ao processo Node. Se a remoção recusar porque há mudanças ou bloqueio, leia o status da worktree e preserve o trabalho antes de liberar a pasta.

O [artigo 0009](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0009_opencode_9router_ollama/article/ARTICLE.md) volta à infraestrutura dos artigos 0002 e 0003 para comparar um caminho por gateway e outro por modelo local.

[Repositório e arquivos do laboratório](https://github.com/pathbit/pathbit-ai-for-devs/tree/master/0008_claude_code_worktrees)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
