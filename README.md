# 🚀 Blog Automação SEO

## Fluxo Automático

Dois workflows independentes:

1. **Enriquecer SERP do Calendário** (todo dia, 10h de Brasília): pesquisa 5 temas da fila no SerpAPI e grava na planilha a palavra-chave, a concorrência, as perguntas (PAA), os H2s e as lacunas. Também salva o briefing em `dados/saida/md/`.
2. **Artigos diários (Gemini)** (09h, 12h e 20h de Brasília): **não pesquisa**. Pega a próxima linha já enriquecida (`SERP_OK`) e gera 1 artigo com o Gemini. A análise de pontuação interna vai para `dados/saida/md/` e não vai para o site. O artigo só é salvo se passar na validação (mínimo de palavras, sem CRM, data correta, estrutura).

O artigo salvo em `dados/saida/html/` é publicado automaticamente na home.

## Como Usar

### 1. Configurar Secrets no GitHub
Settings → Secrets and variables → Actions:

| Secret | Para que serve |
|--------|----------------|
| `SERPAPI_KEY` | Pesquisa SERP via serpapi.com (obrigatória) |
| `GEMINI_API_KEY` | Geração dos artigos das 9h com o Gemini (obrigatória) |
| `BYTEPLUS_API_KEY` | Geração dos artigos das 12h e 20h com a BytePlus ModelArk (cota gratuita) |
| `PEXELS_API_KEY` | Fotos das miniaturas (workflow "Baixar miniaturas") |

### 2. Acompanhar a Automação
- Actions → **Enriquecer SERP do Calendário**: pesquisa e grava as linhas da planilha
- Actions → **Artigos diários (Gemini)**: cada execução mostra se o artigo foi gerado
- Para rodar fora do horário: Actions → **Artigos diários** → **Run workflow**

### 3. Diagnóstico
- **"HTTP 401 na SerpAPI"**: a chave `SERPAPI_KEY` está inválida. Copie a chave exata do painel do serpapi.com e atualize o secret.
- **"HTTP 429 na SerpAPI"**: o limite de buscas do plano foi atingido (250/mês no gratuito).
- **Execução vermelha com "Nenhum dos artigos foi pesquisado"**: a pesquisa falhou em todas as linhas. Veja a causa acima.
- **"HTTP 429" do Gemini ("exceeded your current quota")**: a cota do projeto acabou, geralmente por dia. A execução falha e o artigo fica pendente para a próxima. Não há fallback para outro provedor.
- Pausa entre chamadas ao Gemini: `PAUSA_ENTRE_CHAMADAS` (padrão 15 s; 0 desliga).

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
- SerpAPI: 250 buscas/mês grátis. O fluxo usa 5 por dia (cerca de 155 por mês), no workflow de enriquecimento.
- GitHub Actions: 2.000 minutos/mês grátis
- Gemini API: camada gratuita
