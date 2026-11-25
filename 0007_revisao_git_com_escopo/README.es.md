# Revisión de Git con alcance verificable

[Português (Brasil)](README.md) · [English](README.en.md) · **Español**

Usa una lista versionada de rutas para revisar los cambios que producen los agentes de código. El laboratorio lee el índice, el árbol de trabajo y los archivos nuevos de Git y muestra qué cambios requieren revisión humana.

## Requisitos

- [Python 3.10 o posterior](https://www.python.org/downloads/). El laboratorio recomienda [Python 3.14.7](https://www.python.org/downloads/release/python-3147/), con instaladores para cada sistema.
- [Git 2.28 o posterior](https://git-scm.com/downloads) disponible en la terminal. Comprueba la versión con `git --version`.

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

Ejecuta el laboratorio en la raíz del repositorio. Crea un checkout temporal independiente, prepara un cambio permitido y añade un archivo protegido.

```sh
python3 0007_revisao_git_com_escopo/examples/run_sandbox.py
```

La salida contiene `allowed.ok: true` para el cambio en `src/app.py`. La segunda ronda contiene `blocked.ok: false` y una infracción `protected` para `.github/workflows/check.yml`. El laboratorio devuelve 0 cuando verifica ambos resultados. Cada ejecución del verificador usa 0 para alcance aprobado, 1 para una infracción y 2 para un error de ejecución.

## Verifica el laboratorio

Ejecuta el grupo de pruebas de este artículo en la raíz del repositorio.

```sh
python3 tools/test_engineering_articles.py GitScopeTests -v
```

[Artículo completo](article/ARTICLE.es.md) · [Ejemplo práctico](examples/README.es.md) · [Artículo para LinkedIn](article/ARTICLE_LINKEDIN.es.md) · [Publicación de difusión](article/POST_LINKEDIN.es.md)

---

Developed with ❤️ by [Pathbit](https://www.pathbit.com.br/)
