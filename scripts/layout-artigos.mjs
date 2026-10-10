// Aplica o layout do site (cabeçalho, menu, data e rodapé) nas páginas de artigo.
// Os artigos gerados pela IA são documentos HTML completos e não passam pelo
// Layout.astro. Esta função é aplicada na cópia do build, sem alterar os
// arquivos originais em dados/saida/html/.

const MARCA = 'data-mente-leve-layout';

const NAV = [
  { href: '/', label: 'Início' },
  { href: '/sobre', label: 'Sobre' },
  { href: '/contato', label: 'Contato' },
  { href: '/politica-editorial', label: 'Editorial' },
];

// Mesmo markup de src/layouts/PremiumLayout.astro (cabeçalho e rodapé da home)
const CABECALHO = `
<header ${MARCA} class="sticky top-0 z-40 border-b border-brand-100/80 bg-paper/85 backdrop-blur-md">
  <div class="mx-auto flex max-w-7xl items-center justify-between gap-6 px-5 py-4 lg:px-8">
    <a href="/" class="flex items-center gap-2.5">
      <span class="grid size-9 place-items-center rounded-full bg-brand-600 text-lg text-white shadow-lift">🌿</span>
      <span class="font-display text-xl font-semibold text-brand-700">Mente Leve</span>
    </a>
    <nav aria-label="Menu principal" class="hidden items-center gap-7 text-sm font-medium text-ink-700 md:flex">
      ${NAV.map((item) => `<a href="${item.href}" class="transition hover:text-brand-600">${item.label}</a>`).join('')}
    </nav>
    <a href="/#artigos" class="rounded-full bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-700">Ler artigos</a>
  </div>
</header>`;

const RODAPE = `
<footer ${MARCA} class="mt-24 border-t border-brand-100 bg-brand-900 text-brand-100">
  <div class="mx-auto grid max-w-7xl gap-10 px-5 py-14 lg:grid-cols-[1.4fr_1fr_1fr] lg:px-8">
    <div>
      <p class="font-display text-2xl font-semibold text-white">🌿 Mente Leve</p>
      <p class="mt-3 max-w-sm text-sm leading-relaxed text-brand-200/80">
        Conteúdo informativo sobre saúde mental e bem-estar. Não substitui diagnóstico nem tratamento profissional.
      </p>
    </div>
    <div>
      <p class="text-xs font-semibold uppercase tracking-widest text-sun-400">Blog</p>
      <ul class="mt-4 space-y-2 text-sm">
        ${NAV.map((item) => `<li><a class="hover:text-white" href="${item.href}">${item.label}</a></li>`).join('')}
      </ul>
    </div>
    <div>
      <p class="text-xs font-semibold uppercase tracking-widest text-sun-400">Legal</p>
      <ul class="mt-4 space-y-2 text-sm">
        <li><a class="hover:text-white" href="/privacidade">Privacidade</a></li>
        <li><a class="hover:text-white" href="/termos-de-uso.html">Termos de uso</a></li>
      </ul>
    </div>
  </div>
  <div class="border-t border-white/10 px-5 py-5 text-center text-xs text-brand-200/70 lg:px-8">
    © 2026 Mente Leve. Todos os direitos reservados.
  </div>
</footer>`;

// Lê a data de publicação do JSON-LD (ex.: "2026-10-10T13:53:53-03:00")
// e devolve no formato dd/mm/aaaa, usando a data local já escrita no texto.
export function dataPublicacao(html) {
  const m = html.match(/"datePublished"\s*:\s*"(\d{4})-(\d{2})-(\d{2})/);
  return m ? `${m[3]}/${m[2]}/${m[1]}` : null;
}

export function aplicarLayout(html, { comData = true, folhas = '' } = {}) {
  // Já aplicado: não duplica cabeçalho, data nem rodapé
  if (html.includes(MARCA)) return html;

  let saida = html;

  // 0. CSS do site (mesmos arquivos usados pela home no build)
  if (folhas) saida = saida.replace(/<\/head>/i, folhas + '\n</head>');

  // 1. Cabeçalho e menu logo após a abertura do <body>
  saida = saida.replace(/<body[^>]*>/i, (tag) => tag + CABECALHO);

  // 2. Data visível logo após o primeiro título
  const data = comData ? dataPublicacao(html) : null;
  if (data) {
    const linhaData = `\n<p ${MARCA} style="color:#666;font-size:.9rem;margin-top:-8px;margin-bottom:24px;">Publicado em ${data}</p>`;
    saida = saida.replace(/<\/h1>/i, (tag) => tag + linhaData);
  }

  // 3. Rodapé antes do fechamento do <body>
  saida = saida.replace(/<\/body>/i, RODAPE + '\n</body>');

  return saida;
}

// Páginas institucionais em HTML estático (termos, aviso médico, afiliados):
// troca o menu e o rodapé antigos pelo padrão do site.
export function padronizarPagina(html, folhas = '') {
  const semMenuAntigo = html
    .replace(/<nav class="site-nav"[\s\S]*?<\/nav>/i, '')
    .replace(/<footer class="site-footer"[\s\S]*?<\/footer>/i, '');
  return aplicarLayout(semMenuAntigo, { comData: false, folhas });
}

// Pega as tags <link rel="stylesheet"> da home já construída
export function folhasDoSite(htmlHome) {
  return (htmlHome.match(/<link[^>]+rel="stylesheet"[^>]*>/gi) || []).join('\n');
}
