"""GitHub-сигнал: кодовая база по трендам (третья база пересечения).

Идея автора: тренд = пересечение сигналов из нескольких баз:
  1. Наука (arXiv/OpenAlex) — горячо обсуждается;
  2. Патенты (Google Patents) — коммерциализация растёт;
  3. GitHub — есть кодовая база (реализуемость/экосистема).

GitHub Search API (без ключа: 10 запросов/мин, 60/час).
Для каждого ключевого слова тренда: число репозиториев + топ-5 по звёздам.

Выход: data/raw/github/github_signal_results.json
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

# Ключевые слова трендов (как в патентном/прикладном слое)
TREND_KEYWORDS = {
    "superconducting diode": "superconducting diode",
    "fluxonium": "fluxonium",
    "no-insulation coil": "no-insulation superconducting coil",
    "mgb2": "MgB2 superconducting",
    "graphene": "graphene superconductor",
    "machine learning materials": "machine learning materials discovery",
    "quantum error correction": "quantum error correction",
    "neuromorphic": "neuromorphic computing memristor",
    "spintronics": "spintronics magnon",
    "nv center": "NV center diamond quantum",
    "chiral phonon": "chiral phonon",
    "superconducting magnet": "superconducting magnet",
}


def gh_search(query: str, per_page: int = 5) -> dict:
    """GitHub Search API: репозитории по query."""
    url = ("https://api.github.com/search/repositories?q=" + urllib.parse.quote(query)
           + "&sort=stars&per_page=" + str(per_page))
    req = urllib.request.Request(url, headers={
        "User-Agent": "research-trend-detection",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main() -> None:
    ap = argparse.ArgumentParser(description="GitHub-сигнал по трендам")
    ap.add_argument("--out", default="data/raw/github/github_signal_results.json")
    ap.add_argument("--keywords", default="", help="JSON: {label: query}")
    args = ap.parse_args()

    kw = TREND_KEYWORDS
    if args.keywords:
        kw = json.loads(args.keywords)

    results = []
    for label, query in kw.items():
        try:
            d = gh_search(query)
            total = d.get("total_count", 0)
            repos = [{
                "name": it.get("full_name"),
                "stars": it.get("stargazers_count", 0),
                "description": str(it.get("description") or "")[:100],
            } for it in d.get("items", [])[:5]]
            results.append({"label": label, "query": query, "total_repos": total, "top_repos": repos})
            logger.info("  %-30s репозиториев: %d", label, total)
            time.sleep(7.0)  # вежливая пауза (10 req/min)
        except Exception as e:
            logger.warning("GitHub '%s': %s", label, e)
            results.append({"label": label, "query": query, "total_repos": None, "top_repos": [], "error": str(e)})
            time.sleep(10.0)

    out = {
        "method": "github_search_api",
        "description": "Кодовая база по трендам (GitHub Search API)",
        "source": "https://api.github.com/search/repositories",
        "trends": results,
    }
    out_path = PROJECT_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Записано: %s", out_path)


if __name__ == "__main__":
    main()
