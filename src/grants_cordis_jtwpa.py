#!/usr/bin/env python3
"""CORDIS (Европа, Horizon) — гранты для кейса 007 (JTWPA / квантовые усилители).

Эндпоинт: https://cordis.europa.eu/api/search/results?q=... (без ключа, бесплатно).
Термины — от ПРОБЛЕМЫ (не только JTWPA):
  - traveling wave parametric amplifier, JTWPA, TWPA
  - quantum-limited amplifier / Josephson parametric amplifier
  - qubit readout / quantum amplification (широкий драйвер)
  - DARTWARS (известный проект), kinetic inductance amplifier
Выход: data/raw/grants_foreign/cordis_jtwpa_results.json
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

KEYWORDS = [
    "traveling wave parametric amplifier",
    "travelling wave parametric amplifier",
    "JTWPA",
    "TWPA",
    "Josephson parametric amplifier",
    "kinetic inductance traveling wave",
    "quantum-limited amplifier",
    "DARTWARS",
    "qubit readout amplifier",
    "superconducting microwave amplifier",
]


def _get(url: str, timeout: int = 40, retries: int = 3) -> dict | None:
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120 Safari/537.36"}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            logger.warning("retry %d: %s", attempt + 1, str(e)[:120])
            time.sleep(3 * (attempt + 1))
    return None


def fetch_cordis(keyword: str, num: int = 20, max_pages: int = 4) -> list[dict]:
    rows: list[dict] = []
    search_after: str | None = None
    for page in range(max_pages):
        params = {"q": keyword, "num": str(num)}
        if search_after:
            params["searchAfter"] = search_after
        url = f"{CORDIS_URL}?{urllib.parse.urlencode(params)}"
        data = _get(url)
        if not data or not data.get("status"):
            logger.info("  CORDIS '%s' page %d: нет ответа", keyword, page)
            break
        payload = data.get("payload") or {}
        total = payload.get("total", 0)
        for r in payload.get("results", []):
            prog = ""
            try:
                prog = ((r.get("programme") or [{}])[0].get("title") or "") if isinstance(r.get("programme"), list) else ""
            except Exception:  # noqa: BLE001
                prog = ""
            rows.append({
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
        logger.info("  CORDIS '%s' page %d → %d строк (total %d)", keyword, page, len(rows), total)
        search_after = payload.get("searchAfter")
        if not search_after:
            break
        time.sleep(1.0)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/raw/grants_foreign/cordis_jtwpa_results.json")
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
    out_path.write_text(json.dumps(
        {"method": "CORDIS API api/search/results (без ключа)", "count": len(uniq), "projects": uniq},
        ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Сохранено: %s (%d проектов)", out_path, len(uniq))


if __name__ == "__main__":
    main()
