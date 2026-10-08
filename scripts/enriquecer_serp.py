import os
import sys
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
# Chave do SerpAPI (serpapi.com), lida do secret SERPAPI_KEY
SERPAPI_KEY = os.environ.get('SERPAPI_KEY')
MAX_ROWS_PER_RUN = int(os.environ.get('MAX_ROWS', '10'))
INPUT_CSV = 'dados/calendario_blog_1_ano.csv'
OUTPUT_CSV = 'dados/calendario_blog_1_ano.csv'
# Pasta onde ficam os arquivos Markdown por artigo (a planilha vira apenas índice)
SAIDA_MD_DIR = 'dados/saida/md'

# ============================================
# FUNÇÕES SERP
# ============================================
def buscar_serpapi(keyword, num=5):
    """Busca no Google via SerpAPI (serpapi.com) e devolve no formato usado pelo script"""
    params = {
        "engine": "google", "q": keyword, "api_key": SERPAPI_KEY,
        "gl": "br", "hl": "pt", "google_domain": "google.com.br", "num": num,
    }
    try:
        response = requests.get("https://serpapi.com/search.json", params=params, timeout=20)
        if response.status_code != 200:
            # Diagnóstico: 401 = chave inválida; 429 = limite de buscas do plano
            print(f"⚠️ HTTP {response.status_code} na SerpAPI para '{keyword}': {response.text[:150]}")
            return None
        dados = response.json()
    except Exception as e:
        print(f"Erro na API para {keyword}: {e}")
        return None
    # Converte para a estrutura que o restante do script já usa
    return {
        'organic': [{'title': o.get('title', ''), 'link': o.get('link', '')} for o in dados.get('organic_results', [])],
        'peopleAlsoAsk': [{'question': q.get('question', '')} for q in dados.get('related_questions', [])],
        'relatedSearches': [{'query': r.get('query', '')} for r in dados.get('related_searches', [])],
    }

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
    
    if not SERPAPI_KEY:
        print("❌ SERPAPI_KEY não configurada. Abortando.")
        sys.exit(1)
    
    df = pd.read_csv(INPUT_CSV)
    
    # Garante que as colunas novas existem
    novas_colunas = [
        'Status', 'SERP_Data_Consulta', 'SERP_Dificuldade_Real', 'SERP_Top5_URLs_e_Tipos',
        'SERP_H2s_Comuns', 'SERP_PAA', 'SERP_Pesquisas_Relacionadas', 'SERP_Long_Tails_Vistas',
        'SERP_Lacunas_Identificadas', 'SERP_Fontes_Oficiais_Candidatas', 'SERP_Autoridades_Top5',
        'SERP_Divergencias_Com_Planilha', 'GEMINI_Prompt_Pronto', 'GEMINI_Nota_Autoavaliada',
        'Link_Artigo_Gerado', 'Data_Publicacao',
        # Novas colunas de referência (a planilha vira índice; os dados vão para arquivos .md)
        'SERP_Arquivo_MD', 'GEMINI_Prompt_Arquivo', 'Artigo_Arquivo_HTML'
    ]
    for col in novas_colunas:
        if col not in df.columns:
            df[col] = ''
        # Colunas vazias no CSV são lidas como float64 e não aceitam texto (quebra o pandas atual)
        df[col] = df[col].astype(object)

    # Garante a pasta de saída dos arquivos Markdown
    os.makedirs(SAIDA_MD_DIR, exist_ok=True)

    # Normaliza Status em branco para 'Fila' (todas as 1.095 linhas elegíveis)
    if 'Status' not in df.columns:
        df['Status'] = 'Fila'
    df['Status'] = df['Status'].fillna('').astype(str).str.strip()
    df.loc[df['Status'] == '', 'Status'] = 'Fila'

    # Filtra apenas linhas na fila
    fila = df[df['Status'].isin(['Fila', 'fila'])].head(MAX_ROWS_PER_RUN)
    
    if fila.empty:
        print("✅ Nenhuma linha na fila. Processo concluído.")
        return

    processados = 0
    
    print(f"📋 Processando {len(fila)} artigos...")
    
    for idx, row in fila.iterrows():
        keyword = row['Palavra-chave principal']
        if pd.isna(keyword) or not keyword:
            continue
            
        print(f"🔍 [{idx+1}/{len(fila)}] Buscando: {keyword}")
        
        dados = buscar_serpapi(keyword)
        if not dados:
            print(f"⚠️ Falha na API para {keyword}")
            continue
        
        organicos = dados.get('organic', [])[:5]
        paa = [p['question'] for p in dados.get('peopleAlsoAsk', [])]
        relacionadas = [r['query'] for r in dados.get('relatedSearches', [])]
        
        # Extrai H2s de todos os concorrentes
        todos_h2s = []
        concorrentes_str = []
        analises = []  # guarda a análise de cada página para gerar o briefing .md
        for i, item in enumerate(organicos):
            analise = analisar_pagina(item['link'])
            analises.append(analise)
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
        processados += 1
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
        # Divergências automáticas: Ads vs SERP real + volume vs intenção da SERP
        divergencias = ""
        ads = str(row.get('Concorrência', '')).strip().lower()
        mapa_ads = {'baixo': 'fácil', 'low': 'fácil', 'médio': 'média', 'medio': 'média', 'medium': 'média', 'alto': 'difícil', 'high': 'difícil'}
        esperada = mapa_ads.get(ads, '')
        if esperada and esperada != dificuldade.lower():
            divergencias += f"A planilha diz concorrência Ads '{row['Concorrência']}' mas a SERP real indica '{dificuldade}'. "
        try:
            vol_num = float(str(row.get('Volume (dado)', '0')).replace('.', '').replace(',', ''))
        except ValueError:
            vol_num = 0
        if vol_num >= 5000 and dificuldade == "Difícil":
            divergencias += "Cabeça de termo com alto volume disputado por autoridades — priorizar E-E-A-T forte. "
        df.at[idx, 'SERP_Divergencias_Com_Planilha'] = divergencias.strip()
        
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

        # === Gera os arquivos Markdown por artigo (planilha vira índice com referências) ===
        import unicodedata
        def _slug(kw):
            s = unicodedata.normalize('NFKD', str(kw)).encode('ascii', 'ignore').decode()
            return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:60] or 'sem-kw'
        hora = re.sub(r'\D', '', str(row.get('Horário', ''))).zfill(2)
        base_nome = f"art-{int(row['Dia']):03d}-{hora}h-{_slug(keyword)}"

        # 1) BRIEFING SERP — dados da pesquisa no formato do prompt de auditoria
        serp_md = [f"# Briefing SERP — {keyword}", ""]
        serp_md.append(f"**Consulta:** {datetime.now().strftime('%Y-%m-%d')} | Google Brasil (gl=br, hl=pt) | via SerpAPI")
        serp_md.append(f"**Palavra-chave:** {keyword} | **Tema:** {row['Tema']} | **Volume (planilha):** {row['Volume (dado)']} | **Concorrência Ads (planilha):** {row['Concorrência']}")
        if row.get('Variações (sinônimos)'):
            serp_md.append(f"**Variações:** {row['Variações (sinônimos)']}")
        serp_md += ["", "## CONCORRENTES (Top 5 orgânico)", "posição | título | URL direta | tipo | palavras aproximadas | H2 principais | lida de verdade?", "---|---|---|---|---|---|---"]
        for i, item in enumerate(organicos):
            analise = analises[i]
            serp_md.append(f"{i+1} | {analise['titulo']} | {analise['url']} | {analise['tipo']} | ~{analise['palavras']} | {analise['h2s']} | {'sim' if analise['tipo'] != 'erro' else 'não verifiquei'}")
        serp_md += ["", "## PERGUNTAS DO GOOGLE (PAA)"] + ([f"- {p}" for p in paa] or ["(nenhuma retornada)"])
        serp_md += ["", "## PESQUISAS RELACIONADAS"] + ([f"- {r}" for r in relacionadas] or ["(nenhuma retornada)"])
        serp_md += ["", "## LONG TAILS VISTAS (termo | fonte | na planilha? volume desconhecido)"] + [f"- {lt['termo']} | {lt['fonte']} | volume desconhecido" for lt in long_tails[:30]]
        serp_md += ["", "## LACUNAS (o que o topo não respondeu bem)"] + ([f"- {l}" for l in lacunas] or ["(nenhuma identificada)"])
        serp_md += ["", f"## DIFICULDADE REAL: {dificuldade} (autoridades no top 5: {len(autoridades) if autoridades else sum(1 for it in organicos if any(a in it.get('link','') for a in ['gov.br','wikipedia.org','nih.gov','who.int','hospital','clinica']))})"]
        serp_md += ["", "## FONTES OFICIAIS CANDIDATAS (até 5)"] + ([f"- {u} | aberta de verdade? sim" for u in fontes] or ["(nenhuma)"])
        serp_md += ["", "## AUTORIDADES NO TOP 5"] + ([f"- {a}" for a in autoridades] or ["(nenhuma)"])
        serp_md += ["", "## DIVERGÊNCIAS COM A PLANILHA", divergencias if divergencias else "(nenhuma detectada automaticamente)"]
        caminho_serp = os.path.join(SAIDA_MD_DIR, f"{base_nome}.serp.md")
        with open(caminho_serp, 'w', encoding='utf-8') as f:
            f.write("\n".join(serp_md))

        # 2) PROMPT PRONTO PARA O GEMINI (briefing + Prompt Mestre embutidos num único .md)
        prompt_md = "# Prompt para Gemini — gerar artigo\n\n" + df.at[idx, 'GEMINI_Prompt_Pronto']
        caminho_prompt = os.path.join(SAIDA_MD_DIR, f"{base_nome}.prompt.md")
        with open(caminho_prompt, 'w', encoding='utf-8') as f:
            f.write(prompt_md)

        # 3) Atualiza as colunas de referência do índice
        df.at[idx, 'SERP_Arquivo_MD'] = caminho_serp
        df.at[idx, 'GEMINI_Prompt_Arquivo'] = caminho_prompt
        # Link curto e limpo para uso via API/copy-paste (referência ao arquivo, não o texto inteiro)
        df.at[idx, 'GEMINI_Prompt_Pronto'] = caminho_prompt
        
        # Salva progresso a cada linha
        df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
        print(f"💾 Salvo progresso após {keyword}")
    
    if processados == 0:
        # Sem isso a execução termina "verde" mesmo com a API recusando todas as buscas
        print(f"❌ Nenhum dos {len(fila)} artigos foi pesquisado. Verifique a chave do SerpAPI (HTTP 401 = inválida; 429 = limite de buscas do plano).")
        sys.exit(1)

    print(f"✅ Concluído! {processados} de {len(fila)} artigos processados.")

if __name__ == "__main__":
    main()
