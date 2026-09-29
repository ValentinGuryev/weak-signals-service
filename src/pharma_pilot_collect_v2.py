#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Пилот фарма-валидации v2: counts по ЯКОРНЫМ одобренным препаратам направления.

Почему v2: поиск по общим терминам (CAR-T, CRISPR therapy) даёт шум в OpenAlex
(fulltext ловит упоминания). Чистый сигнал направления = по конкретным одобренным
препаратам (Kymriah, Casgevy, Wegovy...), как в фарме определяют класс.

Для каждого направления:
  - якорные препараты (одобренные FDA/EMA, год одобрения)
  - counts_by_year по каждому (title_and_abstract)
  - суммарный counts (объём темы-как-рынка)
  - корпус топ-работ (для impact/новизны, ограниченный)

Пилот: CAR-T, CRISPR-терапии, микробиом (3 контрастных исхода).
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pharma_calibration" / "data"
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "research (mailto:research@example.com)"}

DIRECTIONS = {
    "car_t": {
        "name": "CAR-T терапии",
        "promise_2018": "Kymriah/Yescarta одобрены 2017 — «прорыв», обещание персонализированной терапии рака",
        "anchors": [  # (препарат, год первого одобрения FDA)
            ("Kymriah", "tisagenlecleucel", 2017),
            ("Yescarta", "axicabtagene", 2017),
            ("Breyanzi", "lisocabtagene", 2021),
            ("Carvykti", "ciltacabtagene", 2022),
        ],
    },
    "crispr_therapy": {
        "name": "CRISPR-терапии (gene editing)",
        "promise_2018": "CRISPR «революция» с 2016; обещание Casgevy (серповидноклеточная) в разработке",
        "anchors": [
            ("Casgevy", "exagamglogene", 2023),
            ("Lyfgenia", "lovotibeglogene", 2023),
        ],
    },
    "microbiome_therapy": {
        "name": "Микробиом-терапии",
        "promise_2018": "«Следующий рубеж» ~2015; обещание FMT/LBP-терапий",
        "anchors": [
            ("Rebyota", "fecal microbiota", 2022),
            ("Vowst", "fecal microbiota spores", 2023),
        ],
    },
}

MAX_WORKS = 150


def api_get(url: str) -> dict:
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            print(f"    retry {attempt+1}: {e}")
            time.sleep(2 + attempt * 3)
    return {}


def anchor_query(anchor_name: str, anchor_term: str) -> str:
    # запрос по торговому имени ИЛИ генерическому — чисто
    return f'"{anchor_name}" OR "{anchor_term}"'


def collect(direction: str, cfg: dict) -> dict:
    print(f"\n=== {cfg['name']} ===")
    per_anchor = {}
    total_counts = defaultdict(int)
    works_by_id = {}

    for anchor_name, anchor_term, fda_year in cfg["anchors"]:
        q = anchor_query(anchor_name, anchor_term)
        enc = urllib.parse.quote(q)
        url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
               f",publication_year:2000-2026&group_by=publication_year&per-page=200")
        d = api_get(url)
        gb = {int(g["key"]): g["count"] for g in d.get("group_by", [])}
        per_anchor[anchor_name] = {"fda_year": fda_year, "counts": dict(sorted(gb.items()))}
        for y, c in gb.items():
            total_counts[y] += c
        # корпус (топ по цитируемости)
        if len(works_by_id) < MAX_WORKS:
            url2 = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
                    f",publication_year:2000-2026&per-page=50&sort=cited_by_count:desc")
            d2 = api_get(url2)
            for w in d2.get("results", []):
                wid = w["id"]
                if wid not in works_by_id and len(works_by_id) < MAX_WORKS:
                    works_by_id[wid] = {
                        "id": wid, "title": w.get("title"), "year": w.get("publication_year"),
                        "cited_by": w.get("cited_by_count"),
                    }
        time.sleep(1)

    return {
        "direction": direction, "name": cfg["name"], "promise_2018": cfg["promise_2018"],
        "anchors": per_anchor, "total_counts_by_year": dict(sorted(total_counts.items())),
        "total": sum(total_counts.values()), "corpus_size": len(works_by_id),
        "works": list(works_by_id.values()),
    }


def main():
    for direction, cfg in DIRECTIONS.items():
        res = collect(direction, cfg)
        with open(OUT / f"{direction}_v2.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        c = res["total_counts_by_year"]
        def seg(a, b): return sum(v for y, v in c.items() if a <= y <= b)
        print(f"  {direction}: total={res['total']} | до2010={seg(2000,2010)} 11-15={seg(2011,2015)} "
              f"16-18={seg(2016,2018)} 19-21={seg(2019,2021)} 22-26={seg(2022,2026)} | корпус={res['corpus_size']}")
    print("\nГотово v2.")


if __name__ == "__main__":
    main()
