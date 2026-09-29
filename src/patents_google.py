"""Google Patents (XHR) — патентный слой для трендов.

Без ключа и аккаунта: patents.google.com/xhr/query возвращает JSON.
Используется для «инвестиционного сигнала»: число патентов по ключевым словам
тренда + динамика по годам (признак коммерциализации).

Вход: ключевые слова трендов (вручную или из конфига).
Выход: data/raw/patents/patents_results.json
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

# Ключевые слова трендов (калибровочные + подтверждённые)
TREND_KEYWORDS = {
    "superconducting diode": "superconducting diode",
    "fluxonium": "fluxonium qubit",
    "no-insulation coil": "no-insulation superconducting coil",
    "mgb2": "MgB2 superconducting wire",
    "graphene": "graphene",
    "machine learning materials": "machine learning materials discovery",
    "quantum error correction": "quantum error correction",
    "neuromorphic": "neuromorphic computing memristor",
    "spintronics": "spintronics magnon",
    "nv center": "NV center diamond quantum",
    "chiral phonon": "chiral phonon",
    "superconducting magnet": "superconducting magnet",
}


def fetch_patents(query: str, retries: int = 3) -> dict | None:
    """Запрос к Google Patents XHR. Возвращает результат или None."""
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
            logger.warning("Google Patents retry %d для '%s': %s", attempt + 1, query, e)
            time.sleep(2 * (attempt + 1))
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Google Patents: патентный слой")
    ap.add_argument("--out", default="data/raw/patents/patents_results.json")
    ap.add_argument("--keywords", default="", help="JSON: {label: query} (переопределяет defaults)")
    args = ap.parse_args()

    kw = TREND_KEYWORDS
    if args.keywords:
        kw = json.loads(args.keywords)

    results = []
    for label, query in kw.items():
        res = fetch_patents(query)
        if res is None:
            logger.error("Не удалось получить патенты для '%s'", label)
            results.append({"label": label, "query": query, "patents": None, "error": True})
            continue
        results.append({"label": label, "query": query, "patents": res["total"]})
        logger.info("  %-28s патенты: %d", label, res["total"])
        time.sleep(1.0)  # вежливый интервал

    out = {
        "method": "google_patents_xhr",
        "description": "Число патентов по ключевым словам трендов (Google Patents, без ключа)",
        "source": "https://patents.google.com/xhr/query",
        "trends": results,
    }
    out_path = PROJECT_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Записано: %s", out_path)


if __name__ == "__main__":
    main()
