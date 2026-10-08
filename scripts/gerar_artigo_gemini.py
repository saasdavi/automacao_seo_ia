#!/usr/bin/env python3
"""
Gera artigos HTML com uma IA a partir dos prompts criados pela pesquisa SERP.

Pega linhas do calendário com Status = SERP_OK e sem artigo ainda, envia o prompt
(GEMINI_Prompt_Arquivo) à IA, salva o HTML em dados/saida/html/ e marca a linha
como GERADO. A home publica o artigo sozinha, porque ela lista os HTMLs que existem.

O que a IA escreve depois do </html> (análise interna, checklist, nota) não vai
para o artigo: é salvo em dados/saida/md/<base>.analise.md, que o site não publica.

Variáveis de ambiente:
    LLM_PROVIDER      'openrouter' (padrão), 'gemini' ou 'cerebras'
    GEMINI_API_KEY    chave do Gemini (quando LLM_PROVIDER=gemini)
    GEMINI_MODEL      modelo do Gemini (padrão: gemini-3.8-flash)
    CEREBRAS_API_KEY  chave da Cerebras (quando LLM_PROVIDER=cerebras)
    CEREBRAS_MODEL    modelo da Cerebras (padrão: qwen-3-235b-a22b-instruct-2507)
    OPENROUTER_API_KEY chave do OpenRouter (quando LLM_PROVIDER=openrouter)
    OPENROUTER_MODELS modelos em ordem de preferência, separados por vírgula
                      (padrão: nemotron 3 super e gemma 4 31b, ambos gratuitos)
    MAX_ARTIGOS       quantos artigos gerar nesta execução (padrão: 1)
"""

import csv
import datetime
import html as html_lib
import os
import random
import re
import sys
import time

import requests

CSV_PATH = os.path.join('dados', 'calendario_blog_1_ano.csv')
HTML_DIR = os.path.join('dados', 'saida', 'html')
ANALISE_DIR = os.path.join('dados', 'saida', 'md')
PROVEDOR = os.environ.get('LLM_PROVIDER', 'openrouter')
MODELO_GEMINI = os.environ.get('GEMINI_MODEL', 'gemini-3.8-flash')
MODELO_CEREBRAS = os.environ.get('CEREBRAS_MODEL', 'qwen-3-235b-a22b-instruct-2507')
RODADAS_REESCRITA = int(os.environ.get('RODADAS_REESCRITA') or 2)  # reescritas por modelo após reprovação
MODELOS_OPENROUTER = [
    m.strip() for m in os.environ.get(
        'OPENROUTER_MODELS',
        'apodex/apodex-1.1-mini:free,nvidia/nemotron-3-super-120b-a12b:free,nvidia/nemotron-3.5-lightning:free,thinkingmachines/inkling-small:free,dots-studio/dots-3-note-preview:free,poolside/laguna-s-2.1:free,poolside/laguna-xs-2.1:free,cohere/north-mini-code:free,liquid/lfm-2.5-2.6b:free,google/gemma-4-31b-it:free',
    ).split(',') if m.strip()
]
MAX_ARTIGOS = int(os.environ.get('MAX_ARTIGOS', '1') or 1)
API_GEMINI = 'https://generativelanguage.googleapis.com/v1beta'
URL_CEREBRAS = 'https://api.cerebras.ai/v1/chat/completions'
URL_OPENROUTER = 'https://openrouter.ai/api/v1/chat/completions'
URL_PEXELS = 'https://api.pexels.com/v1/search'


def limpar(texto):
    """Remove cercas de código (```html ... ```) se o modelo as incluir."""
    texto = re.sub(r'^```(?:html)?\s*|\s*```$', '', texto.strip(), flags=re.IGNORECASE).strip()
    if not texto:
        raise RuntimeError('resposta vazia da IA')
    return texto


def data_brasilia():
    """Data e hora atuais em Brasília (UTC-3), para datePublished do artigo."""
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(timespec='seconds')


PADRAO_IMG_PEXELS = re.compile(r'<img\b[^>]*\bdata-pexels="([^"]+)"[^>]*>', re.I)


def buscar_foto_pexels(termo, chave_pexels, usadas):
    """Foto da Pexels para o termo, sem repetir foto já usada no artigo."""
    r = requests.get(
        URL_PEXELS,
        headers={'Authorization': chave_pexels},
        params={'query': termo, 'per_page': 10, 'orientation': 'landscape'},
        timeout=30,
    )
    if r.status_code != 200:
        raise RuntimeError(f'Pexels HTTP {r.status_code}')
    for foto in r.json().get('photos', []):
        if foto['id'] not in usadas:
            return foto
    return None


