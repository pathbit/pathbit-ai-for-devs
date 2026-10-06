import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import { inicializarSchema } from './db/index.js';
import { router as artigosRouter } from './routes/artigos.js';
import { router as feedsRouter } from './routes/feeds.js';
import { router as fontesRouter } from './routes/fontes.js';
import { router as digestRouter } from './routes/digest.js';
import { router as favoritosRouter } from './routes/favoritos.js';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const app = express();
const PORT = process.env.PORT || 3005;

// Inicializa o banco de dados SQLite
inicializarSchema();

// Middlewares
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// Rotas da API (Specs 01 a 06)
app.use('/artigos', artigosRouter);
app.use('/feeds', feedsRouter);
app.use('/fontes', fontesRouter);
app.use('/digest', digestRouter);
app.use('/favoritos', favoritosRouter);

// Rota raiz e dashboard (Spec 06)
app.get(['/', '/dashboard'], (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Middleware de tratamento de erros uniforme (Requisito não-funcional: { "erro": "<mensagem>" })
app.use((err, req, res, next) => {
  console.error('[Error Handler]', err);
  const status = err.status || 500;
  res.status(status).json({
    erro: err.mensagem || err.message || 'Erro interno no servidor'
  });
});

// Inicialização do servidor se executado diretamente
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`========================================================`);
    console.log(`📡 Agregador de Notícias SDD rodando na porta ${PORT}`);
    console.log(`🌐 Dashboard: http://localhost:${PORT}`);
    console.log(`🔗 Healthz / Artigos: http://localhost:${PORT}/artigos`);
    console.log(`========================================================`);
  });
}
