#!/usr/bin/env python3
"""График: сравнение S2 v2 — flux pump (003) vs NI-coils (004).

Показывает: плотность инженерной/фундаментальной лексики по периодам
для двух кейсов. Ключевое: фундаментальная составляющая flux pump выше
(52-80‰ vs 12-18‰ у NI) — разница «тема с физикой → инженерия» vs «чисто инженерная».

Выход: case_studies/004_ni_coils/plots/plot_s2_v2_fp_vs_ni.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "case_studies" / "004_ni_coils" / "plots" / "plot_s2_v2_fp_vs_ni.png"

fp = json.loads((ROOT / "results/case_signals/semantic_v2_fluxpump.json").read_text(encoding="utf-8"))
ni = json.loads((ROOT / "results/case_signals/semantic_v2_ni.json").read_text(encoding="utf-8"))

fp_periods = [p for p in fp if p != "_meta"]
ni_periods = [p for p in ni if p != "_meta"]
x1 = list(range(len(fp_periods)))
x2 = list(range(len(ni_periods)))

fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=True)

# Flux pump
ax = axes[0]
fp_e = [fp[p]["eng_per_1000"] for p in fp_periods]
fp_f = [fp[p]["eff_per_1000"] for p in fp_periods]
ax.plot(x1, fp_e, marker="o", linewidth=2.5, color="#1f77b4", label="инженерная ‰")
ax.plot(x1, fp_f, marker="s", linewidth=2.5, color="#ff7f0e", label="фундаментальная ‰")
ax.fill_between(x1, fp_f, fp_e, alpha=0.1, color="#1f77b4")
ax.set_xticks(x1); ax.set_xticklabels(fp_periods, rotation=30, ha="right", fontsize=8)
ax.set_title("003 Flux pump\n(физ. тема → инженерия)", fontsize=11, fontweight="bold")
ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax.annotate("Фундамент ВЫСОКИЙ\n(52-80‰ — физика)", xy=(5, 64), xytext=(0.3, 100),
            arrowprops=dict(arrowstyle="->", color="#ff7f0e"), fontsize=9, color="#b35900")

# NI
ax = axes[1]
ni_e = [ni[p]["eng_per_1000"] for p in ni_periods]
ni_f = [ni[p]["eff_per_1000"] for p in ni_periods]
ax.plot(x2, ni_e, marker="o", linewidth=2.5, color="#2ca02c", label="инженерная ‰")
ax.plot(x2, ni_f, marker="s", linewidth=2.5, color="#d62728", label="фундаментальная ‰")
ax.fill_between(x2, ni_f, ni_e, alpha=0.1, color="#2ca02c")
ax.set_xticks(x2); ax.set_xticklabels(ni_periods, rotation=30, ha="right", fontsize=8)
ax.set_title("004 NI-coils\n(инженерная с рождения)", fontsize=11, fontweight="bold")
ax.legend(fontsize=8); ax.grid(alpha=0.3)
ax.annotate("Фундамент НИЗКИЙ\n(12-18‰)", xy=(2, 14), xytext=(3.1, 70),
            arrowprops=dict(arrowstyle="->", color="#d62728"), fontsize=9, color="#b30000")

plt.suptitle("S2 v2: flux pump vs NI-coils — продвинутый пайплайн (плотность лексики ‰)\n"
             "Различие: фундаментальная составляющая (52-80‰ vs 12-18‰)",
             fontsize=13, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.9])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
