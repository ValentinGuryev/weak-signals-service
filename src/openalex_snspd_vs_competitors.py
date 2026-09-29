#!/usr/bin/env python3
"""S5 для кейса 006 (SNSPD): counts_by_year SNSPD vs конкуренты детекции одиночных фотонов.

Поиск OpenAlex /works по title.search (группировка по году):
  - SNSPD:     "superconducting nanowire single-photon detector"
  - TES:       "transition edge sensor" (общий класс — и фотоны, и X-ray)
  - InGaAs SPAD / APD:  "InGaAs avalanche photodiode" single photon
  - SPAD (Si): "single photon avalanche diode"
  - MKID:      "microwave kinetic inductance detector"
  - PMT:       "photomultiplier tube" single photon

Выход: data/raw/openalex/snspd_vs_competitors_counts.json
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "snspd_vs_competitors_counts.json"

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"

QUERIES = {
    "SNSPD": '"superconducting nanowire single-photon detector"',
    "TES": '"transition edge sensor"',
    "InGaAs_SPAD": '"InGaAs avalanche photodiode" single photon',
    "Si_SPAD": '"single photon avalanche diode"',
    "MKID": '"microwave kinetic inductance detector"',
    "PMT": '"photomultiplier tube" single photon',
}


def count_year(query: str) -> dict:
    """Год публикации -> число работ (counts_by_year по поиску)."""
    params = {
        "filter": f"title.search:{query}",
        "group_by": "publication_year",
        "mailto": MAILTO,
    }
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.load(r)
            groups = {g["key"]: g["count"] for g in data.get("group_by", [])}
            return groups
        except Exception as e:
            print(f"  попытка {attempt+1}: {e}")
            time.sleep(5 * (attempt + 1))
    return {}


def main() -> None:
    result = {}
    for label, q in QUERIES.items():
        print(f"=== {label}: {q}")
        counts = count_year(q)
        # отфильтровать 2000-2026
        years = {int(y): c for y, c in counts.items() if 2000 <= int(y) <= 2026}
        total = sum(years.values())
        result[label] = {"total": total, "counts_by_year": {y: years[y] for y in sorted(years)}}
        print(f"    total {total}")
        time.sleep(1.2)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(f"\nСохранено: {OUT}")
    print("\n=== Сводка по годам (выборочно) ===")
    for y in [2005, 2010, 2015, 2018, 2020, 2022, 2024, 2026]:
        row = [f"{k}: {v['counts_by_year'].get(y, 0)}" for k, v in result.items()]
        print(f"  {y}: " + " | ".join(row))


if __name__ == "__main__":
    main()
