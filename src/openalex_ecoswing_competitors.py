#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 010 EcoSwing, ШАГ 3 GUIDE: корпус компьютерной литературы по КОНКУРЕНТАМ.

Проблема (мотивация СП-генератора): «генератор 10-20 MW из ветра, меньший вес/размер,
высокий КПД, без редких земель».
Конкуренты (роль 3 в классификации GUIDE ШАГ 2):
 1. PM-магниты прямого привода (PMSG/PM-DD) — действующий лидер
 2. DFIG + редуктор (doubly-fed) — действующий лидер
 3. Гидравлическая трансмиссия — альтернатива без магнитов
 4. Магнитный редуктор / псевдопрямой привод — альтернатива без магнитов
 5. Редкоземельные-свободные машины (ещё один путь) — молодой конкурент
Для каждого: полные записи, counts по годам (динамика). Способ — как openalex_ecoswing.py.
Выход: data/raw/openalex/ecoswing_competitors_corpus.json
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "openalex" / "ecoswing_competitors_corpus.json"
HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
SELECT = ("id,doi,title,display_name,publication_year,cited_by_count,publication_date,"
          "abstract_inverted_index,authorships,referenced_works,type,concepts")

# Конкуренты: (имя, запрос)
COMPETITORS = {
    "PM_DD": '"permanent magnet" AND ("direct drive" OR "direct-drive") AND "wind"',
    "DFIG": '"doubly fed induction generator" AND "wind turbine"',
    "hydraulic": '"hydraulic transmission" AND "wind turbine"',
    "magnetic_gear": '("magnetic gear" OR "pseudo direct drive") AND "wind turbine"',
    "no_rare_earth": '("rare earth free" OR "rare-earth-free" OR "ferrite") AND "wind generator"',
    "EcoSwing": '"EcoSwing"',
}


def api_get(url: str) -> dict:
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception as e:
            print(f"    retry {attempt+1}: {e}")
            time.sleep(2 + attempt * 4)
    return {}


def fetch_all(query: str, seen: dict, max_pages: int = 2):
    enc = urllib.parse.quote(query)
    cursor = "*"
    pages = 0
    while cursor and pages < max_pages:
        url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
               f"&per-page=100&select={SELECT}&cursor={cursor}&mailto={MAILTO}")
        d = api_get(url)
        results = d.get("results", [])
        if not results:
            break
        for w in results:
            wid = w.get("id")
            if wid and wid not in seen:
                inv = w.get("abstract_inverted_index")
                abstract = None
                if inv:
                    pos = {}
                    for word, idxs in inv.items():
                        for i in idxs:
                            pos[i] = word
                    abstract = " ".join(pos[i] for i in sorted(pos))
                authors = []
                for a in (w.get("authorships") or []):
                    au = a.get("author") or {}
                    inst = ((a.get("institutions") or [{}])[0] or {}).get("display_name")
                    authors.append({"name": au.get("display_name"), "institution": inst})
                seen[wid] = {
                    "id": wid, "doi": w.get("doi"), "title": w.get("title") or w.get("display_name"),
                    "year": w.get("publication_year"), "date": w.get("publication_date"),
                    "cited_by": w.get("cited_by_count"), "abstract": abstract,
                    "authors": authors, "references": w.get("referenced_works"),
                    "type": w.get("type"),
                    "concepts": [c.get("display_name") for c in (w.get("concepts") or [])],
                    "competitor": None,  # заполняем ниже
                }
        pages += 1
        cursor = d.get("meta", {}).get("next_cursor")
        print(f"    query: '{query[:45]}...' страница {pages}, накоплено {len(seen)}")
        time.sleep(1)
    return seen


def count_year(query: str) -> dict:
    enc = urllib.parse.quote(query)
    url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
           f"&group_by=publication_year&per-page=1&mailto={MAILTO}")
    d = api_get(url)
    return {g["key"]: g["count"] for g in d.get("group_by", [])}


def main():
    seen = {}
    counts = {}
    for name, q in COMPETITORS.items():
        print(f"\n=== {name}: {q}")
        fetch_all(q, seen)
        counts[name] = count_year(q)
        time.sleep(1)

    # пометить принадлежность к конкурентам
    comp_of = {}  # id -> список конкурентов
    for name, q in COMPETITORS.items():
        for wid, w in seen.items():
            t = (w["title"] or "") + " " + (w["abstract"] or "")
            # простая эвристика: конкурент по своему запросу
            if name == "EcoSwing":
                continue
            if "wind" not in t.lower() and name != "EcoSwing":
                continue
            comp_of.setdefault(wid, []).append(name)
    for wid in seen:
        if wid in comp_of:
            seen[wid]["competitors"] = comp_of[wid]

    works = sorted(seen.values(), key=lambda w: (w["year"] or 0))
    corpus = {
        "case": "010_ecoswing_sc_wind", "signal": "s1_competitors", "date": "2026-09-10",
        "method": "OpenAlex title_and_abstract.search, полные записи, cursor-пагинация, дедуп по id",
        "competitors": COMPETITORS, "counts_by_year": counts,
        "n_works": len(works), "works": works,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False)
    print(f"\nГотово: {len(works)} работ -> {OUT}")
    print("Counts по конкурентам (2005-18 / 2019-26):")
    for name, cy in counts.items():
        old = sum(v for k, v in cy.items() if 2005 <= int(k) <= 2018)
        new = sum(v for k, v in cy.items() if 2019 <= int(k) <= 2026)
        print(f"  {name:<16} 2005-18={old:<6} 2019-26={new}")


if __name__ == "__main__":
    main()