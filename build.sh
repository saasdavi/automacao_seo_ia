#!/bin/bash
# Script de build para Vercel

set -e

echo "📦 Instalando dependências..."
pip install -q pandas requests beautifulsoup4

echo "🔨 Gerando homepage..."
python scripts/gerar_home.py

echo "✅ Build completo!"
echo "📍 Arquivos em: dados/saida/html/"
