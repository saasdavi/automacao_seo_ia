import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
import time

# ============================================
# CONFIGURAÇÕES
# ============================================
SERPER_API_KEY = os.environ.get('SERPER_API_KEY')
MAX_ROWS_PER_RUN = int(os.environ.get('MAX_ROWS', '10'))
INPUT_CSV = 'dados/calendario_blog_1_ano.csv'
OUTPUT_CSV = 'dados/calendario_blog_1_ano.csv'

# ============================================
# FUNÇÕES SERP
# ============================================
def buscar_serper(keyword, num=5):
    """Busca no Google via Serper.dev"""
    url = "https://google.serper.dev/search"
    payload = {"q": keyword, "gl": "br", "hl": "pt", "num": num}
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erro na API para {keyword}: {e}")
    return None

def analisar_pagina(url):
    """Extrai título e H2s de uma página"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        r = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        title = soup.find('title').get_text().strip() if soup.find('title') else "Sem título"
        h2s = [h2.get_text().strip() for h2 in soup.find_all('h2') if h2.get_text().strip()][:8]
        text = soup.get_text()
        word_count = len(text.split())
        
        # Classificar tipo
        tipo = "blog"
        if any(x in url for x in ['hospital', 'saude', 'clinica', 'hc.', 'hosp']):
            tipo = "hospital"
        elif 'wikipedia' in url:
            tipo = "enciclopédia"
        elif 'gov.br' in url or 'ms.gov' in url or 'embrapa' in url:
            tipo = "portal oficial"
        elif any(x in url for x in ['uol', 'g1', 'folha', 'estadao']):
            tipo = "portal de notícias"
        elif any(x in url for x in ['minhavida', 'tuasaude', 'drashirley', 'drauziovarella']):
            tipo = "portal de saúde"
        
        return {
            'titulo': title,
            'url': url,
            'tipo': tipo,
            'palavras': word_count,
            'h2s': '; '.join(h2s)
        }
    except Exception as e:
        return {'titulo': 'Erro', 'url': url, 'tipo': 'erro', 'palavras': 0, 'h2s': str(e)}

def classificar_dificuldade(organicos):
    """Define dificuldade baseado em autoridades no Top 5"""
    autoridades = ['gov.br', 'wikipedia.org', 'nih.gov', 'who.int', 'hospital', 'clinica', 
                   'minhavida.com.br', 'tuasaude.com', 'drashirley', 'drauziovarella',
                   'einstein.br', 'sbpt.org.br', 'sbcardiologia.org.br']
    count = sum(1 for item in organicos if any(a in item.get('link', '') for a in autoridades))
    if count >= 3:
        return "Difícil"
    if count >= 1:
        return "Média"
    return "Fácil"

def identificar_lacunas(paa, h2s_geral):
    """Compara PAA com H2s dos concorrentes para achar gaps"""
    lacunas = []
    for pergunta in paa:
        if not any(pergunta.lower() in h2.lower() for h2 in h2s_geral):
            lacunas.append(pergunta)
    return lacunas[:6]

def extrair_long_tails(organicos):
    """Extrai long tails dos snippets"""
    long_tails = []
    for item in organicos:
        snippet = item.get('snippet', '')
        # Buscar termos de 3+ palavras
        termos = re.findall(r'\b\w+(?:\s+\w+){2,5}\b', snippet)
        for t in termos[:5]:
            long_tails.append({'termo': t, 'fonte': item.get('link', '')})
    return long_tails[:30]

def montar_prompt_gemini(row, dados_serp):
    """Monta o texto exato que o Gemini vai ler"""
    return f"""CONTEXTO DA PLANILHA:
- Palavra-chave: {row['Palavra-chave principal']}
- Tema: {row['Tema']} | Volume: {row['Volume (dado)']} | Concorrência Ads: {row['Concorrência']}
- Variações: {row.get('Variações (sinônimos)', '')}

