#!/usr/bin/env python3
"""График взаимных цитирований кластеров текстурирования (кейс 001).

4 кластера-конкурента одной проблемы (текстурированная подложка 2G-лент):
IBAD-MgO / IBAD-YSZ / RABiTS / ISD.

Две панели:
1. Тепловая карта полной матрицы взаимных цитирований (% ссылок A на корпус B);
2. Динамика ключевых пар по периодам (1991-2005 / 2006-2015 / 2016-2026).

Данные: ibad_abstracts_corpus.json (tech-разметка), ibad_references.json.
Выход: case_studies/001_ibad_mgo/plots/plot_s3_cross_texturing.png
"""
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "raw" / "openalex" / "ibad_abstracts_corpus.json"
REFS = ROOT / "data" / "raw" / "openalex" / "ibad_references.json"
OUT = ROOT / "case_studies" / "001_ibad_mgo" / "plots" / "plot_s3_cross_texturing.png"

w = json.loads(CORPUS.read_text(encoding="utf-8"))["works"]
refs = json.loads(REFS.read_text(encoding="utf-8"))

MAIN = ["ibad_mgo", "ibad_ysz", "rabits", "isd"]
LABEL = {"ibad_mgo": "IBAD-MgO", "ibad_ysz": "IBAD-YSZ", "rabits": "RABiTS", "isd": "ISD"}
year_of = {x["id"]: x["year"] for x in w}
clusters = defaultdict(set)
for x in w:
    if x.get("tech") in MAIN:
        clusters[x["tech"]].add(x["id"])

PERIODS = [("1991-2005", 1991, 2005), ("2006-2015", 2006, 2015), ("2016-2026", 2016, 2026)]


def cross(a, b, y0=None, y1=None):
    a_ids = [i for i in clusters[a] if year_of.get(i) and (y0 is None or y0 <= year_of[i] <= y1)]
    if not a_ids:
        return 0.0
    tot = 0; hits = 0
    for wid in a_ids:
        rl = refs.get(wid) or []
        tot += len(rl)
        hits += sum(1 for r in rl if r in clusters[b])
    return 100 * hits / tot if tot else 0.0


# Полная матрица
M = np.zeros((4, 4))
for i, a in enumerate(MAIN):
    for j, b in enumerate(MAIN):
        if i != j:
            M[i, j] = cross(a, b)

# Динамика избранных пар
dyn_pairs = [("ibad_mgo", "rabits"), ("ibad_ysz", "rabits"),
             ("isd", "ibad_mgo"), ("ibad_ysz", "isd")]
dyn = {f"{LABEL[a]}→{LABEL[b]}": [cross(a, b, y0, y1) for _, y0, y1 in PERIODS]
       for a, b in dyn_pairs}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.2),
                               gridspec_kw={"width_ratios": [1, 1.25]})

# --- Панель 1: тепловая карта ---
im = ax1.imshow(M, cmap="YlOrRd", vmin=0, vmax=7)
ax1.set_xticks(range(4)); ax1.set_yticks(range(4))
ax1.set_xticklabels([LABEL[b] for b in MAIN], rotation=40, ha="right", fontsize=9)
ax1.set_yticklabels([LABEL[a] for a in MAIN], fontsize=9)
ax1.set_title("Полная матрица: % ссылок A→B\n(все эпохи 1991-2026)", fontsize=11)
for i in range(4):
    for j in range(4):
        if i != j:
            ax1.text(j, i, f"{M[i, j]:.1f}%", ha="center", va="center",
                     fontsize=10, color="black" if M[i, j] < 4 else "white")
        else:
            ax1.text(j, i, "—", ha="center", va="center", fontsize=10, color="#999")
fig.colorbar(im, ax=ax1, shrink=0.85, label="% ссылок")

# --- Панель 2: динамика ---
x = np.arange(len(PERIODS))
colors = {"IBAD-MgO→RABiTS": "#1f77b4", "IBAD-YSZ→RABiTS": "#d62728",
          "ISD→IBAD-MgO": "#2ca02c", "IBAD-YSZ→ISD": "#9467bd"}
for pair, vals in dyn.items():
    ax2.plot(x, vals, marker="o", lw=2, label=pair, color=colors.get(pair))
ax2.set_xticks(x)
ax2.set_xticklabels([p for p, _, _ in PERIODS])
ax2.set_xlabel("Период")
ax2.set_ylabel("% ссылок A на корпус B")
ax2.set_title("Динамика взаимных цитирований по периодам\n(ключевые пары)", fontsize=11)
ax2.grid(axis="y", alpha=0.3)
ax2.legend(fontsize=8, loc="upper left")
ax2.axhline(0.3, color="gray", ls=":", lw=1)
ax2.text(2.02, 0.35, "уровень изоляции fp/joint (0.3%)", fontsize=7, color="gray", ha="right")

fig.suptitle("Взаимные цитирования кластеров текстурирования: IBAD-MgO / IBAD-YSZ / RABiTS / ISD (кейс 001)\n"
             "НЕТ изоляции: 0.5-4.3% взаимных ссылок (fp/joint = 0.3%). Одно сообщество, общий фундамент (Jaccard 5-13%).",
             fontsize=11.5, fontweight="bold")
fig.text(0.01, 0.01,
         "Источник: OpenAlex, ibad_abstracts_corpus (427 работ, tech-разметка) + ibad_references (424).\n"
         "Диагональ опущена (внутрикластерные ссылки). Метод: % ссылок работ кластера A на корпус кластера B.\n"
         "Разбор: case_studies/001_ibad_mgo/signals/s3_cross_texturing_clusters.md",
         fontsize=7.5, style="italic", color="gray")

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
