import Parser from 'rss-parser';
import { db } from '../db/index.js';
import { classificarCategoria } from './aiService.js';

const parser = new Parser({
  timeout: 10000,
  headers: {
    'User-Agent': 'Pathbit-SDD-Aggregator/1.0'
  }
});

// Normaliza datas para YYYY-MM-DD
export function formatarDataISO(dataString) {
  if (!dataString) {
    return new Date().toISOString().slice(0, 10);
  }
  try {
    const d = new Date(dataString);
    if (isNaN(d.getTime())) {
      return new Date().toISOString().slice(0, 10);
    }
    return d.toISOString().slice(0, 10);
  } catch {
    return new Date().toISOString().slice(0, 10);
  }
}

// Importa artigos de uma URL RSS e deduplica por link
export async function importarFeed(url) {
  if (!url || typeof url !== 'string' || !url.trim()) {
    throw { status: 422, mensagem: 'URL do feed é obrigatória e deve ser válida' };
  }

  let feed;
  try {
    feed = await parser.parseURL(url.trim());
  } catch (err) {
    throw { status: 422, mensagem: `Falha ao ler o feed RSS da URL informada: ${err.message}` };
  }

  const nomeFonte = feed.title || new URL(url).hostname;
  let importados = 0;

  const stmtExiste = db.prepare('SELECT id FROM artigo WHERE link = ?');
  const stmtInsere = db.prepare(`
    INSERT INTO artigo (titulo, link, data_publicacao, fonte, conteudo, categoria)
    VALUES (?, ?, ?, ?, ?, ?)
  `);

  const transacao = db.transaction((itens) => {
    for (const item of itens) {
      const link = (item.link || item.guid || '').trim();
      if (!link) continue;

      const jaExiste = stmtExiste.get(link);
      if (!jaExiste) {
        const titulo = (item.title || 'Sem título').trim();
        const dataPublicacao = formatarDataISO(item.pubDate || item.isoDate);
        const conteudo = (item.contentSnippet || item.content || item.summary || '').trim();
        const categoria = classificarCategoria(titulo, conteudo);

        stmtInsere.run(titulo, link, dataPublicacao, nomeFonte, conteudo, categoria);
        importados++;
      }
    }
  });

  if (feed.items && Array.isArray(feed.items)) {
    transacao(feed.items);
  }

  return {
    importados,
    totalNoFeed: feed.items ? feed.items.length : 0,
    fonte: nomeFonte
  };
}

// Lista artigos com filtros e ordenação por data decrescente
export function listarArtigos({ categoria, fonte, busca, apenasFavoritos, limit = 50, offset = 0 } = {}) {
  let query = 'SELECT * FROM artigo WHERE 1=1';
  const params = [];

  if (categoria && categoria !== 'Todos') {
    query += ' AND categoria = ?';
    params.push(categoria);
  }

  if (fonte) {
    query += ' AND fonte LIKE ?';
    params.push(`%${fonte}%`);
  }

  if (busca) {
    query += ' AND (titulo LIKE ? OR conteudo LIKE ?)';
    params.push(`%${busca}%`, `%${busca}%`);
  }

  if (apenasFavoritos) {
    query += ' AND favorito = 1';
  }

  query += ' ORDER BY data_publicacao DESC, id DESC LIMIT ? OFFSET ?';
  params.push(Number(limit), Number(offset));

  const stmt = db.prepare(query);
  return stmt.all(...params);
}

// Alterna o status de favorito
export function setFavorito(id, statusFavorito) {
  const stmtVerifica = db.prepare('SELECT id FROM artigo WHERE id = ?');
  const artigo = stmtVerifica.get(id);

  if (!artigo) {
    return null;
  }

  const stmtUpdate = db.prepare('UPDATE artigo SET favorito = ? WHERE id = ?');
  stmtUpdate.run(statusFavorito ? 1 : 0, id);

  return { id, favorito: statusFavorito ? 1 : 0 };
}