DADOS SERP (Extraídos ao vivo):
- Dificuldade Real: {dados_serp['dificuldade']}
- Fontes Oficiais Candidatas: {dados_serp['fontes']}
- Lacunas do Topo (O que eles não responderam): {dados_serp['lacunas']}
- Autoridades no Top 5: {dados_serp['autoridades']}
- Divergências com a Planilha: {dados_serp['divergencias']}

CONCORRENTES (Top 5):
{dados_serp['concorrentes_formatado']}

PERGUNTAS DO GOOGLE (PAA):
{dados_serp['paa_formatado']}

PESQUISAS RELACIONADAS:
{dados_serp['relacionadas_formatado']}

LONG TAILS VISTAS:
{dados_serp['longtails_formatado']}

H2s COMUNS NO TOPO:
{dados_serp['h2s_formatado']}

---
Agora gere o artigo seguindo o Prompt Mestre v4 abaixo:

Você é um REDATOR SÊNIOR DE SEO E CONTEÚDO, especializado em E-E-A-T, Helpful Content System, Schema Markup e diretrizes YMYL do Google.

FORMATO DE ENTREGA: HTML completo com Schema JSON-LD tipo MedicalWebPage, imagens do Pexels (4 imagens), CSS interno profissional, mínimo 1.500 palavras, parágrafos ≤50 palavras, H2s baseados nas PAA, seção "Resumindo", seção "Fontes" com 6+ URLs diretas, aviso final de conteúdo informativo, assinatura com CRM.

REGRAS: Palavra-chave no H1, primeiro parágrafo e 1 H2. Hierarquia H1→H2→H3. Mínimo 3 links contextuais para fontes oficiais. Alt text único 50-125 caracteres para cada imagem.

PROIBIDO: Palavra "cura", expressões de IA ("vale ressaltar", "é importante destacar", "concluindo"), metalinguagem, dosagens de medicamentos, promessas de resultado garantido, fontes com homepage genérica.

