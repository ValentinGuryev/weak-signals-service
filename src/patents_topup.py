"""Дособор патентного слоя: 4 пропущенных тренда + новые из РНФ-находок.

Google Patents XHR без ключа. Rate-limit жёсткий (~8 запросов) → большие паузы.
Обновляет data/raw/patents/patents_results.json, добавляя недостающие label.

Новые тренды из РНФ-находок (2026-08-17):
  - flux pinning REBCO   (пиннинг в ВТСП-лентах 2G)
  - fluxonics            (флаксоника: логика на квантах потока)
  - force-free coil      (квазибессиловые обмотки ВТСП)
"""
from __future__ import annotations

import argparse
import json
import logging
import time
import urllib.parse
import urllib.request
from pathlib import Path

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

# Пропущенные из-за rate-limit + новые из РНФ-находок
MISSING_KEYWORDS = {
    "spintronics": "spintronics magnon",
    "nv center": "NV center diamond quantum",
    "chiral phonon": "chiral phonon",
    "superconducting magnet": "superconducting magnet",
    "flux pinning REBCO": "flux pinning REBCO coated conductor",
    "fluxonics": "fluxonics superconducting logic",
    "force-free coil": "force-free superconducting coil high field",
}

PAUSE = 12  # сек между запросами (rate-limit ~8)


def fetch_patents(query: str, retries: int = 4) -> dict | None:
    url = "https://patents.google.com/xhr/query?url=" + urllib.parse.quote("q=" + query, safe="")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "application/json",
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            return {
                "total": data.get("results", {}).get("total_num_results", 0),
                "num_pages": data.get("results", {}).get("total_num_pages", 0),
            }
        except Exception as e:
            logger.warning("retry %d для '%s': %s", attempt + 1, query, str(e)[:100])
            time.sleep(5 * (attempt + 1))
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Дособор патентного слоя")
    ap.add_argument("--out", default="data/raw/patents/patents_results.json")
    ap.add_argument("--pause", type=int, default=PAUSE)
    args = ap.parse_args()

    out_path = PROJECT_ROOT / args.out
    # загрузить текущую базу
    if out_path.exists():
        db = json.loads(out_path.read_text(encoding="utf-8"))
        existing = {t["label"] for t in db.get("trends", [])}
    else:
        db = {"method": "google_patents_xhr", "trends": []}
        existing = set()

    # дособираем и новые, и те, что в базе со значением None (rate-limit в прошлый раз)
    to_fetch = {
        k: v for k, v in MISSING_KEYWORDS.items()
        if k not in existing or next((t.get("patents") is None for t in db["trends"] if t["label"] == k), False)
    }
    logger.info("К дособору: %d трендов (в базе %d)", len(to_fetch), len(existing))

    for label, query in to_fetch.items():
        res = fetch_patents(query)
        if res is None:
            logger.error("Не удалось для '%s'", label)
            entry = {"label": label, "query": query, "patents": None, "error": True}
        else:
            logger.info("  %-28s патенты: %d", label, res["total"])
            entry = {"label": label, "query": query, "patents": res["total"]}
        # заменить запись по label (не накапливать дубли)
        db["trends"] = [t for t in db["trends"] if t["label"] != label]
        db["trends"].append(entry)
        db["trends"] = sorted(db["trends"], key=lambda x: (x.get("patents") is None, -(x.get("patents") or 0)))
        out_path.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(args.pause)  # большая пауза против rate-limit

    # финальный note
    missing = [t["label"] for t in db["trends"] if t.get("patents") is None]
    db["note"] = f"Дособрано 2026-08-17 ({len(to_fetch)} трендов). Ещё не собрано: {missing if missing else '—'}"
    out_path.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Итог: %d трендов в базе → %s", len(db["trends"]), out_path)


if __name__ == "__main__":
    main()
