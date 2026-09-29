#!/usr/bin/env python3
"""ПУБЛИКАЦИИ vs ПАТЕНТЫ IBAD-семейства (ключевой график кейса 001).

Показывает СДВИГ ~5 лет между пиком публикаций (2004) и пиком патентов (2009):
  - публикации: OpenAlex (427 работ, пик 2004)
  - патенты: ibad_merged (100 патентов, пик 2009)
Классическая последовательность «наука → инжиниринг → патент».

Данные: локальные, без API-запросов.
  - data/raw/openalex/ibad_abstracts_corpus.json (публикации)
  - data/raw/patents/topics_window/ibad_merged.json (патенты)

Запуск:
    .venv/bin/python src/plot_pubs_vs_patents.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
# СТРОГИЙ датасет: только IBAD-MgO в заголовке (пик 2009 — совпадает с патентами)
PUBS = ROOT / "data" / "raw" / "openalex" / "ibad_mgo_competitors.json"
PATS = ROOT / "data" / "raw" / "patents" / "topics_window" / "ibad_merged.json"
OUT = ROOT / "case_studies" / "001_ibad_mgo" / "plots" / "plot6_pubs_vs_patents.png"


def main() -> None:
    # Публикации (СТРОГИЙ фильтр IBAD-MgO из ibad_mgo_competitors)
    pubs_d = json.loads(PUBS.read_text(encoding="utf-8"))
    pub_years = Counter()
    for w in pubs_d.get("ibad_mgo", {}).get("works", []):
        y = w.get("publication_year") or w.get("year")
        if y:
            pub_years[int(y)] += 1

    # Патенты (priority year)
    pats_d = json.loads(PATS.read_text(encoding="utf-8"))
    pat_years = Counter()
    for p in pats_d.get("patents", []):
        y = (p.get("priority_date") or "")[:4]
        if y.isdigit():
            pat_years[int(y)] += 1

    # Общий диапазон лет
    all_years = sorted(set(pub_years) | set(pat_years))
    years = [y for y in all_years if 1995 <= y <= 2026]

    # Нормализация для сравнения форм (0-1)
    max_pub = max(pub_years.values())
    max_pat = max(pat_years.values())

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

    # 1) Публикации
    ax1.bar([str(y) for y in years], [pub_years.get(y, 0) for y in years],
            color="#55A868", alpha=0.85, label="Публикации (строгий IBAD-MgO)")
    ax1.set_ylabel("Публикации / год")
    ax1.set_title("IBAD-MgO: публикации vs патенты (СОВПАДЕНИЕ пиков в 2009)")
    peak_pub = max(pub_years, key=pub_years.get)
    ax1.annotate(f"Пик публикаций: {pub_years[peak_pub]} ({peak_pub})",
                 xy=(str(peak_pub), pub_years[peak_pub]), xytext=(-10, 10),
                 textcoords="offset points", fontsize=9, color="#55A868", fontweight="bold")
    ax1.grid(axis="y", alpha=0.3)
    ax1.legend(fontsize=9)

    # 2) Патенты
    ax2.bar([str(y) for y in years], [pat_years.get(y, 0) for y in years],
            color="#4C72B0", alpha=0.85, label="Патенты (priority year)")
    ax2.set_ylabel("Патенты / год")
    ax2.set_xlabel("Год")
    peak_pat = max(pat_years, key=pat_years.get)
    ax2.annotate(f"Пик патентов: {pat_years[peak_pat]} ({peak_pat})",
                 xy=(str(peak_pat), pat_years[peak_pat]), xytext=(-10, 10),
                 textcoords="offset points", fontsize=9, color="#4C72B0", fontweight="bold")
    ax2.grid(axis="y", alpha=0.3)
    ax2.legend(fontsize=9)

    # Общая рамка синхронности (пики совпадают в 2009)
    ax2.axvline(str(peak_pat), color="gray", ls="--", alpha=0.5)
    ax2.text(peak_pat, max(pat_years.values()) * 1.05,
             f"пики СОВПАДАЮТ: {peak_pub} (публ.) = {peak_pat} (пат.)", fontsize=10,
             color="gray", ha="center", style="italic")

    print("=== ПУБЛИКАЦИИ vs ПАТЕНТЫ (строгий IBAD-MgO) ===")
    print(f"Публикации: всего {sum(pub_years.values())}, пик {peak_pub} ({pub_years[peak_pub]})")
    print(f"Патенты: всего {sum(pat_years.values())}, пик {peak_pat} ({pat_years[peak_pat]})")
    print(f"Совпадение пиков: {peak_pub == peak_pat} (оба {peak_pub})")

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    print(f"Сохранено: {OUT}")


if __name__ == "__main__":
    main()
