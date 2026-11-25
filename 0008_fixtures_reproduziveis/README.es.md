# Fixtures reproducibles para pruebas de integración

[Português (Brasil)](README.md) · [English](README.en.md) · **Español**

Genera una muestra estable de pedidos a partir de datos sintéticos. El laboratorio fija la fecha, calcula valores por ID y compara la salida con un archivo esperado versionado.

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

En la raíz del repositorio, ejecuta el modo de comparación. Lee el archivo de entrada y el esperado sin escribir en ellos.

```sh
python3 0008_fixtures_reproduziveis/src/build_fixture.py 0008_fixtures_reproduziveis/examples/orders.json.example --check 0008_fixtures_reproduziveis/examples/orders.expected.json
```

El mensaje `Fixture matches` indica que la salida coincide byte a byte. La CLI devuelve 0 cuando coincide, 1 cuando difiere y 2 cuando no puede generar o leer un archivo.

## Verifica el laboratorio

Ejecuta el grupo de pruebas de este artículo en la raíz del repositorio.

```sh
python3 tools/test_engineering_articles.py FixtureTests -v
```

[Artículo completo](article/ARTICLE.es.md) · [Ejemplo práctico](examples/README.es.md) · [Artículo para LinkedIn](article/ARTICLE_LINKEDIN.es.md) · [Publicación de difusión](article/POST_LINKEDIN.es.md)

---

Developed with ❤️ by [Pathbit](https://www.pathbit.com.br/)
