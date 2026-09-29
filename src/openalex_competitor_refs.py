#!/usr/bin/env python3
"""Докачка references для корпусов конкурентов SNSPD (TES, SPAD) — cross-citation.

Пакетно через OpenAlex (filter=openalex_id:A|B|..., до 50 за запрос),
select=referenced_works. 159+180 работ → ~7 запросов.

Выход: data/raw/openalex/{tes,spad}_refs.json  {work_id: [referenced_works]}
"""
from __future__ import annotations

import json
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
HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
BATCH = 50

TARGETS = ["tes", "spad"]


def fetch_batch(ids: list[str]) -> list[dict] | None:
    params = {"filter": "openalex_id:" + "|".join(ids),
              "select": "id,referenced_works", "per-page": str(BATCH), "mailto": MAILTO}
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode()).get("results", [])
        except Exception as e:
            wait = 20 * (attempt + 1)
            print(f"  429/err — пауза {wait}с")
            time.sleep(wait)
    return None


def main() -> None:
    for name in TARGETS:
        corpus_f = PROJECT_ROOT / "data" / "raw" / "openalex" / f"{name}_corpus.json"
        if not corpus_f.exists():
            print(f"{name}: нет корпуса")
            continue
        corpus = json.loads(corpus_f.read_text(encoding="utf-8"))
        ids = [w["id"] for w in corpus]
        print(f"=== {name}: {len(ids)} работ")
        result = {}
        for start in range(0, len(ids), BATCH):
            batch = ids[start:start + BATCH]
            short = [i.replace("https://openalex.org/", "") for i in batch]
            res = fetch_batch(short)
            if not res:
                print(f"  пачка {start//BATCH}: НЕТ — стоп")
                break
            for w in res:
                result[w["id"]] = w.get("referenced_works", [])
            if (start // BATCH) % 3 == 0:
                print(f"  пачка {start//BATCH+1}: +{len(res)} (всего {len(result)})")
            time.sleep(1.2)
        out = PROJECT_ROOT / "data" / "raw" / "openalex" / f"{name}_refs.json"
        out.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        print(f"  → {len(result)} работ с refs → {out}")


if __name__ == "__main__":
    main()
