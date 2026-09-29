#!/usr/bin/env python3
"""График: статьи по годам — RCE (reactive co-evaporation) vs TLAG + SNF-доклады.

Данные (ОБНОВЛЕНО 2026-09-01):
- Новый корпус: data/raw/openalex/rce_tlag_corpus.json (RCE 48, TLAG 29)
- SNF-доклады (конференции IEEE-CSC/ESAS): из анализа имён файлов

Показывает:
- Сплошные столбцы: статьи OpenAlex (RCE/co-evap 48, TLAG 29)
- Пунктирные маркеры: SNF-доклады (RCE 6, TLAG 8) — конференционная активность

Выход: case_studies/002_rce_dr_sunam/plots/plot8_rcetlag_pubs.png (перезаписан)
"""
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "raw" / "openalex" / "rce_tlag_corpus.json"
OUT = ROOT / "case_studies" / "002_rce_dr_sunam" / "plots" / "plot8_rcetlag_pubs.png"

corpus = json.loads(CORPUS.read_text(encoding="utf-8"))

# Топики в новом корпусе
by_method = {"RCE co-evaporation": [], "TLAG": []}
for w in corpus:
    t = w.get("topic", "")
    if t == "RCE/co-evap":
        by_method["RCE co-evaporation"].append(w.get("year") or 0)
    elif t == "TLAG":
        by_method["TLAG"].append(w.get("year") or 0)

# SNF-доклады по годам (из анализа имён файлов)
snf_rce = [2013, 2014, 2016, 2021]  # + 2 без года
snf_tlag = [2021, 2022, 2023, 2023, 2023, 2024, 2025]  # + 1 без года

colors = {"RCE co-evaporation": "#d62728", "TLAG": "#1f77b4"}
labels = {"RCE co-evaporation": "RCE co-evaporation (SuNAM)", "TLAG": "TLAG (Puig/ICMAB)"}

all_years = list(range(1988, 2027))

fig, ax = plt.subplots(figsize=(12, 6.5))

for method in ["RCE co-evaporation", "TLAG"]:
    cnt = Counter(by_method.get(method, []))
    y = [cnt.get(yr, 0) for yr in all_years]
    off = -0.2 if method.startswith("RCE") else 0.2
    ax.bar([yr + off for yr in all_years], y, width=0.4,
           label=labels[method], color=colors[method], alpha=0.85)

# SNF-доклады как пунктирные маркеры
rce_snf = [sum(1 for yr in snf_rce if yr == y) for y in all_years]
tlag_snf = [sum(1 for yr in snf_tlag if yr == y) for y in all_years]
ax.plot([y - 0.2 for y in all_years], rce_snf, '--', color="#d62728", alpha=0.6, linewidth=1.5,
        label="SNF-доклады RCE")
ax.plot([y + 0.2 for y in all_years], tlag_snf, '--', color="#1f77b4", alpha=0.6, linewidth=1.5,
        label="SNF-доклады TLAG")

# Аннотации пиков
rce_cnt = Counter(by_method["RCE co-evaporation"])
tlag_cnt = Counter(by_method["TLAG"])
rce_peak = max(rce_cnt.items(), key=lambda x: x[1]) if rce_cnt else (0, 0)
tlag_peak = max(tlag_cnt.items(), key=lambda x: x[1]) if tlag_cnt else (0, 0)
ax.annotate(f"Пик RCE: {rce_peak[0]} ({rce_peak[1]} статей)\n+ SNF-доклад 2013 (EUCAS)",
            xy=(rce_peak[0], rce_peak[1]), xytext=(1995, max(rce_peak[1], tlag_peak[1]) + 1),
            arrowprops=dict(arrowstyle="->", color="#d62728"), fontsize=9, color="#d62728")
ax.annotate(f"Пик TLAG: {tlag_peak[0]} ({tlag_peak[1]} статей)\n+ SNF-доклады 2021-2025 (Puig)",
            xy=(tlag_peak[0], tlag_peak[1]), xytext=(2012, max(rce_peak[1], tlag_peak[1]) + 0.5),
            arrowprops=dict(arrowstyle="->", color="#1f77b4"), fontsize=9, color="#1f77b4")

ax.set_xlabel("Год")
ax.set_ylabel("Число публикаций")
ax.set_title("Публикации по годам: RCE co-evaporation vs TLAG\n(OpenAlex статьи + SNF-доклады, кейс 002)")
ax.set_xticks(range(1988, 2027, 2))
ax.legend(fontsize=8)
ax.grid(axis="y", alpha=0.3)

fig.text(0.01, 0.01,
         "OpenAlex: rce_tlag_corpus.json (RCE 48, TLAG 29) — title_and_abstract.search + SC-фильтр.\n"
         "SNF-доклады: конференции IEEE-CSC/ESAS (RCE 4+2, TLAG 7+1) — не индексируются OpenAlex.\n"
         "Обновлено 2026-09-01: новый корпус (data/raw/openalex/rce_tlag_corpus.json).",
         fontsize=8, style="italic", color="gray")

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
