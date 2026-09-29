#!/usr/bin/env python3
"""NSF (США) — гранты для кейса 007 (JTWPA / квантовые усилители).

Эндпоинт: https://api.nsf.gov/services/v1/awards.json?keyword=... (без ключа).
Термины — от ПРОБЛЕМЫ + конкурентов:
  - traveling wave parametric amplifier / JTWPA / TWPA
  - Josephson parametric amplifier / quantum-limited amplifier
  - qubit readout / quantum-limited microwave / kinetic inductance amplifier
Выход: data/raw/grants_foreign/nsf_jtwpa_results.json
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

KEYWORDS = [
    "traveling wave parametric amplifier",
    "travelling wave parametric amplifier",
    "JTWPA",
    "TWPA",
    "Josephson parametric amplifier",
    "quantum-limited amplifier",
    "kinetic inductance amplifier",
    "qubit readout amplifier",
    "superconducting microwave amplifier",
    "quantum limited microwave",
]


def fetch_nsf(keyword: str, rpp: int = 25) -> list[dict]:
    params = {
        "keyword": keyword,
        "rpp": str(rpp),
        "printFields": "id,title,org,piFirstName,piLastName,awardeeName,startDate,expDate,awardAmount,abstractText,agency,fundsObligatedAmt",
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
                    "org": a.get("awardeeName") or a.get("org", {}).get("name"),
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


def main() -> None:
    all_rows: list[dict] = []
    for kw in KEYWORDS:
        all_rows.extend(fetch_nsf(kw))
        time.sleep(1.2)
    seen: set[str] = set()
    uniq: list[dict] = []
    for r in all_rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        uniq.append(r)
    out_path = PROJECT_ROOT / "data/raw/grants_foreign/nsf_jtwpa_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(
        {"method": "NSF API awards (без ключа)", "count": len(uniq), "grants": uniq},
        ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Сохранено: %s (%d грантов)", out_path, len(uniq))


if __name__ == "__main__":
    main()
