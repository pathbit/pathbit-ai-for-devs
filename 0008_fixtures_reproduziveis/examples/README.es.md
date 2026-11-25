# Ejercicio en un entorno aislado

[Português (Brasil)](README.md) · [English](README.en.md) · **Español**

Consulta la [guía del módulo](../README.es.md#requisitos) para preparar el entorno. Ejecuta los comandos en la raíz del repositorio.

```sh
python3 0008_fixtures_reproduziveis/src/build_fixture.py 0008_fixtures_reproduziveis/examples/orders.json.example
python3 0008_fixtures_reproduziveis/src/build_fixture.py 0008_fixtures_reproduziveis/examples/orders.json.example --check 0008_fixtures_reproduziveis/examples/orders.expected.json
```

La primera salida aparece en la terminal. Contiene tres pedidos ordenados por `customer_id`. El nombre `Ana Araújo` aparece en UTF-8 y todos los pedidos tienen la fecha `2026-01-15T12:00:00Z`. Consulta la muestra completa en [orders.expected.json](orders.expected.json).

Copia [orders.json.example](orders.json.example) a `orders-edited.json` en una carpeta temporal. Invierte el orden de `customers` y repite el comando de comparación con tu copia como entrada. Sigue devolviendo 0. Cambia `seed` a `another-seed` y repite. La CLI ahora devuelve 1 y conserva el archivo esperado.

Si el cambio es intencional, genera una salida candidata en una ruta nueva, revisa el diff de valores y actualiza la referencia después de la revisión. El [artículo](../article/ARTICLE.es.md) explica qué cambios afectan la salida.
