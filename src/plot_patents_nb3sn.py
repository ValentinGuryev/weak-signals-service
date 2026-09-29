#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011: график патентного сигнала ТРЕНДА Nb3Sn (по новому видению).

Тренд = Nb3Sn-полости (5 патентов), контроль = Nb-полости (54 релев.).
Вход: data/raw/patents/cases/011_srf_cavities.json (79 уник/59 релев, Lens 2026-09-11).
Выход: case_studies/011_srf_cavities/plots/patents_nb3sn_by_year.png
API: 0 (локальные данные).
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/raw/patents/cases/011_srf_cavities.json"
OUT = ROOT / "case_studies/011_srf_cavities/plots/patents_nb3sn_by_year.png"

PAT_NB3SN = re.compile(r"nb\s*3\s*sn|niobium[\s-]?tin|niob[\s-]?tin|b3sn", re.I)

d = json.loads(DATA.read_text(encoding="utf-8"))
pats = d["patents"]
nb3sn = [p for p in pats if PAT_NB3SN.search((p.get("title") or "") + " " + (p.get("abstract") or ""))]
nb_ctrl = [p for p in pats if p.get("relevant") and p not in nb3sn]

yc_trend = Counter(p.get("year") for p in nb3sn if p.get("year"))
yc_ctrl = Counter(p.get("year") for p in nb_ctrl if p.get("year"))

years = range(1990, 2027)
c_trend = [yc_trend.get(y, 0) for y in years]
c_ctrl = [yc_ctrl.get(y, 0) for y in years]

fig, ax = plt.subplots(figsize=(13, 5.5))
ax.bar([y - 0.2 for y in years], c_ctrl, width=0.4, color="#1f77b4", alpha=0.85, label=f"Nb SRF (контроль, зрел.) — {len(nb_ctrl)} патентов")
ax.bar([y + 0.2 for y in years], c_trend, width=0.4, color="#d62728", alpha=0.9, label=f"Nb3Sn SRF (тренд) — {len(nb3sn)} патентов")
ax.axvline(2018, color="black", ls="--", lw=1.1)
ax.text(2018.2, max(c_ctrl) * 0.93, "окно 2018", fontsize=9, rotation=90, va="top")
ax.set_title(f"Патентный сигнал кейса 011: Nb3Sn-полости (тренд, 5) vs Nb-полости (контроль, {len(nb_ctrl)})\n"
             "Nb3Sn: 5 патентов 2018-2024, все — техпроцесс покрытия (IMP CAS ×3, CN Nonferrous, Rey US)",
             fontsize=11)
ax.set_xlabel("год"); ax.set_ylabel("патенты/год"); ax.grid(alpha=0.3); ax.legend(fontsize=9)
fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("saved:", OUT)
print(f"Nb3Sn: {len(nb3sn)} патентов | Nb контроль: {len(nb_ctrl)}")
print("Nb3Sn по годам:", dict(sorted(yc_trend.items())))
print("Nb контроль по годам:", dict(sorted(yc_ctrl.items())))