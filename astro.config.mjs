import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import { cpSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { gerarFeeds } from './scripts/gerar-feeds.mjs';
import { aplicarLayout } from './scripts/layout-artigos.mjs';

// Os artigos ficam em dados/saida/html (fora de public/), então são copiados
// para a raiz do build. Sem isso, os links dos cards apontam para 404.
// Depois da cópia, gera sitemap.xml, rss.xml e robots.txt.
const copiarArtigos = {
  name: 'copiar-artigos',
  hooks: {
    'astro:build:done': ({ dir }) => {
      const origem = path.join(process.cwd(), 'dados', 'saida', 'html');
      const destino = fileURLToPath(dir);
      for (const arquivo of readdirSync(origem)) {
        if (/^(art-.*|termos-de-uso)\.html$/.test(arquivo)) {
          const caminhoDestino = path.join(destino, arquivo);
          cpSync(path.join(origem, arquivo), caminhoDestino);
          // Artigos recebem cabeçalho, menu, data e rodapé do site (só na cópia do build)
          if (arquivo.startsWith('art-')) {
            const html = readFileSync(caminhoDestino, 'utf8');
            writeFileSync(caminhoDestino, aplicarLayout(html));
          }
        }
      }
      gerarFeeds(destino, origem);
    },
  },
};

export default defineConfig({
  integrations: [copiarArtigos],
  output: 'static',
  // Link antigo do modelo premium passa a cair na home
  redirects: {
    '/modelo-premium': '/',
  },
  outDir: './dist',
  publicDir: './public',
  vite: {
    plugins: [tailwindcss()],
  },
});
