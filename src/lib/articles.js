import fs from 'node:fs';
import path from 'node:path';

const CSV_PATH = path.join(process.cwd(), 'dados', 'calendario_blog_1_ano.csv');
const ARTICLES_DIR = path.join(process.cwd(), 'dados', 'saida', 'html');

// Pool de fotos por tema, gerado por scripts/baixar_miniaturas.py (Pexels, salvo no repo)
const MANIFESTO_PATH = path.join(process.cwd(), 'dados', 'miniaturas.json');
const pool = fs.existsSync(MANIFESTO_PATH)
  ? JSON.parse(fs.readFileSync(MANIFESTO_PATH, 'utf-8'))
  : {};

// Escolhe uma foto do tema para cada card, sem repetir dentro da página.
// Sem foto disponível para o tema, o card mostra um bloco da marca.
function atribuirMiniaturas(cards) {
  const usadas = new Set();
  for (const card of cards) {
    if (card.imagemPropria) {
      card.imagem = card.imagemPropria;
      continue;
    }
    const fotos = pool[card.tema] ?? [];
    const livre = fotos.find(f => !usadas.has(f));
    if (livre) {
      usadas.add(livre);
      card.imagem = livre;
    } else {
      card.imagem = null;
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

  atribuirMiniaturas([...published, ...upcoming]);

  return { published, upcoming, temas };
}
