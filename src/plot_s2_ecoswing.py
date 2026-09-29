#!/usr/bin/env python3
"""График S2 (шаг 4б GUIDE): семантический сдвиг в корпусе EcoSwing.

Панель A: смена фокуса — ключевые слова по периодам (‰ на 1000 слов):
  тема остывает (wind/turbine), растут интеграция/эффективность/водород.
Панель B: фокус-группы (приложение-драйвер, инженерия/zrenость, фундамент, материал) —
  стадия зрелости по периодам.
Выход: case_studies/010_ecoswing_sc_wind/plots/plot_s2_semantic_shift.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
TRENDS = ROOT / "results" / "case_signals" / "wordshift_trends_ecoswing.json"
OUT = ROOT / "case_studies" / "010_ecoswing_sc_wind" / "plots" / "plot_s2_semantic_shift.png"

res = json.loads(TRENDS.read_text(encoding="utf-8"))
periods = res["periods"]
tr = res["trends"]

FOCUS = {
    "приложение-драйвер": ["offshore", "onshore", "nacelle", "tower", "drivetrain", "gearbox",
                            "directdrive", "aircraft", "hydrogen", "microgrid", "grid", "storag"],
    "инженерия (S2)": ["cooling", "cryogenic", "efficiency", "torque", "density",
                        "reliability", "maintenance", "cost", "industrial", "commercial",
                        "prototype", "fabrication", "manufactur", "scaleup", "testing",
                        "optimiz", "integration", "rotor", "stator", "armature", "design"],
    "фундамент/эффект": ["discovery", "mechanism", "theoret", "fundament", "phenomen",
                          "novel", "breakthrough", "record", "insight", "physics"],
    "материал/архитектура": ["coatedconductor", "mgb2", "magnet", "fieldcoil", "winding",
                              "coil", "permanentmagnet", "ferrite", "ndfeb", "rareearth",
                              "induction", "synchronous"],
}


def freq(word: str) -> list[float]:
    return tr.get(word, {}).get("freqs", [0.0] * len(periods))


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Панель A: смена фокуса (конкретные слова)
words_a = [("wind", "#d62728"), ("turbin", "#ff7f0e"), ("effici", "#2ca02c"),
           ("integr", "#1f77b4"), ("hydrogen", "#9467bd"), ("stator", "#8c564b")]
for w, c in words_a:
    ax1.plot(periods, freq(w), marker="o", label=f"«{w}»", color=c, lw=2)
ax1.set_title("Смена фокуса: тема остывает (wind/turbine ↓),\nрастут efficiency/integration/hydrogen ↑", fontsize=10.5)
ax1.set_ylabel("частота, ‰ (на 1000 слов)")
ax1.legend(fontsize=8, ncol=2)
ax1.grid(alpha=0.3)
ax1.tick_params(axis="x", rotation=30)

# Панель B: фокус-группы (стадия зрелости)
for g, words in FOCUS.items():
    sums = [sum(freq(w)[i] for w in words) for i in range(len(periods))]
    ax2.plot(periods, sums, marker="s", lw=2, label=f"{g}")
ax2.set_title("Фокус-группы лексики: стадия зрелости\n(пик инженерии 2015-19, экономика не растёт)", fontsize=10.5)
ax2.set_ylabel("суммарная частота группы, ‰")
ax2.legend(fontsize=8)
ax2.grid(alpha=0.3)
ax2.tick_params(axis="x", rotation=30)

fig.suptitle("S2 — семантический сдвиг: СП-генераторы для ветра (кейс 010 EcoSwing)",
             fontsize=12.5)
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("saved:", OUT)