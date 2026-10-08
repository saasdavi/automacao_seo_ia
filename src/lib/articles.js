import fs from 'node:fs';
import path from 'node:path';

const CSV_PATH = path.join(process.cwd(), 'dados', 'calendario_blog_1_ano.csv');
const ARTICLES_DIR = path.join(process.cwd(), 'dados', 'saida', 'html');

// Thumbnails temáticas (mesmo critério da home atual)
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
export function loadArticles() {
  const rows = readRows().map(row => {
    const file = path.basename(row['Artigo_Arquivo_HTML'] || '');
    const hasFile = file && file.toLowerCase() !== 'nan' && fs.existsSync(path.join(ARTICLES_DIR, file));
    return {
      titulo: capitalize(row['Palavra-chave principal']),
      tema: row['Tema'],
      data: row['Data'],
      horario: row['Horário'],
      time: parseDate(row['Data']).getTime(),
      slug: hasFile ? `/${file}` : null,
      descricao: hasFile ? metaDescription(file) : '',
      // Miniatura própria por artigo (coluna Imagem_Miniatura); sem ela, usa a imagem do tema
      imagem: row['Imagem_Miniatura'] && row['Imagem_Miniatura'].startsWith('http')
        ? row['Imagem_Miniatura']
        : thumbFor(row['Tema']),
    };
  });

  const published = rows.filter(r => r.slug).sort((a, b) => b.time - a.time);
  const upcoming = rows.filter(r => !r.slug).sort((a, b) => a.time - b.time).slice(0, 9);
  const temas = [...new Set(rows.map(r => r.tema).filter(Boolean))].sort();

  return { published, upcoming, temas };
}
