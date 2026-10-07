import { Router } from 'express';
import { obterDigestHoje } from '../services/digestService.js';

export const router = Router();

// GET /digest/hoje - Resumo diário agrupado das principais notícias (Spec 05)
router.get('/hoje', (req, res) => {
  const digest = obterDigestHoje();
  res.json(digest);
});
