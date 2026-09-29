#!/usr/bin/env python3
"""S3-cross + эволюция цитирований для кейса 008 (СП-авиадвигатели).

Три блока (санкция: <=25 запросов OpenAlex):
  1. Траектории цитирования ядер core по годам (cites:W<id>, group_by) — 5 запросов.
  2. Названия топ-N внешних референсов core (batch по id) — 2 запроса.
  3. Корпуса конкурентов (полный select: id,title,year,cited_by,abstract,references,authorships)
     для cross-эволюции core <-> конкуренты — пагинация, ~17 запросов.
Выход: results/case_signals/s3_cross_evolution_aircraft.json + графики.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OA = ROOT / "data" / "raw" / "openalex"
OUT_DIR = ROOT / "results" / "case_signals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAILTO = "research@example.com"
HEADERS = {"User-Agent": f"research (mailto:{MAILTO})"}
SELECT = ("id,title,publication_year,cited_by_count,abstract_inverted_index,"
          "referenced_works,authorships,primary_location")

# Ядра core (топ по внутренним ссылкам)
CORE_ANCHORS = {
    "W2096918924": "2009 MEA/HTS обзор",        # Next Generation MEA (58 внутр.)
    "W2125204175": "2005 Masson SC motor",       # High Power Density SC Motor (28)
    "W2061142259": "2015 HTS Distributed Propulsion",  # (29)
    "W3106549481": "2020 ASuMED",                # (35)
    "W3038788421": "2020 fully-SC air-core",     # (28)
}

# Конкуренты: термины для корпусов (узкие, ядро конкуренции)
COMPETITORS = {
    "pm_motor": '"permanent magnet" motor aircraft propulsion',
    "h2_fuelcell": '"hydrogen" "fuel cell" aircraft propulsion',
    "cryo_motor": 'cryogenic motor aircraft propulsion',
    "cryo_cual": 'cryogenic (copper OR aluminum OR aluminium) motor aircraft',
}


def abstract_text(w):
    inv = w.get("abstract_inverted_index") or {}
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def fetch_paged(query, extra_filters="", max_pages=12):
    """Пагинация cursor по поисковому запросу."""
    results, cursor, pages = [], "*", 0
    while cursor and pages < max_pages:
        f = f"title_and_abstract.search:{query}"
        if extra_filters:
            f += f",{extra_filters}"
        params = {"filter": f, "per-page": "100", "cursor": cursor,
                  "mailto": MAILTO, "select": SELECT}
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
            results.extend(data.get("results", []))
            cursor = data.get("meta", {}).get("next_cursor")
            pages += 1
            time.sleep(0.35)
        except Exception as e:
            print(f"    ! fetch: {e}", file=sys.stderr)
            time.sleep(10)
            break
    return results, pages


def fetch_by_ids(ids, select=SELECT):
    """Один batch-запрос по списку id (до 100)."""
    idf = "|".join("https://openalex.org/" + i if not i.startswith("http") else i for i in ids)
    params = {"filter": f"openalex_id:{idf}", "per-page": "100",
              "mailto": MAILTO, "select": select}
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r).get("results", [])


def group_by_year(filter_str):
    """counts работ по годам для filter (например cites:W..., publication_year>2000)."""
    params = {"filter": filter_str, "group_by": "publication_year",
              "per-page": "50", "mailto": MAILTO}
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return {g["key"]: g["count"] for g in (json.load(r).get("group_by") or [])}


def main() -> None:
    budget_log = []
    result = {"anchors_trajectories": {}, "external_refs": {}, "competitors": {}}

    # ---- Блок 1: траектории ядер core по годам (5 запросов) ----
    print("== Блок 1: траектории ядер ==")
    for wid, label in CORE_ANCHORS.items():
        try:
            cy = group_by_year(f"cites:W{wid},from_publication_date:2000-01-01")
            result["anchors_trajectories"][label] = dict(sorted(cy.items()))
            print(f"  {label}: {sum(cy.values())} цит. всего, пик {max(cy, key=cy.get) if cy else '?'}")
        except Exception as e:
            print(f"  ! {label}: {e}")
        budget_log.append(("trajectory", wid))
        time.sleep(0.5)

    # ---- Блок 2: внешние референсы core (2 batch-запроса) ----
    print("\n== Блок 2: внешние референсы core ==")
    corp = json.loads((OA / "sc_aircraft_motors_corpus.json").read_text(encoding="utf-8"))["works"]
    ids = {w["id"] for w in corp}
    ext = Counter()
    for w in corp:
        for r in (w.get("referenced_works") or []):
            if r not in ids:
                ext[r] += 1
    top_ext = [wid for wid, _ in ext.most_common(200)]
    ext_by_year = defaultdict(Counter)  # year -> ext_id -> count
    for w in corp:
        for r in (w.get("referenced_works") or []):
            if r not in ids and r in set(top_ext):
                ext_by_year[w["year"]][r] += 1
    for chunk_i in range(0, len(top_ext), 100):
        chunk = top_ext[chunk_i:chunk_i + 100]
        try:
            works = fetch_by_ids(chunk)
            meta = {w["id"]: w for w in works}
            for wid in chunk:
                w = meta.get("https://openalex.org/" + wid)
                if w:
                    result["external_refs"][wid] = {
                        "title": w.get("title"), "year": w.get("publication_year"),
                        "cited_by": w.get("cited_by_count"),
                        "n_cited_by_core": ext[wid],
                        "cited_by_core_years": {str(y): c for y, c in ext_by_year.items()},
                    }
            print(f"  chunk {chunk_i//100+1}: {len(works)} работ получено")
        except Exception as e:
            print(f"  ! chunk: {e}")
        budget_log.append(("external_refs", f"chunk{chunk_i//100+1}"))
        time.sleep(0.5)

    # ---- Блок 3: корпуса конкурентов (пагинация) ----
    print("\n== Блок 3: корпуса конкурентов ==")
    for name, query in COMPETITORS.items():
        works, pages = fetch_paged(query)
        # дедуп по id
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
        result["competitors"][name] = {
            "query": query, "works": uniq, "n_raw": len(works), "pages": pages,
        }
        print(f"  {name}: {len(uniq)} работ (raw {len(works)}, {pages} стр.)")
        budget_log.append(("competitor", name))
        time.sleep(0.6)

    # ---- Сохранение ----
    out = OUT_DIR / "s3_cross_evolution_aircraft.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(OUT_DIR / "s3_cross_evolution_budget.json", "w") as f:
        json.dump({"requests": budget_log, "n_requests": len(budget_log)}, f, ensure_ascii=False, indent=1)
    print(f"\nСохранено: {out}")
    print(f"Запросов использовано: {len(budget_log)}")


if __name__ == "__main__":
    main()
