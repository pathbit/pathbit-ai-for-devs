import { db } from '../db/index.js';
import { importarFeed } from './feedService.js';

export function cadastrarFonte({ nome, url }) {
  if (!nome || typeof nome !== 'string' || !nome.trim()) {
    throw { status: 422, mensagem: 'Nome da fonte é obrigatório' };
  }
  if (!url || typeof url !== 'string' || !url.trim()) {
    throw { status: 422, mensagem: 'URL do feed é obrigatória' };
  }

  const nomeLimpo = nome.trim();
  const urlLimpa = url.trim();

  const stmtExiste = db.prepare('SELECT id FROM fonte WHERE url = ?');
  if (stmtExiste.get(urlLimpa)) {
    throw { status: 422, mensagem: 'Já existe uma fonte cadastrada com esta URL' };
  }

  const stmt = db.prepare(`
    INSERT INTO fonte (nome, url, ativa, ultima_atualizacao)
    VALUES (?, ?, 1, datetime('now'))
  `);

  const info = stmt.run(nomeLimpo, urlLimpa);
  return {
    id: info.lastInsertRowid,
    nome: nomeLimpo,
    url: urlLimpa,
    ativa: 1,
    ultima_atualizacao: new Date().toISOString()
  };
}

export function listarFontes() {
  const stmt = db.prepare('SELECT * FROM fonte ORDER BY id ASC');
  return stmt.all();
}

export async function atualizarFonte(id) {
  const stmt = db.prepare('SELECT * FROM fonte WHERE id = ?');
  const fonte = stmt.get(id);

  if (!fonte) {
    throw { status: 404, mensagem: 'Fonte não encontrada' };
  }

  const resultado = await importarFeed(fonte.url);

  const agora = new Date().toISOString();
  const stmtUpdate = db.prepare('UPDATE fonte SET ultima_atualizacao = ? WHERE id = ?');
  stmtUpdate.run(agora, id);

  return {
    fonteId: id,
    nome: fonte.nome,
    importados: resultado.importados,
    ultima_atualizacao: agora
  };
}

export async function atualizarTodasFontes() {
  const fontes = db.prepare('SELECT * FROM fonte WHERE ativa = 1').all();
  const resultados = [];
  let totalImportados = 0;

  for (const f of fontes) {
    try {
      const res = await atualizarFonte(f.id);
      resultados.push(res);
      totalImportados += res.importados;
    } catch (err) {
      resultados.push({
        fonteId: f.id,
        nome: f.nome,
        erro: err.mensagem || err.message
      });
    }
  }

  return {
    totalFontes: fontes.length,
    totalImportados,
    detalhes: resultados
  };
}
