#!/usr/bin/env python3
"""Докачка counts_by_year для ядра S5 (теплопроводная электроизоляция).

Ядро: 32 работы из hts_insulation_rct_corpus.json с topic in (insulation_thermal,
insulation_materials) и cited_by >= 10. Исключены rct_contact/rct_control/smart.

Метод: OpenAlex /works?filter=ids.openalex:<id1>|<id2>|... (OR до 25-50 за запрос)
+ select counts_by_year. Прямой доступ (SOCKS-прокси недоступен).
Выход: data/raw/openalex/s5_insulation_core_counts.json
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "hts_insulation_rct_corpus.json"
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "s5_insulation_core_counts.json"

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"

CORE_TOPICS = {"insulation_thermal", "insulation_materials"}
MIN_CIT = 10


def fetch_batch(ids: list[str]) -> list[dict]:
    filter_str = "ids.openalex:" + "|".join(ids)
    params = {
        "filter": filter_str, "per-page": "100", "mailto": MAILTO,
        "select": "id,title,publication_year,cited_by_count,counts_by_year",
    }
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode()).get("results", [])
        except Exception as e:
            print(f"  [err] attempt {attempt}: {str(e)[:70]}")
            time.sleep(15 * (attempt + 1))
    return []


def main():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    core = [w for w in corpus
            if w.get("topic") in CORE_TOPICS and (w.get("cited_by") or 0) >= MIN_CIT]
    print(f"Ядро S5: {len(core)} работ (теплопроводная электроизоляция, cit>={MIN_CIT})")

    ids = [w["id"] for w in core]
    results = {}
    for i in range(0, len(ids), 25):
        batch = ids[i:i + 25]
        print(f"  батч {i // 25 + 1}: {len(batch)} ID")
        for r in fetch_batch(batch):
            results[r["id"]] = r
        time.sleep(1.5)

    # сохранить counts_by_year для найденных
    out = []
    missing = 0
    for w in core:
        r = results.get(w["id"])
        if not r:
            missing += 1
            continue
        out.append({
            "id": w["id"], "title": w.get("title"),
            "year": w.get("year") or w.get("publication_year"),
            "cited_by": w.get("cited_by"),
            "counts_by_year": r.get("counts_by_year"),
        })
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"Сохранено: {len(out)} работ (не найдено: {missing}) → {OUT}")


if __name__ == "__main__":
    main()
