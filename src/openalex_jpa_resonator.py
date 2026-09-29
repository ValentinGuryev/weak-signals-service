#!/usr/bin/env python3
"""Сбор JPA-резонаторного корпуса + references (для S3-cross кейса 007).

JPA резонаторный — главный конкурент-предшественник JTWPA (узкополосный).
Запрос: title_and_abstract.search "Josephson parametric amplifier" МИНУС traveling-wave
(те, что с traveling — уже в JTWPA-корпусе).
Выход: data/raw/openalex/jpa_resonator_corpus.json (полные записи)
        data/raw/openalex/jpa_resonator_full.json (references)
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "data/raw/openalex/jpa_resonator_corpus.json"
OUT_REF = PROJECT_ROOT / "data/raw/openalex/jpa_resonator_full.json"

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
SEL = "id,title,publication_year,cited_by_count,abstract_inverted_index,authorships,primary_location"
BATCH = 50

# Прокси через SOCKS-прокси (порт 9051): прямой IP исчерпал дневной бюджет
import socks as _socks
import socket as _socket
_socks.set_default_proxy(_socks.SOCKS5, "127.0.0.1", 9051)
_socket.socket = _socks.socksocket


def abstracts(w: dict) -> str:
    inv = w.get("abstract_inverted_index") or {}
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def fetch(fs: str, max_pages: int = 8) -> list[dict]:
    results, cursor, pages = [], "*", 0
    while cursor and pages < max_pages:
        params = {"filter": fs, "per-page": "100", "cursor": cursor, "mailto": MAILTO, "select": SEL}
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        ok = False
        for att in range(6):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=45) as r:
                    d = json.load(r)
                results.extend(d.get("results", []))
                cursor = d.get("meta", {}).get("next_cursor")
                pages += 1
                ok = True
                break
            except Exception as e:
                time.sleep(40 if "429" in str(e) else 12)
        if not ok:
            break
        time.sleep(1.2)
    return results


def simplify(w: dict) -> dict:
    authors = []
    for a in (w.get("authorships") or []):
        au = a.get("author") or {}
        inst = (a.get("institutions") or [{}])[0]
        authors.append({"name": au.get("display_name"),
                        "inst": (inst.get("display_name") if inst else None),
                        "country": (inst.get("country_code") if inst else None)})
    return {"id": w["id"], "title": w.get("title"), "year": w.get("publication_year"),
            "cited_by": w.get("cited_by_count"), "authors": authors[:10],
            "source": ((w.get("primary_location") or {}).get("source") or {}).get("display_name")}


def main():
    print("=== Сбор JPA-резонаторного корпуса ===")
    raw = fetch('title_and_abstract.search:"Josephson parametric amplifier"', max_pages=8)
    print(f"Сырых: {len(raw)}")
    # отбор: резонаторный JPA (БЕЗ traveling wave — те в JTWPA-корпусе)
    corpus = {}
    for w in raw:
        t = ((w.get("title") or "") + " " + abstracts(w)).lower()
        if "traveling" in t or "travelling" in t:
            continue  # это JTWPA, уже есть
        y = w.get("publication_year") or 0
        if not (2000 <= y <= 2026):
            continue
        corpus[w["id"]] = simplify(w)
    print(f"JPA-резонаторных: {len(corpus)}")
    OUT.write_text(json.dumps(list(corpus.values()), ensure_ascii=False, indent=1), encoding="utf-8")

    # докачка references
    print("=== Докачка references ===")
    full = {}
    ids = [w["id"].replace("https://openalex.org/", "") for w in corpus.values()]
    for i in range(0, len(ids), BATCH):
        batch = ids[i:i + BATCH]
        params = {"filter": "openalex_id:" + "|".join(batch),
                  "select": "id,referenced_works", "per-page": str(BATCH), "mailto": MAILTO}
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        for att in range(6):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=45) as r:
                    d = json.load(r)
                for w in d.get("results", []):
                    full[w["id"]] = {"referenced_works": w.get("referenced_works", []), "abstract": ""}
                break
            except Exception as e:
                time.sleep(40 if "429" in str(e) else 12)
        time.sleep(1.2)
        print(f"  пачка {i//BATCH+1}/{(len(ids)-1)//BATCH+1}: {len(full)}")
    OUT_REF.write_text(json.dumps(full, ensure_ascii=False), encoding="utf-8")
    print(f"JPA references: {len(full)} → {OUT_REF}")


if __name__ == "__main__":
    main()
