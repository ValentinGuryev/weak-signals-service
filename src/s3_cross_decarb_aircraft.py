#!/usr/bin/env python3
"""Кейс 008: (1) counts полей декарбонизации авиации + (2) корпуса SAF/BLI/аммиак для cross.

Санкция: 20 запросов OpenAlex. Паузы 3-4с, retry при 429.
Часть 1 (counts, group_by): новые поля-энергоносители для нормировки 'всё поле декарбонизации'.
Часть 2 (корпуса с references): узкие корпуса SAF/turboelectric-BLI/ammonia для cross-цитирования.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OA = ROOT / "data" / "raw" / "openalex"
OUT = ROOT / "results" / "case_signals" / "s3_cross_decarb_aircraft.json"
BUDGET = ROOT / "results" / "case_signals" / "s3_decarb_budget.json"

MAILTO = "research@example.com"
HEADERS = {"User-Agent": f"research (mailto:{MAILTO})"}
SELECT = ("id,title,publication_year,cited_by_count,abstract_inverted_index,"
          "referenced_works,authorships,primary_location")
PAUSE = 4.0  # секунд между запросами (защита от rate-limit)


def group_by_year(query, pause=PAUSE):
    """counts работ по годам для title_and_abstract.search (1 запрос)."""
    params = {"filter": f"title_and_abstract.search:{query}",
              "group_by": "publication_year", "per-page": "50", "mailto": MAILTO}
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
            return {g["key"]: g["count"] for g in (data.get("group_by") or [])}
        except Exception as e:
            print(f"    ! {type(e).__name__}: {e} (attempt {attempt+1})", flush=True)
            time.sleep(12 * (attempt + 1))
    return {}


def abstract_text(w):
    inv = w.get("abstract_inverted_index") or {}
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def fetch_paged(query, max_pages=6):
    """Пагинация cursor, с паузами и retry."""
    results, cursor, pages = [], "*", 0
    while cursor and pages < max_pages:
        params = {"filter": f"title_and_abstract.search:{query}",
                  "per-page": "100", "cursor": cursor, "mailto": MAILTO, "select": SELECT}
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        for attempt in range(4):
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.load(r)
                results.extend(data.get("results", []))
                cursor = data.get("meta", {}).get("next_cursor")
                pages += 1
                time.sleep(PAUSE)
                break
            except Exception as e:
                print(f"    ! {type(e).__name__}: {e} (attempt {attempt+1})", flush=True)
                time.sleep(12 * (attempt + 1))
        else:
            break
    return results, pages


# Часть 1: counts полей декарбонизации (нормировка 'всё поле')
DECARB_FIELDS = {
    "saf": '"sustainable aviation fuel" OR "alternative aviation fuel" OR "biojet" OR "bio-jet"',
    "hydrogen_aviation": '"hydrogen" aircraft propulsion OR "hydrogen-powered aircraft" OR "liquid hydrogen" aircraft',
    "electric_aircraft_all": '"electric aircraft" OR "electrified aircraft" OR "electric propulsion" aircraft',
    "turboelectric_bli": '"turboelectric" OR "boundary layer ingestion" OR "distributed electric propulsion"',
    "ammonia_aviation": '"ammonia" aircraft OR "ammonia" aviation OR "power-to-liquid" aviation',
    "battery_aviation": '"battery" electric aircraft OR "lithium" aircraft battery',
}

# Часть 2: узкие корпуса конкурентов (с references) для cross
CROSS_CORPORA = {
    "saf_core": '"sustainable aviation fuel" aircraft',
    "turbo_bli": '"turboelectric" aircraft OR "boundary layer ingestion" aircraft',
    "ammonia_av": '"ammonia" aircraft propulsion OR "ammonia" aviation fuel',
}


def main() -> None:
    result = {"decarb_counts": {}, "cross_corpora": {}}
    budget_log = []

    print("== Часть 1: counts полей декарбонизации ==")
    for name, q in DECARB_FIELDS.items():
        cy = group_by_year(q)
        result["decarb_counts"][name] = {k: v for k, v in sorted(cy.items())}
        tot = sum(cy.values())
        peak = max(cy, key=cy.get) if cy else "?"
        print(f"  {name}: всего~{tot}, пик {peak}", flush=True)
        budget_log.append(("counts", name))
        time.sleep(PAUSE)

    print("\n== Часть 2: корпуса конкурентов (references) ==")
    for name, q in CROSS_CORPORA.items():
        works, pages = fetch_paged(q)
        seen, uniq = set(), []
        for w in works:
            if w["id"] in seen:
                continue
            seen.add(w["id"])
            uniq.append({
                "id": w["id"], "title": w.get("title"), "year": w.get("publication_year"),
                "cited_by": w.get("cited_by_count"), "abstract": abstract_text(w),
                "referenced_works": w.get("referenced_works") or [],
            })
        result["cross_corpora"][name] = {"query": q, "works": uniq,
                                         "n_raw": len(works), "pages": pages}
        print(f"  {name}: {len(uniq)} работ (raw {len(works)}, {pages} стр.)", flush=True)
        budget_log.append(("corpus", name))
        time.sleep(PAUSE)

    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    BUDGET.write_text(json.dumps({"requests": budget_log, "n_requests": len(budget_log)},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT}")
    print(f"Запросов: {len(budget_log)}")


if __name__ == "__main__":
    main()
