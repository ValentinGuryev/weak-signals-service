#!/usr/bin/env python3
"""Грантовый сигнал кейса 010 (EcoSwing): ветро-специфичные СП-генераторы → интерес ПЕРВООЧЕРЕДНО ЕС.

Левая панель: таймлайн программ/грантов (ЕС-ветро-программы — ядро, выделены темно-синим/бордо;
остальные — класс «СП-машины», не ветер — серым/пунктиром).
Правая панель: ВЕТЕР-СПЕЦИФИЧНЫЕ гранты/программы по географии (ЕС = 3, США = 1(10MW), РФ/ЯП/КНР = 0).
Выход: case_studies/010_ecoswing_sc_wind/plots/plot_grants_signal.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "case_studies" / "010_ecoswing_sc_wind" / "plots" / "plot_grants_signal.png"

# (метка, старт, конец, цвет, группа)
# Blue = ЕС-программы ПО ВЕТРУ (выделенные); cyan = ЕС-класс СП-машин (НЕ ветер);
# green = РФ-класс СП-машин (МАИ) — ветер НЕ выделен (лишь упоминание в 18-79-00306);
bars = [
    # --- ЕС: ВЕТЕР (выделенные программы, ядро сигнала) ---
    ("UpWind (ЕС FP6)",             2006, 2011, "#08519c", "EU-wind"),
    ("INNWIND (ЕС FP7)",            2013, 2017, "#08519c", "EU-wind"),
    ("EcoSwing (ЕС H2020, €10.6M)", 2015, 2019, "#a1001a", "EU-wind-core"),
    # --- ЕС: класс СП-машины (транспорт/авиа — НЕ ветер) ---
    ("ASuMED (DE, H2020)",          2017, 2020, "#7fc7d9", "EU-machine"),
    ("HIVOMOT (EU, H2020)",         2021, 2023, "#7fc7d9", "EU-machine"),
    # --- США ---
    ("NIST ATP (AMSC, grant 70NANB7H7055)", 2007, 2014, "#d62728", "US"),
    # --- Россия (РНФ): КЛАСС сп-машины (МАИ) — ветро-программы НЕТ ---
    ("РНФ 16-19-10054 (пиннинг ВТСП, КрНЦ)", 2016, 2018, "#eeeeee", "RU-nonwind"),
    ("РНФ 17-19-01269 (машины, АВИА)", 2017, 2019, "#eeeeee", "RU-nonwind"),
    ("РНФ 18-79-00306 (обмотки; ветер лишь упомянут)", 2018, 2020, "#a8d5a2", "RU-windmention"),
    ("РНФ 19-79-10206 (крио, ВТСП-машины)", 2019, 2021, "#eeeeee", "RU-nonwind"),
    ("РНФ 23-19-00624 (методики ВТСП-машин)", 2023, 2025, "#eeeeee", "RU-nonwind"),
    # --- Япония ---
    ("KAKEN Kyoto HTS-ISM (3 кВт, 99%)", 2024, 2025, "#9467bd", "JP"),
]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), gridspec_kw={"width_ratios": [1.6, 1]})

# Левая: таймлайн
color_map = {"EU-wind": "#08519c", "EU-wind-core": "#a1001a", "EU-machine": "#7fc7d9", "US": "#d62728",
             "RU-nonwind": "#eeeeee", "RU-windmention": "#a8d5a2", "JP": "#9467bd"}
for i, (label, start, end, _, grp) in enumerate(bars):
    ax1.barh(i, end - start, left=start, height=0.55, color=color_map[grp], alpha=0.9,
             edgecolor="black", linewidth=0.4)
    ax1.text(end + 0.15, i, f"{start}-{end}", va="center", fontsize=7.5, color="gray")
ax1.set_yticks(range(len(bars)))
ax1.set_yticklabels([b[0] for b in bars], fontsize=8.5)
ax1.set_xlim(2000, 2028)
ax1.set_xlabel("Годы")
ax1.set_title("Кто и когда финансировал\n(ЕС — ядро: UpWind→INNWIND→EcoSwing)", fontsize=11)
ax1.grid(axis="x", alpha=0.25)

# Правая: география — ТОЛЬКО ВЕТЕР-специфичные гранты/программы
geo = {
    "ЕС (ветер, выделенные)": 3,      # UpWind, INNWIND, EcoSwing
    "США (NIST ATP 10MW)": 1,         # ветро-программа AMSC
    "Россия (ветер упомянут)": 0,     # 0 выделенных; 18-79-00306 лишь упоминает
    "Япония (KAKEN)": 0,
    "Китай (NSFC)": 0,
}
labels = list(geo.keys())
vals = list(geo.values())
colors = ["#08519c", "#d62728", "#2ca02c", "#9467bd", "#8c8c8c"]
bars2 = ax2.barh(labels, vals, color=colors, alpha=0.85)
ax2.set_title("ВЕТЕР-специфичные гранты/программы\nпо географии (не класс «СП-машины»)", fontsize=10.5)
ax2.set_xlim(0, 4)
for b, v in zip(bars2, vals):
    ax2.text(b.get_width() + 0.05, b.get_y() + b.get_height()/2, str(v), va="center", fontsize=9)
ax2.grid(axis="x", alpha=0.25)
ax2.annotate("РФ: 0 ветер-программ; 18-79-00306 лишь упоминает ветерустановку.\nКНР: 0 в локальной базе NSFC (129 грантов).",
             xy=(0.5, -0.32), xycoords="axes fraction", ha="center", fontsize=8.5, style="italic",
             color="#555555")

fig.suptitle("Грантовый сигнал S1d — СП-генераторы для ветроэнергетики (кейс 010 EcoSwing)",
             fontsize=12.5, y=1.0)
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("saved:", OUT)