#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011: докачка корпуса проблемными формулировками (ШАГ 2 GUIDE — «от проблемы»), v2.

ИДЕМПОТЕНТНЫЙ MERGE: seen = srf_corpus.json ∪ существующий srf_problem_supplement.json.
Ранняя остановка на запросах, уже полностью покрытых корпусом (3 пустых страницы подряд).
На 429 — длинный backoff (30/60/120 с), переживающий окно rate-limit'а.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data/raw/openalex/srf_corpus.json"
SUPP = ROOT / "data/raw/openalex/srf_problem_supplement.json"
HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
MAX_PAGES = 25

SELECT = ("id,doi,title,display_name,publication_year,cited_by_count,publication_date,"
          "abstract_inverted_index,authorships,referenced_works,type,concepts")

QUERIES = [
    ("B1 normal-conducting", '"normal conducting" AND ("linac" OR "accelerator" OR "cavity" OR "structure")'),
    ("B2 copper structure", '"copper" AND ("accelerating structure" OR "RF cavity")'),
    ("B3 CLIC", '"CLIC" AND ("collider" OR "accelerator" OR "structure")'),
    ("B4 two-beam", '"two-beam accelerator"'),
    ("A1 high-gradient structures", '"high gradient" AND ("linac" OR "accelerator" OR "cavity")'),
    ("A7 accelerating gradient", '"accelerating gradient"'),
    ("C1 DLA", '"dielectric laser acceleration" OR "dielectric laser accelerator"'),
    ("C2 dielectric wakefield", '"dielectric wakefield"'),
    ("C5 THz structures", '"THz" AND ("accelerator" OR "linac") AND ("structure" OR "cavity")'),
    ("C3 plasma wakefield", '"plasma wakefield acceleration"'),
    ("C4 laser wakefield", '"laser wakefield acceleration"'),
    ("E1 MgB2 SRF", '"MgB2" AND ("radiofrequency" OR "SRF" OR "RF cavity")'),
    ("E2 NbN film SRF", '"NbN" AND ("SRF" OR "superconducting RF" OR "RF cavity")'),
    ("E3 NbTiN film SRF", '"NbTiN" AND ("cavity" OR "SRF" OR "radiofrequency")'),
    ("E4 SIS multilayer", '"SIS multilayer"'),
]


def api_get(url: str) -> dict:
    for attempt, wait in [(1, 30), (2, 60), (3, 120)]:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            print(f"    retry {attempt}: {e} — жду {wait}s", flush=True)
            time.sleep(wait)
    return {}


def parse_work(w: dict) -> dict:
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
    return {
        "id": w.get("id"), "doi": w.get("doi"), "title": w.get("title") or w.get("display_name"),
        "year": w.get("publication_year"), "date": w.get("publication_date"),
        "cited_by": w.get("cited_by_count"), "abstract": abstract,
        "authors": authors, "references": w.get("referenced_works"),
        "type": w.get("type"),
        "concepts": [c.get("display_name") for c in (w.get("concepts") or [])],
    }


def main():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    seen = {w["id"] for w in corpus["works"]}
    supp = {}
    if SUPP.exists():
        old = json.loads(SUPP.read_text(encoding="utf-8"))
        for w in old["works"]:
            supp[w["id"]] = w
            seen.add(w["id"])
    print(f"seen: корпус {len(corpus['works'])} + дополнение {len(supp)} = {len(seen)}", flush=True)

    for label, q in QUERIES:
        enc = urllib.parse.quote(q)
        cursor = "*"
        pages = 0
        zero_pages = 0
        n_new = 0
        print(f"=== {label} …", flush=True)
        while cursor and pages < MAX_PAGES:
            url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
                   f"&per-page=200&select={SELECT}&cursor={cursor}&mailto={MAILTO}")
            d = api_get(url)
            results = d.get("results", [])
            if not results:
                break
            add = 0
            for w in results:
                wid = w.get("id")
                if wid and wid not in seen:
                    seen.add(wid)
                    supp[wid] = parse_work(w)
                    add += 1
            n_new += add
            pages += 1
            cursor = d.get("meta", {}).get("next_cursor")
            zero_pages = zero_pages + 1 if add == 0 else 0
            print(f"    стр.{pages}: +{add} (по запросу {n_new}; в дополнении {len(supp)})", flush=True)
            time.sleep(2.5)
            if zero_pages >= 3:
                print("    → перекрыто, ранняя остановка", flush=True)
                break
        print(f"  ИТОГО {label}: +{n_new}", flush=True)

    works = sorted(supp.values(), key=lambda w: (w["year"] or 0))
    out = {
        "case": "011_srf_cavities", "signal": "s1a_publications_supplement",
        "date": "2026-09-13", "parent": "srf_corpus.json",
        "method": "OpenAlex title_and_abstract.search, полные записи, cursor, дедуп по id, MERGE-идемпотентно",
        "queries": [q for _, q in QUERIES], "n_works": len(works), "works": works,
    }
    SUPP.parent.mkdir(parents=True, exist_ok=True)
    with open(SUPP, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"\nГотово: дополнение {len(works)} работ → {SUPP}", flush=True)
    print(f"Объединённый корпус: {len(corpus['works']) + len(works)}", flush=True)


if __name__ == "__main__":
    main()