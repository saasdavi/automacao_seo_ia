#!/usr/bin/env python3
"""
Baixa fotos realistas da Pexels por tema e grava em public/miniaturas/.

Gera dados/miniaturas.json com o pool de fotos de cada tema. A home escolhe
uma foto por card a partir desse pool, sem repetir na mesma página.

Uso (no GitHub Actions ou local):
    PEXELS_API_KEY=... python scripts/baixar_miniaturas.py
"""

import json
import os
import re
import sys
import unicodedata

import requests

API = 'https://api.pexels.com/v1/search'
SAIDA_DIR = os.path.join('public', 'miniaturas')
MANIFESTO = os.path.join('dados', 'miniaturas.json')
POR_TEMA = 12

# Consulta em inglês por tema (a Pexels responde melhor em inglês)
CONSULTAS = {
    'Estresse': 'stressed person working',
    'Sono': 'peaceful sleep bedroom',
    'Insônia / Sono': 'sleep insomnia bedroom night',
    'Ansiedade': 'anxious person thinking',
    'Meditação': 'meditation calm person',
    'Memória': 'brain memory thinking',
    'Bem-estar': 'wellbeing relaxation nature',
    'Mindfulness': 'mindfulness calm breathing',
    'Autoestima': 'confident woman smiling',
    'Autoconhecimento': 'self reflection journaling',
    'Autocuidado': 'self care relaxing bath',
    'Foco e concentração': 'focus concentration study',
    'Inteligência emocional': 'emotional intelligence friends talking',
    'Pânico': 'calm breathing outdoors',
    'Qualidade de vida': 'healthy lifestyle walking outdoors',
    'Relaxamento': 'relaxation yoga beach',
    'Solidão': 'lonely person window',
}
CONSULTA_PADRAO = 'calm mental health'


def slug(texto):
    s = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-') or 'tema'


def temas_do_calendario():
    import csv
    with open(os.path.join('dados', 'calendario_blog_1_ano.csv'), encoding='utf-8-sig') as f:
        return sorted({row['Tema'].strip() for row in csv.DictReader(f) if row.get('Tema')})


def buscar(chave, consulta):
    r = requests.get(
        API,
        params={'query': consulta, 'per_page': POR_TEMA, 'orientation': 'landscape'},
        headers={'Authorization': chave},
        timeout=20,
    )
    r.raise_for_status()
    return r.json().get('photos', [])


def main():
    chave = os.environ.get('PEXELS_API_KEY')
    if not chave:
        print('PEXELS_API_KEY não configurada. Abortando.')
        return 1

    os.makedirs(SAIDA_DIR, exist_ok=True)
    manifesto = {}
    vistos = set()
    temas = temas_do_calendario()

    for tema in temas:
        consulta = CONSULTAS.get(tema, CONSULTA_PADRAO)
        try:
            fotos = buscar(chave, consulta)
        except requests.RequestException as e:
            print(f'Falha em "{tema}" ({consulta}): {e}')
            continue

        pool = []
        for foto in fotos:
            # Mesma foto não entra em dois temas (evita repetir na mesma página)
            if foto['id'] in vistos:
                continue
            vistos.add(foto['id'])
            nome = f"{slug(tema)}-{foto['id']}.jpg"
            caminho = os.path.join(SAIDA_DIR, nome)
            if not os.path.exists(caminho):
                img = requests.get(foto['src']['landscape'], timeout=30)
                img.raise_for_status()
                with open(caminho, 'wb') as f:
                    f.write(img.content)
            pool.append(f'/miniaturas/{nome}')
        manifesto[tema] = pool
        print(f'{tema}: {len(pool)} fotos ({consulta})')

    with open(MANIFESTO, 'w', encoding='utf-8') as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=2)
    print(f'Manifesto salvo: {MANIFESTO} ({len(manifesto)} temas)')
    return 0 if manifesto else 1


if __name__ == '__main__':
    sys.exit(main())
