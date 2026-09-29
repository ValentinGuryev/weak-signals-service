#!/usr/bin/env python3
"""Грантовый отклик кейса 005 (SMES): исследовательские гранты = 0 + нац. программы.

Левая панель: NSF/CORDIS/KAKEN/РНФ гранты по SMES (все 0 — пустота).
Правая панель: национальные программы (NEDO, K-SMES, DOE-ETM, BNL, CAS) — горизонтальные полосы.
Выход: case_studies/005_SMES/plots/plot_grants_signal.png
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "case_studies" / "005_SMES" / "plots" / "plot_grants_signal.png"

# Национальные программы (из литературы кейса): (название, старт, конец, страна)
programs = [
    ("DOE SMES-ETM (США, 20 MWh)", 1985, 1995, "#1f77b4"),
    ("Япония NEDO LTS (100 MW)", 1991, 2003, "#9467bd"),
    ("K-SMES фаза 1-3 (Корея)", 2003, 2012, "#ff7f0e"),
    ("Япония HTS feasibility", 2005, 2010, "#9467bd"),
    ("BNL HTS SMES (США)", 2013, 2016, "#1f77b4"),
    ("Китай CAS SMES", 2014, 2026, "#d62728"),
]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={"width_ratios": [1, 1.4]})

# Левая: грантовые фонды — пусто
funds = ["NSF (США)", "CORDIS (ЕС)", "KAKEN (Япония)", "NIH (США)", "РНФ (Россия)", "NSFC (Китай)"]
vals = [0, 0, 0, 0, 0, 0]
bars = ax1.barh(funds, vals, color="#c9211e", alpha=0.7)
ax1.set_title("Исследовательские гранты по SMES\n(NSF/CORDIS/KAKEN/РНФ — 0 находок)", fontsize=11)
ax1.set_xlim(0, 1)
ax1.set_xticks([])
for bar, v in zip(bars, vals):
    ax1.text(0.05, bar.get_y() + bar.get_height()/2, f"{v} грантов", va="center", fontsize=10,
             color="#c9211e", fontweight="bold")
ax1.grid(axis="x", alpha=0.2)
ax1.annotate("SMES не получал исследовательских грантов\n(финансирование — только гос. программы)",
             xy=(0.5, -0.15), xycoords="axes fraction", ha="center", fontsize=9, style="italic")

# Правая: национальные программы
for i, (name, start, end, color) in enumerate(programs):
    ax2.barh(i, end - start, left=start, height=0.5, color=color, alpha=0.85,
             edgecolor="black", linewidth=0.5)
    ax2.text(end + 0.3, i, f"{start}-{end}", va="center", fontsize=8, color="gray")
ax2.set_yticks(range(len(programs)))
ax2.set_yticklabels([p[0] for p in programs], fontsize=9)
ax2.set_xlim(1980, 2028)
ax2.set_title("Национальные ПРОГРАММЫ финансирования SMES\n(не гранты — гос. программы развития)", fontsize=11)
ax2.axvspan(2003, 2012, color="#2ca02c", alpha=0.12)
ax2.text(2007.5, -0.8, "окно «ВТСП-SMES как тренд»", ha="center", fontsize=8, color="#2ca02c")
ax2.set_xlabel("Год")
ax2.grid(axis="x", alpha=0.3)

fig.suptitle("Грантовый отклик кейса 005 (SMES): пустота грантов, жизнь — только в гос. программах",
             fontsize=13)
fig.text(0.01, 0.01,
         "Источники: NSF/CORDIS API (2026-09-02, 0 SMES-грантов); KAKEN/NIH/РНФ — 0.\n"
         "Программы: Tatsuta 2004 (NEDO), KERI 2006/2009 + Lee 2012 (K-SMES), BPA 1979/Gupta 2015 (США), Li 2022 (CAS).\n"
         "Вывод: отсутствие грантового отклика = ранний сигнал «ложного тренда».",
         fontsize=8, style="italic", color="gray")
plt.tight_layout(rect=[0, 0.03, 1, 0.93])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
