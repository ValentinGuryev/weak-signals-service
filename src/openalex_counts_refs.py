#!/usr/bin/env python3
"""Докачка counts_by_year + referenced_works из OpenAlex для графа знания IBAD.

Что докачиваем для КАЖДОЙ работы корпуса (426):
1. counts_by_year — цитаты по годам получения (для «возникновения кластера цитирований» S3)
2. referenced_works — список работ, на которые ссылается данная работа (для графа знания)

Запускать, когда OpenAlex снимет 429 (rate limit после больших прогонов).

Выход:
- data/raw/openalex/ibad_counts_by_year.json   {work_id: {year: count}}
- data/raw/openalex/ibad_references.json       {work_id: [referenced_work_ids]}
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Опциональный SOCKS5-прокси (VPS) для обхода rate-limit OpenAlex.
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 1080
try:
    from proxy_requests import enable_proxy_simple
    enable_proxy_simple(PROXY_HOST, PROXY_PORT)
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "ibad_abstracts_corpus.json"
OUT_CITES = PROJECT_ROOT / "data" / "raw" / "openalex" / "ibad_counts_by_year.json"
OUT_REFS = PROJECT_ROOT / "data" / "raw" / "openalex" / "ibad_references.json"

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"


def fetch_work(work_id: str, retries: int = 4) -> dict | None:
    """Одна работа с counts_by_year и referenced_works."""
    wid = work_id.replace("https://openalex.org/", "")
    url = (f"https://api.openalex.org/works/{wid}?select=id,counts_by_year,referenced_works"
           f"&mailto={MAILTO}")
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if "429" in str(e):
                # rate limit — ждём дольше
                time.sleep(20 * (a + 1))
            else:
                time.sleep(5)
    return None


def main() -> None:
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    works = data["works"]
    print(f"Корпус: {len(works)} работ")

    # resume из существующих файлов
    cites = {}
    if OUT_CITES.exists():
        cites = json.loads(OUT_CITES.read_text(encoding="utf-8"))
    refs = {}
    if OUT_REFS.exists():
        refs = json.loads(OUT_REFS.read_text(encoding="utf-8"))

    todo = [w for w in works if w["id"] not in cites]
    print(f"Докачать: {len(todo)} работ")

    for i, w in enumerate(todo):
        wid = w["id"]
        d = fetch_work(wid)
        if d:
            cites[wid] = {str(y["year"]): y["cited_by_count"]
                          for y in (d.get("counts_by_year") or [])}
            refs[wid] = d.get("referenced_works") or []
        # накопительное сохранение каждые 25
        if i % 25 == 0:
            OUT_CITES.write_text(json.dumps(cites, ensure_ascii=False), encoding="utf-8")
            OUT_REFS.write_text(json.dumps(refs, ensure_ascii=False), encoding="utf-8")
            print(f"  ...{i}/{len(todo)} (сохранено {len(cites)})", flush=True)
        time.sleep(1.5)  # вежливость к OpenAlex

    OUT_CITES.write_text(json.dumps(cites, ensure_ascii=False), encoding="utf-8")
    OUT_REFS.write_text(json.dumps(refs, ensure_ascii=False), encoding="utf-8")
    print(f"\nГотово: {len(cites)} работ с counts_by_year, {len(refs)} с references")
    print(f"Сохранено: {OUT_CITES}, {OUT_REFS}")


if __name__ == "__main__":
    main()
