# -*- coding: utf-8 -*-
"""
Gera a home page do blog Mente Leve (dados/saida/html/index.html) a partir do
calendario_blog_1_ano.csv: banner grande com o artigo em destaque + grade de
quadros com os próximos artigos, cada um com data marcada (dd/mm/aa) e horário.
Regra: quadro clicável apenas se o HTML do artigo existir; caso contrário,
aparece como "em breve" (sem link quebrado).
"""
import os
import re
import unicodedata
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(BASE, 'dados', 'calendario_blog_1_ano.csv')
OUT = os.path.join(BASE, 'dados', 'saida', 'html', 'index.html')

def slug_html(row):
    """Caminho relativo do HTML do artigo (coluna Artigo_Arquivo_HTML ou padrão)."""
    v = str(row.get('Artigo_Arquivo_HTML', '') or '').strip()
    if v and v.lower() != 'nan':
        return os.path.basename(v)
    return None

def titulo_do_artigo(row):
    """Tenta extrair o <title> do HTML gerado; senão capitaliza a keyword."""
    f = slug_html(row)
    if f:
        path = os.path.join(BASE, 'dados', 'saida', 'html', f)
        if os.path.exists(path):
            try:
                with open(path, encoding='utf-8') as fh:
                    m = re.search(r'<title>(.*?)</title>', fh.read(), re.S)
                    if m:
                        t = re.sub(r'\s*[-|–]\s*Mente Leve.*$', '', m.group(1), flags=re.I).strip()
                        if t:
                            return t
            except Exception:
                pass
    kw = str(row['Palavra-chave principal'])
    return kw.capitalize()

def resumo_do_artigo(row):
    """Primeira frase do parágrafo lead do HTML, se existir."""
    f = slug_html(row)
    if f:
        path = os.path.join(BASE, 'dados', 'saida', 'html', f)
        if os.path.exists(path):
            try:
                with open(path, encoding='utf-8') as fh:
                    html = fh.read()
                # primeiro <p> dentro do <article>
                corpo = html.split('<article>')[-1]
                m = re.search(r'<p[^>]*>(.*?)</p>', corpo, re.S)
                if m:
                    txt = re.sub(r'<[^>]+>', '', m.group(1))
                    txt = re.sub(r'\s+', ' ', txt).strip()
                    return (txt[:160] + '…') if len(txt) > 160 else txt
            except Exception:
                pass
    return f"Artigo informativo sobre {str(row['Palavra-chave principal'])}. Tema: {row['Tema']}."

