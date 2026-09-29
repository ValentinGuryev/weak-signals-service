#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 012: дособор групп CU-DC, GIL, URBAN, DATACENTER (после сброса rate-limit).
MERGE-идемпотентно в dc_cables_problem.json; прогресс-сохранение после каждого запроса.
"""
from __future__ import annotations
import json, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/raw/openalex/dc_cables_problem.json"
HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
MAX_PAGES = 25
SELECT = ("id,doi,title,display_name,publication_year,cited_by_count,publication_date,"
          "abstract_inverted_index,authorships,referenced_works,type,concepts")
QUERIES = [
    ("CU-DC", "d1 xlpe underground", '"XLPE" AND ("cable" OR "underground" OR "transmission")'),
    ("CU-DC", "d2 hvdc underground", '"HVDC" AND ("underground" OR "city" OR "space")'),
    ("CU-DC", "d3 hvdc transmission", '"HVDC" AND ("transmission" OR "line")'),
    ("CU-DC", "d4 copper loss", '"power loss" AND ("cable" OR "transmission line") AND ("city" OR "underground")'),
    ("GIL", "g1 gil", '"gas-insulated" AND ("line" OR "transmission" OR "cable")'),
    ("GIL", "g2 gil hvdc", '"gas insulated line"'),
    ("URBAN", "u1 urban grid", '"urban" AND ("power grid" OR "distribution" OR "transmission") AND "cable"'),
    ("URBAN", "u2 underground line", '"underground" AND ("power line" OR "cable" OR "transmission")'),
    ("URBAN", "u3 right of way", '"right of way" AND ("power" OR "transmission" OR "cable")'),
    ("URBAN", "u4 substation city", '"substation" AND ("city" OR "urban") AND ("capacity" OR "expansion")'),
    ("DATACENTER", "e1 dc data center", '"data center" AND ("DC power" OR "380 V" OR "800 V" OR "distribution")'),
    ("DATACENTER", "e2 hvdc data center", '"HVDC" AND ("data center" OR "hyperscaler")'),
    ("DATACENTER", "e3 datacenter efficiency", '"data center" AND ("efficiency" OR "power delivery") AND ("DC" OR "voltage")'),
    ("DATACENTER", "e4 dc microgrid", '"data center" AND "microgrid" AND "DC"'),
]


def api_get(url):
    """Не сдаёмся на 429: ретрай с нарастающим backoff до 300с (лимит окна ~60-300с)."""
    attempt = 0
    while True:
        attempt += 1
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            wait = min(300, 30 * (2 ** min(attempt, 4)))  # 60/120/240/300/300...
            print(f"    retry {attempt}: {e} — жду {wait}s", flush=True)
            time.sleep(wait)


def parse_work(w, group):
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
        "group": group,
    }


def save(supp, queries):
    ws = sorted(supp.values(), key=lambda w: (w["year"] or 0))
    out = {
        "case": "012_dc_hvdc_cables", "signal": "s1a_publications_problem",
        "date": "2026-09-14",
        "method": "OpenAlex title_and_abstract.search от проблемы (7 групп) — полный корпус; "
                   "CU-DC/GIL/URBAN/DATACENTER дособрано (tmux/VPS-фоновый сбор)",
        "queries": [{"group": g, "label": l, "query": q} for g, l, q in queries],
        "n_works": len(ws), "works": ws,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)


def main():
    old = json.loads(OUT.read_text(encoding="utf-8"))
    supp = {w["id"]: w for w in old["works"]}
    seen = set(supp)
    print(f"seen: {len(seen)}", flush=True)
    AllQueries = old.get("queries", []) + [{"group": g, "label": l, "query": q} for g, l, q in QUERIES]
    for group, label, q in QUERIES:
        enc = urllib.parse.quote(q)
        cursor = "*"
        pages = 0
        zero = 0
        n_new = 0
        print(f"=== [{group}] {label} …", flush=True)
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
                    supp[wid] = parse_work(w, group)
                    add += 1
            n_new += add
            pages += 1
            cursor = d.get("meta", {}).get("next_cursor")
            zero = zero + 1 if add == 0 else 0
            print(f"    стр.{pages}: +{add} (по {label}: {n_new}; всего {len(supp)})", flush=True)
            time.sleep(1.5)
            if zero >= 3:
                print("    → перекрыто", flush=True)
                break
        print(f"  ИТОГО [{group}] {label}: +{n_new}", flush=True)
        save(supp, AllQueries)
    print(f"\nГОТОВО: {len(supp)} работ → {OUT}", flush=True)


if __name__ == "__main__":
    main()
