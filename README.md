# 🚀 Blog Automação SEO

## Fluxo de Trabalho

1. **GitHub Action** extrai dados SERP das keywords da planilha
2. **Script Python** analisa concorrentes, H2s, PAA e long tails
3. **Briefing** é gerado automaticamente na coluna `GEMINI_Prompt_Pronto`
4. **Gemini** lê o briefing + prompt mestre e gera artigo HTML
5. **Você** revisa e publica

## Como Usar

### 1. Configurar Secrets no GitHub
- Vá em: Settings → Secrets and variables → Actions
- Adicione: `SERPER_API_KEY` (chave gratuita da Serper.dev - 2.500 buscas/mês)

### 2. Rodar a Automação
- Vá em: Actions → "Enriquecer SERP do Calendário"
- Clique em "Run workflow"
- Escolha quantos artigos processar (recomendado: 10)

### 3. Gerar Artigo com Gemini
- Abra `dados/calendario_blog_1_ano.csv`
- Copie o conteúdo da coluna `GEMINI_Prompt_Pronto` da linha desejada
- Cole no chat do Gemini
- Receba o artigo HTML pronto com nota de qualidade

## Estrutura de Colunas da Planilha Final

| Bloco | Colunas |
|-------|---------|
| A - Dados Base | Dia, Data, Horário, Tema, Palavra-chave principal, Volume, Concorrência, Variações |
| B - SERP (auto) | Status, Data Consulta, Dificuldade Real, Top5 URLs, H2s Comuns, PAA, Pesquisas Relacionadas, Long Tails, Lacunas, Fontes Oficiais, Autoridades, Divergências |
| C - Gemini (auto) | GEMINI_Prompt_Pronto, Nota Autoavaliada, Link Artigo Gerado, Data Publicação |

## Créditos Gratuitos
- Serper.dev: 2.500 buscas/mês grátis
- GitHub Actions: 2.000 minutos/mês grátis
- Gemini API: camada gratuita generosa
