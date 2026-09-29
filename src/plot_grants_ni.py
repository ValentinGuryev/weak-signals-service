#!/usr/bin/env python3
"""График грантового сигнала NI-coils: KAKEN (Япония) по годам + институты.

Фикс 2026-09-01: аннотации больше не перекрываются — добавлен запас по ylim,
подписи с фоном (bbox), позиции вынесены за пределы данных.
Выход: case_studies/004_ni_coils/plots/plot_grants_kaken.png
"""
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "case_studies" / "004_ni_coils" / "plots" / "plot_grants_kaken.png"

d = json.loads((ROOT / "data/raw/grants_foreign/kaken_results.json").read_text(encoding="utf-8"))
ni = [g for g in d["grants"] if "insulat" in str(g.get("query", "")).lower()]

def start_year(g):
    m = re.match(r"(\d{4})", g.get("period", ""))
    return int(m.group(1)) if m else None

from collections import Counter
by_year = Counter(start_year(g) for g in ni if start_year(g))
years = list(range(2012, 2026))
counts = [by_year.get(y, 0) for y in years]

by_inst = Counter(g.get("institution", "") for g in ni)
inst_top = by_inst.most_common(6)
inst_names = [i.replace("University", "Univ.").replace("Institute of Physical and Chemical Research", "RIKEN") for i, _ in inst_top]
inst_counts = [c for _, c in inst_top]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Панель 1: по годам
ax = axes[0]
bars = ax.bar(years, counts, color="#1f77b4", alpha=0.85)
# Запас сверху, чтобы подписи не вылезали за график
ax.set_ylim(0, max(counts) * 1.6)
ax.set_xlabel("Год старта гранта")
ax.set_ylabel("Число грантов KAKEN")
ax.set_title("Гранты KAKEN по NI-coils: 17 грантов 2012-2024\n(Япония, гос. поддержка JSPS)", fontsize=11, fontweight="bold")
ax.set_xticks(years[::2])
ax.grid(axis="y", alpha=0.3)

# Аннотации: текст над областью данных, с фоном, без пересечения с барами
ax.annotate("Стабильный поток\n1-3 гранта/год",
            xy=(2018, max(counts)), xytext=(2013.5, max(counts) * 1.35),
            arrowprops=dict(arrowstyle="->", color="darkblue"),
            fontsize=9, color="darkblue",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
ax.annotate("Активен\n2024-2026 (Waseda)",
            xy=(2024, counts[12]), xytext=(2019.5, max(counts) * 1.15),
            arrowprops=dict(arrowstyle="->", color="darkred"),
            fontsize=9, color="darkred",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightsalmon", alpha=0.7))

# Панель 2: институты
ax = axes[1]
ax.barh(inst_names[::-1], inst_counts[::-1], color="#2ca02c", alpha=0.85)
ax.set_xlim(0, max(inst_counts) * 1.3)
ax.set_xlabel("Число грантов")
ax.set_title("Институты (KAKEN, NI-coils)", fontsize=11, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
# Подпись лидера — справа от бара, не перекрывает
ax.text(max(inst_counts) + 0.15, len(inst_names) - 1, "лидер: Waseda", fontsize=9,
        color="darkgreen", va="center")

plt.suptitle("Грантовый сигнал кейса 004: NI-coils — Япония финансирует стабильно\n"
             "(государственные гранты JSPS/KAKEN, без промышленных партнёров в данных)",
             fontsize=12, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.88])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
