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
from collections import Counter

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
# Fora do briefing: vídeo, playlist, rede social, loja e buscadores (não são blog nem site de conteúdo)
FORA_DO_BRIEFING = ['youtube.com', 'youtu.be', 'spotify.com', 'amazon.', 'mercadolivre.', 'shopee.',
                    'magazineluiza.', 'americanas.', 'submarino.', 'instagram.com', 'facebook.com',
                    'tiktok.com', 'twitter.com', 'x.com/', 'linkedin.com', 'pinterest.', 'reddit.com', 'google.']
AUTORIDADE_PADROES = ['gov.br', 'wikipedia', 'nih.gov', 'who.int', 'cdc.gov', 'hospital', 'clinica',
                      'einstein.br', 'sbpt.org.br', 'sbcardiologia.org.br']
OFICIAL_PADROES = ['.gov.br', '.gov/', 'nih.gov', 'who.int', 'cdc.gov', '.edu.br', '.org.br', '.jus.br']
STOP_PALAVRAS = set('de da do das dos e a o os as em no na nos nas para por com um uma uns umas que se ao aos ou '
                    'como mais mas seu sua seus suas é são ser ter pelo pela isso este esta esse essa quando '
                    'sobre entre até muito também já'.split())
JUNK_H2 = ('newsletter', 'leia também', 'leia tambem', 'entrar', 'conteúdos', 'conteudos', 'ver também',
           'ver tambem', 'compartilh', 'comentár', 'comentar', 'inscre', 'cookie', 'menu', 'pesquisar',
           'assine', 'receba', 'siga', 'publicidade', 'anúncio', 'anuncio', 'saiba mais', 'referências',
           'referencias', 'notas', 'bibliografia', 'navegação', 'eba!', 'seu e-mail')

def eh_concorrente(link):
    """True só para blog ou site de conteúdo (sem vídeo, rede social, loja ou buscador)."""
    l = (link or '').lower()
    return bool(l) and not any(d in l for d in FORA_DO_BRIEFING)

def buscar_serpapi(keyword, num=5):
    """Busca no Google via SerpAPI (serpapi.com) e devolve no formato usado pelo script"""
    params = {
        "engine": "google", "q": keyword, "api_key": SERPAPI_KEY,
        "gl": "br", "hl": "pt", "google_domain": "google.com.br", "num": num,
    }
    # Até 2 tentativas: a SerpAPI às vezes demora mais que um timeout curto
    dados = None
    for tentativa in (1, 2):
        try:
            response = requests.get("https://serpapi.com/search.json", params=params, timeout=60)
            if response.status_code != 200:
                # Diagnóstico: 401 = chave inválida; 429 = limite de buscas do plano
                print(f"⚠️ HTTP {response.status_code} na SerpAPI para '{keyword}': {response.text[:150]}")
                return None
            dados = response.json()
            break
        except requests.Timeout as e:
            print(f"⏱️ Timeout na SerpAPI para '{keyword}' (tentativa {tentativa}): {e}")
        except Exception as e:
            print(f"Erro na API para {keyword}: {e}")
            return None
    if dados is None:
        return None
    # Converte para a estrutura que o restante do script já usa
    return {
        'organic': [{'title': o.get('title', ''), 'link': o.get('link', '')} for o in dados.get('organic_results', [])],
        'peopleAlsoAsk': [{'question': q.get('question', '')} for q in dados.get('related_questions', [])],
        'relatedSearches': [{'query': r.get('query', '')} for r in dados.get('related_searches', [])],
    }

def tipo_pagina(url):
    u = url.lower()
    if any(x in u for x in ['gov.br', '.gov/', 'who.int', 'nih.gov', 'cdc.gov']):
        return 'portal oficial'
    if 'wikipedia' in u:
        return 'enciclopédia'
    if any(x in u for x in ['hospital', 'clinica', 'hc.', 'hosp']):
        return 'hospital'
    if any(x in u for x in ['uol', 'g1.', 'folha', 'estadao', 'itatiaia', 'cnn']):
        return 'portal de notícias'
    if any(x in u for x in ['minhavida', 'tuasaude', 'drashirley', 'drauziovarella']):
        return 'portal de saúde'
    return 'blog'

