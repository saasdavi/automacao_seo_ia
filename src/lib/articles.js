import fs from 'node:fs';
import path from 'node:path';

const CSV_PATH = path.join(process.cwd(), 'dados', 'calendario_blog_1_ano.csv');
const ARTICLES_DIR = path.join(process.cwd(), 'dados', 'saida', 'html');

// Thumbnails de reserva (usadas só se a Pexels não responder ou não houver chave)
const THUMBS = {
  Estresse: 'photo-1599643478518-a784e5dc4c8f',
  Sono: 'photo-1541123603104-852fc75f7404',
  'Insônia / Sono': 'photo-1531407979302-6e57a23a7c4d',
  Ansiedade: 'photo-1506794778202-cad84cf45f1d',
  Meditação: 'photo-1528148343865-f218b37f5a5c',
  Memória: 'photo-1516534775068-bb57c960e9c8',
  'Bem-estar': 'photo-1506926613408-eca07ce68773',
};
const FALLBACK = 'photo-1497206365907-3ff1691d8134';

export function thumbFor(tema, width = 800, height = 520) {
  const id = THUMBS[tema] ?? FALLBACK;
  return `https://images.unsplash.com/${id}?w=${width}&h=${height}&fit=crop&q=80`;
}

// Consulta em inglês por tema (a Pexels responde melhor em inglês)
const CONSULTAS_PEXELS = {
  Estresse: 'stressed person',
  Sono: 'sleeping peacefully bedroom',
  'Insônia / Sono': 'sleeping peacefully bedroom',
  Ansiedade: 'anxious person thinking',
  Meditação: 'meditation calm',
  Memória: 'thinking brain memory',
  'Bem-estar': 'wellbeing relaxation nature',
};
const CONSULTA_PADRAO = 'calm mental health';

// Busca fotos na Pexels no momento do build. Sem chave ou em caso de erro, devolve lista vazia.
const PEXELS_KEY = process.env.PEXELS_API_KEY;
const cacheConsultas = new Map();

async function fotosPexels(consulta) {
  if (!PEXELS_KEY) return [];
  if (cacheConsultas.has(consulta)) return cacheConsultas.get(consulta);
  let fotos = [];
  try {
    const url = `https://api.pexels.com/v1/search?query=${encodeURIComponent(consulta)}&per_page=15&orientation=landscape`;
    const r = await fetch(url, { headers: { Authorization: PEXELS_KEY } });
    if (r.ok) {
      const data = await r.json();
      fotos = (data.photos ?? []).map(p => ({ id: p.id, url: p.src.large }));
    } else {
      console.warn(`Pexels respondeu ${r.status} para "${consulta}"`);
    }
  } catch (err) {
    console.warn(`Falha na Pexels para "${consulta}": ${err.message}`);
  }
  cacheConsultas.set(consulta, fotos);
  return fotos;
}

// Escolhe uma foto para cada card sem repetir dentro da página
async function atribuirMiniaturas(cards) {
  const usadas = new Set();
  for (const card of cards) {
    if (card.imagemPropria) {
      card.imagem = card.imagemPropria;
      continue;
    }
    const fotos = await fotosPexels(CONSULTAS_PEXELS[card.tema] ?? CONSULTA_PADRAO);
    const livre = fotos.find(f => !usadas.has(f.id));
    if (livre) {
      usadas.add(livre.id);
      card.imagem = livre.url;
    } else {
      card.imagem = thumbFor(card.tema);
    }
  }
}

// Parser de CSV que respeita campos entre aspas
function parseCSV(text) {
  const rows = [];
  let row = [];
  let field = '';
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { row.push(field.trim()); field = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(field.trim()); field = '';
      rows.push(row); row = [];
    } else field += c;
  }
  if (field || row.length) { row.push(field.trim()); rows.push(row); }
  return rows;
}

function readRows() {
  const text = fs.readFileSync(CSV_PATH, 'utf-8').replace(/^﻿/, '');
  const [headers, ...body] = parseCSV(text);
  return body
    .filter(cols => cols.some(Boolean))
    .map(cols => Object.fromEntries(headers.map((h, i) => [h, cols[i] ?? ''])));
}

// Palavras-chave vêm em minúsculas no CSV; capitaliza só a primeira letra
function capitalize(str) {
  return str ? str.charAt(0).toLocaleUpperCase('pt-BR') + str.slice(1) : str;
}

function parseDate(str) {
  const [d, m, y] = str.split('/');
  return new Date(Number(y), Number(m) - 1, Number(d));
}

function metaDescription(file) {
  try {
    const html = fs.readFileSync(path.join(ARTICLES_DIR, file), 'utf-8');
    const m = html.match(/<meta\s+name="description"\s+content="([^"]*)"/i);
    return m ? m[1] : '';
  } catch {
    return '';
  }
}

// Retorna { published, upcoming, temas } prontos para a página
export async function loadArticles() {
  const rows = readRows().map(row => {
    const file = path.basename(row['Artigo_Arquivo_HTML'] || '');
    const hasFile = file && file.toLowerCase() !== 'nan' && fs.existsSync(path.join(ARTICLES_DIR, file));
    const propria = row['Imagem_Miniatura'];
    return {
      titulo: capitalize(row['Palavra-chave principal']),
      tema: row['Tema'],
      data: row['Data'],
      horario: row['Horário'],
      time: parseDate(row['Data']).getTime(),
      slug: hasFile ? `/${file}` : null,
      descricao: hasFile ? metaDescription(file) : '',
      // Miniatura própria por artigo (coluna Imagem_Miniatura) tem prioridade sobre a Pexels
      imagemPropria: propria && propria.startsWith('http') ? propria : null,
      imagem: null,
    };
  });

  const published = rows.filter(r => r.slug).sort((a, b) => b.time - a.time);
  const upcoming = rows.filter(r => !r.slug).sort((a, b) => a.time - b.time).slice(0, 9);
  const temas = [...new Set(rows.map(r => r.tema).filter(Boolean))].sort();

  await atribuirMiniaturas([...published, ...upcoming]);

  return { published, upcoming, temas };
}
