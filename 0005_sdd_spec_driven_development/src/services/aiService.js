import { db } from '../db/index.js';

// Função para categorizar artigo com base no vocabulário
export function classificarCategoria(titulo = '', conteudo = '') {
  const texto = `${titulo} ${conteudo}`.toLowerCase();

  if (/ai|artificial intelligence|llm|claude|openai|deepseek|machine learning|intelig[eê]ncia artificial|agente|gpt|transformer/i.test(texto)) {
    return 'IA & Agentes';
  }
  if (/security|vulnerability|cve|auth|seguran[çc]a|malware|breach|exploit|crypto/i.test(texto)) {
    return 'Segurança';
  }
  if (/kubernetes|docker|cloud|aws|azure|gcp|devops|ci\/cd|pipeline|infra/i.test(texto)) {
    return 'Cloud & DevOps';
  }
  if (/react|vue|angular|css|frontend|front-end|ui\/ux|html|browser|dom|vite/i.test(texto)) {
    return 'Frontend';
  }
  if (/database|sql|sqlite|postgres|node|python|golang|backend|back-end|api|rest|graphql/i.test(texto)) {
    return 'Engenharia de Software';
  }
  return 'Geral';
}

// Serviço de resumo com suporte a Anthropic SDK, 9Router ou fallback heurístico local
export async function resumirArtigo(artigoId) {
  const stmtArtigo = db.prepare('SELECT id, titulo, link, fonte, conteudo, resumo FROM artigo WHERE id = ?');
  const artigo = stmtArtigo.get(artigoId);

  if (!artigo) {
    return { erro: 'Artigo não encontrado', status: 404 };
  }

  // Se já possui resumo, retorna do cache (Requisito Spec 03)
  if (artigo.resumo && artigo.resumo.trim().length > 0) {
    return {
      id: artigo.id,
      titulo: artigo.titulo,
      resumo: artigo.resumo,
      cached: true
    };
  }

  const promptConteudo = (artigo.conteudo || artigo.titulo).slice(0, 1500);
  let resumoGerado = '';

  const apiKey = process.env.ANTHROPIC_API_KEY;
  const baseUrl = process.env.ANTHROPIC_BASE_URL;

  // Se houver chave ou base URL configurada (ex: 9Router na porta 20128)
  if (apiKey || (baseUrl && baseUrl.includes('20128'))) {
    try {
      const response = await fetch(`${baseUrl || 'https://api.anthropic.com/v1'}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey || 'local-claudegravity-token',
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: process.env.AI_MODEL || 'claude-3-5-sonnet-20241022',
          max_tokens: 300,
          messages: [
            {
              role: 'user',
              content: `Resuma o seguinte artigo técnico em exatamente 2 a 3 frases claras e objetivas em português do Brasil:\n\nTítulo: ${artigo.titulo}\nConteúdo: ${promptConteudo}`
            }
          ]
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.content && data.content[0] && data.content[0].text) {
          resumoGerado = data.content[0].text.trim();
        }
      }
    } catch (e) {
      console.warn(`[AI Service] Falha na chamada da API externa: ${e.message}. Usando sumarizador estruturado.`);
    }
  }

  // Fallback heurístico inteligente se não houver resposta externa
  if (!resumoGerado) {
    const textoLimpo = promptConteudo
      .replace(/<[^>]+>/g, '')
      .replace(/\s+/g, ' ')
      .trim();

    const frases = textoLimpo.split(/(?<=[.!?])\s+/).filter(f => f.length > 20);
    if (frases.length >= 2) {
      resumoGerado = `${frases[0]} ${frases[1]}`;
    } else {
      resumoGerado = `Este artigo aborda os desenvolvimentos recentes de "${artigo.titulo}". Ele explora implicações práticas e recomendações para engenheiros de software e arquitetos de soluções.`;
    }
  }

  // Salva no banco SQLite
  const stmtUpdate = db.prepare('UPDATE artigo SET resumo = ? WHERE id = ?');
  stmtUpdate.run(resumoGerado, artigo.id);

  return {
    id: artigo.id,
    titulo: artigo.titulo,
    resumo: resumoGerado,
    cached: false
  };
}
