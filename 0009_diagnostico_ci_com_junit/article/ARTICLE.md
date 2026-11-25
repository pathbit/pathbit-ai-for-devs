# Diagnóstico de CI com relatórios JUnit

**Português (Brasil)** · [English](ARTICLE.en.md) · [Español](ARTICLE.es.md)

![Relatórios JUnit resultam em aprovação, falha ou evidência insuficiente](../assets/00_cover_ci_junit.png)

Ao diagnosticar um CI vermelho, abra a evidência da execução antes de pedir uma correção ao agente. `api` pode ter registrado uma asserção falha, enquanto `storage` pode nem ter publicado um relatório. As duas situações exigem ações distintas. A primeira pede investigar um comportamento. A segunda pede recuperar a evidência do job.

## Pré-requisitos

- [Python 3.10 ou posterior](https://www.python.org/downloads/). A versão recomendada para o laboratório é o [Python 3.14.7](https://www.python.org/downloads/release/python-3147/), com instaladores para cada sistema.
- Ambiente virtual opcional. Veja [como preparar](../README.md#pré-requisitos).

## Registre quais jobs eram obrigatórios

O relatório disponível diz o que aconteceu em uma suíte, mas a lista de jobs esperados precisa vir de fora dos XMLs. No laboratório, `--jobs api storage` define a lista. Cada artefato de origem tem o nome `<job>.xml` e vem da mesma execução. Guarde o identificador da execução de CI e o commit junto ao resumo.

A CLI aceita o subconjunto de XML JUnit com raiz `<testsuite>` ou `<testsuites>` com suítes diretas. Ela conta elementos `<testcase>` e classifica `<failure>`, `<error>` e `<skipped>`. Quando presentes, os totais declarados devem bater com os casos. O laboratório trabalha com XML UTF-8 local de até 1 MiB e rejeita DTD. Elementos de resultado desconhecidos deixam o relatório inconclusivo. Confirme o formato exportado pelo seu runner antes de reaproveitar o parser. [ElementTree na biblioteca padrão](https://docs.python.org/3/library/xml.etree.elementtree.html).

## Separe falha de evidência insuficiente

| Evidência da execução | Estado agregado | Saída |
| --- | --- | --- |
| Todos os relatórios necessários têm testes e todos passam | `passed` | 0 |
| Algum relatório válido contém falha ou erro de teste | `failed` | 1 |
| Ausência, XML inválido, relatório vazio ou teste pulado, sem falha observada | `inconclusive` | 2 |

A falha observada tem prioridade no agregado. No cenário de exemplo, `api` rejeita o contrato e `storage` está ausente. O comando retorna 1 e registra os dois motivos. Um relatório incompleto por teste pulado impede aprovação nesta política. Defina quais skips são aceitáveis com a equipe antes de adaptar a regra ao seu projeto.

## Passe a evidência certa para a próxima pessoa

Leia os contadores do resumo e abra o relatório de origem para investigar a asserção, o ambiente ou a configuração. O JSON mantém contagens e motivos, sem copiar mensagens e stack traces que podem incluir dados internos. Use os XMLs apenas no acesso previsto para os artefatos do CI.

Rode esse resumo junto aos status dos jobs. Um build pode falhar depois de escrever um XML aprovado, e CI pode encerrar antes de iniciar os testes. Use a conclusão do pipeline, o gate HTTP do [artigo 0006](../../0006_gate_de_release_de_contratos/article/ARTICLE.md) e as evidências geradas para tomar a decisão final.

## Show-Me-The-Code

### Opção 1. Rode no seu ambiente

O [guia do módulo](../README.md) executa o cenário aprovado usando Python e XMLs locais.

### Opção 2. Compare os três cenários locais

O [exemplo isolado](../examples/README.md) inclui uma falha e uma execução inconclusiva. Compare os motivos esperados antes de conectar o verificador ao CI.

## Aplique a sequência em uma entrega

Confira [o escopo das mudanças](../../0007_revisao_git_com_escopo/article/ARTICLE.md), preserve [as entradas dos testes](../../0008_fixtures_reproduziveis/article/ARTICLE.md) e examine o resultado da execução. Cada etapa deixa uma evidência diferente para a revisão.
