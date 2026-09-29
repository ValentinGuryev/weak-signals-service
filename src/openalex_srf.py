#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011 SRF: сбор первичной литературы (S1a) — ниобиевые сверхпроводящие ВЧ-полости.

Стратегия «полного корпуса» (как openalex_ecoswing.py):
- Широкие запросы по терминам темы (title_and_abstract.search), полные записи
  (abstract, authors+affiliations, references, cited_by, concepts), cursor-пагинация per-page=200.
- Дедупликация по id OpenAlex.

Терминология (внутренний контракт §7.2 — терминология кейса):
  Имена: "SRF", "superconducting radio frequency", "superconducting RF",
         "niobium cavity" (ядро: Nb), "Nb3Sn cavity" (ветка), "superconducting cavity"
  Применение: accelerator / cavity / RF
Намеренно НЕ: "Josephson junction" и пр. (шум).

Выход: data/raw/openalex/srf_corpus.json
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "openalex" / "srf_corpus.json"
HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"

QUERIES = [
    # ядро: SRF
    '"superconducting radio frequency"\nOR\n"superconducting RF"\nOR\n"SRF cavity"\nOR\n"SRF cavities"',
    '"SRF accelerator"\nOR\n"superconducting accelerator cavity"\nOR\n"superconducting RF cavity"',
    # материал: ниобий
    '"niobium cavity"\nOR\n"niobium SRF"\nOR\n"niobium superconducting cavity"',
    '"Nb3Sn cavity"\nOR\n"Nb3Sn SRF"\nOR\n"niobium-tin cavity"',
    # широкое родовое (ускорительные полости)
    '"superconducting cavity" AND ("accelerator" OR "CERN" OR "Fermilab" OR "JLab" OR "KEK")',
]

SELECT = ("id,doi,title,display_name,publication_year,cited_by_count,publication_date,"
          "abstract_inverted_index,authorships,referenced_works,type,concepts")


def api_get(url: str) -> dict:
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            print(f"    retry {attempt + 1}: {e}")
            time.sleep(2 + attempt * 4)
    return {}


def fetch_all(query: str, seen: dict):
    """Cursor-пагинация по одному запросу; добавляет в seen (id -> запись)."""
    enc = urllib.parse.quote(query)
    cursor = "*"
    pages = 0
    while cursor:
        url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
               f"&per-page=200&select={SELECT}&cursor={cursor}&mailto={MAILTO}")
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
                }
        pages += 1
        cursor = d.get("meta", {}).get("next_cursor")
        print(f"    query: '{query[:60].replace(chr(10),' ')}...' страница {pages}, накоплено {len(seen)}")
        time.sleep(1)
    return seen


def main():
    seen = {}
    for q in QUERIES:
        print(f"\n=== Запрос: {q.replace(chr(10), ' OR ')}")
        fetch_all(q, seen)
        time.sleep(1)

    works = sorted(seen.values(), key=lambda w: (w["year"] or 0))
    corpus = {
        "case": "011_srf_cavities", "signal": "s1a_publications", "date": "2026-09-11",
        "method": "OpenAlex title_and_abstract.search, полные записи (abstract+authors+references),"
                  " cursor-пагинация, дедуп по id",
        "queries": QUERIES, "n_works": len(works), "works": works,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False)
    print(f"\nГотово: {len(works)} работ -> {OUT}")

    from collections import Counter
    c = Counter(w["year"] for w in works)
    print("По годам:", dict(sorted((k, v) for k, v in c.items() if k)))


if __name__ == "__main__":
    main()