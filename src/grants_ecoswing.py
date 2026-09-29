#!/usr/bin/env python3
"""Гранты для кейса 010 (EcoSwing / СП-генераторы для ветроэнергетики) — NSF + CORDIS (free API, без ключа).

Термины — от ядра (проекты EcoSwing/UpWind/INNWIND/SUPRAPOWER) И от проблемы
(ветрогенератор/ветротурбина на СП, СП-электрическая машина):
  - ядро: EcoSwing, INNWIND, SUPRAPOWER
  - проблема: superconducting wind (turbine/generator/energy), superconducting generator,
    superconducting electrical machine, HTS generator
Выход: data/raw/grants_foreign/nsf_ecoswing_results.json, cordis_ecoswing_results.json
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

NSF_URL = "https://api.nsf.gov/services/v1/awards.json"
CORDIS_URL = "https://cordis.europa.eu/api/search/results"

NSF_KEYWORDS = [
    "EcoSwing",
    "superconducting wind",
    "superconducting wind turbine",
    "superconducting wind generator",
    "superconducting generator",
    "superconducting machine",
    "high temperature superconducting generator",
]

CORDIS_KEYWORDS = [
    "EcoSwing",
    "superconducting wind",
    "superconducting wind turbine",
    "superconducting wind generator",
    "superconducting electrical machine",
    "superconducting machine",
    "INNWIND",
    "SUPRAPOWER",
]


def fetch_nsf(keyword: str, rpp: int = 25) -> list[dict]:
    params = {
        "keyword": keyword,
        "rpp": str(rpp),
        "printFields": "id,title,org,awardeeName,piFirstName,piLastName,startDate,expDate,awardAmount,abstractText,agency,fundsObligatedAmt",
    }
    url = f"{NSF_URL}?{urllib.parse.urlencode(params)}"
    rows: list[dict] = []
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research"})
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.loads(r.read().decode())
            for a in data.get("response", {}).get("award", []):
                rows.append({
                    "source": "NSF", "query": keyword,
                    "id": a.get("id"),
                    "title": a.get("title"),
                    "org": a.get("awardeeName") or (a.get("org") or {}).get("name"),
                    "pi": f"{a.get('piFirstName') or ''} {a.get('piLastName') or ''}".strip(),
                    "amount": a.get("fundsObligatedAmt") or a.get("awardAmount"),
                    "year": (a.get("startDate") or "")[:4],
                    "start": a.get("startDate"),
                    "abstract": (a.get("abstractText") or "")[:2500],
                    "url": f"https://www.nsf.gov/awardsearch/showAward?AWD_ID={a.get('id')}",
                })
            break
        except Exception as e:  # noqa: BLE001
            logger.warning("NSF '%s' попытка %d: %s", keyword, attempt + 1, str(e)[:100])
            time.sleep(5 * (attempt + 1))
    logger.info("  NSF '%s' → %d строк", keyword, len(rows))
    return rows


def fetch_cordis(keyword: str, num: int = 20, max_pages: int = 3) -> list[dict]:
    """CORDIS: поиск по ключу, пагинация по searchAfter."""
    rows: list[dict] = []
    search_after: str | None = None
    for page in range(1, max_pages + 1):
        q = urllib.parse.quote(f"'{keyword}'")
        url = f"{CORDIS_URL}?q={q}&p={page}&num={num}"
        if search_after:
            url += f"&searchAfter={urllib.parse.quote(search_after)}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"})
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001
            logger.warning("CORDIS '%s' page %d: %s", keyword, page, str(e)[:120])
            break
        if not data.get("status"):
            break
        payload = data.get("payload", {})
        results = payload.get("results", [])
        if not results:
            break
        for r in results:
            rows.append({
                "source": "cordis",
                "query": keyword,
                "id": r.get("reference") or r.get("id"),
                "acronym": r.get("acronym"),
                "title": (r.get("title") or {}).get("title") if isinstance(r.get("title"), dict) else r.get("title"),
                "programme": "; ".join(p.get("title", "") for p in (r.get("programme") or [])),
                "start": r.get("startDate"),
                "end": r.get("endDate"),
                "teaser": (r.get("teaser") or "")[:2000],
                "country": r.get("coordinatedIn"),
                "contentType": r.get("contentType"),
                "url": f"https://cordis.europa.eu/project/id/{r.get('reference') or r.get('id')}",
            })
        logger.info("  CORDIS '%s' page %d → %d строк (total %s)", keyword, page, len(results), payload.get("total"))
        search_after = payload.get("searchAfter")
        if not search_after:
            break
        time.sleep(1.0)
    return rows


def main() -> None:
    nsf_rows: list[dict] = []
    for kw in NSF_KEYWORDS:
        nsf_rows.extend(fetch_nsf(kw))
        time.sleep(1.2)
    seen: set[str] = set()
    nsf_uniq: list[dict] = []
    for r in nsf_rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        nsf_uniq.append(r)
    nsf_path = PROJECT_ROOT / "data/raw/grants_foreign/nsf_ecoswing_results.json"
    nsf_path.write_text(json.dumps(
        {"method": "NSF API awards (без ключа)", "count": len(nsf_uniq), "grants": nsf_uniq},
        ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("NSF сохранено: %s (%d)", nsf_path, len(nsf_uniq))

    cordis_rows: list[dict] = []
    for kw in CORDIS_KEYWORDS:
        cordis_rows.extend(fetch_cordis(kw))
        time.sleep(0.8)
    seen = set()
    cordis_uniq: list[dict] = []
    for r in cordis_rows:
        k = str(r.get("id") or r.get("title"))
        if k in seen:
            continue
        seen.add(k)
        cordis_uniq.append(r)
    cordis_path = PROJECT_ROOT / "data/raw/grants_foreign/cordis_ecoswing_results.json"
    cordis_path.write_text(json.dumps(
        {"method": "CORDIS API api/search/results (без ключа)", "count": len(cordis_uniq), "projects": cordis_uniq},
        ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("CORDIS сохранено: %s (%d)", cordis_path, len(cordis_uniq))


if __name__ == "__main__":
    main()