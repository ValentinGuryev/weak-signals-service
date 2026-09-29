#!/usr/bin/env python3
"""График: статьи по годам — теплопроводящая изоляция + контроль R_ct + smart (кейс 004).

Тема: конкурирующая технология к NI-coils (не убирать изоляцию, а улучшить её /
контролировать контактное сопротивление). Вопрос: почему не взлетела.

Данные: data/raw/openalex/hts_insulation_rct_corpus.json (254 работы, OpenAlex).
Выход: case_studies/004_ni_coils/plots/plot_insulation_rct_years.png
"""
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "raw" / "openalex" / "hts_insulation_rct_corpus.json"
OUT = ROOT / "case_studies" / "004_ni_coils" / "plots" / "plot_insulation_rct_years.png"

works = json.loads(CORPUS.read_text(encoding="utf-8"))

TOPIC_META = {
    "insulation_thermal": ("Теплопроводящая изоляция", "#1f77b4"),
    "insulation_materials": ("Изоляц. материалы (полиимид/керамика)", "#2ca02c"),
    "rct_contact": ("Контактное сопротивление R_ct", "#ff7f0e"),
    "rct_control": ("Контроль R_ct (оксиды/покрытия)", "#d62728"),
    "smart_insulation": ("Переключаемая (varistor/V₂O₃)", "#9467bd"),
}

# Только с 1995 (до этого шум: 1974, 1980-е единичные)
year_min, year_max = 1995, 2026
all_years = list(range(year_min, year_max + 1))

counts = {}
for topic, (label, color) in TOPIC_META.items():
    cy = Counter(w["year"] for w in works if w.get("year") and w["topic"] == topic and year_min <= w["year"] <= year_max)
    counts[topic] = [cy.get(y, 0) for y in all_years]

totals = [sum(counts[t][i] for t in TOPIC_META) for i in range(len(all_years))]

fig, ax = plt.subplots(figsize=(14, 7))
bottom = [0] * len(all_years)
for topic, (label, color) in TOPIC_META.items():
    vals = counts[topic]
    ax.bar(all_years, vals, bottom=bottom, color=color, alpha=0.85, label=f"{label} ({sum(vals)})")
    bottom = [b + v for b, v in zip(bottom, vals)]

max_tot = max(totals)
ax.set_ylim(0, max_tot * 1.35)

milestones = [
    (2010, "Sumption: ZnO-изоляция не дала выигрыша", "darkblue", "lightblue"),
    (2011, "Старт NI (альтернатива)", "darkgreen", "lightgreen"),
    (2016, "MI появляется (эволюция NI)", "darkgreen", "lightgreen"),
    (2020, "Lu: оксиды Ebonol C (R_ct)", "darkred", "lightsalmon"),
    (2022, "Varistor (smart-изоляция)", "purple", "lavender"),
    (2025, "RINC-провал (delamination)", "darkred", "lightsalmon"),
]
for y, label, color, bg in milestones:
    if y < year_min or y > year_max:
        continue
    tot = totals[y - year_min]
    yt = max_tot * (1.04 + 0.055 * (milestones.index((y, label, color, bg)) % 3))
    ax.annotate(label, xy=(y, tot), xytext=(y, yt),
                arrowprops=dict(arrowstyle="->", color=color, lw=1),
                fontsize=7.5, color=color, ha="center",
                bbox=dict(boxstyle="round,pad=0.25", facecolor=bg, alpha=0.8, edgecolor=color))

ax.set_xlabel("Год")
ax.set_ylabel("Число публикаций")
ax.set_title("Теплопроводящая изоляция + контроль R_ct — публикации по годам (кейс 004)\n"
             f"OpenAlex: {len(works)} работ, {year_min}-{year_max}")
ax.set_xticks(all_years[::2])
ax.legend(fontsize=9, loc="upper left", ncol=2)
ax.grid(axis="y", alpha=0.3)

ax.text(0.985, 0.55,
        "R_ct растёт (NI-экосистема), а НЕ изоляция:\n"
        "• изоляция — плато/слабо растёт\n"
        "• R_ct — рост 2016+, пик 2020-26\n"
        "• smart (varistor) — микротренд 2022+\n"
        "Вывод: конкуренция ушла в контроль\n"
        "контакта, а не в улучшение изоляции",
        transform=ax.transAxes, fontsize=8.5, va="center", ha="right",
        bbox=dict(boxstyle="round", facecolor="#eef", alpha=0.85, edgecolor="#999"))

fig.text(0.01, 0.01,
         "Источник: data/raw/openalex/hts_insulation_rct_corpus.json (254 работы, 5 подтем).\n"
         "Метод: title_and_abstract.search + SC-фильтр (см. src/openalex_hts_insulation_rct.py).\n"
         "Ключевое: рост идёт в R_ct (эволюция NI), а не в теплопроводящую изоляцию (тупик).",
         fontsize=8, style="italic", color="gray")

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
