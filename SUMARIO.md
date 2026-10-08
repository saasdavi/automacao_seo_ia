# 📋 SUMÁRIO — Pipeline de Automação SEO

Data de execução: 08/10/2026
Repositório: `saasdavi/automacao_seo_ia` (branch `main`)

---

## ✅ O que foi implementado

### Tarefa 1 — Planilha do Calendário (`dados/calendario_blog_1_ano.csv`)
- Arquivo criado com **todas as 24 colunas na ordem especificada**:
  - **Bloco A (Dados Base)**: Dia, Data, Horário, Tema, Palavra-chave principal, Volume (dado), Concorrência, Variações (sinônimos)
  - **Bloco B (SERP – preenchido pelo script)**: Status (= "Fila"), SERP_Data_Consulta, SERP_Dificuldade_Real, SERP_Top5_URLs_e_Tipos, SERP_H2s_Comuns, SERP_PAA, SERP_Pesquisas_Relacionadas, SERP_Long_Tails_Vistas, SERP_Lacunas_Identificadas, SERP_Fontes_Oficiais_Candidatas, SERP_Autoridades_Top5, SERP_Divergencias_Com_Planilha
  - **Bloco C (Gemini – preenchido pelo script)**: GEMINI_Prompt_Pronto, GEMINI_Nota_Autoavaliada, Link_Artigo_Gerado, Data_Publicacao
- Encoding **UTF-8 com BOM**, compatível com Excel/Google Sheets e com o script.
- ⚠️ **Contém apenas o cabeçalho (0 linhas de dados).** Os arquivos-fonte reais informados nas instruções — `planejamento novo blog - Calendário.csv`, `Keyword Stats 2026-10-07 at 21_46_30.csv` e `pautas-mestre - pautas-mestre.csv` — **não estão presentes no repositório** (verificado via busca em disco, histórico git e branches remotas). Conforme a regra "use os dados REAIS / não invente dados", as 1.095 linhas NÃO foram geradas artificialmente. Basta anexar o CSV real do calendário ao repositório que o pipeline passa a operar sobre ele.

### Tarefa 2 — Script Python (`scripts/enriquecer_serp.py`)
- Criado com conteúdo exato solicitado (~250 linhas).
- Funções: `buscar_serper`, `analisar_pagina`, `classificar_dificuldade`, `identificar_lacunas`, `extrair_long_tails`, `montar_prompt_gemini`.
- Lê `dados/calendario_blog_1_ano.csv`, processa no máximo `MAX_ROWS` artigos com `Status = Fila`, grava os blocos SERP + Gemini e salva progresso a cada linha.
- Aborta com mensagem clara se `SERPER_API_KEY` não estiver configurada (comportamento validado em execução local).
- Sintaxe validada (`ast.parse` OK).

### Tarefa 3 — GitHub Action (`.github/workflows/enriquecer-serp.yml`)
- Workflow `workflow_dispatch` com input numérico `lotes` (padrão 10).
- Passos: checkout → Python 3.11 → `pip install pandas requests beautifulsoup4` → roda `scripts/enriquecer_serp.py` com `SERPER_API_KEY` (secret) e `MAX_ROWS` → commit + push do CSV atualizado.
- YAML validado com `pyyaml` (✅ OK).

### Tarefa 4 — Prompt Mestre Gemini v4 (`prompts/prompt_mestre_gemini_v4.txt`)
- Criado com conteúdo exato: fluxo PESQUISAR → ESCREVER → AUDITAR → CORRIGIR → ENTREGAR, diretrizes E-E-A-T / Helpful Content / YMYL, formato HTML + Schema MedicalWebPage, regras PROIBIDO/OBRIGATÓRIO e tabela de Análise de Pontuação (nota ≥ 9,0 = PRONTO PARA IMPORTAÇÃO).

### Tarefa 5 — Documentação
- `README.md` substituído pelo conteúdo exato solicitado (fluxo de trabalho, passo a passo de uso, tabela de blocos A/B/C, créditos gratuitos).
- `secrets.md` criado com instruções de configuração da `SERPER_API_KEY` (Serper.dev) e `PEXELS_API_KEY` (opcional).

### Tarefa 6 — Dependências
- `requirements.txt` criado: `pandas>=2.0.0`, `requests>=2.31.0`, `beautifulsoup4>=4.12.0`.

### Tarefa 7 — Estrutura de pastas
```
dados/                      (.gitkeep + calendario_blog_1_ano.csv)
dados/saida/                (.gitkeep)
scripts/                    (enriquecer_serp.py, run_pipeline.sh, seed_data.py, .gitkeep)
prompts/                    (prompt_mestre_gemini_v4.txt, .gitkeep)
.github/workflows/          (enriquecer-serp.yml, ci.yml)
```

---

## 🔜 Pendências externas (dependem do usuário)

| Item | Ação necessária |
|---|---|
| Dados reais do calendário | Anexar `planejamento novo blog - Calendário.csv` (1.095 linhas) ao repositório; o script passará a enriquecê-lo |
| Keyword Stats | Anexar o(s) CSV(s) do Google Keyword Planner para cruzamento de volume/concorrência |
| `SERPER_API_KEY` | Configurar em Settings → Secrets and variables → Actions (instruções em `secrets.md`) |
| Executar o pipeline | Actions → "Enriquecer SERP do Calendário" → Run workflow → lotes = 10 |

---

## 🧪 Verificações realizadas

- ✅ YAML do workflow parseado sem erros
- ✅ Script Python com sintaxe válida e comportamento de aborta sem API key confirmado em execução
- ✅ Colunas do CSV exatamente na ordem especificada (24 colunas)
- ✅ UTF-8 com BOM no CSV
- ✅ Todos os arquivos das tarefas 2–7 presentes e commitados em `main`
