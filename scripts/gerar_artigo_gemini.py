#!/usr/bin/env python3
"""
Gera artigos HTML com a API do Gemini a partir dos prompts criados pela pesquisa SERP.

Pega linhas do calendário com Status = SERP_OK e sem artigo ainda, envia o prompt
(GEMINI_Prompt_Arquivo) ao Gemini, salva o HTML em dados/saida/html/ e marca a linha
como GERADO. A home publica o artigo sozinha, porque ela lista os HTMLs que existem.

Variáveis de ambiente:
    GEMINI_API_KEY   chave da API do Gemini (obrigatória)
    GEMINI_MODEL     modelo (padrão: gemini-3.8-flash)
    MAX_ARTIGOS      quantos artigos gerar nesta execução (padrão: 1)
"""

import csv
import os
import random
import re
import sys
import time

import requests

CSV_PATH = os.path.join('dados', 'calendario_blog_1_ano.csv')
HTML_DIR = os.path.join('dados', 'saida', 'html')
MODELO = os.environ.get('GEMINI_MODEL', 'gemini-3.8-flash')
MAX_ARTIGOS = int(os.environ.get('MAX_ARTIGOS', '1') or 1)
API = 'https://generativelanguage.googleapis.com/v1beta'


def modelo_disponivel(chave):
    """Escolhe um modelo flash disponível para a chave (o Google aposenta modelos com o tempo)."""
    r = requests.get(f'{API}/models', headers={'x-goog-api-key': chave}, params={'pageSize': 100}, timeout=60)
    r.raise_for_status()
    candidatos = [
        m['name'].split('/')[-1] for m in r.json().get('models', [])
        if 'generateContent' in m.get('supportedGenerationMethods', [])
        and 'flash' in m['name'] and 'lite' not in m['name']
    ]
    # Nomes mais altos (versão mais nova) primeiro
    return sorted(candidatos, reverse=True)[0] if candidatos else None


def com_tentativas(prompt, chave, modelo, maximo=5):
    """Repete quando o Gemini está sobrecarregado (503) ou com limite de uso (429).
    Espera cada vez mais (2, 4, 8, 16... segundos) com uma pausa aleatória, para não insistir no mesmo instante."""
    for tentativa in range(1, maximo + 1):
        try:
            return gerar(prompt, chave, modelo)
        except RuntimeError as e:
            temporario = 'HTTP 503' in str(e) or 'HTTP 429' in str(e)
            if not temporario or tentativa == maximo:
                raise
            espera = min(2 ** tentativa, 64) + random.uniform(0, 2)
            print(f'⏳ Modelo ocupado (tentativa {tentativa}/{maximo}). Nova tentativa em {espera:.0f}s...')
            time.sleep(espera)


def gerar(prompt, chave, modelo):
    r = requests.post(
        f'{API}/models/{modelo}:generateContent',
        headers={'x-goog-api-key': chave, 'Content-Type': 'application/json'},
        json={'contents': [{'parts': [{'text': prompt}]}]},
        timeout=180,
    )
    if r.status_code != 200:
        raise RuntimeError(f'HTTP {r.status_code}: {r.text[:200]}')
    data = r.json()
    partes = data.get('candidates', [{}])[0].get('content', {}).get('parts', [])
    texto = ''.join(p.get('text', '') for p in partes).strip()
    # Remove cercas de código (```html ... ```) se o modelo as incluir
    texto = re.sub(r'^```(?:html)?\s*|\s*```$', '', texto, flags=re.IGNORECASE).strip()
    if not texto:
        raise RuntimeError('resposta vazia do Gemini')
    return texto


def main():
    chave = os.environ.get('GEMINI_API_KEY')
    if not chave:
        print('❌ GEMINI_API_KEY não configurada. Abortando.')
        return 1

    with open(CSV_PATH, encoding='utf-8-sig', newline='') as f:
        leitor = csv.DictReader(f)
        colunas = leitor.fieldnames
        linhas = list(leitor)

    candidatas = [
        l for l in linhas
        if l.get('Status', '').strip() == 'SERP_OK'
        and not l.get('Artigo_Arquivo_HTML', '').strip()
        and os.path.isfile(l.get('GEMINI_Prompt_Arquivo', '').strip())
    ][:MAX_ARTIGOS]

    if not candidatas:
        print('✅ Nenhum prompt pendente para gerar.')
        return 0

    geradas, falhas = 0, 0
    modelo = MODELO
    for linha in candidatas:
        prompt_path = linha['GEMINI_Prompt_Arquivo'].strip()
        base = os.path.basename(prompt_path).replace('.prompt.md', '')
        nome_html = f'{base}.html'
        print(f'🤖 Gerando {nome_html} ({modelo})...')
        try:
            with open(prompt_path, encoding='utf-8') as f:
                prompt = f.read()
            try:
                html = com_tentativas(prompt, chave, modelo)
            except RuntimeError as e:
                # 404 = modelo aposentado: troca pelo flash mais novo disponível e tenta de novo
                if 'HTTP 404' not in str(e):
                    raise
                novo = modelo_disponivel(chave)
                if not novo or novo == modelo:
                    raise
                print(f'↪️ {modelo} indisponível; usando {novo}')
                modelo = novo
                html = com_tentativas(prompt, chave, modelo)
        except (requests.RequestException, RuntimeError) as e:
            print(f'⚠️ Falha em {base}: {e}')
            falhas += 1
            continue

        os.makedirs(HTML_DIR, exist_ok=True)
        with open(os.path.join(HTML_DIR, nome_html), 'w', encoding='utf-8') as f:
            f.write(html)
        linha['Artigo_Arquivo_HTML'] = nome_html
        linha['Status'] = 'GERADO'
        geradas += 1
        print(f'✅ {nome_html} salvo')

    with open(CSV_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        # \n (e não \r\n) para não reescrever todas as linhas do arquivo no git
        escritor = csv.DictWriter(f, fieldnames=colunas, lineterminator='\n')
        escritor.writeheader()
        escritor.writerows(linhas)

    print(f'Concluído: {geradas} gerado(s), {falhas} falha(s).')
    return 1 if geradas == 0 else 0


if __name__ == '__main__':
    sys.exit(main())
