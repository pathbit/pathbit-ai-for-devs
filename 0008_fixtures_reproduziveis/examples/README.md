# Exercício no ambiente isolado

**Português (Brasil)** · [English](README.en.md) · [Español](README.es.md)

Abra o [guia do módulo](../README.md#pré-requisitos) para preparar o ambiente. Execute os comandos na raiz do repositório.

```sh
python3 0008_fixtures_reproduziveis/src/build_fixture.py 0008_fixtures_reproduziveis/examples/orders.json.example
python3 0008_fixtures_reproduziveis/src/build_fixture.py 0008_fixtures_reproduziveis/examples/orders.json.example --check 0008_fixtures_reproduziveis/examples/orders.expected.json
```

A primeira saída vai para o terminal. Ela contém três pedidos ordenados por `customer_id`. O nome `Ana Araújo` aparece em UTF-8 e todos os pedidos têm a data `2026-01-15T12:00:00Z`. Confira a amostra completa em [orders.expected.json](orders.expected.json).

Em uma pasta temporária, copie [orders.json.example](orders.json.example) para `orders-edited.json`. Inverta a ordem de `customers` e repita o comando de comparação, trocando o argumento de entrada pelo caminho da sua cópia. O resultado continua 0. Altere `seed` para `another-seed` e repita. Agora a CLI retorna 1 e mantém o arquivo esperado.

Se a mudança for intencional, gere uma saída candidata em um caminho novo, inspecione o diff de valores e atualize a referência após revisão. O [artigo](../article/ARTICLE.md) mostra quais mudanças afetam a saída.
