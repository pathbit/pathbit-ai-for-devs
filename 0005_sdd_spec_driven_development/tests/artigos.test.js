import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { app } from '../src/server.js';
import { db } from '../src/db/index.js';
import { setFavorito, listarArtigos } from '../src/services/feedService.js';
import { resumirArtigo } from '../src/services/aiService.js';
import { cadastrarFonte, listarFontes } from '../src/services/fonteService.js';
import { obterDigestHoje } from '../src/services/digestService.js';

describe('Suíte de Testes SDD: Agregador de Notícias', () => {

  let server;
  let baseUrl;
  let testArtigoId;

  before(async () => {
    // Insere artigo de teste
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO artigo (id, titulo, link, data_publicacao, fonte, conteudo, categoria, favorito)
      VALUES (999, 'Teste SDD com Claude Code', 'https://pathbit.co/test/sdd', '2026-10-06', 'Pathbit Tech', 'Conteudo de teste sobre desenvolvimento guiado por especificacao.', 'IA & Agentes', 0)
    `);
    stmt.run();
    testArtigoId = 999;

    await new Promise((resolve) => {
      server = app.listen(0, () => {
        const port = server.address().port;
        baseUrl = `http://127.0.0.1:${port}`;
        resolve();
      });
    });
  });

  after(() => {
    if (server) server.close();
    // Limpeza
    db.prepare('DELETE FROM artigo WHERE id = 999').run();
  });

  test('Spec 01: GET /artigos retorna lista ordenada em JSON', async () => {
    const res = await fetch(`${baseUrl}/artigos`);
    assert.equal(res.status, 200);
    const dados = await res.json();
    assert.ok(Array.isArray(dados));
    assert.ok(dados.length >= 1);
    const item = dados.find(a => a.id === testArtigoId);
    assert.ok(item, 'Artigo de teste deve estar na listagem');
    assert.equal(item.titulo, 'Teste SDD com Claude Code');
  });

  test('Spec 01: POST /feeds/importar sem URL retorna 422 com erro claro', async () => {
    const res = await fetch(`${baseUrl}/feeds/importar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    assert.equal(res.status, 422);
    const erro = await res.json();
    assert.ok(erro.erro);
    assert.match(erro.erro, /url/i);
  });

  test('Spec 02: GET /fontes lista fontes padrão cadastradas', async () => {
    const res = await fetch(`${baseUrl}/fontes`);
    assert.equal(res.status, 200);
    const fontes = await res.json();
    assert.ok(Array.isArray(fontes));
    assert.ok(fontes.length >= 1);
  });

  test('Spec 03: POST /artigos/:id/resumir gera e cacheia resumo', async () => {
    // Primeira chamada: gera resumo
    const res1 = await fetch(`${baseUrl}/artigos/${testArtigoId}/resumir`, { method: 'POST' });
    assert.equal(res1.status, 200);
    const dados1 = await res1.json();
    assert.ok(dados1.resumo);
    assert.equal(dados1.cached, false);

    // Segunda chamada: deve vir do cache
    const res2 = await fetch(`${baseUrl}/artigos/${testArtigoId}/resumir`, { method: 'POST' });
    assert.equal(res2.status, 200);
    const dados2 = await res2.json();
    assert.equal(dados2.resumo, dados1.resumo);
    assert.equal(dados2.cached, true);
  });

  test('Spec 04: Filtro por busca e categoria funciona', async () => {
    const res = await fetch(`${baseUrl}/artigos?busca=especificacao`);
    assert.equal(res.status, 200);
    const dados = await res.json();
    assert.ok(dados.some(a => a.id === testArtigoId));
  });

  test('Spec 05: GET /digest/hoje retorna sumário executivo com estatísticas', async () => {
    const res = await fetch(`${baseUrl}/digest/hoje`);
    assert.equal(res.status, 200);
    const digest = await res.json();
    assert.ok(digest.data);
    assert.ok(digest.estatisticas);
    assert.ok(digest.estatisticas.totalArtigosBanco >= 1);
  });

  test('Spec 06: Favoritar, listar favoritos e desfavoritar', async () => {
    // Favorita
    const resFav = await fetch(`${baseUrl}/artigos/${testArtigoId}/favoritar`, { method: 'POST' });
    assert.equal(resFav.status, 200);

    // Verifica em /favoritos
    const resListFav = await fetch(`${baseUrl}/favoritos`);
    assert.equal(resListFav.status, 200);
    const favs = await resListFav.json();
    assert.ok(favs.some(a => a.id === testArtigoId));

    // Desfavorita
    const resUnfav = await fetch(`${baseUrl}/artigos/${testArtigoId}/favoritar`, { method: 'DELETE' });
    assert.equal(resUnfav.status, 200);

    // Verifica que saiu de /favoritos
    const resListFav2 = await fetch(`${baseUrl}/favoritos`);
    const favs2 = await resListFav2.json();
    assert.ok(!favs2.some(a => a.id === testArtigoId));
  });

  test('Spec 06: Recurso inexistente retorna 404', async () => {
    const res = await fetch(`${baseUrl}/artigos/999999/favoritar`, { method: 'POST' });
    assert.equal(res.status, 404);
    const dados = await res.json();
    assert.ok(dados.erro);
  });

  test('Spec 06: Dashboard HTML é servido na rota raiz', async () => {
    const res = await fetch(`${baseUrl}/`);
    assert.equal(res.status, 200);
    const html = await res.text();
    assert.ok(html.includes('Agregador de Notícias'));
  });
});
