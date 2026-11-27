import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

if (!existsSync('.pathbit-aggregator-lab') || process.env.NODE_ENV === 'test') {
  throw new Error('Run from a disposable aggregator created by prepare_aggregator_lab.py.');
}
const databasePath = resolve('data/lab.sqlite');
process.env.DATABASE_PATH = databasePath;

const { db, inicializarSchema } = await import(pathToFileURL(resolve('src/db/index.js')));
inicializarSchema();
const insert = db.prepare(`
  INSERT INTO artigo (titulo, link, data_publicacao, fonte, conteudo, categoria, favorito)
  VALUES (@title, @url, @published, @source, @body, @category, @favorite)
  ON CONFLICT(link) DO NOTHING
`);
const entries = [
  { title: 'MCP no Agregador', url: 'https://example.org/mcp', published: '2026-11-27T09:30:00Z',
    source: 'Pathbit Lab', body: 'Um laboratório de navegador usa dados locais.', category: 'Ferramentas', favorite: 0 },
  { title: 'Roteamento no OpenCode', url: 'https://example.org/routing', published: '2026-11-27T09:00:00Z',
    source: 'Pathbit Lab', body: 'Compare um gateway e um servidor de modelos local.', category: 'Modelos', favorite: 0 },
  { title: '=Arquitetura, "em prática"', url: 'https://example.org/architecture', published: '2026-11-27T08:30:00Z',
    source: 'Pathbit Lab', body: 'O título cobre a proteção para planilhas do laboratório.', category: 'Engenharia', favorite: 1 }
];
db.transaction(() => entries.forEach((entry) => insert.run(entry)))();
console.log(`Lab database: ${databasePath}`);
db.close();
