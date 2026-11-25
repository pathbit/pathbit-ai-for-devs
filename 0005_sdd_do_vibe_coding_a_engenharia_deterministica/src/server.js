import express from 'express';
import 'dotenv/config';
import path from 'path';
import { fileURLToPath } from 'url';
import { inicializarSchema } from './db/index.js';
import { router as artigosRouter } from './routes/artigos.js';
import { router as feedsRouter } from './routes/feeds.js';
import { router as fontesRouter } from './routes/fontes.js';
import { router as digestRouter } from './routes/digest.js';
import { router as favoritosRouter } from './routes/favoritos.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const app = express();
const PORT = process.env.PORT || 3005;
const HOST = process.env.HOST || '127.0.0.1';

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
  const server = app.listen(PORT, HOST, () => {
    const porta = server.address().port;
    console.log(`========================================================`);
    console.log(`📡 Agregador de Notícias SDD rodando na porta ${porta}`);
    console.log(`🌐 Dashboard: http://${HOST}:${porta}`);
    console.log(`🔗 API de artigos: http://${HOST}:${porta}/artigos`);
    console.log(`========================================================`);
  });
}
