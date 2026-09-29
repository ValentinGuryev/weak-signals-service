"""CORDIS: сбор EU contribution для проектов 2027 через detail-страницы (Playwright).

Detail-страница: https://cordis.europa.eu/project/id/{id} → EU contribution (€).
Запуск: LD_LIBRARY_PATH=~/local-libs/usr/lib/x86_64-linux-gnu python src/cordis_funding.py
"""
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

# id проектов 2027 (из cordis_results.json)
PROJECT_IDS = [
    "101040179", "101053801", "101054327", "101075602", "101094300",
    "101150440", "101150858", "101161930", "101172819", "101202931",
    "101204715", "101214315", "101218253", "101248573", "101269798",
    "101271945", "101273266", "101283792", "101288263",
]


def main() -> None:
    from playwright.sync_api import sync_playwright

    out_path = PROJECT_ROOT / "data" / "raw" / "grants_foreign" / "cordis_funding.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(user_agent="Mozilla/5.0")

        for pid in PROJECT_IDS:
            try:
                page.goto(f"https://cordis.europa.eu/project/id/{pid}", timeout=40000, wait_until="domcontentloaded")
                page.wait_for_timeout(5000)
                txt = page.inner_text("body")
                # EU contribution: «EU contribution\n€ 150 000,00» (€ на отдельной строке)
                m = re.search(r"EU contribution\s*\n?\s*€\s*([\d\s\.,]+)", txt)
                eu = m.group(1).strip() if m else None
                m2 = re.search(r"Total cost\s*\n?\s*(No data|[\d\s\.,]+)\s*€", txt)
                total = m2.group(1).strip() if m2 else None
                # Start/End
                m3 = re.search(r"Start date\s*\|\s*([^\n]+)", txt)
                m4 = re.search(r"End date\s*\|\s*([^\n]+)", txt)
                results.append({
                    "id": pid,
                    "eu_contribution": eu.strip() if eu else None,
                    "total_cost": total.strip() if total else None,
                    "start": m3.group(1).strip() if m3 else None,
                    "end": m4.group(1).strip() if m4 else None,
                })
                logger.info("  %s → EU: %s | total: %s", pid, eu, total)
            except Exception as e:
                logger.error("  %s ERR: %s", pid, str(e)[:100])
                results.append({"id": pid, "error": str(e)[:100]})
            time.sleep(1.5)

        browser.close()

    out_path.write_text(json.dumps({"method": "CORDIS detail pages (Playwright)", "count": len(results),
                                    "projects": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Сохранено: %s (%d)", out_path, len(results))


if __name__ == "__main__":
    main()
