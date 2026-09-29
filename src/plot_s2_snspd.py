#!/usr/bin/env python3
"""График S2 для кейса 006 (SNSPD): семантические сдвиги по Медведеву.

Данные: results/case_signals/wordshift_trends_snspd.json (wordshift + LLM-фильтр).
Показывает частоты (‰) ключевых терминов по периодам — сдвиги, выявленные в semantic_s2.md:
  Рост: quantum, imaging, lidar, temporal, array (применения расширяются)
  Угасание/смена: sspd→snspd (термин), nbn→wsi/nbtin (материал), efficiency (остыла)
Выход: case_studies/006_snspd/plots/plot_s2_semantic_shift.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "case_studies" / "006_snspd" / "plots" / "plot_s2_semantic_shift.png"

d = json.loads((ROOT / "results/case_signals/wordshift_trends_snspd.json").read_text(encoding="utf-8"))
ranked = {m["word"]: m for m in d["ranked"]}
periods = d["periods"]
x = list(range(len(periods)))

def series(words):
    """Серию частот (‰) для списка слов."""
    out = []
    for w in words:
        m = ranked.get(w)
        out.append(m["freqs"] if m else [0] * len(periods))
    return out

fig, axes = plt.subplots(1, 2, figsize=(16, 6.5))

# Панель 1: РОСТ — применения расширяются + квантовый контекст
ax = axes[0]
grow_sets = [
    ("quantum", "#1f77b4", "o-", "quantum (квантовый контекст)"),
    ("imaging", "#d62728", "o-", "imaging (имиджинг)"),
    ("lidar", "#ff7f0e", "s-", "lidar"),
    ("temporal", "#2ca02c", "s-", "temporal (врем. разрешение)"),
    ("array", "#9467bd", "^--", "array (массивы)"),
]
for w, c, m, label in grow_sets:
    f = series([w])[0]
    ax.plot(x, f, m, linewidth=2.2, color=c, label=label, markersize=6)
ax.set_xticks(x); ax.set_xticklabels(periods, rotation=30, ha="right")
ax.set_ylabel("частота, ‰ (нормировка на корпус)")
ax.set_title("РОСТ: применения расширяются + квантовый контекст\n(после LLM-фильтра оборотов)", fontsize=11, fontweight="bold")
ax.legend(fontsize=8, loc="upper left"); ax.grid(alpha=0.3)

# Панель 2: УГАСАНИЕ/СМЕНА — термин, материал, параметр
ax = axes[1]
fall_sets = [
    ("sspd", "#8c564b", "o-", "термин SSPD (→ SNSPD)"),
    ("snspd", "#1f77b4", "o--", "термин SNSPD"),
    ("nbn", "#d62728", "s-", "материал NbN (→ NbTiN/WSi)"),
    ("wsi", "#2ca02c", "s--", "материал WSi (аморфный)"),
    ("efficiency", "#ff7f0e", "^-", "efficiency (остыла — предел достигнут)"),
]
for w, c, m, label in fall_sets:
    f = series([w])[0]
    ax.plot(x, f, m, linewidth=2.2, color=c, label=label, markersize=6)
ax.set_xticks(x); ax.set_xticklabels(periods, rotation=30, ha="right")
ax.set_ylabel("частота, ‰ (нормировка на корпус)")
ax.set_title("СМЕНА: термин SSPD→SNSPD, материал NbN→WSi,\nбазовый параметр efficiency остывает", fontsize=11, fontweight="bold")
ax.legend(fontsize=8, loc="upper right"); ax.grid(alpha=0.3)

plt.suptitle("S2 кейс 006 (SNSPD): семантические сдвиги по Медведеву (wordshift + LLM-фильтр)\n"
             "термины с монотонным трендом, частота на 1000 слов", fontsize=13, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.92])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
