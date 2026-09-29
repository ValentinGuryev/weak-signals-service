#!/usr/bin/env python3
"""График S2 v2 для кейса 003: flux pump — плотность инженерной/фундаментальной лексики.

Продвинутый пайплайн (сбалансированные словари + плотность ‰).
Выход: case_studies/003_flux_pump_space/plots/plot_s2_v2_fluxpump.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "case_studies" / "003_flux_pump_space" / "plots" / "plot_s2_v2_fluxpump.png"

d = json.loads((ROOT / "results/case_signals/semantic_v2_fluxpump.json").read_text(encoding="utf-8"))
periods = [p for p in d if p != "_meta"]
x = list(range(len(periods)))

engs = [d[p]["eng_per_1000"] for p in periods]
effs = [d[p]["eff_per_1000"] for p in periods]
deltas = [d[p]["delta_mean"] for p in periods]
ns = [d[p]["n"] for p in periods]

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Панель 1: плотность
ax = axes[0]
ax.plot(x, engs, marker="o", linewidth=2.5, color="#1f77b4", label="инженерная лексика ‰")
ax.plot(x, effs, marker="s", linewidth=2.5, color="#ff7f0e", label="фундаментальная лексика ‰")
ax.fill_between(x, effs, engs, alpha=0.1, color="#1f77b4")
ax.set_xticks(x); ax.set_xticklabels(periods, rotation=30, ha="right")
ax.set_title("Плотность лексики: инженерия vs фундамент (‰)", fontsize=11, fontweight="bold")
ax.legend(fontsize=9); ax.grid(alpha=0.3)
# Запас по ylim под аннотацию
ax.set_ylim(0, max(engs + effs) * 1.3)
ax.annotate("Фундамент значим\n(52-80‰ — физика механизма)", xy=(4, 69), xytext=(0.2, max(engs + effs) * 1.18),
            arrowprops=dict(arrowstyle="->", color="#ff7f0e"), fontsize=9, color="#b35900",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="lightyellow", alpha=0.8, edgecolor="#ff7f0e"))

# Панель 2: Δ и объём
ax = axes[1]
ax.bar(x, deltas, color="#1f77b4", alpha=0.8, label="Δ (инж−фунд) ‰")
ax.set_xticks(x); ax.set_xticklabels(periods, rotation=30, ha="right")
ax.set_title("Δ (инженерия − фундамент) + число работ", fontsize=11, fontweight="bold")
ax.set_ylabel("Δ ‰", color="#1f77b4")
ax2 = ax.twinx()
ax2.plot(x, ns, marker="D", color="#2ca02c", linewidth=2, label="работ")
ax2.set_ylabel("работ", color="#2ca02c")
ax.legend(loc="upper left", fontsize=8); ax2.legend(loc="upper right", fontsize=8)
ax.grid(alpha=0.3)

plt.suptitle("S2 v2 кейс 003: flux pump — физика + инженерия (плотность маркеров ‰)\n"
             "Фундамент значим (52-80‰), инженерия доминирует (172-227‰) — «открытие → инженерия»",
             fontsize=13, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.9])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
