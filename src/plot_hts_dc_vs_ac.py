#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 012: график «количество статей по годам» HTS-DC (тренд) vs HTS-AC (конкурент 1).

Абсолютные числа из корпуса dc_cables_problem.json. Без новых API-запросов.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data/raw/openalex/dc_cables_problem.json"
OUT = ROOT / "case_studies/012_dc_hvdc_cables/plots/hts_dc_vs_ac_by_year.png"

Y0, Y1 = 1995, 2026  # обрезаем хвосты до 1995 (пре-история мала)


def counts(group: str) -> dict:
    d = json.loads(CORPUS.read_text(encoding="utf-8"))
    c = Counter(w.get("year") for w in d["works"] if w.get("group") == group and w.get("year"))
    return {y: c[y] for y in range(Y0, Y1 + 1) if c.get(y)}


def main() -> None:
    hts_dc = counts("HTS-DC")
    hts_ac = counts("HTS-AC")

    years = list(range(Y0, Y1 + 1))
    dc = [hts_dc.get(y, 0) for y in years]
    ac = [hts_ac.get(y, 0) for y in years]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([y - 0.2 for y in years], dc, width=0.4, label="HTS-DC (тренд)", color="#1f77b4")
    ax.bar([y + 0.2 for y in years], ac, width=0.4, label="HTS-AC (конкурент 1)", color="#ff7f0e")
    ax.set_xlabel("Год")
    ax.set_ylabel("Статей в год (абс.)")
    ax.set_title("Кейс 012: публикации HTS-DC vs HTS-AC по годам (OpenAlex, title+abstract)")
    ax.set_xticks(range(Y0, Y1 + 1, 2))
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # аннотации ключевых лет
    for y in (2000, 2005, 2010, 2013, 2018, 2020, 2023, 2025):
        if y in hts_dc:
            ax.annotate(str(hts_dc[y]), (y - 0.2, hts_dc[y]), ha="center", va="bottom",
                        fontsize=8, color="#1f77b4")
        if y in hts_ac:
            ax.annotate(str(hts_ac[y]), (y + 0.2, hts_ac[y]), ha="center", va="bottom",
                        fontsize=8, color="#ff7f0e")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"График → {OUT}")
    print(f"HTS-DC всего: {sum(hts_dc.values())} | HTS-AC всего: {sum(hts_ac.values())}")
    print("По годам:")
    for y in years:
        if hts_dc.get(y) or hts_ac.get(y):
            print(f"  {y}: DC={hts_dc.get(y,0)}  AC={hts_ac.get(y,0)}")


if __name__ == "__main__":
    main()