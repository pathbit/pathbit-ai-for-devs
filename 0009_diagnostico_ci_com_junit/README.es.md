# Diagnóstico de CI con informes JUnit

[Português (Brasil)](README.md) · [English](README.en.md) · **Español**

Reúne la evidencia de los jobs obligatorios y distingue pruebas aprobadas, fallos registrados y resultados inconclusos. El laboratorio resume XML locales en JSON sin depender de un servidor de CI.

## Requisitos

- [Python 3.10 o posterior](https://www.python.org/downloads/). El laboratorio recomienda [Python 3.14.7](https://www.python.org/downloads/release/python-3147/), con instaladores para cada sistema.

Los scripts usan solo la biblioteca estándar de Python. Para trabajar en un entorno aislado, créalo en la raíz del repositorio.

```sh
python3 -m venv .venv
. .venv/bin/activate
```

Usa PowerShell en Windows. Una vez activado el entorno, usa `python` en lugar de `python3` en los comandos siguientes.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Inicio rápido

En la raíz del repositorio, ejecuta el caso en que las dos suites obligatorias concluyeron correctamente.

```sh
python3 0009_diagnostico_ci_com_junit/src/diagnose_reports.py --reports 0009_diagnostico_ci_com_junit/examples/passed --jobs api storage
```

La salida muestra `status: passed`, dos pruebas aprobadas en `api` y una en `storage`. El ejemplo que falla devuelve 1. Cuando la evidencia es incompleta, la CLI devuelve 2.

## Verifica el laboratorio

Ejecuta el grupo de pruebas de este artículo en la raíz del repositorio.

```sh
python3 tools/test_engineering_articles.py CiReportsTests -v
```

[Artículo completo](article/ARTICLE.es.md) · [Ejemplo práctico](examples/README.es.md) · [Artículo para LinkedIn](article/ARTICLE_LINKEDIN.es.md) · [Publicación de difusión](article/POST_LINKEDIN.es.md)

---

Developed with ❤️ by [Pathbit](https://www.pathbit.com.br/)
