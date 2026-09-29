"""Скачать 100 патентов с точной фразой "superconducting diode".

Google Patents XHR: q="superconducting diode" (в кавычках = точная фраза).
num=25, page=0..3. Извлекаем: номер, название, реферат, assignee, даты.
Rate-limit жёсткий → большие паузы + ретраи.

Результат: data/raw/patents/superconducting_diode_patents.json
"""
from __future__ import annotations

import json
import logging
import time
import urllib.parse
import urllib.request
from pathlib import Path

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

QUERY = '"superconducting diode"'
NUM = 25  # макс на страницу
TOTAL = 100


def fetch_page(query: str, num: int, page: int, retries: int = 5) -> dict | None:
    url = "https://patents.google.com/xhr/query?url=" + urllib.parse.quote(f"q={query}&num={num}&page={page}", safe="")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://patents.google.com/",
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001
            wait = 30 * (attempt + 1)
            logger.warning("стр %d попытка %d: %s → ждём %ds", page, attempt + 1, str(e)[:80], wait)
            time.sleep(wait)
    return None


def extract_patents(data: dict | None) -> list[dict]:
    if not data:
        return []
    out = []
    for cluster in data.get("results", {}).get("cluster", []):
        for r in cluster.get("result", []):
            p = r.get("patent", {})
            if not p:
                continue
            out.append({
                "publication_number": p.get("publication_number"),
                "title": p.get("title"),
                "abstract": (p.get("abstract") or "")[:2000],
                "assignee": p.get("assignee"),
                "priority_date": p.get("priority_date"),
                "grant_date": p.get("grant_date"),
                "filing_date": p.get("filing_date"),
                "inventor": p.get("inventor"),
                "url": f"https://patents.google.com/patent/{p.get('publication_number')}",
            })
    return out


def main() -> None:
    out_path = PROJECT_ROOT / "data" / "raw" / "patents" / "superconducting_diode_patents.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    all_patents: list[dict] = []
    pages = (TOTAL + NUM - 1) // NUM
    for page in range(pages):
        data = fetch_page(QUERY, NUM, page)
        pats = extract_patents(data)
        logger.info("Страница %d → %d патентов (всего %d)", page, len(pats), len(all_patents))
        all_patents.extend(pats)
        if len(pats) < NUM:
            break
        time.sleep(20)  # большая пауза между страницами

    # дедупликация
    seen = set()
    uniq = []
    for p in all_patents:
        k = p.get("publication_number")
        if k in seen:
            continue
        seen.add(k)
        uniq.append(p)

    out_path.write_text(json.dumps({
        "query": QUERY,
        "total_results": TOTAL,
        "downloaded": len(uniq),
        "patents": uniq,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Сохранено: %s (%d патентов)", out_path, len(uniq))


if __name__ == "__main__":
    main()