def main():
    df = pd.read_csv(CSV)
    df['Data_dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    publicados = df[df.apply(lambda r: bool(slug_html(r)) and os.path.exists(
        os.path.join(BASE, 'dados', 'saida', 'html', slug_html(r))), axis=1)]
    destaques = df.sort_values(['Data_dt', 'Horário']).head(9)  # 3 primeiros dias

    nav = '''<nav class="site-nav" aria-label="Menu principal">
    <a href="/">Início</a><a href="/sobre.html">Sobre</a><a href="/contato.html">Contato</a><a href="/politica-editorial.html">Política editorial</a><a href="/aviso-medico.html">Aviso médico</a><a href="/divulgacao-afiliados.html">Divulgação de afiliados</a><a href="/privacidade.html">Privacidade</a><a href="/termos-de-uso.html">Termos de uso</a>
</nav>'''

    hero = ''
    cards = ''
    for i, (_, row) in enumerate(destaques.iterrows()):
        f = slug_html(row)
        existe = f and os.path.exists(os.path.join(BASE, 'dados', 'saida', 'html', f))
        data_fmt = row['Data_dt'].strftime('%d/%m/%y')
        tema = row['Tema']
        hora = row['Horário']
        titulo = titulo_do_artigo(row)
        if i == 0 and existe:
            # BANNER GRANDE — artigo em destaque
            hero = f'''<a class="hero" href="/{f}">
  <div class="hero-body">
    <span class="badge">★ Em destaque · {tema}</span>
    <h2 class="hero-title">{titulo}</h2>
    <p class="hero-desc">{resumo_do_artigo(row)}</p>
    <span class="hero-meta">📅 Publicado em {data_fmt} às {hora}</span>
  </div>
</a>'''
        elif existe:
            cards += f'''<a class="card" href="/{f}">
  <div class="card-top"><span class="tag">{tema}</span><span class="date">{data_fmt} · {hora}</span></div>
  <h3>{titulo}</h3>
  <p>{resumo_do_artigo(row)}</p>
</a>'''
        else:
            cards += f'''<div class="card card-soon">
  <div class="card-top"><span class="tag">{tema}</span><span class="date">{data_fmt} · {hora}</span></div>
  <h3>{titulo}</h3>
  <p class="soon">Em produção — entra no ar automaticamente nesta data.</p>
</div>'''

    n_pub = len(publicados)
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mente Leve — Saúde Mental e Bem-Estar</title>
<meta name="description" content="Blog Mente Leve: artigos informativos sobre ansiedade, estresse, sono, meditação, memória e bem-estar mental. Novos textos todos os dias às 09h, 12h e 20h.">
<style>
body {{ font-family: Georgia, 'Times New Roman', serif; color:#222; background:#fafafa; line-height:1.7; margin:0; padding:0; }}
.wrap {{ max-width: 980px; margin:0 auto; padding: 24px 20px; }}
.site-header {{ background:#006400; color:#fff; padding:16px 20px; text-align:center; }}
.site-header .site-title {{ font-size:1.5rem; font-weight:bold; letter-spacing:.5px; }}
.site-header .site-tag {{ font-size:.9rem; opacity:.9; }}
.site-nav {{ background:#f0f4f0; border-bottom:1px solid #dfe8df; padding:10px 20px; text-align:center; }}
.site-nav a {{ color:#006400; text-decoration:none; font-size:.95rem; margin:0 10px; white-space:nowrap; }}
.site-nav a:hover {{ text-decoration:underline; }}
.hero {{ display:block; text-decoration:none; color:inherit; background:linear-gradient(135deg,#006400,#0a7d0a); border-radius:14px; overflow:hidden; margin:18px 0 30px; box-shadow:0 6px 18px rgba(0,100,0,.18); }}
.hero-body {{ padding: 42px 36px; }}
.hero .badge {{ display:inline-block; background:#ffd54d; color:#333; font-size:.8rem; font-weight:bold; padding:4px 12px; border-radius:20px; margin-bottom:14px; }}
.hero-title {{ color:#fff; font-size:2.1rem; margin:0 0 12px; line-height:1.25; }}
.hero-desc {{ color:#e8f3e8; font-size:1.1rem; margin:0 0 16px; max-width:640px; }}
.hero-meta {{ color:#cfe6cf; font-size:.9rem; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:18px; }}
.card {{ background:#fff; border:1px solid #e4ece4; border-radius:12px; padding:20px; text-decoration:none; color:inherit; transition:transform .15s, box-shadow .15s; display:block; }}
.card:hover {{ transform:translateY(-3px); box-shadow:0 8px 20px rgba(0,0,0,.08); }}
.card h3 {{ color:#006400; font-size:1.15rem; margin:10px 0 8px; line-height:1.35; }}
.card p {{ font-size:.95rem; color:#444; margin:0; }}
.card-top {{ display:flex; justify-content:space-between; align-items:center; gap:8px; }}
.tag {{ background:#e8f3e8; color:#006400; font-size:.75rem; font-weight:bold; padding:3px 10px; border-radius:14px; }}
.date {{ color:#777; font-size:.8rem; white-space:nowrap; }}
.card-soon {{ opacity:.75; border-style:dashed; cursor:default; }}
.soon {{ font-style:italic; color:#777; }}
h2.section {{ color:#006400; font-size:1.5rem; border-bottom:2px solid #e0e8e0; padding-bottom:6px; margin-top:8px; }}
.site-footer {{ background:#f7f7f7; border-top:1px solid #eaeaea; margin-top:48px; padding:28px 20px; text-align:center; font-size:.9rem; color:#555; }}
.site-footer .footer-links a {{ color:#006400; text-decoration:none; margin:0 8px; }}
@media (max-width:600px) {{ .site-nav a {{ display:inline-block; margin:4px 8px; }} .hero-body {{ padding:28px 22px; }} .hero-title {{ font-size:1.5rem; }} }}
</style>
</head>
<body>
<div class="site-header">
  <div class="site-title">🌿 Mente Leve</div>
  <div class="site-tag">Saúde mental e bem-estar · novos artigos todos os dias às 09h, 12h e 20h</div>
</div>
{nav}
<div class="wrap">
{hero}
<h2 class="section">Próximas publicações</h2>
<div class="grid">
{cards}
</div>
<p style="color:#555;font-size:.95rem;margin-top:26px;">📊 {n_pub} artigo(s) já publicado(s) de 1.095 programados no calendário 08/10/2026 → 07/10/2027. Este conteúdo é informativo e não substitui a orientação de um profissional de saúde.</p>
</div>
<footer class="site-footer">
  <div class="footer-links">
    <a href="/index.html">Início</a> · <a href="/sobre.html">Sobre</a> · <a href="/contato.html">Contato</a> · <a href="/politica-editorial.html">Política editorial</a> · <a href="/aviso-medico.html">Aviso médico</a> · <a href="/divulgacao-afiliados.html">Divulgação de afiliados</a> · <a href="/privacidade.html">Privacidade</a> · <a href="/termos-de-uso.html">Termos de uso</a>
  </div>
  <p style="margin-top:14px;">🌿 <strong>Mente Leve</strong> — conteúdo informativo sobre saúde mental e bem-estar.<br>
  Este site não substitui diagnóstico ou tratamento profissional. Procure um médico ou psicólogo.</p>
  <p>© 2026 Mente Leve. Todos os direitos reservados.</p>
</footer>
</body>
</html>'''

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print(f"✅ Home gerada: {OUT} | destaque={'sim' if hero else 'nenhum'} | quadros={destaques.shape[0]-1} | publicados={n_pub}")

if __name__ == '__main__':
    main()
