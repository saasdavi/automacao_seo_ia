# -*- coding: utf-8 -*-
"""
Script para processar artigos gerados pelo Gemini e salvá-los como arquivos HTML.
Lê o CSV do calendário e, para cada artigo que tem HTML na coluna Artigo_Arquivo_HTML,
garante que o arquivo existe na pasta dados/saida/html/

Uso:
  python scripts/processar_artigos.py --gerar-faltantes
    Gera stubs HTML para artigos que faltam

  python scripts/processar_artigos.py --validar
    Valida integridade dos arquivos existentes
"""
import os
import sys
import argparse
import pandas as pd
import re
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(BASE, 'dados', 'calendario_blog_1_ano.csv')
HTML_DIR = os.path.join(BASE, 'dados', 'saida', 'html')


def garantir_diretorio():
    """Cria o diretório de saída se não existir."""
    os.makedirs(HTML_DIR, exist_ok=True)


def gerar_stub_html(titulo, tema, data, hora, palavra_chave):
    """
    Gera um HTML stub para um artigo em desenvolvimento.
    Este será substituído pelo HTML real do Gemini depois.
    """
    slug_titulo = re.sub(r'[^\w\s-]', '', titulo.lower()).replace(' ', '-')

    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo} — Mente Leve</title>
<meta name="description" content="Artigo sobre {palavra_chave}. Tema: {tema}. Publicado em {data} às {hora}.">
<style>
body {{
  font-family: Georgia, 'Times New Roman', serif;
  line-height: 1.7;
  color: #222;
  background: #fafafa;
  margin: 0;
  padding: 0;
}}
.wrap {{
  max-width: 680px;
  margin: 0 auto;
  padding: 24px 20px;
}}
.site-header {{
  background: #006400;
  color: #fff;
  padding: 16px 20px;
  text-align: center;
}}
.site-header .site-title {{
  font-size: 1.5rem;
  font-weight: bold;
}}
.site-nav {{
  background: #f0f4f0;
  padding: 10px 20px;
  text-align: center;
  border-bottom: 1px solid #dfe8df;
}}
.site-nav a {{
  color: #006400;
  text-decoration: none;
  margin: 0 10px;
  font-size: 0.95rem;
}}
article {{
  background: #fff;
  padding: 40px;
  border-radius: 8px;
  margin: 20px 0;
}}
article h1 {{
  color: #006400;
  font-size: 2rem;
  margin-top: 0;
}}
.meta {{
  color: #777;
  font-size: 0.9rem;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}}
.status {{
  background: #fff3cd;
  border: 1px solid #ffc107;
  color: #664d03;
  padding: 16px;
  border-radius: 6px;
  margin: 20px 0;
}}
</style>
</head>
<body>
<div class="site-header">
  <div class="site-title">🌿 Mente Leve</div>
</div>
<nav class="site-nav">
  <a href="/">Início</a> · <a href="/sobre.html">Sobre</a>
</nav>
<div class="wrap">
  <article>
    <h1>{titulo}</h1>
    <div class="meta">
      📅 {data} às {hora} · 📌 {tema}
    </div>
    <div class="status">
      <strong>ℹ️ Em produção</strong><br>
      Este artigo sobre "<strong>{palavra_chave}</strong>" está em desenvolvimento e será preenchido com conteúdo em breve.
    </div>
    <p style="text-align: center; color: #999; margin-top: 40px; font-style: italic;">
      Volte em breve para ler o conteúdo completo.
    </p>
  </article>
</div>
</body>
</html>'''
    return html


def processar_artigos_faltantes():
    """Gera stubs para artigos que ainda não têm HTML."""
    garantir_diretorio()

    if not os.path.exists(CSV):
        print(f"❌ CSV não encontrado: {CSV}")
        return

    df = pd.read_csv(CSV)
    criados = 0
    ja_existem = 0

    for idx, row in df.iterrows():
        arquivo = str(row.get('Artigo_Arquivo_HTML', '')).strip()
        if not arquivo or arquivo.lower() == 'nan':
            continue

        caminho = os.path.join(HTML_DIR, arquivo)
        if os.path.exists(caminho):
            ja_existem += 1
            continue

        # Cria stub HTML
        titulo = row['Palavra-chave principal'].capitalize()
        tema = row['Tema']
        data = row['Data']
        hora = row['Horário']

        html = gerar_stub_html(titulo, tema, data, hora, row['Palavra-chave principal'])

        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ Criado: {arquivo}")
            criados += 1
        except Exception as e:
            print(f"❌ Erro ao criar {arquivo}: {e}")

    print(f"\n📊 Resumo: {criados} novo(s) | {ja_existem} já existente(s)")


def validar_artigos():
    """Valida integridade dos arquivos HTML existentes."""
    garantir_diretorio()

    if not os.path.exists(CSV):
        print(f"❌ CSV não encontrado: {CSV}")
        return

    df = pd.read_csv(CSV)
    validos = 0
    invalidos = 0
    faltantes = []

    for idx, row in df.iterrows():
        arquivo = str(row.get('Artigo_Arquivo_HTML', '')).strip()
        if not arquivo or arquivo.lower() == 'nan':
            continue

        caminho = os.path.join(HTML_DIR, arquivo)

        if not os.path.exists(caminho):
            faltantes.append(arquivo)
            invalidos += 1
            continue

        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                if '<html' in conteudo.lower() and '</html>' in conteudo.lower():
                    validos += 1
                else:
                    print(f"⚠️  {arquivo} - HTML malformado")
                    invalidos += 1
        except Exception as e:
            print(f"❌ {arquivo} - Erro: {e}")
            invalidos += 1

    print(f"\n📊 Validação:")
    print(f"✅ Válidos: {validos}")
    print(f"❌ Inválidos/Faltantes: {invalidos}")

    if faltantes:
        print(f"\n📋 Arquivos faltantes ({len(faltantes)}):")
        for f in faltantes[:5]:
            print(f"  - {f}")
        if len(faltantes) > 5:
            print(f"  ... e mais {len(faltantes) - 5}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Processar artigos do blog')
    parser.add_argument('--gerar-faltantes', action='store_true', help='Gera stubs para artigos faltantes')
    parser.add_argument('--validar', action='store_true', help='Valida integridade dos arquivos')

    args = parser.parse_args()

    if args.gerar_faltantes:
        processar_artigos_faltantes()
    elif args.validar:
        validar_artigos()
    else:
        print("Use: --gerar-faltantes ou --validar")
        sys.exit(1)
