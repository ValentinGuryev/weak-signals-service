#!/usr/bin/env python3
"""График S5: цитирования ядра теплопроводной электроизоляции по годам.

Индикатор S5: «куда и как упираются конкуренты». Ядро = 32 работы по
теплопроводной ЭЛЕКТРОизоляции (insulation_thermal + insulation_materials, cit>=10).
R_ct (контактное сопротивление) и smart-изоляция (varistor/V2O3) — ИСКЛЮЧЕНЫ.

Данные: data/raw/openalex/s5_insulation_core_counts.json (OpenAlex counts_by_year).
Выход: case_studies/004_ni_coils/plots/plot_s5_insulation_core_citations.png
"""
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
COUNTS = ROOT / "data" / "raw" / "openalex" / "s5_insulation_core_counts.json"
OUT = ROOT / "case_studies" / "004_ni_coils" / "plots" / "plot_s5_insulation_core_citations.png"

works = json.loads(COUNTS.read_text(encoding="utf-8"))

# Цитирования ядра по годам
cites = defaultdict(int)
pub_years = defaultdict(int)
for w in works:
    py = w.get("year")
    if py and 1990 <= py <= 2026:
        pub_years[py] += 1
    for c in w.get("counts_by_year") or []:
        y = c.get("year")
        if y and 1990 <= y <= 2026:
            cites[y] += c.get("cited_by_count", 0)

all_years = list(range(1990, 2027))
cites_vals = [cites.get(y, 0) for y in all_years]
pub_vals = [pub_years.get(y, 0) for y in all_years]

fig, ax1 = plt.subplots(figsize=(13, 6.5))

# Основная ось: цитирования (bar)
ax1.bar(all_years, cites_vals, color="#1f77b4", alpha=0.85, label="Цитирования ядра (сумма)")
ax1.set_xlabel("Год")
ax1.set_ylabel("Число цитирований ядра в год", color="#1f77b4")
ax1.tick_params(axis="y", labelcolor="#1f77b4")
max_c = max(cites_vals)
ax1.set_ylim(0, max_c * 1.35)

# Вторая ось: новые публикации ядра (линия)
ax2 = ax1.twinx()
ax2.plot(all_years, pub_vals, color="#d62728", marker="o", ms=4, lw=1.5,
         label="Новые публикации ядра в год")
ax2.set_ylabel("Число новых публикаций ядра в год", color="#d62728")
ax2.tick_params(axis="y", labelcolor="#d62728")
ax2.set_ylim(0, max(pub_vals) * 3 + 1)

# Вехи
milestones = [
    (2010, "Sumption: ZnO-изоляция\nне дала выигрыша", "darkred"),
    (2013, "Ультратонкий полиимид\n(electrodeposition)", "darkblue"),
    (2019, "Эпоксид+BN-наполнители\n(k~0.5 W/mK, предел)", "darkred"),
    (2023, "Пик цитирований ядра\n(84)", "darkgreen"),
    (2025, "Спад (тема на плато)", "darkred"),
]
for y, label, color in milestones:
    if y < 1990 or y > 2026:
        continue
    tot = cites.get(y, 0)
    yt = max_c * (1.04 + 0.07 * (milestones.index((y, label, color)) % 3))
    ax1.annotate(label, xy=(y, tot), xytext=(y, yt),
                 arrowprops=dict(arrowstyle="->", color=color, lw=1),
                 fontsize=7.5, color=color, ha="center",
                 bbox=dict(boxstyle="round,pad=0.25", facecolor="#fff", alpha=0.85, edgecolor=color))

ax1.set_title("S5: Ядро теплопроводной ЭЛЕКТРОизоляции — цитирования по годам (кейс 004)\n"
              f"32 работы, суммарно {sum(cites.values())} цитирований, {min(works, key=lambda w: w['year'] or 0)['year']}-2026\n"
              "R_ct и smart-изоляция ИСКЛЮЧЕНЫ (отдельные подтемы)")
ax1.set_xticks(all_years[::2])
ax1.grid(axis="y", alpha=0.3)

# Пояснение
ax1.text(0.985, 0.50,
         "S5: «куда упираются конкуренты»\n"
         "• Цитирования растут 2012→2023 (11→84)\n"
         "• Пик 2023, затем СПАД 2024-26\n"
         "• Новые публикации — единицы/год (плато)\n"
         "• Вывод: тема «теплопроводная изоляция»\n"
         "  достигла насыщения, НО не решила проблему\n"
         "  (изоляция не даёт току уйти поперёк)\n"
         "• Конкуренция ушла в R_ct (эволюция NI)",
         transform=ax1.transAxes, fontsize=8.5, va="center", ha="right",
         bbox=dict(boxstyle="round", facecolor="#eef", alpha=0.85, edgecolor="#999"))

# Легенды
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, fontsize=9, loc="upper left")

fig.text(0.01, 0.01,
         "Источник: OpenAlex counts_by_year, ядро = 32 работы (insulation_thermal + insulation_materials, cit>=10).\n"
         "Скрипт: src/openalex_s5_insulation_counts.py + src/plot_s5_insulation_core_citations.py\n"
         "S5: индикатор «куда и как упираются конкуренты» — плато/насыщение без решения проблемы.",
         fontsize=8, style="italic", color="gray")

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
