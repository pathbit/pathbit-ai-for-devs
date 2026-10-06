import { Router } from 'express';
import { importarFeed } from '../services/feedService.js';

export const router = Router();

// POST /feeds/importar - Importa feed RSS (Spec 01)
router.post('/importar', async (req, res) => {
  const { url } = req.body || {};
  if (!url) {
    return res.status(422).json({ erro: 'O campo url é obrigatório' });
  }

  try {
    const resultado = await importarFeed(url);
    res.json(resultado);
  } catch (err) {
    res.status(err.status || 500).json({ erro: err.mensagem || err.message });
  }
});