def h2_util(t):
    t = t.strip()
    return len(t) >= 12 and not any(j in t.lower() for j in JUNK_H2)

def analisar_pagina(url):
    """Abre a página e lê o conteúdo principal. 'lida' só é verdadeiro com texto de verdade."""
    base = {'url': url, 'titulo': '', 'tipo': tipo_pagina(url), 'palavras': 0, 'h2s': [],
            'lida': False, 'texto': '', 'erro': ''}
    try:
        r = requests.get(url, headers=UA, timeout=12)
    except requests.RequestException as e:
        base['erro'] = type(e).__name__
        return base
    if r.status_code != 200:
        base['erro'] = f'HTTP {r.status_code}'
        return base
    soup = BeautifulSoup(r.text, 'html.parser')
    base['titulo'] = soup.title.get_text(' ').strip() if soup.title else ''
    for t in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'noscript', 'svg']):
        t.decompose()
    alvo = soup.find('article') or soup.find('main') or soup.body or soup
    texto = ' '.join(alvo.get_text(' ').split())
    palavras = len(texto.split())
    h2s = [h.get_text(' ').strip() for h in alvo.find_all('h2')]
    base.update({'palavras': palavras, 'h2s': [h for h in h2s if h2_util(h)][:8], 'texto': texto,
                 'lida': palavras >= 150})
    if not base['lida']:
        base['erro'] = 'pouco texto (possível bloqueio ou página sem artigo)'
    return base

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

def tokens_uteis(s):
    return {w for w in re.findall(r'[a-zà-ú0-9]+', s.lower()) if w not in STOP_PALAVRAS and len(w) >= 3}

def identificar_lacunas(paa, h2s_geral):
    """Pergunta do Google é lacuna se nenhum H2 dos concorrentes lidos cobre pelo menos 60% das suas palavras"""
    h2_tokens = [tokens_uteis(h) for h in h2s_geral]
    lacunas = []
    for pergunta in paa:
        pt = tokens_uteis(pergunta)
        if not pt:
            continue
        if not any(len(pt & h) / len(pt) >= 0.6 for h in h2_tokens):
            lacunas.append(pergunta)
    return lacunas[:6]

def termos_do_tema(keyword, variacoes):
    """Palavras do tema: da palavra-chave e das variações da planilha (sem palavras vazias)"""
    partes = [keyword] + re.split(r'[;,]', variacoes or '')
    return {w for p in partes for w in re.findall(r'[a-zà-ú0-9]+', str(p).lower())
            if len(w) >= 4 and w not in STOP_PALAVRAS}

def extrair_long_tails(lidas, keyword, variacoes, minimo=2, limite=20):
    """Expressões de 3 a 5 palavras que: contêm o tema, não começam nem terminam com palavra vazia,
    e aparecem em pelo menos `minimo` páginas lidas. Ordenadas por nº de páginas."""
    tema = termos_do_tema(keyword, variacoes)
    cont = Counter()
    for p in lidas:
        palavras = re.findall(r'[a-zà-ú0-9]+', p['texto'].lower())
        vistos = set()
        for k in (3, 4, 5):
            for i in range(len(palavras) - k + 1):
                g = palavras[i:i + k]
                if g[0] in STOP_PALAVRAS or g[-1] in STOP_PALAVRAS:
                    continue
                if not tema.intersection(g):
                    continue
                vistos.add(' '.join(g))
        cont.update(vistos)
    out = [(t, n) for t, n in cont.items() if n >= minimo]
    out.sort(key=lambda x: (-x[1], -len(x[0].split()), x[0]))
    return out[:limite]

def primeira_frase_com_tema(texto, keyword):
    tema = termos_do_tema(keyword, '')
    for frase in re.split(r'(?<=[.!?])\s+', texto):
        if 40 <= len(frase) <= 220 and tema.intersection(re.findall(r'[a-zà-ú0-9]+', frase.lower())):
            return frase.strip()
    return ''

