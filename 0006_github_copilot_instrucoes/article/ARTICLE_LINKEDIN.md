# O Copilot conhece a unidade do dinheiro do seu projeto?

No exemplo, a função de frete trabalha em centavos. Colocamos essa convenção em `.github/copilot-instructions.md` e mantivemos as regras de testes em um arquivo com `applyTo`.

## Três lugares para três tipos de informação

| Informação | Onde guardar | Exemplo do laboratório |
| --- | --- | --- |
| Convenção válida para todo o projeto | `.github/copilot-instructions.md` | Dinheiro em centavos e testes com `unittest` |
| Regra condicionada aos arquivos em contexto | `.github/instructions/python-tests.instructions.md` | Testar o ponto de corte e o valor logo abaixo |
| Entrega desta conversa | Prompt do chat | Adicionar casos para o frete grátis |

Abra a pasta `examples` como raiz do workspace. No exemplo, o arquivo de instruções geral indica `src/pricing.py` como fonte da regra e fornece o comando de teste que já existe. Registre no arquivo o que o agente teria dificuldade para inferir ou costuma errar. Quando a estrutura do projeto mudar, ajuste os caminhos no mesmo PR.

## Oriente apenas os testes Python

O arquivo de regras para testes começa com este front matter. [Arquivo completo](https://github.com/pathbit/pathbit-ai-for-devs/blob/master/0006_github_copilot_instrucoes/examples/.github/instructions/python-tests.instructions.md).

```yaml
---
applyTo: 'tests/**/*.py'
---
```

O padrão é relativo ao workspace e se aplica a Python dentro de `tests/`. No chat local do VS Code, uma instrução com `applyTo` pode entrar no contexto quando um arquivo correspondente está em uso. Abra ou anexe `tests/test_pricing.py` ao prompt para tornar a comparação observável. A documentação do VS Code descreve também a inclusão manual de uma instrução e o diagnóstico de personalizações. [Instruções personalizadas no VS Code](https://code.visualstudio.com/docs/agent-customization/custom-instructions).

## Experimente no seu projeto de estudo

O caso de frete grátis passa de `750` para `0` entre `9_999` e `10_000`. Use o chat para propor o teste, confira o diff e rode `unittest`.

O que deixava o prompt longo vira uma instrução revisável junto ao código.

[Guia, exemplo e comandos no GitHub](https://github.com/pathbit/pathbit-ai-for-devs/tree/master/0006_github_copilot_instrucoes)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
