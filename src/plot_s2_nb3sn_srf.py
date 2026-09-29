#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011: график wordshift-семантики Nb3Sn SRF (S2).

Две панели: (A) Nb3Sn-подмножество — маркеры материала vs физики/приёмов;
(B) Nb3Sn vs Nb-control по ключевым маркерам.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
TR = ROOT / "results/case_signals/wordshift_trends_nb3sn_srf.json"
OUT = ROOT / "case_studies/011_srf_cavities/plots/plot_s2_semantic_shift.png"

d = json.loads(TR.read_text(encoding="utf-8"))
pers = d["periods"]
M = d["markers"]

colors = {
    "mat_coat": "#d62728", "mat_film": "#ff7f0e", "mat_vdp": "#2ca02c",
    "phys_grad": "#1f77b4", "phys_q0": "#9467bd", "phys_rs": "#8c564b",
    "app_cryomod": "#17becf", "cryo_cool": "#e377c2", "app_compact": "#7f7f7f",
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))

ax1.set_title("Nb3Sn SRF: семантика абстрактов, частота на 1000 слов\n"
              "материал/процесс vs физика/применения", fontsize=10)
for m in ["mat_coat", "mat_film", "mat_vdp", "phys_grad", "phys_q0", "phys_rs"]:
    ax1.plot(pers, [M[m][p] for p in pers], marker="o", ms=3, lw=1.8,
             color=colors[m], label=m)
ax1.axvline("2016-18", color="black", ls="--", lw=1.0)
ax1.text(1.02, ax1.get_ylim()[1] * 0.9, "окно 2018", fontsize=8)
ax1.set_ylabel("‰"); ax1.grid(alpha=0.3); ax1.legend(fontsize=8)

ax2.set_title("Применения/системы (после-2018 рост):\ncryomodule, cryocooler, compact", fontsize=10)
for m in ["app_cryomod", "cryo_cool", "app_compact", "mat_vdp"]:
    ax2.plot(pers, [M[m][p] for p in pers], marker="o", ms=3, lw=1.8,
             color=colors[m], label=m)
ax2.axvline("2016-18", color="black", ls="--", lw=1.0)
ax2.set_ylabel("‰"); ax2.grid(alpha=0.3); ax2.legend(fontsize=8)

fig.suptitle("S2 — семантический сдвиг Nb3Sn SRF (wordshift, 207 работ; ⚠️ ранние периоды малы)", fontsize=12)
fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("saved:", OUT)