// Aplica o layout do site (cabeçalho, menu, data e rodapé) nas páginas de artigo.
// Os artigos gerados pela IA são documentos HTML completos e não passam pelo
// Layout.astro. Esta função é aplicada na cópia do build, sem alterar os
// arquivos originais em dados/saida/html/.

const MARCA = 'data-mente-leve-layout';

const CABECALHO = `
<header ${MARCA} style="background:#006400;color:#fff;padding:16px 20px;text-align:center;">
  <a href="/" style="color:#fff;text-decoration:none;font-size:1.5rem;font-weight:bold;">🌿 Mente Leve</a>
</header>
<nav ${MARCA} style="background:#f0f4f0;border-bottom:1px solid #dfe8df;padding:10px 20px;text-align:center;font-size:.95rem;">
  <a href="/" style="color:#006400;text-decoration:none;margin:0 8px;">Início</a> ·
  <a href="/#artigos" style="color:#006400;text-decoration:none;margin:0 8px;">Todos os artigos</a> ·
  <a href="/sobre" style="color:#006400;text-decoration:none;margin:0 8px;">Sobre</a> ·
  <a href="/contato" style="color:#006400;text-decoration:none;margin:0 8px;">Contato</a>
</nav>`;

const RODAPE = `
<footer ${MARCA} style="background:#f7f7f7;border-top:1px solid #eaeaea;margin-top:48px;padding:28px 20px;text-align:center;font-size:.9rem;color:#555;">
  <div>
    <a href="/" style="color:#006400;text-decoration:none;margin:0 8px;">Início</a> ·
    <a href="/sobre" style="color:#006400;text-decoration:none;margin:0 8px;">Sobre</a> ·
    <a href="/contato" style="color:#006400;text-decoration:none;margin:0 8px;">Contato</a> ·
    <a href="/politica-editorial" style="color:#006400;text-decoration:none;margin:0 8px;">Política editorial</a> ·
    <a href="/privacidade" style="color:#006400;text-decoration:none;margin:0 8px;">Privacidade</a>
  </div>
  <p style="margin-top:14px;">🌿 <strong>Mente Leve</strong> — conteúdo informativo sobre saúde mental e bem-estar.<br>Este site não substitui diagnóstico ou tratamento profissional.</p>
</footer>`;

// Lê a data de publicação do JSON-LD (ex.: "2026-10-10T13:53:53-03:00")
// e devolve no formato dd/mm/aaaa, usando a data local já escrita no texto.
export function dataPublicacao(html) {
  const m = html.match(/"datePublished"\s*:\s*"(\d{4})-(\d{2})-(\d{2})/);
  return m ? `${m[3]}/${m[2]}/${m[1]}` : null;
}

export function aplicarLayout(html) {
  // Já aplicado: não duplica cabeçalho, data nem rodapé
  if (html.includes(MARCA)) return html;

  let saida = html;

  // 1. Cabeçalho e menu logo após a abertura do <body>
  saida = saida.replace(/<body[^>]*>/i, (tag) => tag + CABECALHO);

  // 2. Data visível logo após o primeiro título
  const data = dataPublicacao(html);
  if (data) {
    const linhaData = `\n<p ${MARCA} style="color:#666;font-size:.9rem;margin-top:-8px;margin-bottom:24px;">Publicado em ${data}</p>`;
    saida = saida.replace(/<\/h1>/i, (tag) => tag + linhaData);
  }

  // 3. Rodapé antes do fechamento do <body>
  saida = saida.replace(/<\/body>/i, RODAPE + '\n</body>');

  return saida;
}
