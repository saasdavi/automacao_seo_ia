# 🔐 Configuração de Secrets

## SerpAPI (pesquisa Google)
1. Acesse: https://serpapi.com
2. Crie conta (plano gratuito: 250 buscas/mês)
3. Copie a API Key no painel
4. No GitHub: Settings → Secrets and variables → Actions → New repository secret
5. Nome: `SERPAPI_KEY`
6. Valor: cole sua chave

## Gemini (geração dos artigos)
1. Acesse: https://aistudio.google.com/apikey
2. Crie a chave
3. Nome do secret: `GEMINI_API_KEY`

## Pexels API (fotos das miniaturas)
1. Acesse: https://www.pexels.com/api/
2. Crie chave gratuita
3. Nome do secret: `PEXELS_API_KEY` (usado pelo workflow "Baixar miniaturas")
