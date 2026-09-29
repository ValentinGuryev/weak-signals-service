#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 012: относительная публикационная активность DC-ВТСП-линий в общем корпусе
методов решения проблемы передачи мощности (7 групп таксономии).

Показывает: долю публикаций по DC-ВТСП (и конкурентов: AC-ВТСП, медь-DC) от ВСЕГО
корпуса по годам. Ключевой вопрос кейса: «как в 2018 (окно) предугадать, что AC-ВТСП
уступит DC-ВТСП?» — отвечаем: тренд ДОЛИ DC уже шёл вверх, доля AC уже падала.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/raw/openalex/dc_cables_problem.json"
OUT = ROOT / "case_studies/012_dc_hvdc_cables/plots/rel_share_dc_vs_alternatives.png"

YEARS = range(1990, 2027)
FOCUS = {"HTS-DC": "#2ca02c", "HTS-AC": "#d62728", "CU-DC": "#1f77b4"}


def main() -> None:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    bg = Counter((w.get("year"), w.get("group")) for w in d["works"])

    totals = {y: sum(bg.get((y, g), 0) for g in {"HTS-DC", "HTS-AC", "CU-DC", "CU-CRYO", "GIL", "URBAN", "DATACENTER"}) for y in YEARS}
    share = {g: [bg.get((y, g), 0) / max(totals[y], 1) * 100 for y in YEARS] for g in FOCUS}

    fig, (ax, axb) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                 gridspec_kw={"height_ratios": [2, 1]})
    for g, col in FOCUS.items():
        ax.plot(YEARS, share[g], marker="o", ms=3, color=col, lw=2,
                label={"HTS-DC": "ВТСП DC-линии (ядро)", "HTS-AC": "ВТСП AC-линии", "CU-DC": "медный DC (XLPE/HVDC)"}[g])

    ax.axvline(2018, color="red", ls="--", lw=1.5)
    ax.text(2018.2, ax.get_ylim()[1],
            "окно 2018", color="red", fontsize=10)

    # подписи значений в ключевых годах
    for y in (2014, 2018, 2022, 2025):
        for g in FOCUS:
            idx = YEARS.index(y)
            ax.annotate(f"{share[g][idx]:.1f}%", (y, share[g][idx]),
                        textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8, color=FOCUS[g])

    ax.set_ylabel("Доля публикаций от корпуса, %")
    ax.set_title("Кейс 012: доля DC/AC-линий в корпусе методов передачи мощности (по годам)")
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(alpha=0.3)

    # нижняя панель: доля DC СРЕДИ ВТСП-линий (DC/(DC+AC)) + отношение DC/AC
    dc = [bg.get((y, "HTS-DC"), 0) for y in YEARS]
    ac = [bg.get((y, "HTS-AC"), 0) for y in YEARS]
    share_dc_vts = [100 * a / max(a + b, 1) for a, b in zip(dc, ac)]
    axb.plot(YEARS, share_dc_vts, color="#2ca02c", lw=2.2, marker="s", ms=3)
    axb.axhline(50, color="gray", ls=":", lw=1)
    axb.axvline(2018, color="red", ls="--", lw=1.5)
    axb.text(2018.2, axb.get_ylim()[1], "окно 2018", color="red", fontsize=9)
    axb.fill_between(YEARS, 50, share_dc_vts, where=[s >= 50 for s in share_dc_vts],
                     color="#2ca02c", alpha=0.15)
    for y in (2010, 2014, 2018):
        idx = YEARS.index(y)
        axb.annotate(f"{share_dc_vts[idx]:.0f}%", (y, share_dc_vts[idx]),
                     textcoords="offset points", xytext=(0, 7), ha="center", fontsize=9, color="#2ca02c")
    axb.set_ylabel("Доля DC среди ВТСП-линий, %")
    axb.set_ylim(0, 100)
    axb.grid(alpha=0.3)

    ax.set_xlim(1990, 2026)
    ax.set_xlabel("Год")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"График → {OUT}")
    print("\nКлючевые цифры (доля от корпуса, %):")
    print(f"  {'год':6}{'HTS-DC':>9}{'HTS-AC':>9}{'CU-DC':>9}")
    for y in (2005, 2010, 2014, 2018, 2020, 2022, 2024, 2025):
        idx = YEARS.index(y)
        print(f"  {y:<6}{share['HTS-DC'][idx]:8.2f}%{share['HTS-AC'][idx]:8.2f}%{share['CU-DC'][idx]:8.2f}%")
    # знак тренда до 2018
    i18 = YEARS.index(2018)
    i14 = YEARS.index(2014)
    print("\nТренд ДО окна (2014→2018):")
    for g in FOCUS:
        dlt = share[g][i18] - share[g][i14]
        print(f"  {g}: {share[g][i14]:.2f}% → {share[g][i18]:.2f}% (Δ={dlt:+.2f} п.п.)")


if __name__ == "__main__":
    main()