#!/usr/bin/env python3
"""Seed de dados: prepara o diretório data/raw.

IMPORTANTE: este script NÃO inventa dados de keywords/cronograma.
Ele apenas verifica se os arquivos de entrada fornecidos
(`Keyword Stats *.csv` e `Pasted_Text_*.txt`) estão presentes em
`data/raw/` com os nomes canônicos esperados pelo pipeline
(`keyword_stats.csv` e `cronograma.txt`). Caso existam arquivos com o
nome original do export do Keyword Planner, eles são copiados para o
nome canônico.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"


def canonicalizar() -> int:
    """Copiar arquivos de entrada para nomes canônicos, se necessário."""
    RAW.mkdir(parents=True, exist_ok=True)
    faltando: list[str] = []

    # CSV do Keyword Planner -> data/raw/keyword_stats.csv
    alvo_csv = RAW / "keyword_stats.csv"
    if not alvo_csv.exists():
        candidatos = sorted(RAW.glob("Keyword Stats*.csv")) + sorted(RAW.glob("*keyword*stats*.csv"))
        if candidatos:
            shutil.copy(candidatos[0], alvo_csv)
            print(f"[seed] {candidatos[0].name} -> {alvo_csv.relative_to(RAIZ)}")
        else:
            faltando.append("keyword_stats.csv")

    # Cronograma em texto -> data/raw/cronograma.txt
    alvo_txt = RAW / "cronograma.txt"
    if not alvo_txt.exists():
        candidatos = sorted(RAW.glob("Pasted_Text_*.txt")) + sorted(RAW.glob("*cronograma*.txt"))
        if candidatos:
            shutil.copy(candidatos[0], alvo_txt)
            print(f"[seed] {candidatos[0].name} -> {alvo_txt.relative_to(RAIZ)}")
        else:
            faltando.append("cronograma.txt")

    if faltando:
        print(
            "[seed] Arquivos ausentes em data/raw/: "
            + ", ".join(faltando)
            + "\n[seed] Coloque-os manualmente (não geramos dados fictícios).",
            file=sys.stderr,
        )
        return 1
    print("[seed] Dados de entrada OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(canonicalizar())
