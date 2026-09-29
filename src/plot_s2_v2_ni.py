#!/usr/bin/env python3
"""График S2 v2 для кейса 004: плотность инженерной vs фундаментальной лексики.

Выход: case_studies/004_ni_coils/plots/plot_s2_v2_ni.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "case_studies" / "004_ni_coils" / "plots" / "plot_s2_v2_ni.png"

d = json.loads((ROOT / "results/case_signals/semantic_v2_ni.json").read_text(encoding="utf-8"))
periods = list(d.keys())
periods = [p for p in periods if p != "_meta"]
x = list(range(len(periods)))

engs = [d[p]["eng_per_1000"] for p in periods]
effs = [d[p]["eff_per_1000"] for p in periods]
deltas = [d[p]["delta_mean"] for p in periods]
ns = [d[p]["n"] for p in periods]

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Панель 1: плотность
ax = axes[0]
ax.plot(x, engs, marker="o", linewidth=2.5, color="#2ca02c", label="инженерная лексика ‰")
ax.plot(x, effs, marker="s", linewidth=2, color="#d62728", label="фундаментальная лексика ‰")
ax.fill_between(x, effs, engs, alpha=0.1, color="#2ca02c")
ax.set_xticks(x); ax.set_xticklabels(periods, rotation=30, ha="right")
ax.set_title("Плотность лексики: инженерия vs фундамент (‰)", fontsize=11, fontweight="bold")
ax.legend(fontsize=9); ax.grid(alpha=0.3)
# Запас по ylim под аннотации
ax.set_ylim(0, max(engs + effs) * 1.3)
ax.annotate("Пик инженерии: 2011-2015 (227‰)\nпервые NI-работы", xy=(1, 227), xytext=(0.1, max(engs + effs) * 1.22),
            arrowprops=dict(arrowstyle="->", color="darkgreen"), fontsize=9, color="darkgreen",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="lightgreen", alpha=0.7, edgecolor="darkgreen"))
ax.annotate("Стабильная инженерия\n(157-194‰)", xy=(3, 172), xytext=(2.3, max(engs + effs) * 1.05),
            arrowprops=dict(arrowstyle="->", color="darkgreen"), fontsize=9, color="darkgreen",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="lightgreen", alpha=0.7, edgecolor="darkgreen"))

# Панель 2: Δ и объём
ax = axes[1]
ax.bar(x, deltas, color="#2ca02c", alpha=0.8, label="Δ (инж−фунд) ‰")
ax.set_xticks(x); ax.set_xticklabels(periods, rotation=30, ha="right")
ax.set_title("Δ (инженерия − фундамент) + число работ", fontsize=11, fontweight="bold")
ax.set_ylabel("Δ ‰", color="#2ca02c")
ax2 = ax.twinx()
ax2.plot(x, ns, marker="D", color="#1f77b4", linewidth=2, label="работ")
ax2.set_ylabel("работ", color="#1f77b4")
ax.legend(loc="upper left", fontsize=8); ax2.legend(loc="upper right", fontsize=8)
ax.grid(alpha=0.3)

plt.suptitle("S2 v2 кейс 004: NI-coils — инженерная тема с рождения (2011)\n"
             "(сбалансированные словари, плотность маркеров)", fontsize=13, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.9])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
