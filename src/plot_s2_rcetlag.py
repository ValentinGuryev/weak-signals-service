#!/usr/bin/env python3
"""График S2 для кейса 002: wordshift RCE vs TLAG.

2 панели (как кейс 003): растущая/падающая лексика.
Выход: case_studies/002_rce_dr_sunam/plots/plot_s2_wordshift_rcetlag.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "case_studies" / "002_rce_dr_sunam" / "plots" / "plot_s2_wordshift_rcetlag.png"

rce = json.loads((ROOT / "results/case_signals/wordshift_trends_rce.json").read_text(encoding="utf-8"))
tlag = json.loads((ROOT / "results/case_signals/wordshift_trends_tlag.json").read_text(encoding="utf-8"))
periods = rce["periods"]
x = list(range(len(periods)))

# RCE: ключевые слова (стемы)
rce_up = ["fabric", "proces", "react", "current", "reel-to-reel"]
rce_down = ["substrat", "sputter", "power", "nonlinear", "simul", "weak"]
# TLAG: ключевые
tlag_up = ["transient", "ultrafast", "kinet", "non-equilibrium", "high-throughput",
           "synchrotron", "x-ray", "character", "fabric", "deposit"]

def freq(d, key):
    m = d["trends"].get(key)
    return m["freqs"] if m else None

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# RCE up/down
for key in rce_up:
    f = freq(rce, key)
    if f:
        axes[0][0].plot(x, f, marker="o", label=key, linewidth=2)
axes[0][0].set_xticks(x); axes[0][0].set_xticklabels(periods, rotation=30, ha="right", fontsize=8)
axes[0][0].set_title("RCE: растущая лексика", fontsize=11, fontweight="bold")
axes[0][0].legend(fontsize=7); axes[0][0].grid(alpha=0.3)

for key in rce_down:
    f = freq(rce, key)
    if f:
        axes[0][1].plot(x, f, marker="s", label=key, linewidth=2)
axes[0][1].set_xticks(x); axes[0][1].set_xticklabels(periods, rotation=30, ha="right", fontsize=8)
axes[0][1].set_title("RCE: падающая лексика", fontsize=11, fontweight="bold")
axes[0][1].legend(fontsize=7); axes[0][1].grid(alpha=0.3)

# TLAG up (down пусто — тема молодая)
for key in tlag_up:
    f = freq(tlag, key)
    if f:
        axes[1][0].plot(x, f, marker="o", label=key, linewidth=2)
axes[1][0].set_xticks(x); axes[1][0].set_xticklabels(periods, rotation=30, ha="right", fontsize=8)
axes[1][0].set_title("TLAG: растущая лексика (R&D)", fontsize=11, fontweight="bold")
axes[1][0].legend(fontsize=7); axes[1][0].grid(alpha=0.3)

# Панель объёма: period_totals
ax = axes[1][1]
tot_rce = [rce["period_totals"].get(p, 0) for p in periods]
tot_tlag = [tlag["period_totals"].get(p, 0) for p in periods]
ax.bar([i - 0.2 for i in x], tot_rce, width=0.4, label="RCE", color="#d62728", alpha=0.8)
ax.bar([i + 0.2 for i in x], tot_tlag, width=0.4, label="TLAG", color="#1f77b4", alpha=0.8)
ax.set_xticks(x); ax.set_xticklabels(periods, rotation=30, ha="right", fontsize=8)
ax.set_title("Объём публикаций (слова абстрактов)", fontsize=11, fontweight="bold")
ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.3)
ax.annotate("RCE угас (×15)", xy=(4, 82), xytext=(2.5, 600),
            arrowprops=dict(arrowstyle="->", color="#d62728"), fontsize=9, color="#d62728")
ax.annotate("TLAG R&D-волна", xy=(4, 1351), xytext=(0.2, 1100),
            arrowprops=dict(arrowstyle="->", color="#1f77b4"), fontsize=9, color="#1f77b4")

plt.suptitle("S2 кейс 002: семантический сдвиг RCE vs TLAG (wordshift)", fontsize=13, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
