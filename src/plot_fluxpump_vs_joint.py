#!/usr/bin/env python3
"""График: динамика публикаций flux pump (CC) vs сверхпроводящее соединение ВТСП-2G.

Экспертная гипотеза (пользователь): flux pump ценен, ПОКА нет сверхпроводящего
соединения ВТСП-2G. Если соединение удастся — ценность насоса упадёт.

Данные: data/raw/openalex/fluxpump_vs_joint_counts.json
Выход: case_studies/003_flux_pump_space/plots/plot9_fluxpump_vs_joint.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
AGG = ROOT / "data" / "raw" / "openalex" / "fluxpump_vs_joint_counts.json"
OUT = ROOT / "case_studies" / "003_flux_pump_space" / "plots" / "plot9_fluxpump_vs_joint.png"

agg = json.loads(AGG.read_text(encoding="utf-8"))
years = agg["years"]
labels = {"Flux pump (CC)": "Flux pump на CC (HTS)", "Сверхпроводящее соединение": "Сверхпроводящее соединение ВТСП-2G"}
colors = {"Flux pump (CC)": "#1f77b4", "Сверхпроводящее соединение": "#d62728"}

fig, ax = plt.subplots(figsize=(12, 6.5))

for topic in ["Flux pump (CC)", "Сверхпроводящее соединение"]:
    cnt = agg["counts"][topic]
    off = -0.2 if topic.startswith("Flux") else 0.2
    ax.bar([y + off for y in years], cnt, width=0.4, label=labels[topic],
           color=colors[topic], alpha=0.85)

# Аннотации ключевых точек
fp = agg["counts"]["Flux pump (CC)"]
jt = agg["counts"]["Сверхпроводящее соединение"]
ax.annotate("Взрыв flux pump\n(2019-2021)", xy=(2020, fp[years.index(2020)]),
            xytext=(2010, 35), arrowprops=dict(arrowstyle="->", color="#1f77b4"),
            fontsize=9, color="#1f77b4")
ax.annotate("Пик соединений\n(2019), стабильно 5-14", xy=(2019, jt[years.index(2019)]),
            xytext=(2003, 15), arrowprops=dict(arrowstyle="->", color="#d62728"),
            fontsize=9, color="#d62728")

ax.set_xlabel("Год")
ax.set_ylabel("Число публикаций (OpenAlex, title+abstract)")
ax.set_title("Динамика публикаций: flux pump на CC vs сверхпроводящее соединение ВТСП-2G\n(кейс 003 — конкуренция технологий)")
ax.legend(fontsize=9)
ax.grid(axis="y", alpha=0.3)
ax.set_xticks(range(min(years), max(years)+1, 2))

fig.text(0.01, 0.01, "OpenAlex через прокси, 2026-08-31. title_and_abstract.search + SC-фильтр.\n"
         "Flux pump: 290 работ. Соединение: 104 работы. Гипотеза: соединение = конкурент flux pump.",
         fontsize=8, style="italic", color="gray")

plt.tight_layout()
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
