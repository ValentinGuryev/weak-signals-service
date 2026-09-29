#!/usr/bin/env python3
"""Докачка абстрактов + referenced_works для корпуса JTWPA (кейс 007).

Оптимизация (как openalex_snspd_full.py): filter=openalex_id:A|B|C... до 50 id за запрос,
select=id,abstract_inverted_index,referenced_works → всё одним запросом на пачку.
241 работа → ~5 запросов.

Выход:
- data/raw/openalex/jtwpa_full.json  {work_id: {abstract, referenced_works}}
- пересчитывает data/raw/openalex/jtwpa_counts.json по дедуплицированному корпусу
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "jtwpa_corpus.json"
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "jtwpa_full.json"
AGG = PROJECT_ROOT / "data" / "raw" / "openalex" / "jtwpa_counts.json"

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
BATCH = 50


def fetch_batch(ids: list[str]) -> list[dict] | None:
    params = {"filter": "openalex_id:" + "|".join(ids),
              "select": "id,abstract_inverted_index,referenced_works",
              "per-page": str(BATCH), "mailto": MAILTO}
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode()).get("results", [])
        except Exception as e:
            wait = 12 * (attempt + 1)
            if "429" in str(e):
                print(f"    429 — пауза {wait}с (упрёмся — VPS-прокси)")
            time.sleep(wait)
    return None


def invert_abstract(inv: dict) -> str:
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def main() -> None:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    print(f"Корпус (дедуп): {len(corpus)} работ")

    result = {}
    if OUT.exists():
        result = json.loads(OUT.read_text(encoding="utf-8"))
        print(f"resume: уже есть {len(result)}")

    all_ids = [w["id"] for w in corpus]
    todo = [i for i in all_ids if i not in result]
    print(f"докачать: {len(todo)}")

    for start in range(0, len(todo), BATCH):
        batch = todo[start:start + BATCH]
        short = [i.replace("https://openalex.org/", "") for i in batch]
        res = fetch_batch(short)
        if not res:
            print(f"  пачка {start//BATCH}: НЕТ ОТВЕТА — стоп")
            break
        for w in res:
            wid = w["id"]
            result[wid] = {
                "abstract": invert_abstract(w.get("abstract_inverted_index") or {}),
                "referenced_works": w.get("referenced_works", []),
            }
        OUT.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        print(f"  пачка {start//BATCH+1}/{len(todo)//BATCH+1}: +{len(res)} (всего {len(result)})")
        time.sleep(1.2)

    # --- пересчёт counts по годам на дедуплицированном корпусе ------------------
    agg = json.loads(AGG.read_text(encoding="utf-8")) if AGG.exists() else {}
    by_year = defaultdict(lambda: defaultdict(int))
    for w in corpus:
        y = w["year"] or 0
        if 2000 <= y <= 2026:
            by_year[w["class"]][y] += 1
    agg["total_A"] = sum(1 for w in corpus if w["class"] == "A")
    agg["total_B"] = sum(1 for w in corpus if w["class"] == "B")
    agg["counts_A"] = {y: by_year["A"][y] for y in sorted(by_year["A"])}
    agg["counts_B"] = {y: by_year["B"][y] for y in sorted(by_year["B"])}
    AGG.write_text(json.dumps(agg, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\ncounts пересчитаны (дедуп): A={agg['total_A']}, B={agg['total_B']}")

    with_abs = sum(1 for v in result.values() if v["abstract"])
    with_refs = sum(1 for v in result.values() if v["referenced_works"])
    print(f"с абстрактом: {with_abs}, с references: {with_refs}")


if __name__ == "__main__":
    main()
