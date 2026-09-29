"""CORDIS (Европа, Horizon) — гранты через API api/search/results (добавлено 2026-08-18).

Эндпоинт: https://cordis.europa.eu/api/search/results?q=...&p=1&num=10
Формат ответа: {"status": true, "payload": {"total": N, "results": [...], "searchAfter": "..."}}
Пагинация: searchAfter (курсор) → p=N.

Результат: data/raw/grants_foreign/cordis_results.json
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

CORDIS_URL = "https://cordis.europa.eu/api/search/results"
# Ключевые направления сверхпроводимости (как в других базах)
KEYWORDS = [
    "coated conductor",
    "REBCO",
    "HTS tape",
    "superconducting wire",
    "superconducting magnet",
    "flux pinning",
    "superconducting qubit",
    "josephson junction",
    "MgB2",
    "superconducting cable",
    "cost reduction superconductor",
    "manufacturing HTS",
]

# Для этих ключей берём ВСЕ страницы (до 10) — там ключевые проекты по удешевлению CC
FULL_PAGES = {"coated conductor", "HTS tape", "manufacturing HTS", "cost reduction superconductor", "superconducting wire", "superconducting cable"}


def _get(url: str, timeout: int = 40, retries: int = 3) -> dict | None:
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            logger.warning("retry %d: %s", attempt + 1, str(e)[:120])
            time.sleep(3 * (attempt + 1))
    return None


def fetch_cordis(keyword: str, num: int = 20, max_pages: int = 3) -> list[dict]:
    """CORDIS: поиск по ключевому слову, пагинация по searchAfter."""
    rows: list[dict] = []
    search_after: str | None = None
    max_p = max_pages if keyword not in FULL_PAGES else 10
    for page in range(1, max_p + 1):
        q = urllib.parse.quote(f"'{keyword}'")
        url = f"{CORDIS_URL}?q={q}&p={page}&num={num}"
        if search_after:
            url += f"&searchAfter={urllib.parse.quote(search_after)}"
        data = _get(url)
        if not data or not data.get("status"):
            logger.warning("CORDIS '%s' page %d: нет данных", keyword, page)
            break
        payload = data.get("payload", {})
        results = payload.get("results", [])
        if not results:
            break
        for r in results:
            prog = "; ".join(p.get("title", "") for p in (r.get("programme") or []))
            rows.append({
                "source": "cordis",
                "query": keyword,
                "id": r.get("reference") or r.get("id"),
                "acronym": r.get("acronym"),
                "title": (r.get("title") or {}).get("title") if isinstance(r.get("title"), dict) else r.get("title"),
                "programme": prog,
                "start": r.get("startDate"),
                "end": r.get("endDate"),
                "teaser": (r.get("teaser") or "")[:2000],
                "country": r.get("coordinatedIn"),
                "contentType": r.get("contentType"),
                "url": f"https://cordis.europa.eu/project/id/{r.get('reference') or r.get('id')}",
            })
        logger.info("  CORDIS '%s' page %d → %d строк (всего %d)", keyword, page, len(results), payload.get("total"))
        search_after = payload.get("searchAfter")
        if not search_after:
            break
        time.sleep(1.0)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="CORDIS (Европа) гранты")
    ap.add_argument("--out", default="data/raw/grants_foreign/cordis_results.json")
    ap.add_argument("--keywords", nargs="*", default=KEYWORDS)
    ap.add_argument("--num", type=int, default=20)
    args = ap.parse_args()

    out_path = PROJECT_ROOT / args.out
    all_rows: list[dict] = []
    for kw in args.keywords:
        all_rows.extend(fetch_cordis(kw, num=args.num))
        time.sleep(0.8)

    seen: set[str] = set()
    uniq: list[dict] = []
    for r in all_rows:
        k = str(r.get("id") or r.get("title"))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"method": "CORDIS API api/search/results (без ключа)", "count": len(uniq), "projects": uniq},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Сохранено: %s (%d проектов)", out_path, len(uniq))


if __name__ == "__main__":
    main()
