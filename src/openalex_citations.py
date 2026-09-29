"""OpenAlex: цитаты для 8 калибровочных тем.

Берёт ключевые статьи (evidence) калибровочных тем, запрашивает их цитирования
через OpenAlex API (по DOI), считает суммарную динамику цитат по годам.
Цель: добавить «цитатный» сигнал к графу концептов (путь B) и сравнить
детекцию слабого сигнала (рост цитат) с нашим Score и link prediction.

Вход: results/top_trends_deduped.json (тренды + evidence), data/processed/papers.parquet (DOI).
Выход: data/raw/openalex/openalex_calibration_results.json
"""

from __future__ import annotations

import argparse
import json
import logging
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

# Калибровочные темы (tid в topics_full) → имя + окно автора
CAL_TOPICS = {
    1: ("quantum codes", (2022, 2022)),
    4: ("graphene", (2000, 2002)),
    5: ("quantum systems", (2005, 2008)),
    6: ("NV-centers", (2006, 2008)),
    9: ("spintronics", (2007, 2012)),
    14: ("ML-materials", (2023, 2023)),
    15: ("plasmonics", (2024, 2025)),
    19: ("neuromorphic", (2018, 2022)),
}


def fetch_openalex(doi: str, mailto: str = "research@example.com", retries: int = 3) -> dict | None:
    """Получить работу из OpenAlex по DOI (с цитатами)."""
    url = "https://api.openalex.org/works?filter=doi:" + urllib.parse.quote(doi) + "&per-page=1&mailto=" + mailto
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-test"})
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.load(r)
            if d["results"]:
                w = d["results"][0]
                return {
                    "id": w["id"],
                    "year": w.get("publication_year"),
                    "cited_by_count": w.get("cited_by_count", 0),
                    "cited_by_year": {c["year"]: c["cited_by_count"] for c in w.get("counts_by_year", [])},
                }
        except Exception as e:
            logger.warning("OpenAlex retry %d for %s: %s", attempt + 1, doi, e)
            time.sleep(1.5 * (attempt + 1))
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="OpenAlex цитаты для калибровочных тем")
    ap.add_argument("--trends", default="results/top_trends_deduped.json")
    ap.add_argument("--papers", default="data/processed/papers.parquet")
    ap.add_argument("--out", default="data/raw/openalex/openalex_calibration_results.json")
    ap.add_argument("--n-papers", type=int, default=10, help="сколько evidence-статей на тему запрашивать")
    ap.add_argument("--all", action="store_true", help="собрать для ВСЕХ трендов (не только 8 калибровочных)")
    args = ap.parse_args()

    trends = json.loads((PROJECT_ROOT / args.trends).read_text(encoding="utf-8"))["trends"]
    papers = pd.read_parquet(PROJECT_ROOT / args.papers)
    doi_map = dict(zip(papers["arxiv_id"].astype(str), papers["doi"].astype(str)))

    # tid в top_trends_deduped = tid из topics_full
    by_tid = {t["topic_id"]: t for t in trends}

    if args.all:
        # все тренды: имя из label
        target = [(tid, (t.get("label", "")[:30], (None, None))) for tid, t in by_tid.items()]
    else:
        target = [(tid, (name, win)) for tid, (name, win) in CAL_TOPICS.items()]

    results = []
    for tid, (name, win) in target:
        t = by_tid.get(tid)
        if not t:
            logger.warning("Тема tid=%d (%s) не найдена в трендах", tid, name)
            continue
        ev = t.get("evidence", [])[: args.n_papers]
        logger.info("Тема %s (tid=%d): %d evidence-статей, запрос OpenAlex…", name, tid, len(ev))

        fetched = []
        for aid in ev:
            doi = doi_map.get(aid, "")
            if not doi or not str(doi).startswith("https://doi.org/"):
                continue
            doi = str(doi).replace("https://doi.org/", "")
            rec = fetch_openalex(doi)
            if rec:
                fetched.append({"arxiv_id": aid, "doi": doi, **rec})
            time.sleep(0.15)  # вежливый лимит

        # суммарные цитаты по годам
        yearly = {}
        for f in fetched:
            for y, c in f.get("cited_by_year", {}).items():
                yearly[y] = yearly.get(y, 0) + c

        results.append({
            "topic_id": tid,
            "name": name,
            "author_window": list(win),
            "n_papers_fetched": len(fetched),
            "papers": fetched,
            "yearly_citations": {int(y): int(c) for y, c in sorted(yearly.items())},
        })
        logger.info("  получено %d/%d, суммарных цитат всего: %d",
                    len(fetched), len(ev), sum(yearly.values()))

    out = {
        "method": "openalex_citations",
        "description": "Цитаты OpenAlex для 8 калибровочных тем (по evidence-статьям)",
        "source": "https://api.openalex.org",
        "calibration_topics": results,
    }
    out_path = PROJECT_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Записано: %s", out_path)


if __name__ == "__main__":
    main()
