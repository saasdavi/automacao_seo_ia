// Gera sitemap.xml, rss.xml e robots.txt no build.
// Os artigos são HTML prontos em dados/saida/html (copiados para a raiz do dist),
// então os metadados (título, descrição e data) são lidos do próprio HTML.
import { readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import path from 'node:path';

export const SITE_URL = 'https://www.mentemais.blog';
const SITE_NOME = 'Mente Leve';
const SITE_DESCRICAO = 'Blog de saúde mental e bem-estar';

const esc = (s) =>
  String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const hoje = () => new Date().toISOString().slice(0, 10);

function lerArtigos(origem) {
  return readdirSync(origem)
    .filter((f) => /^art-.*\.html$/.test(f))
    .map((arquivo) => {
      const html = readFileSync(path.join(origem, arquivo), 'utf8');
      const titulo = (html.match(/<title>([^<]*)<\/title>/) || [])[1] || arquivo;
      const desc = (html.match(/<meta name="description" content="([^"]*)"/) || [])[1] || '';
      const data = (html.match(/"datePublished":\s*"(\d{4}-\d{2}-\d{2})"/) || [])[1] || hoje();
      return { url: `/${arquivo}`, titulo, desc, data };
    })
    .sort((a, b) => b.data.localeCompare(a.data));
}

// Páginas Astro (index, sobre, contato, etc.) geradas no dist. Os artigos ficam de fora
// porque já vêm de lerArtigos(). 404.html e a página de redirecionamento
// /modelo-premium/ ficam de fora.
function paginasDoBuild(destino) {
  const achados = [];
  const visita = (dir) => {
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) visita(p);
      else if (e.name.endsWith('.html')) achados.push(p);
    }
  };
  visita(destino);
  return achados
    .map((p) => path.relative(destino, p).split(path.sep).join('/'))
    .filter((rel) => rel !== '404.html' && !/^art-/.test(rel) && !rel.startsWith('modelo-premium/'))
    .map((rel) => {
      if (rel === 'index.html') return { url: '/', data: hoje() };
      if (rel.endsWith('/index.html')) return { url: `/${rel.replace(/index\.html$/, '')}`, data: hoje() };
      return { url: `/${rel}`, data: hoje() };
    });
}

function gerarSitemap(destino, paginas) {
  const urls = paginas
    .map((p) => `  <url>\n    <loc>${esc(SITE_URL + p.url)}</loc>\n    <lastmod>${p.data}</lastmod>\n  </url>`)
    .join('\n');
  writeFileSync(
    path.join(destino, 'sitemap.xml'),
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`,
  );
}

function gerarRss(destino, artigos) {
  const itens = artigos
    .map(
      (a) =>
        `    <item>\n      <title>${esc(a.titulo)}</title>\n      <link>${esc(SITE_URL + a.url)}</link>\n      <guid>${esc(SITE_URL + a.url)}</guid>\n      <description>${esc(a.desc)}</description>\n      <pubDate>${new Date(a.data + 'T12:00:00Z').toUTCString()}</pubDate>\n    </item>`,
    )
    .join('\n');
  writeFileSync(
    path.join(destino, 'rss.xml'),
    `<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n  <channel>\n    <title>${esc(SITE_NOME)}</title>\n    <link>${SITE_URL}</link>\n    <description>${esc(SITE_DESCRICAO)}</description>\n    <language>pt-BR</language>\n${itens}\n  </channel>\n</rss>\n`,
  );
}

function gerarRobots(destino) {
  // Não sobrescreve um robots.txt que já exista em public/.
  const caminho = path.join(destino, 'robots.txt');
  if (existsSync(caminho)) return;
  writeFileSync(caminho, `User-agent: *\nAllow: /\n\nSitemap: ${SITE_URL}/sitemap.xml\n`);
}

export function gerarFeeds(destino, origemArtigos) {
  const artigos = lerArtigos(origemArtigos);
  const paginas = [...paginasDoBuild(destino), ...artigos.map((a) => ({ url: a.url, data: a.data }))];
  gerarSitemap(destino, paginas);
  gerarRss(destino, artigos);
  gerarRobots(destino);
}
