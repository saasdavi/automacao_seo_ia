# 🚀 Blog Automação SEO

## Fluxo Automático (3 artigos por dia)

O workflow **Artigos diários (SERP + Gemini)** roda às **09h, 12h e 20h** (horário de Brasília):

1. **Pesquisa SERP** (Serper.dev) do próximo tema da fila no calendário
2. **Briefing** com concorrentes, H2s, PAA e long tails, salvo em `dados/saida/md/`
3. **Gemini** (API) gera o artigo HTML a partir do briefing e do prompt mestre
4. **Artigo** salvo em `dados/saida/html/` e publicado automaticamente na home
5. **Você** revisa o artigo no site

## Como Usar

### 1. Configurar Secrets no GitHub
Settings → Secrets and variables → Actions:

| Secret | Para que serve |
|--------|----------------|
| `SERPER_API_KEY` | Pesquisa SERP (obrigatória) |
| `GEMINI_API_KEY` | Geração dos artigos (obrigatória) |
| `PEXELS_API_KEY` | Fotos das miniaturas (workflow "Baixar miniaturas") |

### 2. Acompanhar a Automação
- Actions → **Artigos diários (SERP + Gemini)**: cada execução mostra quantos artigos foram pesquisados e gerados
- Para rodar fora do horário: Actions → **Artigos diários** → **Run workflow**

### 3. Diagnóstico
- **"HTTP 403 na Serper"**: a chave `SERPER_API_KEY` está inválida ou sem créditos. Troque o secret pela chave do painel do Serper.dev.
- **Execução vermelha com "Nenhum dos artigos foi pesquisado"**: a pesquisa falhou em todas as linhas. Veja a causa acima.
- **Gemini falhou**: confira `GEMINI_API_KEY` e o nome do modelo em `GEMINI_MODEL` (padrão `gemini-2.5-flash`).

### Geração manual (opcional)
- Abra `dados/calendario_blog_1_ano.csv`
- Copie o conteúdo do arquivo indicado em `GEMINI_Prompt_Arquivo` da linha desejada
- Cole no chat do Gemini e salve o HTML em `dados/saida/html/`

## Estrutura de Colunas da Planilha Final

| Bloco | Colunas |
|-------|---------|
| A - Dados Base | Dia, Data, Horário, Tema, Palavra-chave principal, Volume, Concorrência, Variações |
| B - SERP (auto) | Status, Data Consulta, Dificuldade Real, Top5 URLs, H2s Comuns, PAA, Pesquisas Relacionadas, Long Tails, Lacunas, Fontes Oficiais, Autoridades, Divergências |
| C - Gemini (auto) | GEMINI_Prompt_Arquivo, Artigo_Arquivo_HTML, Status (`GERADO`), Data Publicação |

## Créditos Gratuitos
- Serper.dev: 2.500 buscas/mês grátis (3 artigos por dia usam cerca de 90 por mês)
- GitHub Actions: 2.000 minutos/mês grátis
- Gemini API: camada gratuita
