# Ejercicio en un entorno aislado

[Português (Brasil)](README.md) · [English](README.en.md) · **Español**

Consulta la [guía del módulo](../README.es.md#requisitos) para preparar el entorno. Ejecuta los comandos en la raíz del repositorio.

```sh
python3 0009_diagnostico_ci_com_junit/src/diagnose_reports.py --reports 0009_diagnostico_ci_com_junit/examples/passed --jobs api storage
python3 0009_diagnostico_ci_com_junit/src/diagnose_reports.py --reports 0009_diagnostico_ci_com_junit/examples/failed --jobs api storage
python3 0009_diagnostico_ci_com_junit/src/diagnose_reports.py --reports 0009_diagnostico_ci_com_junit/examples/incomplete --jobs api storage
```

Cada carpeta contiene informes de una única ejecución ficticia. El primer comando devuelve 0. El segundo devuelve 1 y registra `test-failures` en `api` y `missing-report` en `storage`. El tercero devuelve 2 con `missing-report` en `api` y `skipped-tests` en `storage`.

Inspecciona [la aserción fallida](failed/api.xml) y [la prueba omitida](incomplete/storage.xml). Ejecuta un caso a la vez si tu terminal se detiene ante errores, ya que los dos últimos comandos deben devolver un estado distinto de cero.

Para probarlo con el CI de tu proyecto, usa XML de una sola ejecución, un archivo `<job>.xml` por job esperado, y ajusta los IDs en `--jobs`. El [artículo](../article/ARTICLE.es.md) describe el formato aceptado y el código de salida.
