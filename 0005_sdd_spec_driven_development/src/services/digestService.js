import { db } from '../db/index.js';

export function obterDigestHoje() {
  const dataHoje = new Date().toISOString().slice(0, 10);

  // Busca os artigos mais recentes
  const stmtArtigos = db.prepare(`
    SELECT id, titulo, link, data_publicacao, fonte, resumo, categoria, favorito
    FROM artigo
    ORDER BY data_publicacao DESC, id DESC
    LIMIT 25
  `);
  const artigos = stmtArtigos.get() ? stmtArtigos.all() : [];

  // Estatísticas por categoria
  const categoriasContagem = {};
  const artigosPorCategoria = {};

  for (const a of artigos) {
    const cat = a.categoria || 'Geral';
    categoriasContagem[cat] = (categoriasContagem[cat] || 0) + 1;
    if (!artigosPorCategoria[cat]) {
      artigosPorCategoria[cat] = [];
    }
    artigosPorCategoria[cat].push(a);
  }

  // Estatísticas gerais
  const totalArtigos = db.prepare('SELECT COUNT(*) as total FROM artigo').get().total;
  const totalFavoritos = db.prepare('SELECT COUNT(*) as total FROM artigo WHERE favorito = 1').get().total;
  const totalResumidos = db.prepare('SELECT COUNT(*) as total FROM artigo WHERE resumo IS NOT NULL AND length(resumo) > 0').get().total;
  const totalFontes = db.prepare('SELECT COUNT(*) as total FROM fonte').get().total;

  return {
    data: dataHoje,
    titulo: `Digest Executivo de Tecnologia · ${dataHoje}`,
    totalNoDigest: artigos.length,
    estatisticas: {
      totalArtigosBanco: totalArtigos,
      totalFavoritos,
      totalResumidos,
      totalFontes
    },
    distribuicaoCategorias: categoriasContagem,
    destaques: artigos.slice(0, 5),
    gruposPorCategoria: artigosPorCategoria
  };
}
