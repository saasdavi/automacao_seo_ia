# 🔐 Configuração de Secrets

## SerpAPI (pesquisa Google)
1. Acesse: https://serpapi.com
2. Crie conta (plano gratuito: 250 buscas/mês)
3. Copie a API Key no painel
4. No GitHub: Settings → Secrets and variables → Actions → New repository secret
5. Nome: `SERPAPI_KEY`
6. Valor: cole sua chave

## OpenRouter (geração dos artigos com modelos gratuitos)
1. Acesse: https://openrouter.ai/settings/keys
2. Crie uma chave e defina um limite de gastos na conta
3. Nome do secret: `OPENROUTER_API_KEY`
4. Modelos usados (gratuitos, em ordem): `thinkingmachines/inkling:free`, `apodex/apodex-1.1-mini:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3.5-lightning:free`, `thinkingmachines/inkling-small:free`, `dots-studio/dots-3-note-preview:free`, `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `cohere/north-mini-code:free`, `liquid/lfm-2.5-2.6b:free`, `google/gemma-4-31b-it:free`

## Pexels API (fotos das miniaturas)
1. Acesse: https://www.pexels.com/api/
2. Crie chave gratuita
3. Nome do secret: `PEXELS_API_KEY` (usado pelo workflow "Baixar miniaturas")
