import { Router } from 'express';
import { listarArtigos } from '../services/feedService.js';

export const router = Router();

// GET /favoritos - Lista os artigos favoritados (Spec 06)
router.get('/', (req, res) => {
  const favoritos = listarArtigos({ apenasFavoritos: true, limit: 100 });
  res.json(favoritos);
});
