#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 012: патентный сигнал HTS-DC кабелей (Lens, sc_dc_cables.json).
График: патенты по годам + топ-игроки + классификация ТНК/НИИ/стартап. Без API.  """
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
PAT = ROOT / "data/raw/patents/cases/sc_dc_cables.json"
OUT = ROOT / "case_studies/012_dc_hvdc_cables/plots/patents_hts_dc_by_year.png"

# Классификация assignee по типу (ТНК / НИИ+универ / стартап-частник)
TNC = re.compile(
    r"SUMITOMO|NEXANS|GENERAL ELECTRIC|MITSUBISHI|TOSHIBA|HITACHI|FURUKAWA|FUJI|ABB\b|SIEMENS|"
    r"HYUNDAI|LS CABLE|AMSC|FUJIKURA|SEI\b|SHOWA|YAZAKI|TELEDYNE|SCHNEIDER|FURUKAWA"
)
LAB = re.compile(
    r"UNIV|UNIVERSITY|INSTITUTE|INST\b|RESEARCH|KEPCO|KERI|ORNL|FNAL|Fermi|JLAB|ACADEMY|"
    r"ЭЛЕКТРО|ИНСТИТУТ|УНИВЕРСИТЕТ|КУРЧАТОВ|MOSCOW|НИЦ|АКАДЕМИИ"
)

def classify(name: str) -> str:
    n = (name or "").upper()
    if LAB.search(n):
        return "НИИ/университет"
    if TNC.search(n):
        return "ТНК/корпорация"
    return "стартап/частник"


def main() -> None:
    d = json.loads(PAT.read_text(encoding="utf-8"))
    ps = d["patents"]

    # 1) по годам
    ys = Counter(p.get("year") for p in ps if p.get("year"))
    years = list(range(1968, 2027))
    vals = [ys.get(y, 0) for y in years]

    # 2) игроки + классификация
    assignees = Counter(p.get("assignee") for p in ps if p.get("assignee"))
    cls_total = Counter(classify(a) for a, _ in assignees.items())
    # доля с учётом числа патентов
    cls_pat = Counter()
    for p in ps:
        cls_pat[classify(p.get("assignee"))] += 1

    fig = plt.figure(figsize=(13, 7))
    ax = fig.add_subplot(111)
    ax.bar(years, vals, color="#2ca02c", alpha=0.85)
    ax.set_xlabel("Год")
    ax.set_ylabel("Патенты (абс.)")
    ax.set_title(f"Кейс 012: патентный сигнал HTS-DC кабелей — Lens, {len(ps)} патентов "
                 f"({d['inventions']} изобретений)")
    ax.set_xticks(range(1968, 2027, 3))
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.3)
    for y in (2004, 2005, 2010, 2014, 2018, 2022, 2023):
        if y in ys:
            ax.annotate(str(ys[y]), (y, ys[y]), ha="center", va="bottom", fontsize=8)
    ax.axvline(2018, color="red", ls="--", lw=1.2)
    ax.text(2018, max(vals) * 0.95, "окно 2018", color="red", fontsize=9, ha="center")

    # панель: топ assignee
    ax2 = fig.add_axes([0.71, 0.80, 0.26, 0.18])
    top = assignees.most_common(7)
    names = [n[:24] for n, _ in top]
    cnt = [c for _, c in top]
    ax2.barh(range(len(names))[::-1], cnt, color="#2ca02c", alpha=0.85)
    ax2.set_yticks(range(len(names))[::-1])
    ax2.set_yticklabels(names, fontsize=7)
    ax2.set_title("Топ-7 assignee", fontsize=9)
    ax2.tick_params(labelsize=7)

    # панель: классификация игроков (доля патентов)
    ax3 = fig.add_axes([0.40, 0.68, 0.30, 0.28])  # круговая — влево и вверх, не перекрывает бары
    labels = list(cls_pat.keys())
    sizes = [cls_pat[l] for l in labels]
    cols = {"ТНК/корпорация": "#d62728", "НИИ/университет": "#1f77b4", "стартап/частник": "#ff7f0e"}
    ax3.pie(sizes, labels=[f"{l}\n{n} ({n/sum(sizes)*100:.0f}%)" for l, n in zip(labels, sizes)],
            colors=[cols[l] for l in labels], startangle=90, textprops={"fontsize": 8})
    ax3.set_title("Доля игроков (по патентам)", fontsize=9)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"График → {OUT}")
    print(f"\nВсего: {len(ps)} патентов | relevant {d['relevant_count']} | изобретений {d['inventions']}")
    print(f"Пики: 2004-05 ({ys.get(2004,0)}/{ys.get(2005,0)}), 2010 ({ys.get(2010,0)}), 2022 ({ys.get(2022,0)})")
    print(f"\nТоп assignee: {assignees.most_common(10)}")
    print(f"\nКлассификация игроков (по патентам): {dict(cls_pat)}")
    print(f"Классификация (по числу assignee): {dict(cls_total)}")


if __name__ == "__main__":
    main()