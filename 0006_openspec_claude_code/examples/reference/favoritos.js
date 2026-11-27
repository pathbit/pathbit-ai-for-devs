import { Router } from 'express';
import { listarArtigos } from '../services/feedService.js';
import { serializeFavorites } from '../services/favoritesCsv.js';

export const router = Router();

function listFavorites() {
  return listarArtigos({ apenasFavoritos: true, limit: 100 });
}

router.get('/', (req, res) => {
  res.json(listFavorites());
});

router.get('/export.csv', (req, res) => {
  res.attachment('favoritos.csv');
  res.type('text/csv').send(serializeFavorites(listFavorites()));
});
