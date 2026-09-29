#!/usr/bin/env python3
"""Патентный отклик кейса 005: SMES vs BESS (2000-2020), по географии.

Выход: case_studies/005_SMES/plots/plot_patents_signal_2000_2020.png
"""
import json
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
smes = json.loads((ROOT / "data/raw/patents/cases/005_smes.json").read_text(encoding="utf-8"))["patents"]
bess = json.loads((ROOT / "data/raw/patents/topics/bess_lens.json").read_text(encoding="utf-8"))["patents"]
OUT = ROOT / "case_studies" / "005_SMES" / "plots" / "plot_patents_signal_2000_2020.png"


def year(p):
    return (p.get("priority_date") or p.get("filing_date") or "")[:4]


def region(p):
    num = (p.get("publication_number") or "").upper()
    a = (p.get("assignee") or "").lower()
    if num.startswith(("CN", "WO")) or any(x in a for x in ["中科", "大学", "电网", "国网", "electric power", "institute of electrical"]):
        return "Китай"
    if num.startswith(("KR",)) or "korea" in a or "keri" in a or "hyundai" in a:
        return "Корея"
    if num.startswith(("JP",)) or any(x in a for x in ["toshiba", "chubu", "hitachi", "fujikura", "mitsubishi", "sumitomo"]):
        return "Япония"
    if num.startswith(("US",)) or "united states" in a or "energy" in a and "us" in a:
        return "США"
    if any(x in a for x in ["siemens", "abb", "rolls", "general electric"]):
        return "Европа"
    return "Прочее"


REGIONS = ["Китай", "Корея", "Япония", "США", "Европа", "Прочее"]
COLORS = {"Китай": "#d62728", "Корея": "#ff7f0e", "Япония": "#9467bd",
          "США": "#1f77b4", "Европа": "#2ca02c", "Прочее": "#8c564b"}

fig, axes = plt.subplots(1, 2, figsize=(15, 6.5), sharey=False)

for ax, (label, pats) in zip(axes, [("SMES (130 патентов)", smes), ("BESS / Li-ion (83 патента)", bess)]):
    by_year = {}
    for p in pats:
        y = year(p)
        if not (y and 2000 <= int(y) <= 2020):
            continue
        by_year.setdefault(y, Counter())[region(p)] += 1
    years = sorted(by_year)
    x = list(range(len(years)))
    bottom = [0] * len(years)
    for r in REGIONS:
        vals = [by_year[y].get(r, 0) for y in years]
        if sum(vals) == 0:
            continue
        ax.bar(x, vals, bottom=bottom, color=COLORS[r], alpha=0.9, label=f"{r} ({sum(vals)})")
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha="right", fontsize=8)
    ax.set_title(f"{label}\n2000-2020, по годам приоритета", fontsize=11)
    ax.set_xlabel("Год")
    ax.set_ylabel("Число патентов")
    ax.legend(fontsize=8, ncol=1)
    ax.grid(axis="y", alpha=0.3)
    ax.set_xlim(-0.5, len(years) - 0.5)

fig.suptitle("Патентный отклик: SMES vs BESS (кейс 005) — «ложный тренд» SMES при взрыве BESS",
             fontsize=13, y=0.99)
fig.text(0.01, 0.01,
         "Источники: SMES — data/raw/patents/cases/005_smes.json (Google+Lens, 130); BESS — bess_lens.json (Lens, 83, 2000-2020).\n"
         "Окно тренда ВТСП-SMES 2003-2012. Патентный crossover BESS>SMES ~2015-2017 (позже публикационного 2009).",
         fontsize=8, style="italic", color="gray")
plt.tight_layout(rect=[0, 0.02, 1, 0.95])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
