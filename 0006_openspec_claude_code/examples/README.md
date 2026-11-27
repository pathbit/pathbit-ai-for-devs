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

## Repita a verificação de limite e ordem

Use uma **segunda cópia descartável** com o patch de referência e `npm ci`. A partir dela, antes de iniciar o aplicativo, semeie 105 favoritos com datas distintas e um artigo mais recente sem marcação.

```bash
node --input-type=module <<'JS'
process.env.DATABASE_PATH = './data/lab.sqlite';
const { db, inicializarSchema } = await import('./src/db/index.js');
inicializarSchema();
const insert = db.prepare(
  'INSERT INTO artigo (titulo, link, data_publicacao, fonte, favorito) VALUES (?, ?, ?, ?, ?)'
);
const baseline = Date.UTC(2026, 0, 1);
db.transaction(() => {
  for (let id = 1; id <= 106; id += 1) {
    const title = id === 105 ? 'Título\ncom duas linhas' : `Artigo ${id}`;
    const link = `https://example.org/favorite-${id}`;
    const published = new Date(baseline + id * 1000).toISOString();
    insert.run(title, link, published, 'Pathbit Lab', id === 106 ? 0 : 1);
  }
})();
db.close();
JS
HOST=127.0.0.1 PORT=19806 DATABASE_PATH="$PWD/data/lab.sqlite" npm start
```

Com a instância em execução, abra outro terminal. A lista de links precisa ir de `105` até `6` e ser idêntica em JSON e CSV. O artigo `106` ficou fora porque não foi marcado. A comparação usa um leitor CSV que entende uma quebra de linha entre aspas.

```bash
python3 - <<'PY'
import csv
from io import StringIO
import json
from urllib.request import urlopen

base = 'http://127.0.0.1:19806'
with urlopen(base + '/favoritos', timeout=5) as response:
    articles = json.load(response)
with urlopen(base + '/favoritos/export.csv', timeout=5) as response:
    rows = list(csv.DictReader(StringIO(response.read().decode('utf-8'))))

links = [row['link'] for row in rows]
assert len(links) == 100
assert links == [article['link'] for article in articles]
assert links == [f'https://example.org/favorite-{id}' for id in range(105, 5, -1)]
assert rows[0]['titulo'] == 'Título\ncom duas linhas'
print('Os 100 links do CSV e do JSON estão na mesma ordem.')
PY
```
