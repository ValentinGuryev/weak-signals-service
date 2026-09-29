"""KAKEN (Япония, JSPS/KAKENHI) — зарубежная грантовая база (часть 6-й базы данных).

KAKEN: база грантов Японского общества содействия науке (JSPS) / KAKENHI.
Сайт: https://kaken.nii.ac.jp/ — отдаёт HTML-таблицы (нет публичного JSON API).
Парсим таблицы поисковой выдачи: grant number, категория, организация, PI, период, аннотация.

Результат: data/raw/grants_foreign/kaken_results.json
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import time
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

KAKEN_SEARCH = "https://kaken.nii.ac.jp/en/search/"
# Ключевые направления сверхпроводимости (как в патентном слое и NSF)
KEYWORDS = [
    "superconducting diode",
    "fluxonium",
    "no-insulation coil",
    "flux pinning",
    "fluxonics",
    "force-free coil",
    "superconducting magnet",
    "mgb2",
    "superconducting qubit",
    "josephson junction",
    "superconductivity",
]


def _fetch(url: str, timeout: int = 40, retries: int = 3) -> str | None:
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001
            logger.warning("retry %d: %s", attempt + 1, str(e)[:120])
            time.sleep(3 * (attempt + 1))
    return None


def _clean(s: str | None) -> str | None:
    if not s:
        return None
    s = unescape(s)
    s = s.replace("&nbsp;", " ").replace("&ndash;", "-")
    return re.sub(r"\s+", " ", s).strip() or None


def parse_rows(html: str) -> list[dict]:
    """Парсинг таблиц KAKEN: каждая <tr> — поле одной записи; записи идут блоками по Grant Number."""
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S)
    grants: list[dict] = []
    cur: dict = {}
    for r in rows:
        t = _clean(re.sub(r"<[^>]+>", "|", r))
        if not t:
            continue
        # начало новой записи: Japan Grant Number JP...
        m = re.search(r"Japan Grant Number\|?\s*\|?\s*(JP\d+[A-Z]?\d*)", t)
        if m:
            if cur:
                grants.append(cur)
            cur = {"grant_number": m.group(1)}
            continue
        if not cur:
            continue
        # поля вида "Ключ| |значение"
        parts = [p.strip() for p in t.split("|") if p.strip()]
        if len(parts) >= 2:
            key, val = parts[0], parts[-1]
            if "Research Category" in key:
                cur["category"] = val
            elif "Review Section" in key:
                cur["review_section"] = val
            elif "Research Institution" in key:
                cur["institution"] = val
            elif "Principal Investigator" in key:
                cur["pi"] = val
            elif "Project Period" in key:
                # формат: ...| | |2025-04-01 – 2028-03-31||Granted
                dates = next((p for p in parts if re.match(r"\d{4}-\d{2}-\d{2}", p)), None)
                status = next((p for p in parts if p in ("Granted", "Completed", "Continuing", "Discontinued")), None)
                cur["period"] = dates or val
                cur["status"] = status or None
            elif "Outline of Research" in key:
                cur["abstract"] = val[:2000]
            elif "Research Field" in key:
                cur["field"] = val
    if cur:
        grants.append(cur)
    return grants


def fetch_kaken(keyword: str, max_pages: int = 3) -> list[dict]:
    grants: list[dict] = []
    for page in range(1, max_pages + 1):
        params = urllib.parse.urlencode({"kw": keyword, "ps": 50, "pg": page})
        html = _fetch(f"{KAKEN_SEARCH}?{params}")
        if not html:
            break
        page_grants = parse_rows(html)
        if not page_grants:
            break
        for g in page_grants:
            g["query"] = keyword
            g["source"] = "kaken"
            g["url"] = f"https://kaken.nii.ac.jp/en/grant/{g['grant_number']}/"
            grants.append(g)
        logger.info("  KAKEN '%s' page=%d → %d записей", keyword, page, len(page_grants))
        if len(page_grants) < 50:
            break
        time.sleep(1.0)
    return grants


def main() -> None:
    ap = argparse.ArgumentParser(description="KAKEN (Япония) гранты")
    ap.add_argument("--out", default="data/raw/grants_foreign/kaken_results.json")
    ap.add_argument("--keywords", nargs="*", default=KEYWORDS)
    args = ap.parse_args()

    out_path = PROJECT_ROOT / args.out
    all_grants: list[dict] = []
    for kw in args.keywords:
        all_grants.extend(fetch_kaken(kw))
        time.sleep(0.8)

    # дедупликация по grant_number
    seen: set[str] = set()
    uniq: list[dict] = []
    for g in all_grants:
        if g["grant_number"] in seen:
            continue
        seen.add(g["grant_number"])
        uniq.append(g)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"method": "KAKEN NII (JSPS) — HTML-парсинг, без ключа",
                    "count": len(uniq), "grants": uniq},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Сохранено: %s (%d грантов)", out_path, len(uniq))


if __name__ == "__main__":
    main()
