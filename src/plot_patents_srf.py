#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011 SRF: график патентного сигнала (S1b).

Панель A: динамика по годам (59 релев. изобретений).
Панель B: игроки/юрисдикции — топ-10 заявителей по изобретениям.
Выход: case_studies/011_srf_cavities/plots/plot_patent_signal.png
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/raw/patents/cases/011_srf_cavities.json"
OUT = ROOT / "case_studies/011_srf_cavities/plots/plot_patent_signal.png"

d = json.loads(DATA.read_text(encoding="utf-8"))
rel = [p for p in d["patents"] if p.get("relevant")]

# Панель A: динамика
yc = Counter(p.get("year") or 0 for p in rel)
years = list(range(min(yc), max(yc) + 1))
counts = [yc.get(y, 0) for y in years]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

ax1.bar(years, counts, color="#1f77b4", alpha=0.85)
ax1.axvline(2010, color="red", ls="--", lw=1.2)
ax1.text(2010.3, max(counts) * 0.9, "пик 2010\n(Mitsubishi)", color="red", fontsize=8)
ax1.set_title(f"Патенты по годам ({len(rel)} релев. изобр.)\nSiemens 1970-71 (истоки) → 2010 (Mitsubishi) → 2021-23 (JLab/CN)", fontsize=10.5)
ax1.set_xlabel("год"); ax1.set_ylabel("патентов"); ax1.grid(alpha=0.3)

# Панель B: игроки (первые 3-4 слова assignee)
def pl(a):
    return (a or "—").split(";")[0].strip()[:42]
ea = Counter(pl(p.get("assignee")) for p in rel)
top = ea.most_common(10)
names = [n for n, _ in top]
vals = [c for _, c in top]
ax2.barh(range(len(top)), vals, color="#2ca02c", alpha=0.85)
ax2.set_yticks(range(len(top)))
ax2.set_yticklabels(names, fontsize=9)
ax2.set_title("Топ-10 заявителей (изобретений)\nлаборатории/академия + пром. подрядчики", fontsize=10.5)
ax2.set_xlabel("изобретений"); ax2.grid(axis="x", alpha=0.3)

fig.suptitle("S1b — Патенты SRF-резонаторов (кейс 011): 106 raw / 79 уник. / 59 релев.", fontsize=13)
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("saved:", OUT)
print("игроки:", dict(top))