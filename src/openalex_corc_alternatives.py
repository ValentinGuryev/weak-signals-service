#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 009: корпус литературы по АЛЬТЕРНАТИВАМ CORC (для нормированного публ. сигнала).

Собирает по каждой технологии-конкуренту CORC полные записи OpenAlex (как corc_corpus):
  - TSTC (twisted stacked-tape cable) — Takayasu MIT
  - Roebel / RACC — KIT
  - CroCo — KIT
  - Slotted-core / TSSC — ENEA/ASIPP
  - VIPER — MIT/CFS
  - Rutherford-HTS (CCRC) — адаптация
  - SPC round-strand (twisted stack в меди) — EPFL
  - STAR wire — CERN/Sapienza
Каждая работа помечается тегом технологии (work['tech']). Дедуп по id (технологии пересекаются).

Выход: data/raw/openalex/corc_alternatives_corpus.json + агрегат counts по технологии/году
       (для нормированного сигнала: CORC vs альтернативы).
"""
from __future__ import annotations

import json
import socket
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

import socks  # SOCKS-прокси для обхода rate-limit OpenAlex

socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9051, rdns=True)
socket.socket = socks.socksocket

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "openalex" / "corc_alternatives_corpus.json"
AGG = ROOT / "data" / "raw" / "openalex" / "corc_alternatives_counts.json"
HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"

SELECT = ("id,doi,title,publication_year,cited_by_count,publication_date,"
          "abstract_inverted_index,authorships,referenced_works,type")

# Технология -> запросы (title_and_abstract)
TECHS = {
    "tstc": ['"twisted stacked-tape cable" OR "twisted stacked-tape conductor" OR "TSTC" AND (REBCO OR HTS)'],
    "roebel": ['"Roebel cable" OR "Roebel conductor" OR "Roebel assembled coated conductor" OR "RACC cable"'],
    "croco": ['"CroCo" AND (REBCO OR HTS OR superconductor OR conductor)'],
    "slotted_core": ['"slotted-core" OR "slotted core" AND (REBCO OR HTS OR superconducting) AND cable',
                     '"Twisted Stack Slotted" OR "TSSC cable"'],
    "viper": ['"VIPER cable" OR "VIPER conductor" OR ("VIPER" AND REBCO AND (cable OR conductor))'],
    "rutherford_hts": ['"Rutherford" AND (REBCO OR "coated conductor") AND (cable OR conductor)'],
    "spc_strand": ['"round strand" AND (REBCO OR HTS OR "coated conductor" OR "twisted stack")'],
    "star_wire": ['"STAR wire" OR "isotropic round wire" AND REBCO'],
}

MIN_YEAR, MAX_YEAR = 2000, 2026


def api_get(url: str) -> dict:
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception as e:
            print(f"    retry {attempt+1}: {e}")
            time.sleep(3 + attempt * 5)
    return {}


def fetch_tech(tech: str, queries: list, seen: dict, tech_tags: dict):
    for q in queries:
        enc = urllib.parse.quote(q)
        cursor = "*"
        pages = 0
        while cursor:
            url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
                   f",publication_year:{MIN_YEAR}-{MAX_YEAR}&per-page=200&select={SELECT}"
                   f"&cursor={cursor}&mailto={MAILTO}")
            d = api_get(url)
            results = d.get("results", [])
            if not results:
                break
            for w in results:
                wid = w.get("id")
                if not wid:
                    continue
                if wid not in seen:
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
                        "id": wid, "doi": w.get("doi"), "title": w.get("title"),
                        "year": w.get("publication_year"), "date": w.get("publication_date"),
                        "cited_by": w.get("cited_by_count"), "abstract": abstract,
                        "authors": authors, "references": w.get("referenced_works"),
                        "type": w.get("type"), "techs": [],
                    }
                # тег технологии (работа может относиться к нескольким)
                if tech not in seen[wid]["techs"]:
                    seen[wid]["techs"].append(tech)
                tech_tags[wid].add(tech)
            pages += 1
            cursor = d.get("meta", {}).get("next_cursor")
            print(f"  [{tech}] '{q[:45]}...' стр.{pages}, всего {len(seen)}")
            time.sleep(1.5)


def main():
    seen, tech_tags = {}, defaultdict(set)
    for tech, queries in TECHS.items():
        print(f"\n=== {tech} ===")
        fetch_tech(tech, queries, seen, tech_tags)

    works = sorted(seen.values(), key=lambda w: (w["year"] or 0))
    # counts по технологии и году (для нормированного сигнала)
    tech_year_counts = defaultdict(lambda: defaultdict(int))
    for w in works:
        for t in w["techs"]:
            tech_year_counts[t][w["year"] or 0] += 1

    corpus = {
        "case": "009_corc_cables", "signal": "s5_cable_alternatives_pubs", "date": "2026-09-09",
        "method": "OpenAlex title_and_abstract, SOCKS-прокси, полные записи, тег технологии (work.techs)",
        "techs_queries": {k: v for k, v in TECHS.items()},
        "n_works": len(works), "works": works,
        "counts_by_tech_year": {t: dict(sorted(y.items())) for t, y in tech_year_counts.items()},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False)
    with open(AGG, "w", encoding="utf-8") as f:
        json.dump(corpus["counts_by_tech_year"], f, ensure_ascii=False, indent=1)
    print(f"\nГотово: {len(works)} работ -> {OUT}")
    for t, y in tech_year_counts.items():
        tot = sum(y.values())
        print(f"  {t}: {tot} работ")


if __name__ == "__main__":
    main()
