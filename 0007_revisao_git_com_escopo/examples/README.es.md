# Ejercicio en un entorno aislado

[Português (Brasil)](README.md) · [English](README.en.md) · **Español**

Consulta la [guía del módulo](../README.es.md#requisitos) para preparar el entorno. Ejecuta los comandos en la raíz del repositorio.

```sh
python3 0007_revisao_git_com_escopo/examples/run_sandbox.py
```

El laboratorio elimina su carpeta temporal al terminar. Compara las dos listas `changes`. En la primera, la entrada de `src/app.py` viene del `index`. En la segunda, la nueva entrada tiene `stage: untracked` y requiere revisión porque está protegida.

Para usar el verificador en otro proyecto, copia la [plantilla de política](scope.json.example), ajusta las rutas y guarda la copia aprobada fuera del árbol que el agente puede modificar. Sustituye los dos marcadores por las rutas de tu checkout y tu política.

```sh
python3 0007_revisao_git_com_escopo/src/check_scope.py --repo /ruta/al/checkout --policy /ruta/a/politica.json
```

El verificador es de solo lectura. Ejecútalo en un checkout dedicado a la tarea para mantener fuera de la decisión los cambios ajenos. Consulta el [artículo](../article/ARTICLE.es.md) para interpretar los cambios de nombre y los códigos de salida.
