#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 010, ШАГ 5: (1) рост публикаций по конкурентам, (2) доля СП-генераторов, (3) S3-cross взаимные цитирования.

Источники: data/raw/openalex/ecoswing_competitors_full.json (21 519 работ, собрано через SOCKS-прокси),
           data/raw/openalex/ecoswing_corpus.json (1857 работ — СП-генераторы).
Выход:    case_studies/010_ecoswing_sc_wind/plots/s3_*.png
           case_studies/010_ecoswing_sc_wind/signals/s3_cross_competitor.md
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CASE = ROOT / "case_studies" / "010_ecoswing_sc_wind"
PLOTS = CASE / "plots"
SIG = CASE / "signals"

# ---------- данные ----------
comp = json.load(open(ROOT / "data/raw/openalex/ecoswing_competitors_full.json", encoding="utf-8"))
sc = json.load(open(ROOT / "data/raw/openalex/ecoswing_corpus.json", encoding="utf-8"))
WS = comp["works"]
SC_WS = sc["works"]

# ---------- классификация конкурентов по ключевым словам (как запросы сборки) ----------
PATTERNS = {
    "PM_DD": [r"permanent magnet", r"pmsg", r"pm[- ]dd", r"pm direct"],
    "DFIG": [r"doubly[- ]?fed induction generator", r"dfig"],
    "hydraulic": [r"hydraulic transmission", r"hydraulic drive"],
    "magnetic_gear": [r"magnetic gear", r"pseudo direct drive"],
    "no_rare_earth": [r"rare earth free", r"rare-earth-free", r"ferrite"],
}
CLASSES = list(PATTERNS.keys())


def text(w):
    return " ".join(filter(None, [w.get("title") or "", w.get("abstract") or ""])).lower()


def classify(w):
    t = text(w)
    return [c for c, pats in PATTERNS.items() if any(re.search(p, t) for p in pats)]


# id -> классы
cls_of = {}
for w in WS:
    cls_of[w["id"]] = classify(w)

# СП-корпус (1857 работ) как отдельный класс "SC_gen"
sc_ids = set()
for w in SC_WS:
    sc_ids.add(w["id"])
# СП-работы, попавшие в корпус конкурентов
sc_also = [w["id"] for w in WS if w["id"] in sc_ids]
print(f"СП-корпус: {len(sc_ids)}; пересечение с корпусом конкурентов: {len(sc_also)}")

ALL_CLASSES = CLASSES + ["SC_gen"]

# id -> классы (у СП-работ в конкурентном корпусе — тоже)
def full_classes(wid):
    c = list(cls_of.get(wid, []))
    if wid in sc_ids:
        c.append("SC_gen")
    return c

# ---------- 1) рост публикаций по годам ----------
Y0, Y1 = 1980, 2027
years = range(Y0, Y1 + 1)
counts = {c: Counter() for c in ALL_CLASSES}
for w in WS:
    y = w.get("year")
    if not y or not (Y0 <= y <= Y1):
        continue
    for c in full_classes(w["id"]):
        counts[c][y] += 1
# СП-работы, которых нет в корпусе конкурентов
for w in SC_WS:
    y = w.get("year")
    if not y or not (Y0 <= y <= Y1) or w["id"] in cls_of:
        continue
    counts["SC_gen"][y] += 1

Y2 = 1998  # начало показа на графике (до 1998 почти 0)
plot_years = list(range(Y2, Y1 + 1))

fig, ax = plt.subplots(figsize=(11, 6))
for c in CLASSES:
    ax.plot(plot_years, [counts[c].get(y, 0) for y in plot_years], label=c, lw=1.8)
ax.plot(plot_years, [counts["SC_gen"].get(y, 0) for y in plot_years], label="SC_gen", lw=2.6, ls="--", color="k")
ax.set_title("Кейс 010: публикации по конкурентам класса-проблемы (OpenAlex, полный корпус 21 519)")
ax.set_xlabel("Год"); ax.set_ylabel("Число работ / год")
ax.legend(fontsize=8); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(PLOTS / "s3_competitors_by_year.png", dpi=140)
plt.close()

# ---------- 2) доля СП-генераторов ----------
total_by_year = Counter()
for w in WS:
    y = w.get("year")
    if y and Y0 <= y <= Y1:
        total_by_year[y] += 1
for w in SC_WS:
    y = w.get("year")
    if y and Y0 <= y <= Y1 and w["id"] not in cls_of:
        total_by_year[y] += 1

sc_yearly = counts["SC_gen"]
share = {y: 100.0 * sc_yearly.get(y, 0) / max(total_by_year.get(y, 0), 1) for y in plot_years}

fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(plot_years, [sc_yearly.get(y, 0) for y in plot_years], color="steelblue", alpha=0.6, label="СП-работы (левая ось)")
ax2 = ax.twinx()
ax2.plot(plot_years, [share.get(y, 0) for y in plot_years], color="darkred", lw=2, label="Доля СП, % (правая ось)")
ax.set_title("Кейс 010: доля сверхпроводящих генераторов в классе-проблеме «ветрогенераторы»")
ax.set_xlabel("Год"); ax.set_ylabel("Число СП-работ / год"); ax2.set_ylabel("Доля СП, %")
ax.legend(loc="upper left", fontsize=8); ax2.legend(loc="upper right", fontsize=8)
ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(PLOTS / "s3_sc_share_by_year.png", dpi=140)
plt.close()

# ---------- 3) S3-cross: взаимные цитирования ----------
# id-классы: множество id на класс
ids_by_class = defaultdict(set)
for w in WS:
    for c in full_classes(w["id"]):
        ids_by_class[c].add(w["id"])
for w in SC_WS:
    ids_by_class["SC_gen"].add(w["id"])

