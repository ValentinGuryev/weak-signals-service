#!/usr/bin/env python3
"""График динамики «мостов» между конкурентами (NI-coils vs теплопроводная изоляция).

Что такое «мост»: работа, которая попадает ОДНОВРЕМЕННО в корпус NI-coils (кейс 004)
и в корпус теплопроводной изоляции (конкурент). Мост = кто-то уже проводит перекрёстное
сравнение = отсутствие изоляции между конкурентами (см. s3_cross_isolation_check.md).

Три панели:
1. Мосты по году публикации (2016-2025) — растут ли (тема структурируется вокруг NI);
2. Перекрёстные ссылки по году цитирующей работы: изоляция→NI vs NI→изоляция (в %);
3. Кумулятивное число мостов + доля мостов в корпусе изоляции.

Данные: ni_coils_corpus.json, hts_insulation_rct_corpus.json,
        ni_coils_references.json, insulation_references.json
Выход: case_studies/004_ni_coils/plots/plot_s3_bridge_dynamics.png
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
NI = ROOT / "data" / "raw" / "openalex" / "ni_coils_corpus.json"
INS = ROOT / "data" / "raw" / "openalex" / "hts_insulation_rct_corpus.json"
NI_REF = ROOT / "data" / "raw" / "openalex" / "ni_coils_references.json"
INS_REF = ROOT / "data" / "raw" / "openalex" / "insulation_references.json"
OUT = ROOT / "case_studies" / "004_ni_coils" / "plots" / "plot_s3_bridge_dynamics.png"

ni = json.loads(NI.read_text(encoding="utf-8"))
ins = json.loads(INS.read_text(encoding="utf-8"))
ni_refs = json.loads(NI_REF.read_text(encoding="utf-8"))
ins_refs = json.loads(INS_REF.read_text(encoding="utf-8"))

ni_ids = {w["id"] for w in ni}
thermal = [w for w in ins if w.get("topic") in ("insulation_thermal", "insulation_materials")]
thermal_ids = {w["id"] for w in thermal}
bridges = [w for w in thermal if w["id"] in ni_ids]

year_of_ni = {w["id"]: w["year"] for w in ni}
year_of_ins = {w["id"]: w["year"] for w in ins}

# --- Панель 1: мосты по году публикации ---
bridge_by_year = Counter(w["year"] for w in bridges if w.get("year"))
y_min, y_max = 2010, 2026
years = list(range(y_min, y_max + 1))
b_vals = [bridge_by_year.get(y, 0) for y in years]
b_cum = []
s = 0
for v in b_vals:
    s += v
    b_cum.append(s)

# --- Панель 2: перекрёстные ссылки по году цитирующей работы (в %) ---
ins_to_ni = defaultdict(int); tot_ins = defaultdict(int)
for wid, rl in ins_refs.items():
    y = year_of_ins.get(wid)
    if y is None:
        continue
    tot_ins[y] += len(rl)
    ins_to_ni[y] += sum(1 for r in rl if r in ni_ids)
ni_to_ins = defaultdict(int); tot_ni = defaultdict(int)
for wid, rl in ni_refs.items():
    if wid not in ni_ids:
        continue
    y = year_of_ni.get(wid)
    if y is None:
        continue
    tot_ni[y] += len(rl)
    ni_to_ins[y] += sum(1 for r in rl if r in thermal_ids)

pct_ins2ni = [100 * ins_to_ni.get(y, 0) / tot_ins[y] if tot_ins.get(y) else 0 for y in years]
pct_ni2ins = [100 * ni_to_ins.get(y, 0) / tot_ni[y] if tot_ni.get(y) else 0 for y in years]

# --- Панель 3: доля мостов в корпусе изоляции (по накопленным годам) ---
thermal_by_year_le = {}
ni_ids_le = {}
for y in years:
    thermal_by_year_le[y] = sum(1 for w in thermal if (w.get("year") or 9999) <= y)
    ni_ids_le[y] = {w["id"] for w in ni if (w.get("year") or 9999) <= y}
bridge_le = []
for y in years:
    # мосты, опубликованные <= y
    bl = sum(1 for w in bridges if (w.get("year") or 9999) <= y)
    bridge_le.append(bl)

fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))

# Панель 1: бары мостов + кумулята
ax = axes[0]
ax.bar(years, b_vals, color="#2ca02c", alpha=0.8, label="Новые мосты в год")
ax.plot(years, b_cum, color="#d62728", marker="o", ms=4, lw=1.8, label="Мосты накопленно")
ax.set_title("1. Мосты по году публикации\n(работы в корпусах И NI, И изоляции)")
ax.set_xlabel("Год"); ax.set_ylabel("Число работ")
ax.set_xticks(years[::2])
ax.grid(axis="y", alpha=0.3)
ax.legend(fontsize=8, loc="upper left")
for x, v in zip(years, b_vals):
    if v:
        ax.annotate(str(v), (x, v), textcoords="offset points", xytext=(0, 2), ha="center", fontsize=7)

# Панель 2: % перекрёстных ссылок
ax = axes[1]
ax.plot(years, pct_ins2ni, color="#1f77b4", marker="o", ms=4, lw=1.8, label="Изоляция → NI (%)")
ax.plot(years, pct_ni2ins, color="#ff7f0e", marker="s", ms=4, lw=1.8, label="NI → изоляция (%)")
ax.axhline(9.58, color="#1f77b4", ls=":", lw=1, alpha=0.6)
ax.axhline(0.99, color="#ff7f0e", ls=":", lw=1, alpha=0.6)
ax.text(2025.5, 10.2, "итого 9.58%", color="#1f77b4", fontsize=7.5, ha="right")
ax.text(2025.5, 1.7, "итого 0.99%", color="#ff7f0e", fontsize=7.5, ha="right")
ax.set_title("2. Перекрёстные ссылки по году цитирующей работы\n(асимметрия: изоляция ссылается на NI, NI — нет)")
ax.set_xlabel("Год"); ax.set_ylabel("% ссылок на корпус конкурента")
ax.set_xticks(years[::2])
ax.set_ylim(0, max(max(pct_ins2ni), 12) * 1.15)
ax.grid(axis="y", alpha=0.3)
ax.legend(fontsize=8, loc="upper left")

# Панель 3: доля мостов
ax = axes[2]
share = [100 * bl / thermal_by_year_le.get(y, 1) if thermal_by_year_le.get(y) else 0 for y, bl in zip(years, bridge_le)]
ax.fill_between(years, share, color="#2ca02c", alpha=0.3)
ax.plot(years, share, color="#2ca02c", marker="o", ms=4, lw=1.8, label="Доля мостов в корпусе изоляции")
ax.set_title("3. Мосты как доля корпуса изоляции\n(накопленно, % к работам изоляции ≤ года)")
ax.set_xlabel("Год"); ax.set_ylabel("% работ изоляции, пересекающихся с NI")
ax.set_xticks(years[::2])
ax.grid(axis="y", alpha=0.3)
ax.legend(fontsize=8, loc="upper left")

fig.suptitle("S3: Динамика «мостов» между NI-coils и теплопроводной изоляцией (кейс 004)\n"
             "Мост = работа в ОБОИХ корпусах → перекрёстное сравнение уже идёт → изоляции конкурентов НЕТ",
             fontsize=12, fontweight="bold")
fig.text(0.01, 0.01,
         "Источник: OpenAlex. Корпуса ni_coils_corpus.json (338) и hts_insulation_rct_corpus.json (thermal+materials 125).\n"
         "References: ni_coils_references.json (8217), insulation_references.json (108, докачан 2026-09-02).\n"
         "Итог: NI→изоляция 0.99% (81/8217), изоляция→NI 9.58% (173/1805), мостов 15 (12% корпуса изоляции).\n"
         "Скрипт: src/plot_s3_bridge_dynamics.py; разбор: case_studies/004_ni_coils/signals/s3_cross_isolation_check.md",
         fontsize=7.5, style="italic", color="gray")

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Сохранено: {OUT}")
