#!/usr/bin/env python3
"""
🤖 Gerador de Artigos com Google Gemini
Lê CSV e gera artigos HTML automaticamente
"""

import os
import csv
import google.generativeai as genai
from pathlib import Path

# ⚙️ CONFIGURAÇÃO
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
CSV_FILE = "dados/calendario_blog_1_ano.csv"
OUTPUT_DIR = "dados/saida/html"

def setup_gemini():
    """Configurar Gemini API"""
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY não configurada!")
        print("Defina: export GEMINI_API_KEY='sua-chave-aqui'")
        exit(1)

    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini conectado")

def criar_pasta_output():
    """Criar pasta de saída se não existir"""
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"✅ Pasta {OUTPUT_DIR} pronta")

def ler_csv():
    """Ler artigos do CSV"""
    if not os.path.exists(CSV_FILE):
        print(f"❌ {CSV_FILE} não encontrado!")
        exit(1)

    artigos = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        artigos = list(reader)

    print(f"✅ {len(artigos)} artigos lidos do CSV")
    return artigos

def gerar_html_artigo(tema, titulo, palavras_chave=""):
    """Gerar artigo em HTML com Gemini"""

    prompt = f"""Escreva um artigo HTML profissional e informativo.

TEMA: {tema}
TÍTULO: {titulo}
PALAVRAS-CHAVE: {palavras_chave}

REQUISITOS:
1. Extensão: 1000-1500 palavras
2. Tom: Informativo, amigável, acessível
3. Estrutura:
   - Introdução impactante
   - 4-5 seções com <h2>
   - Cada seção com 2-3 parágrafos <p>
   - 1-2 listas <ul><li> por seção
   - Conclusão motivadora
   - Isenção de responsabilidade

4. Formatação HTML:
   - Use apenas <h2>, <p>, <ul>, <li>, <strong>, <em>
   - NÃO use <html>, <head>, <body>, <meta>
   - NÃO use <h1> (título já é o h1)

EXEMPLO ESTRUTURA:
<p>Introdução...</p>

<h2>Seção 1: Tópico</h2>
<p>Parágrafo 1...</p>
<p>Parágrafo 2...</p>
<ul>
  <li>Ponto 1</li>
  <li>Ponto 2</li>
</ul>

<h2>Conclusão</h2>
<p>Resumo e chamada à ação...</p>

<p><strong>⚠️ Isenção:</strong> Este conteúdo é informativo. Consulte profissional qualificado.</p>

Retorne APENAS o HTML, sem explicações."""

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Erro gerando artigo: {e}")
        return None

def salvar_artigo(html_content, numero, titulo):
    """Salvar artigo em arquivo HTML"""
    if not html_content:
        return False

    # Criar nome do arquivo
    nome_arquivo = f"art-{numero:03d}-{titulo[:30].replace(' ', '-').lower()}.html"
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)

    # Salvar arquivo
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return nome_arquivo

def processar_artigos(artigos, comecar_de=1, atualizar_csv=False):
    """Processar artigos e gerar HTMLs"""

    artigos_processados = 0
    artigos_pulados = 0

    for idx, artigo in enumerate(artigos[comecar_de-1:], start=comecar_de):
        titulo = artigo.get('Palavra-chave principal', '').strip()
        tema = artigo.get('Tema', '').strip()
        arquivo_html = artigo.get('Artigo_Arquivo_HTML', '').strip()

        if not titulo or not tema:
            print(f"⏭️  #{idx:03d} PULADO - Faltam dados")
            artigos_pulados += 1
            continue

        # Verificar se já existe
        if arquivo_html and arquivo_html.lower() != 'nan':
            arquivo_path = os.path.join(OUTPUT_DIR, arquivo_html)
            if os.path.exists(arquivo_path):
                print(f"⏭️  #{idx:03d} PULADO - Já existe: {arquivo_html}")
                artigos_pulados += 1
                continue

        # Gerar artigo
        print(f"⏳ #{idx:03d} Gerando: {titulo}...")
        html = gerar_html_artigo(tema, titulo)

        if html:
            nome_arquivo = salvar_artigo(html, idx, titulo)
            print(f"✅ #{idx:03d} Salvo: {nome_arquivo}")

            # Atualizar CSV se necessário
            if atualizar_csv:
                artigo['Artigo_Arquivo_HTML'] = nome_arquivo

            artigos_processados += 1
        else:
            print(f"❌ #{idx:03d} Falha ao gerar")
            artigos_pulados += 1

    return artigos_processados, artigos_pulados

def salvar_csv_atualizado(artigos):
    """Atualizar CSV com nomes de arquivos"""
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        if artigos:
            writer = csv.DictWriter(f, fieldnames=artigos[0].keys())
            writer.writeheader()
            writer.writerows(artigos)
    print(f"✅ CSV atualizado: {CSV_FILE}")

def main():
    """Fluxo principal"""

    print("🤖 GERADOR DE ARTIGOS COM GEMINI\n")

    # Setup
    setup_gemini()
    criar_pasta_output()
    artigos = ler_csv()

    # Menu
    print("\n📋 OPÇÕES:")
    print("1. Gerar TODOS os artigos (padrão: começar do #1)")
    print("2. Gerar a partir de artigo específico")
    print("3. Gerar apenas artigos faltantes")
    print("4. Cancelar")

    opcao = input("\nEscolha (1-4): ").strip() or "1"

    comecar_de = 1
    atualizar_csv = False

    if opcao == "1":
        print("\n🚀 Gerando TODOS os artigos...")
        atualizar_csv = True
    elif opcao == "2":
        comecar_de = int(input("Começar do artigo # (ex: 5): ") or "1")
        atualizar_csv = True
    elif opcao == "3":
        print("\n🚀 Gerando apenas artigos faltantes...")
        atualizar_csv = True
    else:
        print("❌ Cancelado")
        exit(0)

    # Processar
    print()
    processados, pulados = processar_artigos(artigos, comecar_de, atualizar_csv)

    # Resultado
    print(f"\n{'='*50}")
    print(f"✅ CONCLUÍDO!")
    print(f"   Artigos gerados: {processados}")
    print(f"   Artigos pulados: {pulados}")
    print(f"   Pasta: {OUTPUT_DIR}")
    print(f"{'='*50}")

    if atualizar_csv:
        resposta = input("\nAtualizar CSV com nomes de arquivos? (s/n): ").lower()
        if resposta == 's':
            salvar_csv_atualizado(artigos)

if __name__ == "__main__":
    main()
