#!/usr/bin/env python3
"""Сбор корпусов PLD и MOCVD (методы роста REBCO) + references.

Цель: проверить изоляцию конкурентов честно:
  RCE (reactive co-evaporation) vs PLD (pulsed laser deposition)
  TLAG (transient liquid assisted growth) vs MOCVD (metal-organic CVD)

Методика (как openalex_growth_methods.py):
- title_and_abstract.search:"<метод>" + SC-фильтр (целые слова)
- PLD: "pulsed laser deposition" ∪ "PLD" (аккуратно)
- MOCVD: "metal organic chemical vapor deposition" ∪ "MOCVD"

Выход:
- data/raw/openalex/pld_mocvd_corpus.json — работы {id,title,year,method}
- data/raw/openalex/pld_mocvd_references.json — id -> [referenced_works]
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "pld_mocvd_corpus.json"
REF_OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "pld_mocvd_references.json"

MAILTO = "research@example.com"
HEADERS = {"User-Agent": f"research (mailto:{MAILTO})"}

METHODS = {
    # Честный контекст: методы производства ЛЕНТ (как RCE), не все PLD-плёнки вообще
    "PLD": ['"pulsed laser deposition" AND ("coated conductor" OR "coated conductors" OR tape)'],
    "MOCVD": ['("metal organic chemical vapor deposition" OR "metal-organic chemical vapor deposition" OR MOCVD) AND (REBCO OR GdBCO OR YBCO OR "coated conductor" OR "coated conductors")'],
}

SC_RE = re.compile(
    r"\bREBCO\b|\bYBCO\b|\bGdBCO\b|\bSmBCO\b|\bEuBCO\b|\bNdBCO\b|coated conductor|coated conductors|"
    r"superconducting|superconductor|\bHTS\b|high.temperature superconducting|"
    r"Ba2Cu3O7|Ba₂Cu₃O₇|yttrium barium|rare.earth|REBa2Cu3O7|cuprate|\bCC\b",
    re.I,
)
NON_SC_RE = re.compile(
    r"\bGaN\b|\bsilicon\b|\bSiC\b|perovskite solar|\bLiNi\b|\bbattery\b|\belectrode\b|"
    r"thermoelectric|\bsemiconductor\b|\bLED\b|laser diode|\bGaAs\b|\bInP\b|"
    r"metal halide|nanowire transistor|ferroelectr|solar cell|thin.film transistor|"
    r"ZnO|\bIGZO\b|memristor|RRAM|ferroelectric RAM|piezoelectric actuator",
    re.I,
)


def abstract_text(work: dict) -> str:
    inv = work.get("abstract_inverted_index") or {}
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def is_sc(work: dict) -> bool:
    text = f"{work.get('title') or ''} {abstract_text(work)}"
    return not NON_SC_RE.search(text) and bool(SC_RE.search(text))


def fetch(filter_str: str, per_page: int = 100, max_pages: int = 15) -> list[dict]:
    results, cursor, pages = [], "*", 0
    while cursor and pages < max_pages:
        params = {
            "filter": filter_str, "per-page": str(per_page), "cursor": cursor, "mailto": MAILTO,
            "select": "id,title,publication_year,abstract_inverted_index",
        }
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            print(f"  [err] p{pages}: {e}")
            time.sleep(20)
            continue
        results.extend(data.get("results", []))
        cursor = data.get("meta", {}).get("next_cursor")
        pages += 1
        time.sleep(0.6)
    return results


def fetch_refs(ids: list[str], batch: int = 40) -> dict:
    """Получить referenced_works для пачки id (через filter=openalex_id|...)."""
    out = {}
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        filt = "|".join(chunk)
        url = (f"https://api.openalex.org/works?filter=ids.openalex:{filt}"
               f"&per-page=50&select=id,referenced_works&mailto={MAILTO}")
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.loads(r.read().decode())
            for w in data.get("results", []):
                wid = w["id"].split("/")[-1]
                out[wid] = [x.split("/")[-1] for x in (w.get("referenced_works") or [])]
        except Exception as e:
            print(f"  [err refs] {i//batch+1}: {e}")
            time.sleep(20)
        time.sleep(0.5)
    return out


def main():
    corpus = {}
    print("=== Сбор корпусов PLD / MOCVD (title_and_abstract + SC-фильтр) ===")
    for label, queries in METHODS.items():
        for q in queries:
            works = fetch(f"title_and_abstract.search:{q}")
            kept = 0
            for w in works:
                if is_sc(w) and w["id"] not in corpus:
                    corpus[w["id"]] = {
                        "id": w["id"], "title": w.get("title"),
                        "year": w.get("publication_year"), "method": label,
                    }
                    kept += 1
            print(f"  → {label} [{q}]: {len(works)} получено, +{kept} SC")
            time.sleep(1)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(list(corpus.values()), f, ensure_ascii=False, indent=1)
    print(f"\nКорпус: {len(corpus)} работ → {OUT}")
    from collections import Counter
    print("по методам:", dict(Counter(w["method"] for w in corpus.values())))

    # references
    ids = list(corpus.keys())
    print(f"\n=== Сбор references для {len(ids)} работ ===")
    refs = fetch_refs(ids)
    with open(REF_OUT, "w", encoding="utf-8") as f:
        json.dump(refs, f, ensure_ascii=False, indent=1)
    print(f"References: {len(refs)} работ → {REF_OUT}")


if __name__ == "__main__":
    main()
