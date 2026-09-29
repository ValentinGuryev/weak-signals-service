#!/usr/bin/env python3
"""S5 для кейса 005 (SMES): counts_by_year SMES vs Li-ion BESS vs supercap.

Поиск OpenAlex /works по title.search:
  - smes:      "superconducting magnetic energy storage"
  - bess:      "battery energy storage system" OR "lithium-ion battery energy storage"
  - liion:     "lithium-ion battery" (для динамики цены-прокси? нет, это статьи)
  - supercap:  "supercapacitor energy storage"

counts_by_year по группам. Прямой доступ (малые запросы).
Выход: data/raw/openalex/smes_vs_bess_counts.json
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "smes_vs_bess_counts.json"

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"

QUERIES = {
    "SMES": '"superconducting magnetic energy storage"',
    "BESS": '"battery energy storage system"',
    "Li-ion": '"lithium-ion battery" energy storage',
    "Supercap": '"supercapacitor" energy storage',
}


def count_year(query: str) -> dict:
    """Год публикации -> число работ (counts_by_year по поиску)."""
    # OpenAlex: /works?filter=title.search:...&group_by=publication_year
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
        years = count_year(q)
        # только 1990-2026
        years = {int(y): c for y, c in years.items() if 1990 <= int(y) <= 2026}
        result[label] = years
        tot = sum(years.values())
        peak = max(years.items(), key=lambda x: x[1]) if years else (0, 0)
        print(f"  всего {tot}, пик {peak}")
        time.sleep(1)

    OUT.write_text(json.dumps({
        "query": "SMES vs BESS vs Li-ion vs Supercap (кейс 005 S5)",
        "downloaded": time.strftime("%Y-%m-%d"),
        "method": "OpenAlex title.search + group_by publication_year",
        "counts": result,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT}")


if __name__ == "__main__":
    main()
