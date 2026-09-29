#!/usr/bin/env python3
"""ГЕОГРАФИЯ ПАТЕНТОВ IBAD-семейства (для кейса 001).

Показывает диффузию технологии: Запад+Япония (изобретатели) → Китай+Корея.
Две панели:
  1. Страна заявителя (assignee) по годам — кто патентует
  2. Накопленная доля: US+EU+JP vs CN+KR+IN

Данные: data/raw/patents/topics_window/ibad_merged.json (100 патентов).

Запуск:
    .venv/bin/python src/plot_patent_geography.py
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
DATA = ROOT / "data" / "raw" / "patents" / "topics_window" / "ibad_merged.json"
OUT = ROOT / "case_studies" / "001_ibad_mgo" / "plots" / "plot7_patent_geography.png"


def assignee_country(assignee: str) -> str:
    a = (assignee or "").lower()
    if re.search(r"fujikura|furukawa|sumitomo|toshiba|istec|swcc|international superconductivity"
                 r"|yoshizumi|fukushima|hatakeyama|昭和|古河|東芝|フジクラ|フルカワ|住友", a):
        return "JP"
    if re.search(r"[가-힣]|sunam|korea|kist|seoul|kim dong jin", a) and not re.search(r"スーパーパワー", a):
        return "KR"
    if re.search(r"[\u4e00-\u9fff]", a) and not re.search(r"[ぁ-んァ-ヶ]", a):
        return "CN"
    if re.search(r"shanghai|suzhou|univ electron|north china|beijing|zhao zuncheng", a):
        return "CN"
    if re.search(r"[ぁ-んァ-ヶ]", a):
        return "JP"
    if re.search(r"univ california|regents|lanl|los alamos|superpower|amsc|american super|houston"
                 r"|argonne|uchicago|univ chicago|guardian|ibeam|leland|stanford|metox|foltyn|jia"
                 r"|arendt|nz applied|mankevich|ut battelle|battelle|oak ridge|ornl|goyal|paranthaman"
                 r"|aytug|alliance sustainable|nrel|teplin|branz|heatherly|univ tennessee|quanxi", a):
        return "US"
    if re.search(r"theva|european|nexans|heraeus|bruker|germany|adelwitz|france|gmbh|barcelona"
                 r"|icmab|coated conductors consul|renaissance fusion", a):
        return "EU"
    return "?"


def main() -> None:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    pats = d["patents"]

    # По годам (priority) и стране заявителя
    years = {}
    for p in pats:
        y = (p.get("priority_date") or "")[:4]
        if not y.isdigit():
            continue
        c = assignee_country(p.get("assignee"))
        years.setdefault(int(y), Counter())[c] += 1

    all_years = sorted(years)
    countries = ["US", "JP", "CN", "KR", "EU", "?"]
    colors = {"US": "#4C72B0", "JP": "#DD8452", "CN": "#C44E52",
              "KR": "#55A868", "EU": "#8172B3", "?": "#CCCCCC"}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9))

    # 1) Стэкинг: страна заявителя по годам
    bottom = [0] * len(all_years)
    for c in countries:
        vals = [years[y].get(c, 0) for y in all_years]
        ax1.bar([str(y) for y in all_years], vals, bottom=bottom,
                label=c, color=colors[c], alpha=0.9)
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax1.set_ylabel("Патенты (priority year)")
    ax1.set_title("География патентования IBAD-семейства (по стране заявителя)")
    ax1.legend(ncol=6, fontsize=8)
    ax1.grid(axis="y", alpha=0.3)

    # 2) Накопленная доля: Запад+JP vs CN+KR
    west = ["US", "EU", "JP"]
    east = ["CN", "KR"]
    cum_west, cum_east = [], []
    w = e = 0
    for y in all_years:
        w += sum(years[y].get(c, 0) for c in west)
        e += sum(years[y].get(c, 0) for c in east)
        cum_west.append(w)
        cum_east.append(e)
    ax2.plot([str(y) for y in all_years], cum_west, "o-", color="#4C72B0",
             label="US+EU+JP (накопл.)")
    ax2.plot([str(y) for y in all_years], cum_east, "s-", color="#C44E52",
             label="CN+KR (накопл.)")
    # Точка перелома (пересечение)
    for i, (y, wv, ev) in enumerate(zip(all_years, cum_west, cum_east)):
        if wv >= ev:
            ax2.axvline(str(y), color="gray", ls="--", alpha=0.5)
            ax2.annotate(f"перелом ~{y}", xy=(str(y), wv), xytext=(10, -10),
                         textcoords="offset points", fontsize=9, color="gray")
            break
    ax2.set_ylabel("Накопленные патенты")
    ax2.set_xlabel("Год")
    ax2.set_title("Накопленная диффузия: Запад+Япония → Китай+Корея")
    ax2.legend(fontsize=9)
    ax2.grid(alpha=0.3)

    # Статистика
    total_c = Counter(assignee_country(p.get("assignee")) for p in pats)
    print("=== География (страна заявителя) ===")
    for c in ["US", "JP", "CN", "KR", "EU", "?"]:
        print(f"  {c}: {total_c.get(c, 0)}")
    print(f"\nЗапад (US+EU+JP): {total_c.get('US',0)+total_c.get('EU',0)+total_c.get('JP',0)}")
    print(f"Восток (CN+KR): {total_c.get('CN',0)+total_c.get('KR',0)}")

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150)
    print(f"\nСохранено: {OUT}")


if __name__ == "__main__":
    main()
