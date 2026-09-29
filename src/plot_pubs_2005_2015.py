#!/usr/bin/env python3
"""График: публикационная активность SMES vs BESS 2005-2015 (окно ВТСП-SMES тренда).

Фокус на 2005-2015: рост SMES-публикаций (видимость тренда) vs взрыв BESS,
пересечение 2009. Выход: case_studies/005_SMES/plots/plot_pubs_2005_2015.png
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data/raw/openalex/smes_vs_bess_counts.json").read_text(encoding="utf-8"))
OUT = ROOT / "case_studies" / "005_SMES" / "plots" / "plot_pubs_2005_2015.png"

counts = DATA["counts"]
years = list(range(2005, 2016))
sm = [counts["SMES"].get(str(y), 0) for y in years]
be = [counts["BESS"].get(str(y), 0) for y in years]
sc = [counts["Supercap"].get(str(y), 0) for y in years]

fig, ax = plt.subplots(figsize=(12, 6.5))
ax.plot(years, sm, "o-", color="#c9211e", lw=2.5, ms=7, label="SMES")
ax.plot(years, be, "s-", color="#1f77b4", lw=2.5, ms=7, label="BESS (Li-ion)")
ax.plot(years, sc, "d--", color="#9467bd", lw=1.5, ms=5, alpha=0.7, label="Суперконденсаторы")

# Заполнение: зона где BESS > SMES
import numpy as np
x = np.array(years)
ax.fill_between(x, np.array(be), np.array(sm), where=np.array(be) > np.array(sm),
                color="#1f77b4", alpha=0.08, interpolate=True)

# Пересечение
ax.plot(2009, counts["SMES"].get("2009", 0), "o", ms=16, mfc="none", mec="#1f77b4", mew=3, zorder=5)
ax.annotate("2009: BESS впервые > SMES\n(ранний сигнал ложности тренда)",
            xy=(2009, 28), xytext=(2006.5, 100),
            arrowprops=dict(arrowstyle="->", color="#1f77b4", lw=1.5),
            fontsize=10, color="#1f77b4", fontweight="bold")

# Окно и события
ax.axvspan(2003, 2012, color="#2ca02c", alpha=0.1)
ax.text(2003.2, 148, "Окно «ВТСП-SMES как тренд» (2003-2012)\nK-SMES: 600kJ построен 2006-09",
        fontsize=9, color="#2ca02c", va="top")
for y, lab in [(2006, "600kJ\nпостроен"), (2012, "K-SMES\nзакрыт")]:
    ax.axvline(y, color="green", ls=":", lw=1)
    ax.text(y, 132, lab, rotation=0, fontsize=8, color="green", ha="center", va="top")

ax.set_xlim(2005, 2015.5)
ax.set_ylim(0, 165)
ax.set_xlabel("Год")
ax.set_ylabel("Число публикаций (OpenAlex title.search)")
ax.set_title("Публикационная активность: SMES vs BESS, 2005-2015 (кейс 005)\n"
             "SMES «выглядит трендом» (K-SMES), но BESS обгоняет с 2009")
ax.legend(fontsize=10, loc="upper left")
ax.grid(alpha=0.3)

fig.text(0.01, 0.01,
         "Источник: OpenAlex title.search + group_by publication_year (2026-09-02).\n"
         "SMES: \"superconducting magnetic energy storage\"; BESS: \"battery energy storage system\".",
         fontsize=8, style="italic", color="gray")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
