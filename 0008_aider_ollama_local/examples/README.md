# Exercício de aider com um modelo local no Ollama

Use uma cópia desta pasta e um repositório Git descartável. Siga o [início rápido](../README.md) para rodar Ollama e Aider. Adicione os dois arquivos ao contexto do Aider.

## Prompt para o Aider

```text
Valide a entrada de total_minutes em src/durations.py. Horas negativas e
minutos menores que 0 ou maiores que 59 devem lançar ValueError. Preserve a
assinatura e a conversão dos valores válidos. Acrescente testes para -1 hora,
-1 minuto, 59 e 60 minutos em tests/test_durations.py.

```

A checagem final é `python3 -m unittest discover -s tests -v`. Confira também se o diff ficou limitado a [durations.py](src/durations.py) e [test_durations.py](tests/test_durations.py).
