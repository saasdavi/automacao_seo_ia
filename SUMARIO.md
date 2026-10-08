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

---

## 🔍 Teste dos Workflows (08/10/2026)

### CI (`.github/workflows/ci.yml`)
- ✅ Executado no GitHub: **success** (run mais recente, commit `0c9b7a6`)
- 🔧 Ajuste feito: validação de sintaxe agora tolera ausência de `src/` (compila `scripts/` sempre e `src/` apenas se existir)

### Enriquecer SERP (`.github/workflows/enriquecer-serp.yml`)
- ✅ Disparado via API (`workflow_dispatch`, sem input → default 10): run `37724016920` → **success**
- Todos os steps passaram: Checkout, Setup Python, Install deps, Rodar script SERP, Commit CSV + push
- Log do script na nuvem: `✅ Nenhuma linha na fila. Processo concluído.` — comportamento correto, pois `calendario_blog_1_ano.csv` ainda tem 0 linhas
- Compatibilidade de secret confirmada: `secrets.SERPER_API_KEY || secrets.SERPAPI_KEY` resolve o nome configurado (`SERPAPI_KEY`)
- Push do step Commit funcionou com `permissions: contents: write` (`Everything up-to-date` = nada a commitar, esperado)

### Pendência única restante
- ⚠️ Os CSVs-fonte reais (`planejamento novo blog - Calendário.csv`, `Keyword Stats...csv`, `pautas-mestre...csv`) **ainda não existem no GitHub** (verificado na árvore git da branch main). Sem eles, a Action roda mas processa 0 artigos. Fazer upload pela interface (Add file → Upload files em `dados/`) ou enviar conteúdo no chat para push automático.

## 🔬 Auditoria ponta a ponta para o teste completo (08/10/2026)

### ✅ Comprovado funcionando (execução real via API do GitHub)
| Etapa | Evidência |
|---|---|
| CI (`ci.yml`) | run 37724201822 → success no push |
| Action SERP — todos os steps | runs 37724016920, 37724446425, 37724458330 → success (Checkout, Python 3.11, pip install, script, commit+push) |
| Compatibilidade de secret | `SERPER_API_KEY \|\| SERPAPI_KEY` funciona com o nome configurado (`SERPAPI_KEY`) |
| Permissão de push do workflow | step "Commit CSV atualizado" conclui sem erro |
| Secrets presentes | GEMINI_API_KEY, GH_REPO, GH_TOKEN, PEXELS_API_KEY, SERPAPI_KEY ✔ |

### ❌ Bloqueios para o "teste completo" (Vercel + Gemini + publicação)
1. **CSVs-fonte não estão no GitHub** — `/contents/dados` mostra apenas `.gitkeep`, `saida/` e `calendario_blog_1_ano.csv` (443 bytes = só cabeçalho, 0 linhas). Sem as 1.095 linhas, a Action processa 0 artigos (roda "sucesso" instantâneo).
2. **Nenhum código usa o GEMINI_API_KEY** — o repo tem só 2 workflows; a geração do artigo ainda é manual (copiar coluna `GEMINI_Prompt_Pronto` e colar no chat Gemini). Não existe automação Gemini publicada.
3. **Vercel não conectado** — API `/deployments` retorna 0; e o repo não contém app publicável (sem frontend/API route/vercel.json). Deploy na Vercel exigiria primeiro criar esse app.

### 📋 Ordem correta para chegar ao deploy
- [ ] 1. Enviar `planejamento novo blog - Calendário.csv` (+ Keyword Stats) para `dados/` no GitHub
- [ ] 2. Popularizar `calendario_blog_1_ano.csv` com as 1.095 linhas + Status="Fila"
- [ ] 3. Rodar Action SERP (lotes=10) e validar colunas preenchidas com dados reais
- [ ] 4. Criar etapa de geração: opção B (workflow `gerar-artigos-gemini.yml`) ou C (app Vercel com API route que lê o CSV e chama Gemini)
- [ ] 5. Conectar repo ao Vercel e testar publicação de 1 artigo


---

## 🧪 TESTE PONTA A PONTA (2026-10-08) — RESULTADO REAL

### ✅ Dados carregados com sucesso
- `dados/planejamento novo blog - Calendário.csv` → **1.095 artigos** confirmados
- Validações: 365 dias únicos | 08/10/2026→07/10/2027 | horários 09h/12h/20h | 0 duplicatas
- Distribuição por tema confere com tabela de potencial (Estresse 129, Insônia 128, Memória 128... Autocuidado 9, Autoconhecimento 3)
- `dados/calendario_blog_1_ano.csv` populado: 1.095 linhas × 24 colunas, Status="Fila", UTF-8 BOM → **push feito e verificado no remoto (1.095 linhas)**

### ✅ Action "Enriquecer SERP" — executada de verdade (runs 37725375434 e 37725468962)
- Todos os steps: success (checkout, Python, pip, script, commit+push)
- Script leu o CSV real e processou as keywords corretamente ("estresse", "meditação para dormir")
- Input `lotes` funcionando (testado com 2 e 1)

### ❌ ÚNICO PROBLEMA RESTANTE — chave Serper inválida
Log oficial da Action:
```
⚠️ HTTP 403 na Serper para 'estresse': {"message":"Unauthorized.","statusCode":403}
```
Significa: o secret `SERPAPI_KEY` no GitHub contém uma chave **inválida/expirada/copiada com erro**.
Correção (2 min): https://serper.dev → dashboard → copiar API Key exata → GitHub Settings → Secrets → atualizar `SERPAPI_KEY` → rodar a Action de novo.

### 🔧 Melhoria aplicada neste teste
- `buscar_serper()` agora loga HTTP status + corpo do erro (commit b3a822d) — diagnósticos futuros instantâneos.
