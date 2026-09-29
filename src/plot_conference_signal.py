#!/usr/bin/env python3
"""Конференционный отклик кейса 005: SMES в IEEE TAS по годам + SNF-доклады.

Показывает: пик конференций 2007 (в окне тренда), спад 2009-2021, возрождение 2024 (Китай).
Выход: case_studies/005_SMES/plots/plot_conference_signal.png
"""
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data/raw/conferences/conference_hits.json").read_text(encoding="utf-8"))
OUT = ROOT / "case_studies" / "005_SMES" / "plots" / "plot_conference_signal.png"

hits = [it for it in DATA.get("items", []) if isinstance(it, dict)
        and "smes" in json.dumps(it, ensure_ascii=False).lower()]
years = Counter((it.get("year") or 0) for it in hits)
all_years = sorted(years)

# SNF доклады (вручную из conference_signal)
snf = {2008: 1, 2010: 1, 2013: 1, 2015: 1, 2023: 1}  # Tixador, Nitta, LIQHYSMES, Gupta, ISS

fig, ax = plt.subplots(figsize=(13, 6.5))
vals = [years.get(y, 0) for y in all_years]
colors = []
for y in all_years:
    if 2003 <= y <= 2012:
        colors.append("#2ca02c")  # окно тренда
    elif y >= 2022:
        colors.append("#d62728")  # возрождение Китай
    else:
        colors.append("#1f77b4")
bars = ax.bar(all_years, vals, color=colors, alpha=0.85, edgecolor="black", linewidth=0.3)

# SNF маркеры
for y, n in snf.items():
    if y in all_years:
        ax.plot(y, years.get(y, 0) + 0.1, "D", color="#8c564b", ms=8, zorder=5)

ax.axvspan(2003, 2012, color="#2ca02c", alpha=0.08)
ax.text(2007.5, max(vals) * 0.95, "окно тренда\nВТСП-SMES (2003-2012)", ha="center", fontsize=9, color="#2ca02c")
ax.annotate("пик 2007 (5)\nK-SMES 600kJ + 800kJ HTS", xy=(2007, 5), xytext=(1997, 5.3),
            arrowprops=dict(arrowstyle="->"), fontsize=9)
ax.annotate("спад 2009-2021\n(программы закрыты)", xy=(2013, 1), xytext=(2014, 4.2),
            arrowprops=dict(arrowstyle="->"), fontsize=9, color="gray")
ax.annotate("возрождение 2024 (5)\nКитай: 1MJ HTS SMES (NMR)", xy=(2024, 5), xytext=(2019, 5.6),
            arrowprops=dict(arrowstyle="->"), fontsize=9, color="#d62728")

ax.set_xlabel("Год")
ax.set_ylabel("Число докладов (IEEE TAS)")
ax.set_title("Конференционный отклик: SMES в IEEE TAS (1993-2025), кейс 005\n"
             "Зелёный = окно тренда; красный = китайское возрождение; ромбы = SNF-доклады")
ax.set_xticks(all_years)
ax.set_xticklabels(all_years, rotation=45, ha="right", fontsize=8)
ax.grid(axis="y", alpha=0.3)

fig.text(0.01, 0.01,
         "Источник: data/raw/conferences/conference_hits.json (IEEE TAS, 54 SMES-работы); SNF index (Tixador 2008,\n"
         "Nitta MT2010, LIQHYSMES 2013, Gupta BNL 2015, ISS 2023). Фазы: активность 1993-2011 → спад → Китай 2024.",
         fontsize=8, style="italic", color="gray")
plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
