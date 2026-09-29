#!/usr/bin/env python3
"""Докачка блока 3 (корпуса конкурентов) для S3-cross 008.
Перезапуск после 429. Ретраи с паузой, мягкие термины.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OA = ROOT / "data" / "raw" / "openalex"
OUT = ROOT / "results" / "case_signals" / "s3_cross_evolution_aircraft.json"
BUDGET_OUT = ROOT / "results" / "case_signals" / "s3_cross_evolution_budget.json"

MAILTO = "research@example.com"
HEADERS = {"User-Agent": f"research (mailto:{MAILTO})"}
SELECT = ("id,title,publication_year,cited_by_count,abstract_inverted_index,"
          "referenced_works,authorships,primary_location")

# Мягкие термины (без жёстких кавычек на всех словах)
COMPETITORS = {
    "pm_motor": '"permanent magnet" motor aircraft',
    "h2_fuelcell": '"fuel cell" aircraft propulsion hydrogen',
    "cryo_motor": 'cryogenic electric motor aircraft propulsion',
    "cryo_cual": 'cryogenic copper motor aircraft OR "cryogenic aluminum" aircraft motor',
}


def abstract_text(w):
    inv = w.get("abstract_inverted_index") or {}
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def fetch_paged_retry(query, max_pages=8, max_retries=4):
    """Пагинация с ретраями на 429 (пауза растёт)."""
    results, cursor, pages = [], "*", 0
    retries = 0
    while cursor and pages < max_pages:
        params = {"filter": f"title_and_abstract.search:{query}",
                  "per-page": "100", "cursor": cursor, "mailto": MAILTO, "select": SELECT}
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
            results.extend(data.get("results", []))
            cursor = data.get("meta", {}).get("next_cursor")
            pages += 1
            retries = 0
            time.sleep(2.5)
        except Exception as e:
            retries += 1
            print(f"    ! {type(e).__name__}: {e} (retry {retries})", flush=True)
            if retries > max_retries:
                print("    сдаюсь на этом запросе", flush=True)
                break
            time.sleep(15 * retries)
    return results, pages


def main() -> None:
    result = json.loads(OUT.read_text(encoding="utf-8"))
    budget = json.loads(BUDGET_OUT.read_text(encoding="utf-8")) if BUDGET_OUT.exists() else {"requests": [], "n_requests": 0}

    comp = result.get("competitors", {})
    for name, query in COMPETITORS.items():
        if name in comp and comp[name].get("works"):
            print(f"пропуск {name}: уже есть {len(comp[name]['works'])}")
            continue
        works, pages = fetch_paged_retry(query)
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
        comp[name] = {"query": query, "works": uniq, "n_raw": len(works), "pages": pages}
        print(f"  {name}: {len(uniq)} работ (raw {len(works)}, {pages} стр.)", flush=True)
        budget["requests"].append(("competitor", name))
        time.sleep(3)
    result["competitors"] = comp
    budget["n_requests"] = len(budget["requests"])
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    BUDGET_OUT.write_text(json.dumps(budget, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено. Запросов в этом запуске: {len(budget['requests'])}")
    for name, c in comp.items():
        print(f"  {name}: {len(c['works'])} работ")


if __name__ == "__main__":
    main()
