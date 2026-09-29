#!/usr/bin/env python3
"""График патентного сигнала кейса 010 (EcoSwing) — v2 финал (база 192/87/48).

Панель A: динамика по ИЗОБРЕТЕНИЯМ (после семейного дедупа GE/игроков).
Панель B: типы игроков (заявители, по изобретениям).
Панель C: топ-заявители по изобретениям (с счётчиком публикаций).
Выход: case_studies/010_ecoswing_sc_wind/plots/plot_patent_signal.png
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
DATA = ROOT / "data/raw/patents/cases/010_sc_wind.json"
OUT = ROOT / "case_studies" / "010_ecoswing_sc_wind" / "plots" / "plot_patent_signal.png"


def inv_id(p):
    t = f"{p.get('title','')} {p.get('abstract','')}"; tl = t.lower(); a = (p.get('assignee') or '').lower()
    if 'general electric' in a or 'gen electric' in a:
        if ('method and apparatus' in tl or 'verfahren und vorrichtung' in tl) and p.get('year') == 2007: return 'ge_wgen_2007'
        if ('driven by a wind' in tl or 'angetriebenen generator' in tl or 'napędzany turbin' in tl or '风力涡轮驱动' in tl or 'génér' in tl): return 'ge_wgen_2018'
        if 'wind turbine having' in tl or 'rotating armature' in tl or 'armature for a wind' in tl: return 'ge_wturb_gen_2018'
        if 'quench protection' in tl or 'quenchschutz' in tl or 'extinction' in tl: return 'ge_quench_2019'
        if 'auto-ramping' in tl or 'herunterfahren' in tl or 'redukcji' in tl: return 'ge_ramp_2019'
        if 'magnetic shield' in tl or 'magnetische abschirmung' in tl: return 'ge_shield_2019'
        if 'cryogenic shielding' in tl or 'cryogenic shield' in tl or 'abschirmbaugruppe' in tl: return 'ge_cryoshield_2018'
        return 'ge_other'
    if 'cooper willard' in a or 'willard cooper' in a: return 'cooperwillard'
    if 'dongfang' in a: return 'dongfang'
    if 'guodian' in a: return f"guodian_{p.get('year')}"
    if 'nanjing' in a: return f"nanjing_{p.get('year')}"
    if 'henan poly' in a: return f"henan_{p.get('year')}"
    if 'hunan' in a: return f"hunan_{p.get('year')}"
    if 'jeju' in a: return 'jeju_vertical'
    if 'sumitomo' in a: return 'sumitomo_windgen'
    if 'alstom' in a: return 'alstom_2004'
    return None


d = json.loads(DATA.read_text(encoding="utf-8"))
rel = [p for p in d["patents"] if p.get("relevant")]
for p in rel:
    p["inv"] = inv_id(p) or p["publication_number"]

inv_groups = {}
for p in rel:
    inv_groups.setdefault(p["inv"], []).append(p)

# --- динамика по изобретениям ---
years_inv = Counter(min(v[0].get("year") or 0 for v in inv_groups.values()) for v in [_ for _ in [None]])
Y = Counter()
for v in inv_groups.values():
    p0 = v[0]; Y[p0.get("year") or 0] += 1
yrange = range(min(Y), max(Y) + 1)

# --- игроки по изобретениям ---
player_inv = Counter()
player_pub = Counter()
for v in inv_groups.values():
    p0 = v[0]
    pl = p0.get("assignee_label") or p0.get("assignee") or "—"
    player_inv[pl] += 1
    player_pub[pl] += len(v)

# --- типы ---
pt = Counter(v[0]["player_type"] for v in inv_groups.values())

fig, axes = plt.subplots(1, 3, figsize=(21, 6))

# A: динамика
ax = axes[0]
ax.bar([y for y in yrange], [Y.get(y, 0) for y in yrange], color="#1f77b4", alpha=0.85)
ax.axvline(2018, color="red", ls="--", lw=1.2)
ax.text(2018.2, max(Y.values()) * 0.88, "EcoSwing-демо", color="red", fontsize=9)
ax.set_title(f"Динамика — ИЗОБРЕТЕНИЯ ({len(inv_groups)})\nпик 2012 (KR) и 2021 (CN/GE)", fontsize=10.5)
ax.set_xlabel("год"); ax.set_ylabel("изобретений"); ax.grid(alpha=0.3)

# B: типы игроков (по изобретениям)
ax = axes[1]
labels = {"company": "компании (ТНК/фирмы)", "research_institute": "НИИ/вузы",
          "government": "гос-структуры", "individual": "частные лица", "other": "другое/неопр."}
order = [k for k in ["company", "research_institute", "government", "individual", "other"] if pt.get(k)]
ax.barh([labels[k] for k in order], [pt[k] for k in order], color="#2ca02c", alpha=0.85)
ax.set_title("Типы игроков (по изобретениям)", fontsize=10.5)
ax.set_xlabel("изобретений"); ax.grid(axis="x", alpha=0.3)

# C: топ заявителей (по изобретениям, публикации в скобках)
ax = axes[2]
top = player_inv.most_common(10)
names = [f"{n[:26]}" for n, _ in top]
vals = [c for _, c in top]
pubs = [player_pub[n] for n, _ in top]
ax.barh(range(len(top)), vals, color="#d62728", alpha=0.85)
ax.set_yticks(range(len(top)))
ax.set_yticklabels([f"{n} ({p} публ.)" for n, p in zip(names, pubs)], fontsize=8)
ax.set_title("Топ-10 заявителей (изобретений)\nпубликаций в скобках", fontsize=10.5)
ax.set_xlabel("изобретений"); ax.grid(axis="x", alpha=0.3)

fig.suptitle("Патентный сигнал — СП-генераторы для ветра (кейс 010 EcoSwing) · база 192 зап. / 87 релев. / 48 изобр.",
             fontsize=12.5)
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("saved:", OUT)
print("годы (изобр.):", dict(sorted(Y.items())))
print("игроки (изобр.):", dict(player_inv.most_common(10)))
print("типы:", dict(pt))