def fontes_oficiais(lidas, keyword):
    """Só páginas oficiais que foram abertas nesta consulta, com uma frase real da página"""
    out = []
    for p in lidas:
        if any(x in p['url'].lower() for x in OFICIAL_PADROES):
            out.append({'url': p['url'], 'frase': primeira_frase_com_tema(p['texto'], keyword)})
    return out[:5]

def calcular_divergencias(row, dificuldade, lidas, organicos):
    out = []
    ads = str(row.get('Concorrência', '')).strip().lower()
    esperada = {'baixo': 'fácil', 'low': 'fácil', 'médio': 'média', 'medio': 'média', 'medium': 'média',
                'alto': 'difícil', 'high': 'difícil'}.get(ads, '')
    if esperada and esperada != dificuldade.lower():
        out.append(f"Planilha diz concorrência Ads '{row.get('Concorrência')}' mas o top 5 indica dificuldade '{dificuldade.lower()}'.")
    if len(lidas) < len(organicos):
        out.append(f"Só {len(lidas)} de {len(organicos)} páginas puderam ser lidas nesta consulta.")
    return out

CAMINHO_PROMPT_MESTRE = os.path.join('prompts', 'prompt_mestre_gemini_v4.txt')

def ler_prompt_mestre():
    """Regras de escrita vêm do arquivo do prompt mestre (fonte única, não do código)."""
    with open(CAMINHO_PROMPT_MESTRE, encoding='utf-8') as f:
        return f.read().strip()

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
Agora gere o artigo seguindo o Prompt Mestre abaixo:

