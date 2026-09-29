#!/usr/bin/env python3
"""Докачка для SNSPD (кейс 006): abstracts + referenced_works пакетно через OpenAlex.

Оптимизация (проверено 2026-09-03): filter=openalex_id:A|B|C... до 50 id за запрос,
select=id,abstract_inverted_index,referenced_works → ВСЁ одним запросом на пачку.
1831 работа → ~37 запросов (не 1831).

Выход:
- data/raw/openalex/snspd_full.json     {work_id: {abstract, referenced_works}} — для S2/S3
- (S2 использует abstract, S3 строит граф из referenced_works)
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Прокси для обхода rate-limit (как openalex_counts_refs — enable_proxy_simple, рабочая)
try:
    from proxy_requests import enable_proxy_simple
    enable_proxy_simple("127.0.0.1", 1080)
except ImportError:
    print("proxy_requests не доступен — работаю напрямую (может быть 429)")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "snspd_corpus.json"
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "snspd_full.json"

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
BATCH = 50


def fetch_batch(ids: list[str]) -> list[dict] | None:
    """Пакетный запрос OpenAlex по списку id."""
    params = {
        "filter": "openalex_id:" + "|".join(ids),
        "select": "id,abstract_inverted_index,referenced_works",
        "per-page": str(BATCH),
        "mailto": MAILTO,
    }
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode()).get("results", [])
        except Exception as e:
            wait = 15 * (attempt + 1)
            if "429" in str(e):
                print(f"  429 — пауза {wait}с")
            time.sleep(wait)
    return None


def invert_abstract(inv: dict) -> str:
    """abstract_inverted_index → текст."""
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def main() -> None:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    works = corpus if isinstance(corpus, list) else corpus.get("works", corpus)
    print(f"Корпус: {len(works)} работ")

    # resume
    result = {}
    if OUT.exists():
        result = json.loads(OUT.read_text(encoding="utf-8"))
        print(f"resume: уже есть {len(result)}")

    all_ids = [w["id"] for w in works]
    todo = [i for i in all_ids if i not in result]
    print(f"докачать: {len(todo)}")

    for start in range(0, len(todo), BATCH):
        batch = todo[start:start + BATCH]
        short = [i.replace("https://openalex.org/", "") for i in batch]
        if start == 0:
            print("  прогрев прокси...")
            time.sleep(5)  # дать прокси подняться после enable_proxy
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
        if (start // BATCH) % 5 == 0:
            OUT.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
            print(f"  пачка {start//BATCH+1}/{len(todo)//BATCH+1}: +{len(res)} (всего {len(result)})")
        time.sleep(1.2)  # вежливо

    OUT.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    print(f"\nСохранено: {OUT} ({len(result)} работ)")
    # статистика
    with_abs = sum(1 for v in result.values() if v["abstract"])
    with_refs = sum(1 for v in result.values() if v["referenced_works"])
    print(f"с абстрактом: {with_abs}, с references: {with_refs}")


if __name__ == "__main__":
    main()