# цитаты: для каждой работы набор ссылок (OpenAlex id внутри 'W...')
def ref_ids(w):
    out = []
    for r in (w.get("references") or []):
        if r:
            m = re.search(r"W\d+", r)
            if m:
                out.append(m.group(0))
    return out

# кэш ссылок
refs_of = {w["id"]: set(ref_ids(w)) for w in WS}
for w in SC_WS:
    refs_of.setdefault(w["id"], set(ref_ids(w)))

# матрица A->B: доля работ в A, ссылающихся хотя бы на одну работу в B
cite_frac = defaultdict(dict)      # A -> B -> (число работ A, ссылающихся на B; всего A)
cite_count = defaultdict(dict)     # суммарно число ссылок A->B
for A in ALL_CLASSES:
    idsA = ids_by_class[A]
    worksA = [w for w in WS + SC_WS if w["id"] in idsA and refs_of.get(w["id"])]
    nA = len(worksA)
    for B in ALL_CLASSES:
        idsB = set()
        for bid in ids_by_class[B]:
            idsB.add(bid.split("/")[-1] if "/" in bid else bid)
        cnt = 0
        tot_links = 0
        for w in worksA:
            r = refs_of.get(w["id"], set())
            hit = r & idsB
            if hit:
                cnt += 1
                tot_links += len(hit)
        cite_frac[A][B] = (cnt, nA)
        cite_count[A][B] = tot_links

# ---------- вывод ----------
lines = []
lines.append("# Кейс 010 — S3-cross: взаимные цитирования конкурентов (ШАГ 5.4 GUIDE)")
lines.append("")
lines.append(f"> **Дата:** 2026-09-10. Корпус: `ecoswing_competitors_full.json` (21 519 работ, собран через SOCKS-прокси) + `ecoswing_corpus.json` (1857 СП-работ).")
lines.append("> Матрица A->B = доля (%) работ класса A, ссылающихся хотя бы на одну работу класса B. Классы: PM_DD, DFIG, hydraulic, magnetic_gear, no_rare_earth, SC_gen (СП-генераторы).")
lines.append("")

lines.append("## 1. Рост публикаций по конкурентам")
lines.append("")
lines.append(f"![График](plots/s3_competitors_by_year.png)")
lines.append("")
lines.append("| Класс | Работ в корпусе | Пик | Год пика | 2018 | 2025 |")
lines.append("|---|---|---|---|---|---|")
for c in ALL_CLASSES:
    s = counts[c]
    peak_y = max((y for y in years), key=lambda y: s.get(y, 0)) if s else None
    peak_v = s.get(peak_y, 0) if peak_y else 0
    lines.append(f"| {c} | {len(ids_by_class[c])} | {peak_v} | {peak_y} | {s.get(2018,0)} | {s.get(2025,0)} |")
lines.append("")

lines.append("## 2. Доля СП-генераторов в классе-проблеме")
lines.append("")
lines.append(f"![Доля](plots/s3_sc_share_by_year.png)")
lines.append("")
lines.append("| Год | СП-работ | Всего в классе | Доля СП, % |")
lines.append("|---|---|---|---|")
for y in [2000, 2005, 2010, 2015, 2018, 2020, 2023, 2025]:
    lines.append(f"| {y} | {sc_yearly.get(y,0)} | {total_by_year.get(y,0)} | {share.get(y,0):.2f} |")
lines.append("")

lines.append("## 3. Матрица взаимных цитирований A→B (% работ A, ссылающихся на B)")
lines.append("")
lines.append("| A \\ B | PM_DD | DFIG | hydraulic | mag_gear | no_RE | SC_gen |")
lines.append("|---|---|---|---|---|---|---|")
for A in ALL_CLASSES:
    row = [A]
    for B in ALL_CLASSES:
        cnt, nA = cite_frac[A][B]
        pct = 100.0 * cnt / nA if nA else 0.0
        row.append(f"{pct:.1f}% ({cnt}/{nA})")
    lines.append("| " + " | ".join(row) + " |")
lines.append("")
lines.append("## 4. Суммарно ссылок A→B")
lines.append("")
lines.append("| A \\ B | PM_DD | DFIG | hydraulic | mag_gear | no_RE | SC_gen |")
lines.append("|---|---|---|---|---|---|---|")
for A in ALL_CLASSES:
    row = [A] + [str(cite_count[A][B]) for B in ALL_CLASSES]
    lines.append("| " + " | ".join(row) + " |")
lines.append("")

out = "\n".join(lines)
(SIG / "s3_cross_competitor.md").write_text(out, encoding="utf-8")

# консольный отчёт (кратко)
print("\n=== Рост по годам (2010-2025) ===")
print("Год | " + " | ".join(ALL_CLASSES) + " | total")
for y in [2010, 2015, 2018, 2020, 2023, 2025]:
    vals = " | ".join(str(counts[c].get(y, 0)) for c in ALL_CLASSES)
    print(f"{y} | {vals} | {total_by_year.get(y,0)}")
print("\n=== Доля СП ===")
for y in [2005, 2010, 2015, 2018, 2020, 2025]:
    print(f"{y}: СП={sc_yearly.get(y,0)} всего={total_by_year.get(y,0)} доля={share.get(y,0):.2f}%")
print("\n=== Матрица цитирований (доли %) ===")
hdr = "A\\B | " + " | ".join(ALL_CLASSES)
print(hdr.replace("mag_gear", "mag_ge"))
for A in ALL_CLASSES:
    row = [A]
    for B in ALL_CLASSES:
        cnt, nA = cite_frac[A][B]
        pct = 100.0 * cnt / nA if nA else 0.0
        row.append(f"{pct:.1f}")
    print(" | ".join(row))
print("\nготово:", SIG / "s3_cross_competitor.md")