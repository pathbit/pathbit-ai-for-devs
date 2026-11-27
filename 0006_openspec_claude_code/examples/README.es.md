# Ejemplo práctico — Evoluciona el agregador con OpenSpec y Claude Code

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

[Inicio rápido](../README.es.md)

Sigue primero el inicio rápido. Ejecuta los comandos en las terminales del laboratorio y usa solo los datos descartables del ejercicio.

```bash
curl -is http://127.0.0.1:19806/favoritos
curl -is http://127.0.0.1:19806/favoritos/export.csv
```

Con la aplicación activa, ejecuta `python3 0006_openspec_claude_code/examples/verify_export.py` desde este repositorio. Marca las tareas tras probar y archiva el cambio desde la copia del laboratorio.

- [proposal](openspec/changes/export-favorites-csv/proposal.md)
- [delta](openspec/changes/export-favorites-csv/specs/favorites/spec.md)
- [HTTP verifier](verify_export.py)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
