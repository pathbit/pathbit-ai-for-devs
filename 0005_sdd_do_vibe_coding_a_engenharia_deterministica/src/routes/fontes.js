import { Router } from 'express';
import { cadastrarFonte, listarFontes, atualizarFonte, atualizarTodasFontes } from '../services/fonteService.js';

export const router = Router();

// GET /fontes - Lista fontes cadastradas (Spec 02)
router.get('/', (req, res) => {
  const fontes = listarFontes();
  res.json(fontes);
});

// POST /fontes - Cadastra nova fonte (Spec 02)
router.post('/', (req, res) => {
  const { nome, url } = req.body || {};
  try {
    const novaFonte = cadastrarFonte({ nome, url });
    res.status(201).json(novaFonte);
  } catch (err) {
    res.status(err.status || 500).json({ erro: err.mensagem || err.message });
  }
});

// POST /fontes/:id/atualizar - Atualiza artigos de uma fonte (Spec 02)
router.post('/:id/atualizar', async (req, res) => {
  const id = Number(req.params.id);
  if (isNaN(id)) {
    return res.status(422).json({ erro: 'ID da fonte inválido' });
  }

  try {
    const resultado = await atualizarFonte(id);
    res.json(resultado);
  } catch (err) {
    res.status(err.status || 500).json({ erro: err.mensagem || err.message });
  }
});

// POST /fontes/atualizar-todas - Atualiza todas as fontes ativas (Spec 02)
router.post('/atualizar-todas', async (req, res) => {
  try {
    const resultado = await atualizarTodasFontes();
    res.json(resultado);
  } catch (err) {
    res.status(500).json({ erro: err.message });
  }
});
