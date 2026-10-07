import { Router } from 'express';
import { listarArtigos, setFavorito } from '../services/feedService.js';
import { resumirArtigo } from '../services/aiService.js';

export const router = Router();

// GET /artigos - Lista artigos com filtros (Spec 01, 04)
router.get('/', (req, res) => {
  const { categoria, fonte, busca, limit, offset } = req.query;
  const artigos = listarArtigos({
    categoria,
    fonte,
    busca,
    limit: limit ? Number(limit) : 50,
    offset: offset ? Number(offset) : 0
  });
  res.json(artigos);
});

// POST /artigos/:id/resumir - Gera resumo por IA (Spec 03)
router.post('/:id/resumir', async (req, res) => {
  const id = Number(req.params.id);
  if (isNaN(id)) {
    return res.status(422).json({ erro: 'ID do artigo inválido' });
  }

  const resultado = await resumirArtigo(id);
  if (resultado.erro) {
    return res.status(resultado.status || 500).json({ erro: resultado.erro });
  }

  res.json(resultado);
});

// POST /artigos/:id/favoritar - Marca como favorito (Spec 06)
router.post('/:id/favoritar', (req, res) => {
  const id = Number(req.params.id);
  if (isNaN(id)) {
    return res.status(422).json({ erro: 'ID do artigo inválido' });
  }

  const resultado = setFavorito(id, true);
  if (!resultado) {
    return res.status(404).json({ erro: 'Artigo não encontrado' });
  }

  res.json(resultado);
});

// DELETE /artigos/:id/favoritar - Desmarca favorito (Spec 06)
router.delete('/:id/favoritar', (req, res) => {
  const id = Number(req.params.id);
  if (isNaN(id)) {
    return res.status(422).json({ erro: 'ID do artigo inválido' });
  }

  const resultado = setFavorito(id, false);
  if (!resultado) {
    return res.status(404).json({ erro: 'Artigo não encontrado' });
  }

  res.json(resultado);
});
