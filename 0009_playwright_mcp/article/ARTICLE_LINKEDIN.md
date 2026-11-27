# O formulário se recupera depois de um erro?

Subimos uma página de frete local e conectamos o Playwright MCP ao VS Code. A interação usa o campo `CEP` e o botão `Calcular frete` pelos nomes expostos ao navegador.

## O que o servidor leva ao assistente

O VS Code inicia um servidor MCP que oferece operações como abrir uma página, obter seu estado e interagir com controles. O snapshot de acessibilidade descreve elementos por papel e nome, como a caixa de texto `CEP` e o botão `Calcular frete`. Isso ajuda a escolher controles a partir do que o navegador expõe ao usuário. [Repositório oficial do Playwright MCP](https://github.com/microsoft/playwright-mcp).

Abra `examples` como raiz do workspace. A [configuração MCP](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0009_playwright_mcp/examples/.vscode/mcp.json) executa o servidor por `npx` com `--isolated` e `--headless`. O perfil isolado começa sem o estado de uma sessão de navegador pessoal. O VS Code pode pedir que você confie no servidor antes de iniciá-lo. Confira o pacote e o comando exibidos na interface. [Configuração de servidores MCP no VS Code](https://code.visualstudio.com/docs/copilot/customization/mcp-servers).

## Modele a experiência antes de pedir o teste

O formulário aceita um CEP no formato de oito dígitos, com hífen opcional. A validação é local e verifica o formato. O valor apresentado é fixo para demonstrar a interação.

| Ação | Resultado na região de status |
| --- | --- |
| Digitar `123` e calcular | `Informe um CEP com 8 dígitos.` |
| Corrigir para `01001-000` e calcular | `Frete simulado: R$ 12,00` |

Faça as duas ações na mesma abertura da página. A segunda etapa verifica também se a mensagem de erro foi substituída. Peça o papel e o nome acessível dos controles, o texto realmente observado e a evidência usada para concluir a verificação.

## Experimente no seu projeto de estudo

Primeiro informe `123` e observe a validação. Na mesma página, corrija para `01001-000` e confira se o status vira `Frete simulado: R$ 12,00`.

O relatório do assistente deve trazer o texto das duas etapas observadas.

[Guia, exemplo e comandos no GitHub](https://github.com/pathbit/pathbit-ai-for-devs/tree/master/0009_playwright_mcp)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
