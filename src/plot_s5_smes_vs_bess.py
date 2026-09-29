#!/usr/bin/env python3
"""S5-график кейса 005: SMES vs BESS vs Li-ion vs Supercap (публикации).

Динамика статей (OpenAlex title.search, group_by year) — конкуренты растут,
SMES стагнирует. Выход: case_studies/SMES/plots/plot_s5_smes_vs_bess.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data/raw/openalex/smes_vs_bess_counts.json").read_text(encoding="utf-8"))
OUT = ROOT / "case_studies" / "SMES" / "plots" / "plot_s5_smes_vs_bess.png"

counts = DATA["counts"]
years = list(range(2005, 2027))

SERIES = [
    ("SMES", "#c9211e", "o-"),
    ("BESS", "#1f77b4", "s-"),
    ("Li-ion", "#2ca02c", "^-"),
    ("Supercap", "#9467bd", "d-"),
]

fig, ax = plt.subplots(figsize=(12, 6.5))
for label, color, fmt in SERIES:
    vals = [counts[label].get(str(y), 0) for y in years]
    ax.plot(years, vals, fmt, color=color, lw=2, ms=4, label=f"{label} ({sum(vals)})")

# аннотации
ax.annotate("SMES: 2005 = 25 > BESS 11\n→ 2025: 27 (плоско)",
            xy=(2005, 25), xytext=(2006, 320),
            arrowprops=dict(arrowstyle="->", color="#c9211e"),
            fontsize=9, color="#c9211e")
ax.annotate("BESS: 693 в 2025 (×60 за 20 лет)",
            xy=(2025, 693), xytext=(2012, 620),
            arrowprops=dict(arrowstyle="->", color="#1f77b4"),
            fontsize=9, color="#1f77b4")

ax.set_xlabel("Год")
ax.set_ylabel("Число статей (title.search)")
ax.set_title("SMES vs конкуренты по хранению энергии: публикации (кейс 005, S5)\n"
             "SMES стагнирует (14-41/год), BESS/Supercap растут экспоненциально")
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

fig.text(0.01, 0.01,
         "Источник: OpenAlex title.search + group_by publication_year (2026-09-02).\n"
         "S5: конкуренты (BESS, supercap) взорвались — SMES проиграл по публикациям и экономике.",
         fontsize=8, style="italic", color="gray")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
