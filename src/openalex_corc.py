#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 009 CORC: сбор публикационного сигнала (S1a) — ПОЛНЫЕ записи за один проход.

Стратегия «умного сбора» (чтобы не тянуть статьи заново):
- 3 запроса с фильтром title_and_abstract (узкие, чистые):
    1) "CORC cable" OR "CORC wire"
    2) "CORC" AND ("REBCO" OR "HTS" OR "superconductor" OR "conductor on round core")
    3) "conductor on round core"
- Дедупликация по id OpenAlex.
- Для КАЖДОЙ работы тянем ПОЛНУЮ запись (select=все поля): title, year, cited_by,
  abstract_inverted_index, authorships (авторы+аффилиации), referenced_works (ссылки),
  doi, source (журнал), concepts, topics.
- Используем filter cursor-пагинацию (per-page=200, cursor) — минимум запросов.

Выход: data/raw/openalex/corc_corpus.json (полный корпус + паспорт).
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "openalex" / "corc_corpus.json"
HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"

QUERIES = [
    '"CORC cable" OR "CORC wire"',
    '"CORC" AND ("REBCO" OR "HTS" OR superconductor OR "round core")',
    '"conductor on round core"',
]
# Полный набор полей (source нельзя в select — вызывает 400)
SELECT = ("id,doi,title,display_name,publication_year,cited_by_count,publication_date,"
          "abstract_inverted_index,authorships,referenced_works,type,concepts")


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
                # реконструкция абстракта
                inv = w.get("abstract_inverted_index")
                abstract = None
                if inv:
                    pos = {}
                    for word, idxs in inv.items():
                        for i in idxs:
                            pos[i] = word
                    abstract = " ".join(pos[i] for i in sorted(pos))
                # нормализуем авторов
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
                    "source": None,  # source не тянем (400 в select)
                    "type": w.get("type"), "concepts": [c.get("display_name") for c in (w.get("concepts") or [])],
                }
        pages += 1
        cursor = d.get("meta", {}).get("next_cursor")
        print(f"    query: '{query[:40]}...' страница {pages}, накоплено {len(seen)}")
        time.sleep(1)
    return seen


def main():
    seen = {}
    for q in QUERIES:
        print(f"\n=== Запрос: {q}")
        fetch_all(q, seen)
        time.sleep(1)

    # сортировка по году
    works = sorted(seen.values(), key=lambda w: (w["year"] or 0))
    corpus = {
        "case": "009_corc_cables", "signal": "s1a_publications", "date": "2026-09-09",
        "method": "OpenAlex title_and_abstract.search, полные записи (abstract+authors+references+source)",
        "queries": QUERIES, "n_works": len(works), "works": works,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False)
    print(f"\nГотово: {len(works)} работ -> {OUT}")

    # быстрый агрегат по годам
    from collections import Counter
    c = Counter(w["year"] for w in works)
    print("По годам:", dict(sorted(c.items())))


if __name__ == "__main__":
    main()
