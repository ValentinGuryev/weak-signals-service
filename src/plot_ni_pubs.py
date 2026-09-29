#!/usr/bin/env python3
"""График: статьи по годам — NI vs MI (кейс 004).

Фикс 2026-09-01: аннотации не перекрываются — запас по ylim, подписи с фоном,
позиции вынесены за данные. Данные: 338 работ (NI 286 + MI 52).
Выход: case_studies/004_ni_coils/plots/plot_pubs_years.png
"""
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "raw" / "openalex" / "ni_coils_corpus.json"
OUT = ROOT / "case_studies" / "004_ni_coils" / "plots" / "plot_pubs_years.png"

works = json.loads(CORPUS.read_text(encoding="utf-8"))
ni_years = Counter(w["year"] for w in works if w.get("year") and w.get("subtopic") == "NI-coils")
mi_years = Counter(w["year"] for w in works if w.get("year") and w.get("subtopic") == "MI-coils")
all_years = list(range(min(ni_years.keys() | mi_years.keys()), max(ni_years.keys() | mi_years.keys()) + 1))

fig, ax = plt.subplots(figsize=(13, 6.5))
ni_vals = [ni_years.get(y, 0) for y in all_years]
mi_vals = [mi_years.get(y, 0) for y in all_years]
totals = [n + m for n, m in zip(ni_vals, mi_vals)]

ax.bar(all_years, ni_vals, color="#1f77b4", alpha=0.9, label=f"NI-coils ({sum(ni_vals)})")
ax.bar(all_years, mi_vals, bottom=ni_vals, color="#ff7f0e", alpha=0.9, label=f"MI-coils ({sum(mi_vals)})")

# Запас сверху под аннотации
max_tot = max(totals)
ax.set_ylim(0, max_tot * 1.45)

milestones = [
    (2011, "Старт NI", "darkblue", "lightblue"),
    (2016, "26 T multi-width", "darkblue", "lightblue"),
    (2020, "32.35 T рекорд", "darkblue", "lightblue"),
    (2023, "SPARC (термояд)", "darkblue", "lightblue"),
    (2026, "MI растёт (9)", "darkred", "lightsalmon"),
]
for y, label, color, bg in milestones:
    if y not in all_years:
        continue
    tot = ni_years.get(y, 0) + mi_years.get(y, 0)
    # Подпись над данными, с запасом; стрелка вниз к бару
    yt = max_tot * (1.02 + 0.06 * (milestones.index((y, label, color, bg)) % 2))
    ax.annotate(label,
                xy=(y, tot), xytext=(y, yt),
                arrowprops=dict(arrowstyle="->", color=color, lw=1),
                fontsize=8, color=color, ha="center",
                bbox=dict(boxstyle="round,pad=0.25", facecolor=bg, alpha=0.75, edgecolor=color))

ax.set_xlabel("Год")
ax.set_ylabel("Число публикаций")
ax.set_title(f"Публикации по годам: NI-coils vs MI-coils (кейс 004)\n"
             f"OpenAlex: 338 работ (NI 286 + MI 52), {all_years[0]}-{all_years[-1]}")
ax.set_xticks(all_years[::2])
ax.legend(fontsize=10, loc="upper left")
ax.grid(axis="y", alpha=0.3)

# Пояснение фаз — в углу, с фоном, не пересекает данные
ax.text(0.985, 0.97, "NI: 2011 старт → 2016-19 рост → плато 2020+ (зрелость)\n"
        "MI: 2016 появление → 2022+ рост → 2025-26 активный (эволюция NI)",
        transform=ax.transAxes, fontsize=8.5, va="top", ha="right",
        bbox=dict(boxstyle="round", facecolor="#eef", alpha=0.85, edgecolor="#999"))

fig.text(0.01, 0.01,
         "Источник: data/raw/openalex/ni_coils_corpus.json (обновлён 2026-09-01: +39 MI-работ).\n"
         "MI-coils (metal-as-insulation) докачаны отдельно — растущий подтренд.",
         fontsize=8, style="italic", color="gray")

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
