"""Прикладной слой: динамика прикладных статей по трендам (OpenAlex).

Закрывает дыру arXiv: прикладные журналы (IEEE TAS, SuST и др.) показывают
индустриальный/прикладной интерес к теме, которого нет на arXiv.

Для каждого ключевого слова тренда:
- число прикладных статей (в выбранных журналах) по годам;
- рост за последние 2 года vs предыдущие 2 (прикладной сигнал).

Источник: OpenAlex (api.openalex.org) — доступен, без ключа.
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

# Прикладные журналы сверхпроводимости (OpenAlex source id, получены ранее)
APP_JOURNALS = {
    "IEEE TAS": "S119074828",
    "SuST": "S93909106",
}

# Ключевые слова трендов (как в патентном слое)
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


def count_works_year(query: str, source_id: str, year: int) -> int:
    """Число статей в журнале source_id по query в год year (OpenAlex)."""
    url = ("https://api.openalex.org/works?filter=primary_location.source.id:"
           f"{source_id},from_publication_date:{year}-01-01,to_publication_date:{year}-12-31"
           f"&search={urllib.parse.quote(query)}&per-page=1&mailto=research@example.com")
    req = urllib.request.Request(url, headers={"User-Agent": "research-test"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode())
    return d.get("meta", {}).get("count", 0)


def load_cache(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cache(path: Path, cache: dict) -> None:
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Прикладной слой: OpenAlex прикладные журналы")
    ap.add_argument("--out", default="data/raw/openalex/applied_layer_results.json")
    ap.add_argument("--years", default="2018,2020,2022,2023,2024,2025", help="годы для динамики")
    args = ap.parse_args()

    years = [int(y) for y in args.years.split(",")]

    cache_path = PROJECT_ROOT / "data/cache/openalex_applied_cache.json"
    cache = load_cache(cache_path)

    results = []
    for label, query in TREND_KEYWORDS.items():
        entry = {"label": label, "query": query, "by_journal": {}}
        for jname, jid in APP_JOURNALS.items():
            yearly = {}
            for y in years:
                key = f"{query}|{jid}|{y}"
                if key in cache and cache[key] is not None:
                    yearly[y] = cache[key]
                    continue
                try:
                    yearly[y] = count_works_year(query, jid, y)
                    cache[key] = yearly[y]
                    save_cache(cache_path, cache)
                    time.sleep(1.0)  # вежливая пауза против 429
                except Exception as e:
                    logger.warning("OpenAlex %s/%s/%d: %s", jname, label, y, e)
                    yearly[y] = None
                    time.sleep(3.0)
            entry["by_journal"][jname] = yearly
        # рост прикладного интереса: 2024-25 vs 2022-23 (по обоим журналам)
        rec = sum((entry["by_journal"].get(j, {}).get(y, 0) or 0) for j in APP_JOURNALS for y in years if y >= 2024)
        prev = sum((entry["by_journal"].get(j, {}).get(y, 0) or 0) for j in APP_JOURNALS for y in years if 2022 <= y < 2024)
        entry["applied_growth"] = (rec / prev) if prev > 0 else (1.0 if rec > 0 else 0.0)
        entry["applied_total_recent"] = rec
        results.append(entry)
        logger.info("  %-30s рост прикладного интереса: %.2f (recent=%d)", label, entry["applied_growth"], rec)

    out = {
        "method": "openalex_applied_journals",
        "description": "Прикладной слой: статьи в IEEE TAS + SuST по трендам (OpenAlex)",
        "journals": APP_JOURNALS,
        "trends": results,
    }
    out_path = PROJECT_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Записано: %s", out_path)


if __name__ == "__main__":
    main()
