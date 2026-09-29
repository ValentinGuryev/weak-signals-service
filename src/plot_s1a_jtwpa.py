#!/usr/bin/env python3
"""S1a-график кейса 007: JTWPA vs KITWPA vs JPA (публикации, OpenAlex).

Динамика публикаций по годам: JTWPA-ядро (кейс), KITWPA (сосед),
JPA резонаторный (конкурент-предшественник). Выход:
case_studies/007_jtwpa/plots/plot_s1a_pubs.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data/raw/openalex/jtwpa_counts.json").read_text(encoding="utf-8"))
OUT = ROOT / "case_studies" / "007_jtwpa" / "plots" / "plot_s1a_pubs.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

ca = {int(k): v for k, v in DATA["counts_A"].items()}
cb = {int(k): v for k, v in DATA["counts_B"].items()}
cc = {int(k): v for k, v in DATA.get("counts_C", {}).items()}
years = list(range(2007, 2027))

SERIES = [
    ("JTWPA (ядро)", ca, "#c9211e", "o-", sum(ca.values())),
    ("KITWPA (сосед)", cb, "#2ca02c", "s-", sum(cb.values())),
    ("JPA резонаторный (конкурент)", cc, "#1f77b4", "^-", sum(cc.values())),
]

fig, ax = plt.subplots(figsize=(12, 6.5))
for label, counts, color, fmt, tot in SERIES:
    vals = [counts.get(y, 0) for y in years]
    ax.plot(years, vals, fmt, color=color, lw=2, ms=4, label=f"{label} ({tot})")

ax.axvline(2018, color="gray", ls="--", lw=1)
ax.text(2018, ax.get_ylim()[1]*0.97 if False else 40, "сигнал 2018", rotation=90,
        va="top", fontsize=9, color="gray")

ax.annotate("Macklin 2015\n(Science, 833 цит.)\nquantum-limited прорыв",
            xy=(2015, 6), xytext=(2008.5, 16),
            arrowprops=dict(arrowstyle="->", color="#c9211e"),
            fontsize=9, color="#c9211e")
ax.annotate("плоско 5-7/год 2014-2020\n(ранняя фаза)",
            xy=(2018, 5), xytext=(2012, 24),
            arrowprops=dict(arrowstyle="->", color="#555555"),
            fontsize=9, color="#555555")
ax.annotate("взлёт 2021+ (×4): масштабирование\nкубитов + аксионы + DARTWARS",
            xy=(2024, 30), xytext=(2019.5, 40),
            arrowprops=dict(arrowstyle="->", color="#c9211e"),
            fontsize=9, color="#c9211e")
ax.annotate("JPA: 431 (×2.3 от JTWPA),\nзрелый резонаторный класс",
            xy=(2025, 46), xytext=(2020, 36),
            arrowprops=dict(arrowstyle="->", color="#1f77b4"),
            fontsize=8.5, color="#1f77b4")

ax.set_xlabel("Год")
ax.set_ylabel("Публикаций в год (OpenAlex, title+abstract)")
ax.set_title("JTWPA vs KITWPA vs JPA — динамика публикаций (кейс 007)")
ax.legend(loc="upper left", fontsize=9)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT, dpi=150)
print(f"Сохранено: {OUT}")
