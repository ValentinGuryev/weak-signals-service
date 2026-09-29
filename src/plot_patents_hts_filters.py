#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс HTS-фильтры: патентный сигнал (S1b) — график.

Панель A: динамика по годам (изобретения).
Панель B: топ-10 заявителей (изобретения).
Выход: case_studies/hts_filters/plots/plot_patent_signal.png
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT/"data/raw/patents/cases/hts_filters.json"
OUT = ROOT/"case_studies/hts_filters/plots/plot_patent_signal.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

d=json.loads(DATA.read_text(encoding="utf-8"))
rel=[p for p in d["patents"] if p.get("relevant")]
# изобретения: rel и не дубль по (assignee,t6title)
import re
def core(t):
    return " ".join(re.sub(r'[^\x00-\x7F]+',' ',str(t)).lower().split()[:6])
seen=set(); inv=[]
for p in sorted(rel, key=lambda x: x.get("year") or 0):
    k=( (p.get("assignee") or "").split(";")[0].strip().lower(), core(p.get("title")) )
    if k in seen: continue
    seen.add(k); inv.append(p)

yc=Counter(p.get("year") or 0 for p in inv)
years=list(range(min(yc),max(yc)+1))
counts=[yc.get(y,0) for y in years]

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(15,6))

ax1.bar(years,counts,color="#1f77b4",alpha=0.85)
for y in (2000,2012,2020):
    ax1.axvline(y,color="gray",ls=":",lw=1)
for y,lbl in [(2000,"2G/3G\nкоммерция"),(2012,"пик CN\nэпизод"),(2020,"квант.\nфильтры")]:
    ax1.text(y,max(counts)*0.97,lbl,fontsize=7.5,ha="center",color="gray")
ax1.set_title(f"HTS-фильтры: патенты по годам ({len(inv)} изобр.)\n2000-е коммерция → 2012 CN-пик → 2020 квантовые",fontsize=10.5)
ax1.set_xlabel("год"); ax1.set_ylabel("изобретений"); ax1.grid(alpha=0.3)

ea=Counter((p.get("assignee") or "—").split(";")[0].strip()[:30] for p in inv)
top=ea.most_common(10)
ax2.barh(range(len(top)),[c for _,c in top],color="#2ca02c",alpha=0.85)
ax2.set_yticks(range(len(top)))
ax2.set_yticklabels([n for n,_ in top],fontsize=8.5)
ax2.set_title("Топ-10 заявителей (изобретений)",fontsize=10.5)
ax2.set_xlabel("изобретений"); ax2.grid(axis="x",alpha=0.3)

fig.suptitle("S1b — Патенты HTS-фильтры (кейс hts_filters): 80 уник. / 74 релев. / 70 изобр.",fontsize=13)
fig.tight_layout()
fig.savefig(OUT,dpi=150,bbox_inches="tight")
print("saved:",OUT)
print("годы:",dict(sorted(yc.items())))
print("игроки:",dict(top))