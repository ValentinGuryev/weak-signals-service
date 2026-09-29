#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Пилот фарма-валидации: сбор публикаций по 3 направлениям (CAR-T, CRISPR, микробиом).

Метод: OpenAlex title_and_abstract.search по рабочим терминам направления.
Для каждого направления:
  - counts_by_year (для S1/роста/EScore)
  - корпус с abstracts (для impact/новизны), ограниченный (первые N по релевантности)
Пилот: 3 направления → проверить, что фичи собираются и модель разделяет.
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

# Направление -> список запросов title_and_abstract (OR через несколько запросов)
DIRECTIONS = {
    "car_t": {
        "name": "CAR-T терапии",
        "queries": ['"CAR T cell" OR "chimeric antigen receptor T"',
                    '"CAR-T therapy" OR "CAR T therapy"'],
        "note": "CAR-T: Kymriah 2017 (первое одобрение) → обещание ~2018",
    },
    "crispr_therapy": {
        "name": "CRISPR-терапии (gene editing therapeutics)",
        "queries": ['"CRISPR" AND (therapy OR therapeutic OR clinical OR "gene editing")'],
        "note": "CRISPR: революция ~2016 → Casgevy 2023 (1-е одобрение)",
    },
    "microbiome_therapy": {
        "name": "Микробиом-терапии",
        "queries": ['"microbiome" AND (therapy OR therapeutic OR "fecal transplant" OR live biotherapeutic)'],
        "note": "Микробиом: 'следующий рубеж' ~2015 → почти нет одобрений",
    },
}

MAX_WORKS_PER_DIR = 400  # ограничение корпуса для пилота


def api_get(url: str) -> dict:
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            print(f"  retry {attempt+1}: {e}")
            time.sleep(2 + attempt * 3)
    return {}


def collect(direction: str, cfg: dict) -> dict:
    print(f"\n=== {cfg['name']} ===")
    counts = defaultdict(int)
    works_by_id = {}

    for qi, q in enumerate(cfg["queries"]):
        enc = urllib.parse.quote(q)
        # counts by year
        url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
               f",publication_year:1995-2026&group_by=publication_year&per-page=200")
        d = api_get(url)
        for grp in d.get("group_by", []):
            counts[int(grp["key"])] += grp["count"]
        # корпус (первые MAX по цитируемости), только если ещё не набрали
        if len(works_by_id) < MAX_WORKS_PER_DIR:
            url2 = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
                    f",publication_year:1995-2026&per-page=100&sort=cited_by_count:desc"
                    f"&select=id,title,publication_year,cited_by_count,abstract_inverted_index")
            # селект без abstract_inverted_index — качаем отдельно? Для пилота возьмём с abs
            url2 = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
                    f",publication_year:1995-2026&per-page=100&sort=cited_by_count:desc")
            d2 = api_get(url2)
            for w in d2.get("results", []):
                wid = w["id"]
                if wid not in works_by_id:
                    works_by_id[wid] = {
                        "id": wid,
                        "title": w.get("title"),
                        "year": w.get("publication_year"),
                        "cited_by": w.get("cited_by_count"),
                        "abstract": _reconstruct_abstract(w.get("abstract_inverted_index")),
                    }
        time.sleep(1)  # rate-limit вежливость

    result = {
        "direction": direction,
        "name": cfg["name"],
        "note": cfg["note"],
        "queries": cfg["queries"],
        "counts_by_year": dict(sorted(counts.items())),
        "total_counted": sum(counts.values()),
        "corpus_size": len(works_by_id),
        "works": list(works_by_id.values()),
    }
    return result


def _reconstruct_abstract(inv):
    if not inv:
        return None
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def main():
    all_data = {}
    for direction, cfg in DIRECTIONS.items():
        res = collect(direction, cfg)
        all_data[direction] = res
        # сохраняем по-направлению
        with open(OUT / f"{direction}.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print(f"  {direction}: counts сумма={res['total_counted']}, корпус={res['corpus_size']}")

    with open(OUT / "pilot_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=1)
    print("\nГотово. Файлы в pharma_calibration/data/")


if __name__ == "__main__":
    main()
