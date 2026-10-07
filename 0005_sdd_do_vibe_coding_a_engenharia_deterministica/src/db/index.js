import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const dbPath = process.env.DATABASE_PATH || path.resolve(__dirname, '../../data/noticias.db');

// Garante que o diretório pai do banco exista
const dbDir = path.dirname(dbPath);
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

export const db = new Database(dbPath);

// Ativa WAL mode para concorrência e performance
db.pragma('journal_mode = WAL');

// Inicialização idempotente do schema conforme as specs 01 a 06
export function inicializarSchema() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS fonte (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nome TEXT NOT NULL,
      url TEXT NOT NULL UNIQUE,
      ativa INTEGER DEFAULT 1,
      ultima_atualizacao TEXT
    );

    CREATE TABLE IF NOT EXISTS artigo (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      titulo TEXT NOT NULL,
      link TEXT NOT NULL UNIQUE,
      data_publicacao TEXT,
      fonte TEXT,
      conteudo TEXT,
      resumo TEXT,
      categoria TEXT DEFAULT 'Geral',
      favorito INTEGER DEFAULT 0
    );

    CREATE INDEX IF NOT EXISTS idx_artigo_data ON artigo(data_publicacao DESC);
    CREATE INDEX IF NOT EXISTS idx_artigo_categoria ON artigo(categoria);
    CREATE INDEX IF NOT EXISTS idx_artigo_favorito ON artigo(favorito);
  `);

  // Fontes recomendadas iniciais para demonstração imediata
  const fontesPadrao = [
    { nome: 'TechCrunch Artificial Intelligence', url: 'https://techcrunch.com/category/artificial-intelligence/feed/' },
    { nome: 'GitHub Engineering Blog', url: 'https://github.blog/engineering/feed/' },
    { nome: 'The Verge Tech', url: 'https://www.theverge.com/rss/tech/index.xml' }
  ];

  const stmtVerifica = db.prepare('SELECT id FROM fonte WHERE url = ?');
  const stmtInsere = db.prepare('INSERT INTO fonte (nome, url) VALUES (?, ?)');

  for (const f of fontesPadrao) {
    const existe = stmtVerifica.get(f.url);
    if (!existe) {
      stmtInsere.run(f.nome, f.url);
    }
  }
}
