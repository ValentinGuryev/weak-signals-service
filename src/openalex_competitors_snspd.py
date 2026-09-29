#!/usr/bin/env python3
"""Сбор корпусов конкурентов SNSPD (TES, InGaAs SPAD) для cross-citation (кейс 006).

Запросы OpenAlex title_and_abstract.search (как для snspd_corpus):
  TES:  "transition edge sensor" + photon/single photon
  SPAD: InGaAs/InP single photon (avalanche) detector

Выход: data/raw/openalex/tes_corpus.json, spad_corpus.json
Формат: список {id,title,year,cited_by} — как snspd_corpus.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from proxy_requests import enable_proxy_simple
    enable_proxy_simple("127.0.0.1", 1080)
except ImportError:
    print("proxy не доступен")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "data/raw/openalex"
HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"

# (имя файла, запрос, макс страниц)
QUERIES = [
    ("tes_corpus", '"transition edge sensor" photon detector', 15),
    ("spad_corpus", '"single photon avalanche diode" OR "InGaAs single-photon detector"', 20),
]

NON_RE = re.compile(r"\bGaN\b|\bsilicon photonics\b|perovskite|\bLED\b", re.I)


def fetch(q: str, pages: int) -> list:
    out, cursor = [], "*"
    while cursor and pages > 0:
        params = {"filter": f"title_and_abstract.search:{q}", "per-page": "100",
                  "cursor": cursor, "mailto": MAILTO,
                  "select": "id,title,publication_year,cited_by_count"}
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        ok = False
        for a in range(5):
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=40) as r:
                    d = json.loads(r.read().decode())
                ok = True
                break
            except Exception as e:
                time.sleep(15 * (a + 1))
        if not ok:
            break
        res = d.get("results", [])
        out.extend(res)
        cursor = d.get("meta", {}).get("next_cursor")
        pages -= 1
        time.sleep(1.5)
    return out


def is_rel(w: dict, kind: str) -> bool:
    t = f"{w.get('title') or ''}".lower()
    if kind == "tes":
        return "transition edge sensor" in t or "transition-edge sensor" in t
    if kind == "spad":
        return ("ingaas" in t or "inp" in t) and ("photon" in t or "avalanche" in t)
    return False


def main() -> None:
    for fname, query, pages in QUERIES:
        kind = fname.split("_")[0]
        print(f"=== {fname}: {query}")
        works = fetch(query, pages)
        print(f"  получено {len(works)}")
        # фильтр релевантности
        rel = [w for w in works if is_rel(w, kind)]
        # компактный формат
        recs = [{"id": w["id"], "title": w.get("title"), "year": w.get("publication_year"),
                 "cited_by": w.get("cited_by_count")} for w in rel]
        # дедуп по id
        seen, uniq = set(), []
        for r in recs:
            if r["id"] in seen:
                continue
            seen.add(r["id"]); uniq.append(r)
        out = OUT_DIR / fname
        out.write_text(json.dumps(uniq, ensure_ascii=False), encoding="utf-8")
        print(f"  → {len(uniq)} релевантных → {out}")


if __name__ == "__main__":
    main()
