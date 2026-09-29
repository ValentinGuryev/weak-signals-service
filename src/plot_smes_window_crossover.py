#!/usr/bin/env python3
"""График: окно «ВТСП-SMES как тренд» (2003-2012) + точка пересечения BESS (2009).

Показывает: SMES-публикации (плато), BESS-публикации (обгон в 2009, экспонента),
окно тренда, ранние сигналы ложности. Выход: case_studies/005_SMES/plots/plot_smes_window_crossover.png
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data/raw/openalex/smes_vs_bess_counts.json").read_text(encoding="utf-8"))
OUT = ROOT / "case_studies" / "005_SMES" / "plots" / "plot_smes_window_crossover.png"

counts = DATA["counts"]
years = list(range(1990, 2026))
sm = [counts["SMES"].get(str(y), 0) for y in years]
be = [counts["BESS"].get(str(y), 0) for y in years]
sc = [counts["Supercap"].get(str(y), 0) for y in years]

fig, ax = plt.subplots(figsize=(13, 7))
ax.plot(years, sm, "o-", color="#c9211e", lw=2, label=f"SMES (плато, {sum(sm)})")
ax.plot(years, be, "s-", color="#1f77b4", lw=2, label=f"BESS (экспонента, {sum(be)})")
ax.plot(years, sc, "d-", color="#9467bd", lw=1.5, alpha=0.7, label=f"Supercap ({sum(sc)})")

# Окно ВТСП-SMES тренда 2003-2012
ax.axvspan(2003, 2012, color="#2ca02c", alpha=0.12, label="Окно «ВТСП-SMES как тренд» (2003-2012)")
# LTS-волна
ax.axvspan(1986, 2003, color="gray", alpha=0.07, label="LTS-волна (1986-2003)")
# Точка пересечения 2009
cross_idx = years.index(2009)
ax.plot(2009, counts["SMES"].get("2009", 0), "o", ms=14, mfc="none", mec="#1f77b4", mew=3)
ax.annotate("2009: BESS впервые обогнал SMES\n(ранний сигнал ложности!)",
            xy=(2009, 28), xytext=(2002, 210),
            arrowprops=dict(arrowstyle="->", color="#1f77b4"),
            fontsize=10, color="#1f77b4", fontweight="bold")

# События
events = [
    (2003, "K-SMES старт (ВТСП)"),
    (2006, "600 kJ построен"),
    (2012, "K-SMES закрыт"),
]
for y, lab in events:
    ax.axvline(y, color="green", ls=":", lw=1)
    ax.text(y, 240, lab, rotation=90, fontsize=8, color="green", ha="right")

ax.set_xlim(1990, 2026)
ax.set_ylim(0, 260)
ax.set_xlabel("Год")
ax.set_ylabel("Число публикаций (title.search)")
ax.set_title("Ложный тренд: ВТСП-SMES (2003-2012) vs BESS — публикации\n"
             "Плато SMES vs экспонента BESS; пересечение 2009 = ранний сигнал")
ax.legend(fontsize=9, loc="upper left")
ax.grid(alpha=0.3)

fig.text(0.01, 0.01,
         "Источник: OpenAlex title.search (2026-09-02). Окно 2003-2012 = ВТСП-SMES (K-SMES).\n"
         "2009: BESS впервые > SMES — сигнал ложности. Детали: signals/false_trend_signals.md",
         fontsize=8, style="italic", color="gray")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
