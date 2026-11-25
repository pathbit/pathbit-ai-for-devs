# Exercício no ambiente isolado

**Português (Brasil)** · [English](README.en.md) · [Español](README.es.md)

Abra o [guia do módulo](../README.md#pré-requisitos) para preparar o ambiente. Execute os comandos na raiz do repositório.

```sh
python3 0007_revisao_git_com_escopo/examples/run_sandbox.py
```

O laboratório remove a pasta temporária ao terminar. Veja a diferença entre as duas listas `changes`. Na primeira, a entrada de `src/app.py` vem do `index`. Na segunda, a entrada nova tem `stage: untracked` e exige revisão por ser protegida.

Para usar em outro projeto, copie o [modelo de política](scope.json.example), ajuste os caminhos e mantenha a cópia aprovada fora da árvore que o agente pode alterar. Substitua os dois caminhos do comando com seu checkout e sua política.

```sh
python3 0007_revisao_git_com_escopo/src/check_scope.py --repo /caminho/do/checkout --policy /caminho/da/politica.json
```

O verificador é de leitura. Rode em um checkout dedicado à tarefa para que mudanças de outras pessoas ou de outras entregas não entrem na mesma decisão. Consulte também o [artigo](../article/ARTICLE.md) para interpretar renomeações e códigos de saída.
