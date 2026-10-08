#!/usr/bin/env python3
"""
Gera artigos HTML com uma IA a partir dos prompts criados pela pesquisa SERP.

Pega linhas do calendário com Status = SERP_OK e sem artigo ainda, envia o prompt
(GEMINI_Prompt_Arquivo) à IA, salva o HTML em dados/saida/html/ e marca a linha
como GERADO. A home publica o artigo sozinha, porque ela lista os HTMLs que existem.

Variáveis de ambiente:
    LLM_PROVIDER     'gemini' (padrão) ou 'cerebras'
    GEMINI_API_KEY   chave do Gemini (quando LLM_PROVIDER=gemini)
    GEMINI_MODEL     modelo do Gemini (padrão: gemini-3.8-flash)
    CEREBRAS_API_KEY chave da Cerebras (quando LLM_PROVIDER=cerebras)
    CEREBRAS_MODEL   modelo da Cerebras (padrão: qwen-3-235b-a22b-instruct-2507)
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
PROVEDOR = os.environ.get('LLM_PROVIDER', 'gemini')
MODELO_GEMINI = os.environ.get('GEMINI_MODEL', 'gemini-3.8-flash')
MODELO_CEREBRAS = os.environ.get('CEREBRAS_MODEL', 'qwen-3-235b-a22b-instruct-2507')
MAX_ARTIGOS = int(os.environ.get('MAX_ARTIGOS', '1') or 1)
API_GEMINI = 'https://generativelanguage.googleapis.com/v1beta'
URL_CEREBRAS = 'https://api.cerebras.ai/v1/chat/completions'


def limpar(texto):
    """Remove cercas de código (```html ... ```) se o modelo as incluir."""
    texto = re.sub(r'^```(?:html)?\s*|\s*```$', '', texto.strip(), flags=re.IGNORECASE).strip()
    if not texto:
        raise RuntimeError('resposta vazia da IA')
    return texto


def modelo_disponivel(chave):
    """Escolhe um modelo flash disponível para a chave do Gemini (o Google aposenta modelos com o tempo)."""
    r = requests.get(f'{API_GEMINI}/models', headers={'x-goog-api-key': chave}, params={'pageSize': 100}, timeout=60)
    r.raise_for_status()
    candidatos = [
        m['name'].split('/')[-1] for m in r.json().get('models', [])
        if 'generateContent' in m.get('supportedGenerationMethods', [])
        and 'flash' in m['name'] and 'lite' not in m['name']
    ]
    # Nomes mais altos (versão mais nova) primeiro
    return sorted(candidatos, reverse=True)[0] if candidatos else None


def modelo_alternativo(chave, atual):
    """Outro modelo flash do Gemini (inclusive 'lite', com menos demanda) para quando o principal está ocupado."""
    r = requests.get(f'{API_GEMINI}/models', headers={'x-goog-api-key': chave}, params={'pageSize': 100}, timeout=60)
    r.raise_for_status()
    candidatos = [
        m['name'].split('/')[-1] for m in r.json().get('models', [])
        if 'generateContent' in m.get('supportedGenerationMethods', [])
        and 'flash' in m['name'] and m['name'].split('/')[-1] != atual
    ]
    return sorted(candidatos, reverse=True)[0] if candidatos else None


def eh_temporario(e):
    """Erros que passam sozinhos: sobrecarga (503), limite de uso (429) e conexão/tempo esgotado."""
    return isinstance(e, requests.RequestException) or 'HTTP 503' in str(e) or 'HTTP 429' in str(e)


def com_tentativas(prompt, chave, modelo, maximo=5):
    """Repete quando a IA está ocupada, esperando cada vez mais (2, 4, 8, 16... segundos)
    com uma pausa aleatória, para não insistir no mesmo instante."""
    for tentativa in range(1, maximo + 1):
        try:
            return chamar(prompt, chave, modelo)
        except (RuntimeError, requests.RequestException) as e:
            if not eh_temporario(e) or tentativa == maximo:
                raise
            espera = min(2 ** tentativa, 64) + random.uniform(0, 2)
            print(f'⏳ Modelo ocupado (tentativa {tentativa}/{maximo}). Nova tentativa em {espera:.0f}s...')
            time.sleep(espera)


def chamar(prompt, chave, modelo):
    if PROVEDOR == 'cerebras':
        return gerar_cerebras(prompt, chave, modelo)
    return gerar_gemini(prompt, chave, modelo)


def gerar_gemini(prompt, chave, modelo):
    r = requests.post(
        f'{API_GEMINI}/models/{modelo}:generateContent',
        headers={'x-goog-api-key': chave, 'Content-Type': 'application/json'},
        json={'contents': [{'parts': [{'text': prompt}]}]},
        timeout=120,
    )
    if r.status_code != 200:
        raise RuntimeError(f'HTTP {r.status_code}: {r.text[:200]}')
    data = r.json()
    partes = data.get('candidates', [{}])[0].get('content', {}).get('parts', [])
    return limpar(''.join(p.get('text', '') for p in partes))


def gerar_cerebras(prompt, chave, modelo):
    r = requests.post(
        URL_CEREBRAS,
        headers={'Authorization': f'Bearer {chave}', 'Content-Type': 'application/json'},
        json={'model': modelo, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 8000},
        timeout=120,
    )
    if r.status_code != 200:
        raise RuntimeError(f'HTTP {r.status_code}: {r.text[:200]}')
    return limpar(r.json()['choices'][0]['message']['content'])


def main():
    nome_chave = 'CEREBRAS_API_KEY' if PROVEDOR == 'cerebras' else 'GEMINI_API_KEY'
    chave = os.environ.get(nome_chave)
    if not chave:
        print(f'❌ {nome_chave} não configurada. Abortando.')
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
    modelo = MODELO_CEREBRAS if PROVEDOR == 'cerebras' else MODELO_GEMINI
    for linha in candidatas:
        prompt_path = linha['GEMINI_Prompt_Arquivo'].strip()
        base = os.path.basename(prompt_path).replace('.prompt.md', '')
        nome_html = f'{base}.html'
        print(f'🤖 Gerando {nome_html} ({PROVEDOR}: {modelo})...')
        try:
            with open(prompt_path, encoding='utf-8') as f:
                prompt = f.read()
            try:
                html = com_tentativas(prompt, chave, modelo)
            except (RuntimeError, requests.RequestException) as e:
                # Só o Gemini tem modelos de reserva
                if PROVEDOR == 'gemini' and 'HTTP 404' in str(e):
                    novo = modelo_disponivel(chave)
                elif PROVEDOR == 'gemini' and eh_temporario(e):
                    novo = modelo_alternativo(chave, modelo)
                else:
                    raise
                if not novo or novo == modelo:
                    raise
                print(f'↪️ {modelo} indisponível agora; tentando {novo}')
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