{ler_prompt_mestre()}
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
        
        organicos = [o for o in dados.get('organic', []) if eh_concorrente(o.get('link', ''))][:5]
        paa = [p['question'] for p in dados.get('peopleAlsoAsk', [])]
        relacionadas = [r['query'] for r in dados.get('relatedSearches', [])]

        # Lê cada concorrente de verdade. Só 'lida' conta quando há texto de artigo.
        analises = []
        for item in organicos:
            analises.append(analisar_pagina(item['link']))
            time.sleep(0.5)  # Respeitar rate limit
        lidas = [a for a in analises if a['lida']]
        todos_h2s = [h for a in lidas for h in a['h2s']]

        variacoes = str(row.get('Variações (sinônimos)', '') or '')
        variacoes = '' if variacoes.strip().lower() == 'nan' else variacoes
        long_tails = extrair_long_tails(lidas, keyword, variacoes)
        lacunas = identificar_lacunas(paa, todos_h2s)
        dificuldade = classificar_dificuldade(organicos)
        fontes = fontes_oficiais(lidas, keyword)
        autoridades = sorted({o['link'].split('/')[2] for o in organicos
                              if any(x in o['link'] for x in AUTORIDADE_PADROES)})[:5]
        divergencias = calcular_divergencias(row, dificuldade, lidas, organicos)
        h2s_unicos = list(dict.fromkeys(todos_h2s))

        df.at[idx, 'Status'] = 'SERP_OK'
        processados += 1
        df.at[idx, 'SERP_Data_Consulta'] = datetime.now().strftime('%Y-%m-%d')
        df.at[idx, 'SERP_Dificuldade_Real'] = dificuldade
        df.at[idx, 'SERP_Top5_URLs_e_Tipos'] = " | ".join([f"{a['titulo']} | {a['url']}" for a in analises])
        df.at[idx, 'SERP_H2s_Comuns'] = "; ".join(h2s_unicos[:10])
        df.at[idx, 'SERP_PAA'] = "; ".join(paa)
        df.at[idx, 'SERP_Pesquisas_Relacionadas'] = "; ".join(relacionadas)
        df.at[idx, 'SERP_Long_Tails_Vistas'] = "; ".join([f"{t} ({n} de {len(lidas)} páginas)" for t, n in long_tails])
        df.at[idx, 'SERP_Lacunas_Identificadas'] = "; ".join(lacunas)
        df.at[idx, 'SERP_Fontes_Oficiais_Candidatas'] = "; ".join(f['url'] for f in fontes)
        df.at[idx, 'SERP_Autoridades_Top5'] = "; ".join(autoridades)
        df.at[idx, 'SERP_Divergencias_Com_Planilha'] = " ".join(divergencias)

        concorrentes_str = [f"{i+1}. {a['titulo']} | {a['url']} | {a['tipo']} | ~{a['palavras']} palavras | H2s: {'; '.join(a['h2s'])}"
                            for i, a in enumerate(analises)]
        dados_serp_dict = {
            'dificuldade': dificuldade,
            'fontes': [f['url'] for f in fontes],
            'lacunas': lacunas,
            'autoridades': autoridades,
            'divergencias': ' '.join(divergencias),
            'concorrentes_formatado': "\n".join(concorrentes_str),
            'paa_formatado': "\n".join([f"- {p}" for p in paa]),
            'relacionadas_formatado': "\n".join([f"- {r}" for r in relacionadas]),
            'longtails_formatado': "\n".join([f"- {t} ({n} de {len(lidas)} páginas)" for t, n in long_tails]),
            'h2s_formatado': "\n".join([f"- {h}" for h in h2s_unicos[:8]]),
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
        serp_md.append(f"**Data da consulta:** {datetime.now().strftime('%Y-%m-%d')} | Google Brasil (gl=br, hl=pt) | SerpAPI + leitura das páginas")
        serp_md.append(f"**Dados da planilha (Keyword Planner):** palavra-chave: {keyword} | tema: {row['Tema']} | volume: {row['Volume (dado)']} | concorrência Ads: {row['Concorrência']}")
        if variacoes:
            serp_md.append(f"**Variações da planilha:** {variacoes}")
        if not lidas:
            serp_md += ["", "**ATENÇÃO: não foi possível abrir nenhuma página concorrente nesta consulta.**"]
        serp_md += ["", "## CONCORRENTES (até 5 resultados orgânicos; sem vídeo, rede social ou loja)",
                    "posição | título | URL direta | tipo | palavras aproximadas | H2 principais | lida de verdade?",
                    "---|---|---|---|---|---|---"]
        for i, a in enumerate(analises):
            situacao = 'sim' if a['lida'] else f"não verifiquei ({a['erro']})"
            serp_md.append(f"{i+1} | {a['titulo'] or '(sem título)'} | {a['url']} | {a['tipo']} | ~{a['palavras']} | {'; '.join(a['h2s']) or '(nenhum H2 útil)'} | {situacao}")
        if not analises:
            serp_md.append("(nenhum concorrente de blog ou site encontrado)")
        serp_md += ["", "## PERGUNTAS DO GOOGLE (As pessoas também perguntam)"] + ([f"- {p}" for p in paa] or ["(nenhuma retornada)"])
        serp_md += ["", "## PESQUISAS RELACIONADAS"] + ([f"- {r}" for r in relacionadas] or ["(nenhuma retornada)"])
        serp_md += ["", "## LONG TAILS VISTAS NAS PÁGINAS LIDAS (termo | em quantas páginas aparece | na planilha?)"] + (
            [f"- {t} | {n} de {len(lidas)} | volume desconhecido" for t, n in long_tails]
            or ["(nenhum termo de 3+ palavras apareceu em 2 ou mais páginas lidas)"])
        serp_md += ["", "## LACUNAS (perguntas do Google que nenhum concorrente lido responde)"] + ([f"- {l}" for l in lacunas] or ["(nenhuma)"])
        serp_md += ["", f"## DIFICULDADE: {dificuldade.lower()} (autoridades no top 5: {len(autoridades)})"]
        serp_md += ["", "## DIVERGÊNCIAS COM A PLANILHA"] + ([f"- {d}" for d in divergencias] or ["(nenhuma)"])
        serp_md += ["", "## FONTES OFICIAIS CANDIDATAS (abertas nesta consulta)"] + (
            [f"- {f['url']} | aberta de verdade? sim | {f['frase'] or '(sem frase com o tema)'}" for f in fontes]
            or ["(nenhuma fonte oficial aberta nesta consulta)"])
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
