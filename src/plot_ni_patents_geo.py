#!/usr/bin/env python3
"""График патентов NI-coils по годам с географией (stacked).

Регионы: США, Китай, Корея, UK, Япония, Европа/WO.
Выход: case_studies/004_ni_coils/plots/plot_patents_years_geo.png
"""
import json
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data/raw/patents/cases/004_ni_coils.json").read_text(encoding="utf-8"))
OUT = ROOT / "case_studies" / "004_ni_coils" / "plots" / "plot_patents_years_geo.png"

pats = DATA["patents"]


def year_of(p):
    """Год: priority_date, иначе filing_date."""
    y = (p.get("priority_date") or "")[:4]
    if not y:
        y = (p.get("filing_date") or "")[:4]
    return y


def region(p):
    num = p.get("publication_number", "").upper()
    a = p.get("assignee", "").lower()
    asg_orig = p.get("assignee", "")
    if num.startswith("JP") or "toshiba" in a or "chubu" in a or "mitsubishi" in a or "railway" in a or "hitachi" in a or "furukawa" in a:
        return "Япония"
    if num.startswith("KR") or "korea" in a or "keri" in a or "kbsi" in a:
        return "Корея"
    if num.startswith("CN") or "shanghai" in a or "jiaotong" in a or "ningbo" in a or "casic" in a or "northwest" in a or "anhui" in a or "beijing" in a or "中科院" in asg_orig or "电工" in asg_orig:
        return "Китай"
    if num.startswith("US") or "massachusetts" in a or "mit" in a or "commonwealth" in a or "florida" in a or "bwx" in a:
        return "США"
    if "tokamak" in a:
        return "UK"
    return "Европа/WO"


REGIONS = ["США", "Китай", "Корея", "UK", "Япония", "Европа/WO"]
COLORS = {"США": "#1f77b4", "Китай": "#d62728", "Корея": "#ff7f0e",
          "UK": "#2ca02c", "Япония": "#9467bd", "Европа/WO": "#8c564b"}

by_year = {}
for p in pats:
    y = year_of(p)
    if not y:
        continue
    by_year.setdefault(y, Counter())[region(p)] += 1

years = sorted(by_year)
x = list(range(len(years)))

fig, ax = plt.subplots(figsize=(13, 6.5))
bottom = [0] * len(years)
for r in REGIONS:
    vals = [by_year[y].get(r, 0) for y in years]
    ax.bar(x, vals, bottom=bottom, color=COLORS[r], alpha=0.9, label=f"{r} ({sum(vals)})")
    bottom = [b + v for b, v in zip(bottom, vals)]

# Вехи
milestones = [
    (2013, "MIT partial insulation"),
    (2019, "Tokamak Energy\n(термояд)"),
    (2025, "CFS quench\ndetection"),
]
for y, label in milestones:
    if y in years:
        i = years.index(y)
        tot = bottom[i]
        ax.annotate(label, xy=(i, tot), xytext=(i, tot + 2.5),
                    arrowprops=dict(arrowstyle="->", color="darkred"),
                    fontsize=8, color="darkred", ha="center")

ax.set_xticks(x)
ax.set_xticklabels(years, rotation=45, ha="right", fontsize=8)
ax.set_xlabel("Год приоритета")
ax.set_ylabel("Число патентов")
ax.set_title(f"Патенты NI-coils по годам с географией (кейс 004)\n"
             f"База: {len(pats)} патентов (Lens + ручные, объединено, без дублей)")
ax.legend(fontsize=9, ncol=2)
ax.grid(axis="y", alpha=0.3)

fig.text(0.01, 0.01,
         "Источник: data/raw/patents/cases/004_ni_coils.json (2026-09-02, 61 патент, дедупл.).\n"
         "География по assignee/номеру. Пик 2019 = Tokamak Energy (UK, термояд) + MIT.\n"
         "Ручные 09-02: +CN115188554A/CN116646170A (IEE CAS), WO2017061563A1, JP2019149344A.",
         fontsize=8, style="italic", color="gray")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