def inserir_imagens_pexels(html, chave_pexels):
    """Troca cada <img data-pexels> pela foto real, com alt do SEO e crédito do fotógrafo.

    A chave fica só no servidor: o HTML publicado não contém chave nem script.
    Sem foto para o termo, a imagem é removida (o artigo continua válido).
    """
    usadas = set()

    def trocar(m):
        tag = m.group(0)
        alt_m = re.search(r'\balt="([^"]*)"', tag)
        alt = html_lib.escape(alt_m.group(1) if alt_m else '', quote=True)
        foto = buscar_foto_pexels(m.group(1), chave_pexels, usadas)
        if not foto:
            return ''
        usadas.add(foto['id'])
        return (
            f'<figure><img src="{foto["src"]["large"]}" alt="{alt}" '
            f'width="{foto["width"]}" height="{foto["height"]}" loading="lazy">'
            f'<figcaption>Foto por <a href="{foto["photographer_url"]}" target="_blank" rel="noopener">'
            f'{html_lib.escape(foto["photographer"])}</a> no '
            f'<a href="{foto["url"]}" target="_blank" rel="noopener">Pexels</a></figcaption></figure>'
        )

    return PADRAO_IMG_PEXELS.sub(trocar, html)


def validar_imagens(html):
    """Regras de SEO e acessibilidade para as imagens. Lista vazia = aprovado."""
    problemas = []
    if 'data-pexels' in html:
        problemas.append('imagem sem foto da Pexels')
    alts = re.findall(r'<img\b[^>]*\balt="([^"]*)"', html, flags=re.I)
    if len(alts) < 1:
        problemas.append('sem imagem no artigo')
    for alt in alts:
        if not 50 <= len(alt) <= 125:
            problemas.append(f'alt com {len(alt)} caracteres (50 a 125)')
        if alt.lower().startswith(('imagem de', 'foto de')):
            problemas.append('alt começa com "imagem de" ou "foto de"')
    if len(set(alts)) != len(alts):
        problemas.append('alt repetido entre imagens')
    return problemas


def validar_artigo(html):
    """Lista o que impede publicar o artigo. Lista vazia = aprovado."""
    problemas = []
    corpo = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', html, flags=re.S | re.I)
    palavras = len(html_lib.unescape(re.sub(r'<[^>]+>', ' ', corpo)).split())
    if palavras < 1400:
        problemas.append(f'{palavras} palavras (mínimo 1.400)')
    if re.search(r'\bCRM\b', html):
        problemas.append('CRM inventado')
    if 'class="assinatura"' in html or "class='assinatura'" in html:
        problemas.append('assinatura com credenciais')
    if 'example.com' in html or 'SUA_CHAVE' in html:
        problemas.append('URL ou chave de exemplo')
    hoje = data_brasilia()[:10]
    m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', html)
    if not m or m.group(1)[:10] != hoje:
        problemas.append(f'datePublished diferente de {hoje}')
    # Regras de SEO e estrutura do prompt
    if len(re.findall(r'<h1[\s>]', html, flags=re.I)) != 1:
        problemas.append('precisa de exatamente 1 H1')
    if not re.search(r'<h2[^>]*>\s*Resumindo\s*</h2>', html, flags=re.I):
        problemas.append('falta a seção "Resumindo"')
    if len(re.findall(r'<a [^>]*href="https?://', html, flags=re.I)) < 6:
        problemas.append('menos de 6 links para fontes')
    paragrafos_longos = sum(
        1 for p_ in re.findall(r'<p[^>]*>(.*?)</p>', corpo, flags=re.S | re.I)
        if len(html_lib.unescape(re.sub(r'<[^>]+>', ' ', p_)).split()) > 50
    )
    if paragrafos_longos > 2:
        problemas.append(f'{paragrafos_longos} parágrafos com mais de 50 palavras')
    return problemas


NOTA_MINIMA = 9.0


def problema_nota(analise):
    """Lê a nota final da análise interna (ex.: 'Nota final: 9,2 / 10'). Sem nota ou abaixo de 9 = reprovado."""
    m = re.search(r'Nota final[^0-9]{0,15}(\d+(?:[.,]\d+)?)', analise or '', flags=re.I)
    if not m:
        return 'sem nota final na análise'
    nota = float(m.group(1).replace(',', '.'))
    if nota < NOTA_MINIMA:
        return f'nota {nota:.1f} (mínimo {NOTA_MINIMA:.1f})'
    return None


