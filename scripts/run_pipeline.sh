#!/usr/bin/env bash
# Executa o pipeline completo: seed -> validação -> exportação.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> 1/3 Preparando dados brutos (data/raw)"
python scripts/seed_data.py || echo "AVISO: dados brutos ausentes — veja instruções acima."

echo "==> 2/3 Validando premissas"
python -m src.cli validate || true

echo "==> 3/3 Exportando saídas (json, csv, ics, md)"
python -m src.cli export --format json,csv,ics,md

echo "Pipeline finalizado. Saídas em data/processed/"