ENTREGUE NO FINAL: Análise de Pontuação com nota de 0 a 10, checklist de 30 itens, tabela de critérios com peso, correções E-E-A-T aplicadas, validação do Schema Markup, lacunas do topo cobertas, pontos de atenção, e status PRONTO PARA IMPORTAÇÃO (se nota ≥ 9,0).
---
"""

# ============================================
# MAIN
# ============================================
def main():
    print(" Iniciando enriquecimento SERP...")
    
    if not SERPER_API_KEY:
        print("❌ SERPER_API_KEY não configurada. Abortando.")
        return
    
    df = pd.read_csv(INPUT_CSV)
    
    # Garante que as colunas novas existem
    novas_colunas = [
        'Status', 'SERP_Data_Consulta', 'SERP_Dificuldade_Real', 'SERP_Top5_URLs_e_Tipos',
        'SERP_H2s_Comuns', 'SERP_PAA', 'SERP_Pesquisas_Relacionadas', 'SERP_Long_Tails_Vistas',
        'SERP_Lacunas_Identificadas', 'SERP_Fontes_Oficiais_Candidatas', 'SERP_Autoridades_Top5',
        'SERP_Divergencias_Com_Planilha', 'GEMINI_Prompt_Pronto', 'GEMINI_Nota_Autoavaliada',
        'Link_Artigo_Gerado', 'Data_Publicacao'
    ]
    for col in novas_colunas:
        if col not in df.columns:
            df[col] = ''
    
    # Filtra apenas linhas na fila
    if 'Status' not in df.columns:
        df['Status'] = 'Fila'
    fila = df[df['Status'].isin(['Fila', 'fila', ''])].head(MAX_ROWS_PER_RUN)
    
    if fila.empty:
        print("✅ Nenhuma linha na fila. Processo concluído.")
        return
    
    print(f"📋 Processando {len(fila)} artigos...")
    
    for idx, row in fila.iterrows():
        keyword = row['Palavra-chave principal']
        if pd.isna(keyword) or not keyword:
            continue
            
        print(f"🔍 [{idx+1}/{len(fila)}] Buscando: {keyword}")
        
        dados = buscar_serper(keyword)
        if not dados:
            print(f"⚠️ Falha na API para {keyword}")
            continue
        
        organicos = dados.get('organic', [])[:5]
        paa = [p['question'] for p in dados.get('peopleAlsoAsk', [])]
        relacionadas = [r['query'] for r in dados.get('relatedSearches', [])]
        
        # Extrai H2s de todos os concorrentes
        todos_h2s = []
        concorrentes_str = []
        for i, item in enumerate(organicos):
            analise = analisar_pagina(item['link'])
            todos_h2s.extend(analise['h2s'].split('; '))
            concorrentes_str.append(f"{i+1}. {analise['titulo']} | {analise['url']} | {analise['tipo']} | {analise['palavras']} palavras | H2s: {analise['h2s']}")
            time.sleep(0.5)  # Respeitar rate limit
        
        # Processa dados
        dificuldade = classificar_dificuldade(organicos)
        lacunas = identificar_lacunas(paa, todos_h2s)
        long_tails = extrair_long_tails(organicos)
        fontes = [item['link'] for item in organicos if any(x in item.get('link', '') for x in ['gov.br', '.org', 'who.int', 'nih.gov'])][:5]
        autoridades = list(set([item['link'].split('/')[2] for item in organicos if any(x in item.get('link', '') for x in ['gov.br', 'wikipedia', 'hospital', 'clinica'])]))[:5]
        
        # Atualiza o DataFrame
        df.at[idx, 'Status'] = 'SERP_OK'
        df.at[idx, 'SERP_Data_Consulta'] = datetime.now().strftime('%Y-%m-%d')
        df.at[idx, 'SERP_Dificuldade_Real'] = dificuldade
        df.at[idx, 'SERP_Top5_URLs_e_Tipos'] = " | ".join([f"{o.get('title','')} | {o.get('link','')}" for o in organicos])
        df.at[idx, 'SERP_H2s_Comuns'] = "; ".join(list(set(todos_h2s))[:10])
        df.at[idx, 'SERP_PAA'] = "; ".join(paa)
        df.at[idx, 'SERP_Pesquisas_Relacionadas'] = "; ".join(relacionadas)
        df.at[idx, 'SERP_Long_Tails_Vistas'] = "; ".join([f"{lt['termo']} ({lt['fonte']})" for lt in long_tails[:20]])
        df.at[idx, 'SERP_Lacunas_Identificadas'] = "; ".join(lacunas)
        df.at[idx, 'SERP_Fontes_Oficiais_Candidatas'] = "; ".join(fontes)
        df.at[idx, 'SERP_Autoridades_Top5'] = "; ".join(autoridades)
        df.at[idx, 'SERP_Divergencias_Com_Planilha'] = ''
        
        # Monta o Prompt para o Gemini
        dados_serp_dict = {
            'dificuldade': dificuldade,
            'fontes': fontes,
            'lacunas': lacunas,
            'autoridades': autoridades,
            'divergencias': '',
            'concorrentes_formatado': "\n".join(concorrentes_str),
            'paa_formatado': "\n".join([f"- {p}" for p in paa]),
            'relacionadas_formatado': "\n".join([f"- {r}" for r in relacionadas]),
            'longtails_formatado': "\n".join([f"- {lt['termo']}" for lt in long_tails[:20]]),
            'h2s_formatado': "\n".join([f"- {h}" for h in list(set(todos_h2s))[:8]])
        }
        df.at[idx, 'GEMINI_Prompt_Pronto'] = montar_prompt_gemini(row, dados_serp_dict)
        
        # Salva progresso a cada linha
        df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
        print(f"💾 Salvo progresso após {keyword}")
    
    print(f"✅ Concluído! {len(fila)} artigos processados.")

if __name__ == "__main__":
    main()