def separar_html(texto):
    """Separa o artigo (do <!DOCTYPE até </html>) do que a IA escreveu depois.

    Sem </html>, a resposta está cortada: vira falha, para não publicar HTML incompleto.
    """
    inicio = texto.lower().find('<!doctype')
    if inicio > 0:
        texto = texto[inicio:]
    fim = texto.lower().find('</html>')
    if fim == -1:
        raise RuntimeError('resposta sem </html> (cortada ou fora do formato)')
    fim += len('</html>')
    return texto[:fim] + '\n', texto[fim:].strip()


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
    if isinstance(e, requests.exceptions.InvalidHeader):
        # Cabeçalho inválido (ex.: chave com espaço) não passa sozinho: repetir não adianta
        return False
    return isinstance(e, requests.RequestException) or 'HTTP 503' in str(e) or 'HTTP 429' in str(e)


def com_tentativas(prompt, chave, modelo, maximo=5):
    """Repete quando a IA está ocupada, esperando cada vez mais (2, 4, 8, 16... segundos)
    com uma pausa aleatória, para não insistir no mesmo instante."""
    for tentativa in range(1, maximo + 1):
        try:
            return chamar(prompt, chave, modelo)
        except (RuntimeError, requests.RequestException) as e:
            # 429 = cota do dia esgotada: repetir não resolve, só gasta cota
            if 'HTTP 429' in str(e) or not eh_temporario(e) or tentativa == maximo:
                raise
            espera = min(2 ** tentativa, 64) + random.uniform(0, 2)
            print(f'⏳ Modelo ocupado (tentativa {tentativa}/{maximo}). Nova tentativa em {espera:.0f}s...')
            time.sleep(espera)


def chamar(prompt, chave, modelo):
    if PROVEDOR == 'cerebras':
        return gerar_cerebras(prompt, chave, modelo)
    if PROVEDOR == 'openrouter':
        return gerar_openrouter(prompt, chave, modelo)
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


class LimiteOpenRouter(RuntimeError):
    """429 do OpenRouter: limite de uso temporário. Carrega o tempo de espera sugerido."""

    def __init__(self, mensagem, espera):
        super().__init__(mensagem)
        self.espera = espera


def gerar_openrouter(prompt, chave, modelo):
    r = requests.post(
        URL_OPENROUTER,
        headers={'Authorization': f'Bearer {chave}', 'Content-Type': 'application/json'},
        json={'model': modelo, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 8000},
        timeout=120,
    )
    if r.status_code == 429:
        retry = r.headers.get('Retry-After', '')
        espera = int(retry) if retry.isdigit() else 300
        raise LimiteOpenRouter(f'HTTP 429: {r.text[:200]}', espera)
    if r.status_code != 200:
        raise RuntimeError(f'HTTP {r.status_code}: {r.text[:200]}')
    conteudo = r.json()['choices'][0]['message'].get('content')
    if not conteudo:
        # Modelo gratuito às vezes devolve vazio: vira reprovação e passa ao próximo modelo
        raise RuntimeError('resposta vazia da IA')
    return limpar(conteudo)


def gerar_uma(prompt, chave, modelo):
    """Uma geração com um modelo. Devolve o texto, ou None para passar ao próximo modelo.

    Em limite de uso (429) espera o tempo indicado pelo OpenRouter, no máximo 2 vezes.
    No Gemini, 404 ou ocupado trocam para outro modelo da mesma família, uma vez."""
    esperas = 0
    while True:
        try:
            return com_tentativas(prompt, chave, modelo)
        except LimiteOpenRouter as e:
            if esperas < 2:
                esperas += 1
                espera = min(e.espera, 600)
                print(f'⏳ {modelo} com limite de uso; esperando {espera}s ({esperas}/2)')
                time.sleep(espera)
                continue
            print(f'↪️ {modelo} sem vaga após 2 esperas; tentando o próximo')
            return None
        except (RuntimeError, requests.RequestException) as e:
            if PROVEDOR == 'gemini' and ('HTTP 404' in str(e) or eh_temporario(e)):
                novo = modelo_disponivel(chave) if 'HTTP 404' in str(e) else modelo_alternativo(chave, modelo)
                if novo and novo != modelo:
                    print(f'↪️ {modelo} indisponível agora; tentando {novo}')
                    try:
                        return com_tentativas(prompt, chave, novo)
                    except (RuntimeError, requests.RequestException) as e2:
                        print(f'↪️ {novo} também falhou: {e2}')
                        return None
            # 403/404 = modelo indisponível para esta chave: passa ao próximo. 401 (chave) segue fatal.
            indisponivel = 'HTTP 403' in str(e) or 'HTTP 404' in str(e)
            if not eh_temporario(e) and 'resposta vazia' not in str(e) and not indisponivel:
                raise
            print(f'↪️ {modelo} indisponível agora; tentando o próximo ({e})')
            return None


