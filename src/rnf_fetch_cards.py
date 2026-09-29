"""Докачка полных карточек РНФ по списку номеров (прямой URL rscf.ru/project/{номер}/).

Использует parse_card из rnf_parser.py. Читает номера из JSON, открывает карточки
по прямым URL, сохраняет результат с аннотацией/публикациями/ключевыми словами.

Запуск:
    LD_LIBRARY_PATH=... .venv/bin/python src/rnf_fetch_cards.py --in data/raw/rnf/rnf_numbers.json \
        --out data/raw/rnf/rnf_cards.json [--limit 20] [--start 0]
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

from rnf_parser import parse_card
from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

BASE_URL = "https://rscf.ru/project/"


def main() -> None:
    ap = argparse.ArgumentParser(description="Докачка карточек РНФ по номерам")
    ap.add_argument("--in", dest="inp", default="data/raw/rnf/rnf_numbers.json")
    ap.add_argument("--out", default="data/raw/rnf/rnf_cards.json")
    ap.add_argument("--limit", type=int, default=0, help="сколько карточек (0=все)")
    ap.add_argument("--start", type=int, default=0, help="с какого номера начать")
    args = ap.parse_args()

    inp_path = PROJECT_ROOT / args.inp
    data = json.loads(inp_path.read_text(encoding="utf-8"))
    numbers = data["unique"] if "unique" in data else [p["number"] for p in data["projects"]]
    numbers = numbers[args.start:]
    if args.limit:
        numbers = numbers[: args.limit]
    logger.info("Номеров на обработку: %d (start=%d, limit=%s)", len(numbers), args.start, args.limit)

    projects: dict[str, dict] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        # прогрев: открываем главную, чтобы сессия была
        page.goto(BASE_URL, timeout=45000)
        page.wait_for_load_state("networkidle", timeout=30000)

        ok, fail = 0, 0
        for i, num in enumerate(numbers, 1):
            url = f"https://rscf.ru/project/{num}/"
            try:
                page.goto(url, timeout=45000)
                page.wait_for_load_state("networkidle", timeout=25000)
                time.sleep(1.2)
                body = page.locator("body").inner_text(timeout=8000)
                if "404" in body[:200] or "Нет такой страницы" in body[:200]:
                    logger.warning("%s: 404", num)
                    fail += 1
                    continue
                card = parse_card(page)
                card["number"] = num
                projects[num] = card
                ok += 1
            except Exception as e:
                logger.warning("%s: %s", num, str(e)[:100])
                fail += 1
            if i % 10 == 0:
                logger.info("Обработано %d/%d (ok=%d, fail=%d)", i, len(numbers), ok, fail)
                # промежуточное сохранение
                _save(args.out, projects, numbers, i)

        browser.close()

    out = {"method": "rnf_fetch_cards", "n_projects": len(projects),
           "n_requested": len(numbers), "n_failed": fail, "projects": list(projects.values())}
    out_path = PROJECT_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("ИТОГО: ok=%d, fail=%d → %s", ok, fail, out_path)


def _save(out: str, projects: dict, numbers: list, done: int) -> None:
    out_path = PROJECT_ROOT / out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = {"method": "rnf_fetch_cards_partial", "n_projects": len(projects),
           "n_requested": done, "projects": list(projects.values())}
    out_path.write_text(json.dumps(tmp, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
