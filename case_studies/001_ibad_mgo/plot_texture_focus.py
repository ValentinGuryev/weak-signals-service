#!/usr/bin/env python3
"""График: «исследовательский фокус уходит из технологии» — убывание текстура-лексики.

Маркер S2 v4 (semantic_markers_v4.md): сумма частот слов текстура/IBAD/ориентация
(textur, biaxial, ibad, ysz, assist, orient, align, epitaxi) на 1000 слов по периодам.

Источник: OpenAlex-корпус абстрактов IBAD (426 работ, 1997-2026).

Выход: case_studies/001_ibad_mgo/plots/plot5_texture_focus.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
DISC = json.loads((ROOT / "results/case_signals/wordshift_trends_openalex.json")
                  .read_text(encoding="utf-8"))
OUT = ROOT / "case_studies" / "001_ibad_mgo" / "plots"

# Текстура/IBAD-лексика (технология шаблона)
TEXTURE_WORDS = ["textur", "biaxial", "ibad", "ysz", "assist", "orient", "align", "epitaxi"]
COLORS = {
    "textur": "#1F618D", "biaxial": "#2980B9", "ibad": "#2E86C1",
    "ysz": "#5499C7", "assist": "#85C1E9", "orient": "#A9CCE3",
    "align": "#AED6F1", "epitaxi": "#D4E6F1",
}

periods = DISC["periods"]
totals = DISC["period_totals"]

# частоты по словам
freq_by_word = {m["word"]: m["freqs"] for m in DISC["ranked"] if m["word"] in TEXTURE_WORDS}
# сумма
sums = np.array([sum(freq_by_word[w][i] for w in TEXTURE_WORDS if w in freq_by_word)
                 for i in range(len(periods))])
# без последнего шумного периода — линейная аппроксимация
x_clean = np.arange(len(periods) - 1)
y_clean = sums[:-1]
k, b = np.polyfit(x_clean, y_clean, 1)

fig, ax = plt.subplots(figsize=(11, 6.5))

# Стек-области по словам
bottom = np.zeros(len(periods))
x = np.arange(len(periods))
for w in TEXTURE_WORDS:
    if w not in freq_by_word:
        continue
    ax.bar(x, freq_by_word[w], bottom=bottom, width=0.6, color=COLORS[w],
           alpha=0.85, label=w, edgecolor="white", lw=0.4)
    bottom += freq_by_word[w]

# Сумма + тренд (без последнего периода)
ax.plot(x, sums, "o-", color="#C0392B", lw=2.5, ms=7, label="Сумма текстура-лексики (‰)")
trend_x = x_clean
trend_y = k * trend_x + b
ax.plot(trend_x, trend_y, "--", color="#C0392B", lw=1.5, alpha=0.7,
        label=f"Линейный тренд (1997-2021): −{abs(k):.0f}‰/период")

# Доверительные интервалы (пер-документный бутстрап, 95%)
# (значения из анализа: суммы с ДИ)
ci_vals = [(64.7, 53.6, 78.2), (51.6, 45.2, 58.4), (45.2, 37.2, 53.0),
           (34.4, 25.8, 41.7), (23.4, 15.0, 32.8), (29.0, 16.0, 44.1)]
means = [v[0] for v in ci_vals]
los = [v[1] for v in ci_vals]
his = [v[2] for v in ci_vals]
ax.errorbar(x, means, yerr=[np.array(means) - np.array(los), np.array(his) - np.array(means)],
            fmt="none", ecolor="#C0392B", elinewidth=1.5, capsize=4, alpha=0.6,
            label="95% ДИ (бутстрап по документам)")

# Аннотации
ax.annotate(f"×3 падение\n(67→22‰)", xy=(4, 22), xytext=(1.2, 45),
            fontsize=11, color="#C0392B", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="#C0392B", lw=1.5))
ax.annotate("2022-2026: малая выборка (19 работ),\nотскок частично реален\n(Fe(Se,Te), широкие ленты)",
            xy=(5, 28), xytext=(3.2, 55), fontsize=9, color="#888",
            arrowprops=dict(arrowstyle="->", color="#888", lw=1))

ax.set_xticks(x)
ax.set_xticklabels([f"{p}\n({totals[p]//1000:.0f}k слов)" for p in periods], fontsize=9)
ax.set_ylabel("Частота на 1000 слов (‰)", fontsize=12)
ax.set_xlabel("Период (статьи OpenAlex по IBAD)", fontsize=12)
ax.set_title("S2 v4: исследовательский фокус уходит из технологии\n"
             "Убывание текстура/IBAD-лексики в абстрактах статей (1997-2026)",
             fontsize=13, fontweight="bold")
ax.legend(fontsize=8, loc="upper right", ncol=2)
ax.grid(axis="y", alpha=0.3)
ax.set_ylim(0, 80)

ax.text(0.99, 0.02,
        "Данные: OpenAlex, 426 работ IBAD-семейства, 364 с абстрактами.\n"
        "Лексика: texture, biaxial, IBAD, YSZ, ion-beam assisted, orientation, alignment, epitaxial.\n"
        "Вывод: тема «как сделать текстуру» ушла из фокуса статей — технология стала рутиной (зрелость).",
        transform=ax.transAxes, fontsize=8, color="#999", va="bottom", ha="right")

plt.tight_layout()
out = OUT / "plot5_texture_focus.png"
OUT.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=160, bbox_inches="tight")
plt.close(fig)
print(f"График 5 → {out}")
print(f"\nСумма текстура-лексики по периодам: {['%.1f' % s for s in sums]}")
print(f"Тренд (без 2022-26): k={k:.2f}‰/период, b={b:.2f}")