def montar_reescrita(prompt, html_anterior, problemas, analise_anterior=None):
    """Mensagem de correção: o artigo anterior e a lista exata do que reprovou."""
    palavras = len(re.sub(r'<[^>]+>', ' ', html_anterior or '').split())
    faltam = max(0, 1400 - palavras)
    linhas = [f'- {p}' for p in problemas]
    if any('palavras' in p for p in problemas):
        linhas.append(f'- O artigo tem {palavras} palavras no corpo. Acrescente pelo menos {faltam + 100} palavras de conteúdo útil (não enchimento).')
    return (f"{prompt}\n\n"
            "=================== REESCRITA ===================\n"
            "O artigo abaixo foi reprovado na validação. Corrija SOMENTE os problemas listados e mantenha o que já estava bom.\n"
            "Devolva o documento HTML completo (do <!DOCTYPE html> até </html>) e, depois, a análise de pontuação.\n\n"
            "PROBLEMAS A CORRIGIR:\n" + "\n".join(linhas) + "\n\n"
            + (("ANÁLISE DE PONTUAÇÃO QUE VOCÊ MESMA FEZ (os itens com nota baixa mostram o que corrigir):\n"
                + analise_anterior[:4000] + "\n\n") if analise_anterior else "")
            + "ARTIGO REPROVADO:\n" + (html_anterior or '(sem HTML válido na resposta anterior)'))


def gerar_validado(prompt, chave, modelos, rodadas):
    """Gera, valida e, se reprovar, pede a correção com a lista de problemas.

    Para cada modelo: até `rodadas` reescritas. Só passa ao próximo modelo depois de
    esgotar as reescritas. Devolve (html, análise)."""
    ultimo_erro = None
    for modelo in modelos:
        anterior, problemas, analise_ant = None, None, None
        for n in range(rodadas + 1):
            atual = prompt if n == 0 else montar_reescrita(prompt, anterior, problemas, analise_ant)
            if n:
                print(f'✏️ {modelo}: reescrita {n}/{rodadas} com a lista de problemas')
            texto = gerar_uma(atual, chave, modelo)
            if texto is None:
                break
            try:
                html, analise = separar_html(texto)
            except RuntimeError as e:
                problemas, anterior, analise_ant = [str(e)], texto, None
                print(f'↪️ {modelo} reprovado: {e}')
                ultimo_erro = e
                continue
            chave_pexels = os.environ.get('PEXELS_API_KEY', '').strip()
            if chave_pexels:
                html = inserir_imagens_pexels(html, chave_pexels)
            problemas = validar_artigo(html) + validar_imagens(html)
            nota = problema_nota(analise)
            if nota:
                problemas.append(nota)
            if not problemas:
                return html, analise
            anterior, analise_ant = html, analise
            print(f'↪️ {modelo} reprovado: {"; ".join(problemas)}')
            ultimo_erro = RuntimeError('; '.join(problemas))
    raise ultimo_erro or RuntimeError('nenhum modelo gerou artigo')


def main():
    nome_chave = {'cerebras': 'CEREBRAS_API_KEY', 'openrouter': 'OPENROUTER_API_KEY'}.get(PROVEDOR, 'GEMINI_API_KEY')
    # strip(): secret colado com espaço ou quebra de linha quebra o cabeçalho HTTP
    chave = (os.environ.get(nome_chave) or '').strip()
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
        quem = ' > '.join(MODELOS_OPENROUTER) if PROVEDOR == 'openrouter' else modelo
        print(f'🤖 Gerando {nome_html} ({PROVEDOR}: {quem})...')
        try:
            with open(prompt_path, encoding='utf-8') as f:
                prompt = f.read().replace('{{DATA_HOJE}}', data_brasilia())
            lista = MODELOS_OPENROUTER if PROVEDOR == 'openrouter' else [modelo]
            rodadas = RODADAS_REESCRITA if PROVEDOR != 'openrouter' else min(RODADAS_REESCRITA, 1)
            html, analise = gerar_validado(prompt, chave, lista, rodadas)
        except (requests.RequestException, RuntimeError) as e:
            print(f'⚠️ Falha em {base}: {e}')
            falhas += 1
            continue

        os.makedirs(HTML_DIR, exist_ok=True)
        with open(os.path.join(HTML_DIR, nome_html), 'w', encoding='utf-8') as f:
            f.write(html)
        if analise:
            # Trabalho de bastidores: guardado para consulta, nunca publicado
            os.makedirs(ANALISE_DIR, exist_ok=True)
            with open(os.path.join(ANALISE_DIR, f'{base}.analise.md'), 'w', encoding='utf-8') as f:
                f.write(analise + '\n')
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
