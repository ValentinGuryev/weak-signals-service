#!/usr/bin/env python3
"""График S2 для кейса 004: wordshift NI-coils.

2 панели: растущая/падающая лексика + объём.
Выход: case_studies/004_ni_coils/plots/plot_s2_wordshift_ni.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "case_studies" / "004_ni_coils" / "plots" / "plot_s2_wordshift_ni.png"

d = json.loads((ROOT / "results/case_signals/wordshift_trends_ni.json").read_text(encoding="utf-8"))
periods = d["periods"]
x = list(range(len(periods)))

growing = ["high-field", "stress", "optim", "mechan", "protect", "model", "non-insul", "applic"]
falling = ["sfcl", "strand", "disturb", "stabl", "calcul", "nbti"]

def freq(key):
    m = d["trends"].get(key)
    return m["freqs"] if m else None

fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Растущая
for key in growing:
    f = freq(key)
    if f:
        axes[0][0].plot(x, f, marker="o", label=key, linewidth=2)
axes[0][0].set_xticks(x); axes[0][0].set_xticklabels(periods, rotation=30, ha="right", fontsize=8)
axes[0][0].set_title("NI-coils: РАСТУЩАЯ лексика (инженерия)", fontsize=11, fontweight="bold")
axes[0][0].legend(fontsize=7); axes[0][0].grid(alpha=0.3)

# Падающая
for key in falling:
    f = freq(key)
    if f:
        axes[0][1].plot(x, f, marker="s", label=key, linewidth=2)
axes[0][1].set_xticks(x); axes[0][1].set_xticklabels(periods, rotation=30, ha="right", fontsize=8)
axes[0][1].set_title("NI-coils: ПАДАЮЩАЯ лексика (проблема/фундамент)", fontsize=11, fontweight="bold")
axes[0][1].legend(fontsize=7); axes[0][1].grid(alpha=0.3)

# Объём
tot = [d["period_totals"].get(p, 0) for p in periods]
axes[1][0].bar(x, tot, color="#2ca02c", alpha=0.85)
axes[1][0].set_xticks(x); axes[1][0].set_xticklabels(periods, rotation=30, ha="right", fontsize=8)
axes[1][0].set_title("Объём публикаций (слова абстрактов)", fontsize=11, fontweight="bold")
axes[1][0].grid(axis="y", alpha=0.3)
axes[1][0].annotate("×17 рост", xy=(4, 8598), xytext=(1.5, 7500),
                    arrowprops=dict(arrowstyle="->"), fontsize=10, color="darkgreen")

# Вывод
axes[1][1].axis("off")
axes[1][1].text(0.05, 0.5,
    "S2-вердикт: NI-coils ПРОШЛИ гейт зрелости\n"
    "«открытие → инженерия»\n\n"
    "Растёт: high-field, stress, optimize,\n"
    "model, mechanism, protect, non-insul\n\n"
    "Падает: sfcl, strand, NbTi, disturbance,\n"
    "stability (ранняя лексика)\n\n"
    "Тема созрела (как flux pump, кейс 003),\n"
    "в отличие от RCE/TLAG (кейс 002)",
    fontsize=11, va="center", ha="left",
    bbox=dict(boxstyle="round", facecolor="#e8f5e9", alpha=0.8))

plt.suptitle("S2 кейс 004: семантический сдвиг NI-coils (wordshift)", fontsize=13, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
