# Exercício de exportação de favoritos no Agregador

O [guia do módulo](../README.md) prepara dois pontos de partida. Use a change pronta para repetir o contrato. Em outra cópia, crie a sua proposta para comparar escopo e critérios.

## Abra os artefatos antes da implementação

- [Contrato JSON vigente](openspec/specs/favorites/spec.md)
- [Proposta](openspec/changes/export-favorites-csv/proposal.md) · [Design](openspec/changes/export-favorites-csv/design.md)
- [Delta de contrato](openspec/changes/export-favorites-csv/specs/favorites/spec.md) · [Tarefas](openspec/changes/export-favorites-csv/tasks.md)

Depois que o servidor estiver rodando, consulte os dois formatos.

```bash
curl -is http://127.0.0.1:19806/favoritos
curl -is http://127.0.0.1:19806/favoritos/export.csv
```

O título começa com `=` no JSON e recebe um apóstrofo no CSV. Use [verify_export.py](verify_export.py) para conferir conteúdo, cabeçalhos, lista vazia e preservação do JSON. Quando usar os arquivos de referência, compare a [rota](reference/favoritos.js) e o [serializador](reference/favoritesCsv.js) com o que o agente propôs.
