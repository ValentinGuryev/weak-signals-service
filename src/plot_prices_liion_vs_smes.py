#!/usr/bin/env python3
"""График цен: Li-ion BESS (экспоненциальное падение) vs SMES (плато) — кейс 005.

Данные:
- Li-ion pack $/кВт·ч: 1991 ~7500 (из −97% Ziegler-Trancik), 2010 ~1100 (BNEF),
  2013 ~650, 2015 ~350, 2018 ~150 (retrospective/Fadly), 2020 ~100, 2025 ~50 (retrospective).
- SMES: $250-360K/кВт·ч (Fadly 2021, $70-100K/MJ), плоская.
Лог-шкала: экспоненциальное падение Li-ion = прямая линия.
Выход: case_studies/005_SMES/plots/plot_prices_liion_vs_smes.png
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "case_studies" / "005_SMES" / "plots" / "plot_prices_liion_vs_smes.png"

# Li-ion точки (год, $/кВт·ч)
liion = [
    (1991, 7500), (2000, 2500), (2005, 1500), (2010, 1100),
    (2013, 650), (2015, 350), (2018, 150), (2020, 100), (2023, 80), (2025, 50),
]
# SMES диапазон (плоский)
smes_lo, smes_hi = 250000, 360000  # $/кВт·ч

fig, ax = plt.subplots(figsize=(12, 7))
ax.set_yscale("log")

# Li-ion
years_l = [p[0] for p in liion]
prices_l = [p[1] for p in liion]
ax.plot(years_l, prices_l, "o-", color="#1f77b4", lw=2.5, ms=6, label="Li-ion battery pack ($/кВт·ч)")

# аннотация экспоненты
ax.annotate("−13…17%/год (learning curve)\n−97% за 1991–2018 [Ziegler&Trancik, MIT]",
            xy=(2010, 1100), xytext=(1994, 3000),
            arrowprops=dict(arrowstyle="->", color="#1f77b4"), fontsize=9, color="#1f77b4")

# SMES плато (заливка диапазона)
ax.fill_between([1990, 2026], smes_lo, smes_hi, color="#c9211e", alpha=0.15)
ax.plot([1990, 2026], [smes_lo, smes_lo], "--", color="#c9211e", lw=1.5, label="SMES: $250–360K/кВт·ч (плато)")
ax.text(1991, smes_hi * 1.2, "SMES (плато, $250–360K/кВт·ч)\n[$70–100K/МДж; Fadly 2021]", color="#c9211e", fontsize=9)

# ключевые годы-маркеры
for y, lab in [(2003, "K-SMES старт"), (2012, "K-SMES закрыт"), (2014, "Gigafactory Tesla"), (2018, "точка решения"), (2025, "JRC: no facilities")]:
    ax.axvline(y, color="gray", ls=":", lw=0.8, alpha=0.6)
    ax.text(y, 400000, lab, rotation=90, fontsize=7.5, color="gray", ha="right")

ax.set_xlim(1990, 2026)
ax.set_ylim(30, 800000)
ax.set_xlabel("Год")
ax.set_ylabel("Стоимость, $/кВт·ч (лог. шкала)")
ax.set_title("Почему SMES проиграл: цена Li-ion падает экспоненциально, SMES — плоское плато (кейс 005)\n"
             "Лог-шкала: экспонента Li-ion = прямая; разрыв ~5000× к 2025")
ax.legend(fontsize=9, loc="lower left")
ax.grid(alpha=0.3, which="both")

fig.text(0.01, 0.01,
         "Источники: Li-ion — Ziegler&Trancik 2020 (MIT, −97% с 1991, 13-17%/год) + BNEF-ориентиры + retrospective (2018: $150, 2025: $50).\n"
         "SMES — Fadly 2021 ($70-100K/МДж = $250-360K/кВт·ч). Лог-шкала подчёркивает экспоненту.",
         fontsize=8, style="italic", color="gray")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
