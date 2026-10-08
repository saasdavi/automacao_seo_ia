import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import { cpSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// Os artigos ficam em dados/saida/html (fora de public/), então são copiados
// para a raiz do build. Sem isso, os links dos cards apontam para 404.
const copiarArtigos = {
  name: 'copiar-artigos',
  hooks: {
    'astro:build:done': ({ dir }) => {
      const origem = path.join(process.cwd(), 'dados', 'saida', 'html');
      const destino = fileURLToPath(dir);
      for (const arquivo of readdirSync(origem)) {
        if (/^(art-.*|termos-de-uso)\.html$/.test(arquivo)) {
          cpSync(path.join(origem, arquivo), path.join(destino, arquivo));
        }
      }
    },
  },
};

export default defineConfig({
  integrations: [copiarArtigos],
  output: 'static',
  outDir: './dist',
  publicDir: './public',
  vite: {
    plugins: [tailwindcss()],
  },
});
