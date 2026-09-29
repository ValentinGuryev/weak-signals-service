#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011 (ТРЕНД Nb3Sn SRF): конференционный сигнал из ЛОКАЛЬНЫХ баз.

ЗАДАЧА: ответить на вопрос «почему Nb упёрся в потолок ~2010-2013» через конференц. сигнал.
Ответ собран ИЗ ЛОКАЛЬНЫХ баз (НОВЫХ API-запросов НЕ требуется):

1. srf_corpus.json (OpenAlex, собран 2026-09-11): conference-papers 1832 шт.,
   из них Nb3Sn SRF — 59 шт. (всплеск 2023+: cryocooler, compact SRF, JLab/Fermilab прототипы). — ОСНОВНОЙ источник.
2. conference_hits.json (IEEE TAS, 2175): Nb3Sn — 149 шт., НО «полостных» только 1 (2026, Co-sputtered Nb3Sn films
   for SRF applications) — всё остальное МАГНИТЫ (ITER, HL-LHC, ундуляторы): SRF-сообщество НЕ публикуется в TAS.
3. results/snf_index/index.csv (IEEE-CSC News Forum, 2326): Nb3Sn — 26 шт., ПОЛОСТЕЙ — 0 (все магниты: LARP/HL-LHC).
4. ninja_conf_hits.json (IOP JPCS, 141): SRF-отсутствует (широкие keywords, шум).

Вывод для нарратива: «упирание» Nb видно в SRF-корпусе (пик ILC-докладов 2007 = ILC RDR на 31.5 МВ/м;
криокулер/гелиевый слой растёт 2002→2024 — давление стоимости крио; первый PoP Nb3Sn 2015 — как следствие).
Полостной конференц. сигнал Nb3Sn: 2016-17 (единичные) → 2023 (16) → 2025 (14): лабораторные прототипы
→ прототипы cryocooler/compact → «в развитии».

Выход:
  data/raw/conferences/srf_nb3sn_conf_subset.json — 59 conf-papers Nb3Sn SRF (паспорт рядом .md)
  case_studies/011_srf_cavities/plots/conf_nb3sn_by_year.png — график
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
SRF = ROOT / "data/raw/openalex/srf_corpus.json"
TAS = ROOT / "data/raw/conferences/conference_hits.json"
SNF = ROOT / "results/snf_index/index.csv"
SUB = ROOT / "data/raw/conferences/srf_nb3sn_conf_subset.json"
OUT = ROOT / "case_studies/011_srf_cavities/plots/conf_nb3sn_by_year.png"

PAT = re.compile(r"nb\s*3\s*sn|niobium[\s-]?tin|niob[\s-]?tin|b3sn", re.I)
PAT_SRF_CTX = re.compile(r"cavit|rf|accelerator|srf", re.I)

SCAN = [
    ("SRF-корпус (conf-papers)", json.loads(SRF.read_text(encoding="utf-8"))["works"],
     lambda w: w.get("type") == "conference-paper" and bool(PAT.search((w.get("title") or "") + " " + (w.get("abstract") or "")))),
    ("IEEE TAS (все)", json.loads(TAS.read_text(encoding="utf-8"))["items"],
     lambda w: bool(PAT.search((w.get("title") or "") + " " + (w.get("abstract") or "")))),
]


def main() -> None:
    for label, items, pred in SCAN:
        sel = [w for w in items if pred(w)]
        cav = [w for w in sel if re.search(r"cavit|rf application|superconducting rf|srf", (w.get("title") or ""), re.I)]
        print(f"{label}: Nb3Sn всего {len(sel)}, из них 'полостных' в title {len(cav)}")

    # ---- основной источник: conf-papers Nb3Sn из SRF-корпуса ----
    works = json.loads(SRF.read_text(encoding="utf-8"))["works"]
    nb_conf = [w for w in works
               if w.get("type") == "conference-paper"
               and PAT.search((w.get("title") or "") + " " + (w.get("abstract") or ""))]
    print("\nNb3Sn SRF conf-papers:", len(nb_conf))

    yc = Counter(w.get("year") for w in nb_conf if w.get("year"))
    lo, hi = 2010, 2026
    years = list(range(lo, hi + 1))
    cnt = [yc.get(y, 0) for y in years]

    # график
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.bar(years, cnt, color="#2ca02c", alpha=0.85)
    for x, y in zip(years, cnt):
        if y:
            ax.text(x, y + 0.2, str(y), ha="center", fontsize=8)
    ax.axvline(2018, color="black", ls="--", lw=1.1)
    ax.text(2018.2, max(cnt) * 0.93, "окно 2018", fontsize=9, rotation=90, va="top")
    for y, lbl in [(2015, "PoP Cornell"), (2023, "всплеск: cryocooler/compact")]:
        ax.annotate(lbl, xy=(y, yc.get(y, 0)), xytext=(y - 3.5, yc.get(y, 0) + max(cnt) * 0.1),
                    fontsize=8, color="darkgreen", arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.set_title(f"Конференционный сигнал ТРЕНДА Nb3Sn SRF ({len(nb_conf)} conf-papers, локальная база)\n"
                 "2016-17 единичные доклады → 2023+ прототипы (cryocooler, compact, JLab/Fermilab)", fontsize=11)
    ax.set_xlabel("год"); ax.set_ylabel("доклады"); ax.grid(alpha=0.3)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    print("saved:", OUT)

    SUB.write_text(json.dumps({
        "case": "011_srf_cavities", "signal": "conference (тренд Nb3Sn SRF)",
        "date": "2026-09-12",
        "source": "srf_corpus.json (type=conference-paper), ЛОКАЛЬНО, 0 API",
        "n_conf_nb3sn": len(nb_conf),
        "by_year": dict(sorted(yc.items())),
        "works_title": [{"year": w.get("year"), "title": w.get("title")} for w in nb_conf],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved:", SUB)

    print("\n== Nb3Sn conf-papers по годам ==")
    for y in sorted(yc):
        print(f"  {y}: {yc[y]}")


if __name__ == "__main__":
    main()