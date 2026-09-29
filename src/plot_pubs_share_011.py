#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011: доля Nb3Sn от ВСЕГО ПОЛЯ ПРОБЛЕМЫ (S1a-дополнение, v3, 2026-09-13).

Знаменатель = объединение SRF-корпуса (7579) + дополнения проблемными формулировками
(12444: NC/медь/CLIC, high-gradient, ускоряющий градиент, DLA, диэлектрический кильватер,
THz, плазменный/лазерный кильватер, MgB2/NbN/NbTiN/SIS в SRF-контексте) = 20023 работ.
Доля Nb3Sn = title-ядро / всего поля за год. Линейная шкала, один график.
Вход: data/raw/openalex/srf_corpus.json + srf_problem_supplement.json
Выход: case_studies/011_srf_cavities/plots/pubs_share_nb3sn_vs_competitors.png
API: 0 (локально)
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
CORPUS = ROOT / "data/raw/openalex/srf_corpus.json"
SUPP = ROOT / "data/raw/openalex/srf_problem_supplement.json"
OUT = ROOT / "case_studies/011_srf_cavities/plots/pubs_share_nb3sn_vs_competitors.png"

PAT_NB3SN = re.compile(r"nb\s*3\s*sn|niobium[\s-]?tin|niob[\s-]?tin|\bb3sn\b", re.I)
PAT_NB = re.compile(r"\bniobium\b|\bNb\b", re.I)
# семейства дополнения (для справки о составе знаменателя, не для графика)
FAMILIES = {
    "NC/медь/CLIC": r"normal conducting|copper|CLIC|two-beam",
    "high-gradient": r"high gradient|accelerating gradient",
    "DLA/кильватер": r"dielectric laser|dielectric wakefield",
    "THz-структуры": r"THz",
    "плазма/лазер": r"plasma wakefield|laser wakefield",
    "материалы-SC": r"MgB2|\bNbN\b|\bNbTiN\b|SIS multilayer",
}

works = []
for p in (CORPUS, SUPP):
    d = json.loads(p.read_text(encoding="utf-8"))
    works.extend(w for w in d["works"] if w.get("year"))
# дедуп по id (страховка на перекрытие)
seen = set(); uniq = []
for w in works:
    if w["id"] not in seen:
        seen.add(w["id"]); uniq.append(w)
works = uniq
print(f"Объединённый корпус: {len(works)} работ (дедуп по id)")

by_year_total = Counter(w["year"] for w in works)
nb3sn_year = Counter()
nb_year = Counter()
for w in works:
    t = w.get("title") or ""
    if PAT_NB3SN.search(t): nb3sn_year[w["year"]] += 1
    if PAT_NB.search(t) and not PAT_NB3SN.search(t): nb_year[w["year"]] += 1

YMIN, YMAX = 2010, 2026
years = list(range(YMIN, YMAX + 1))
share_nb3sn = [100 * nb3sn_year.get(y, 0) / by_year_total.get(y, 1) for y in years]
share_nb = [100 * nb_year.get(y, 0) / by_year_total.get(y, 1) for y in years]

print(f"\n{'год':4} {'всего':>6} {'Nb3Sn':>5} {'% доля':>7} | {'Nb':>5} {'% доля':>7}")
for y in years:
    tot = by_year_total.get(y, 0)
    n3 = nb3sn_year.get(y, 0); nn = nb_year.get(y, 0)
    print(f"{y:4} {tot:6} {n3:5} {100*n3/tot:7.2f} | {nn:5} {100*nn/tot:7.2f}")

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(years, share_nb3sn, lw=2.2, color="#d62728", marker="o", ms=4.5,
        label="Nb3Sn (title-ядро) — тренд")
ax.plot(years, share_nb, lw=1.4, color="#1f77b4", ls="--", alpha=0.75,
        label="Nb (контроль, зрелая технология)")
ax.axvline(2018, color="black", ls="--", lw=1.1)
ax.text(2018.15, max(max(share_nb3sn), max(share_nb)) * 0.92, "окно 2018", fontsize=9, va="top")
ax.set_title("Nb3Sn в поле проблемы «высокоградиентное ускорение частиц»:\n"
             "% от ВСЕГО числа работ поля за год (линейная шкала)\n"
             f"поле = SRF-полости + NC/медь/CLIC + DLA/кильватер + плазма/лазер + SC-материалы ({len(works)} работ)",
             fontsize=10)
ax.set_xlabel("год", fontsize=10)
ax.set_ylabel("% работ поля с Nb3Sn в заголовке", fontsize=10)
ax.set_ylim(0, max(max(share_nb3sn), max(share_nb)) * 1.25)
ax.grid(alpha=0.3)
ax.legend(fontsize=9, loc="upper right")

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"\nsaved: {OUT}")

# состав знаменателя по семействам (для паспорта)
fam_year = {f: Counter() for f in FAMILIES}
for w in works:
    txt = (w.get("title") or "") + " " + (w.get("abstract") or "")
    for f, pat in FAMILIES.items():
        if re.search(pat, txt, re.I):
            fam_year[f][w["year"]] += 1
            break  # первый матч
print("\nСостав знаменателя по семействам (первый матч, сумма < 100%):")
for f, cy in fam_year.items():
    s = sum(v for y, v in cy.items() if 2010 <= y <= 2026)
    print(f"  {f:20} {s} работ в 2010-2026")