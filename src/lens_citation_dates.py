#!/usr/bin/env python3
"""ДОКАЧКА дат цитирующих патентов (для темпорального графа S3).

Проблема: в ibad_merged.json есть cited_by/references (номера патентов),
но нет их дат. Для проверки «ссылки раньше работ» нужны даты цитирующих.

Решение: по номерам из cited_by/references запрашиваем Lens API,
получаем publication_date и priority_date цитирующих патентов.

Выход: data/raw/patents/topics_window/ibad_citation_dates.json
  {
    "US8231979": {"publication": "2012-07-31", "priority": "2006-04-03", "title": "..."},
    ...
  }

Запуск:
    LENS_TOKEN=xxx .venv/bin/python src/lens_citation_dates.py
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

LENS_API = "https://api.lens.org/patent/search"
TOKEN = os.environ.get("LENS_TOKEN", "")
if not TOKEN:
    logger.error("Нет LENS_TOKEN!")
    sys.exit(1)

DATA = PROJECT_ROOT / "data" / "raw" / "patents" / "topics_window"
OUT = DATA / "ibad_citation_dates.json"


def lens_lookup(doc_key: str) -> dict | None:
    """Найти патент по юрисдикции+номеру, вернуть даты."""
    # doc_key = "US_8231979" или "US8231979" или "JP_H04315705"
    s = doc_key.replace("_", "")
    m = __import__("re").match(r"^([A-Z]{2})(.*)$", s)
    if not m:
        return None
    jur, num = m.group(1), m.group(2)
    payload = {
        "query": {"bool": {"must": [
            {"match": {"jurisdiction": jur}},
            {"match": {"doc_number": num}},
        ]}},
        "size": 1,
        "include": ["biblio.publication_reference", "biblio.priority_claims",
                    "biblio.invention_title"],
    }
    req = urllib.request.Request(LENS_API, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read().decode())
        if not d.get("data"):
            return None
        p = d["data"][0]
        b = p.get("biblio", {})
        pr = b.get("publication_reference", {})
        pc = b.get("priority_claims", {})
        title = ""
        for t in b.get("invention_title", []):
            if t.get("lang") == "en":
                title = t.get("text", "")
                break
        return {
            "publication": pr.get("date", ""),
            "priority": pc.get("earliest_claim", {}).get("date", ""),
            "title": title,
        }
    except Exception as e:
        logger.warning("lookup %s: %s", doc_key, str(e)[:60])
        return None


def main() -> None:
    merged = json.loads((DATA / "ibad_merged.json").read_text(encoding="utf-8"))
    pats = merged["patents"]

    # Собираем все уникальные номера цитирующих
    citations = set()
    for p in pats:
        for c in p.get("cited_by", []):
            citations.add(c)
        for c in p.get("references", []):
            citations.add(c)
    logger.info("Уникальных цитирующих патентов: %d", len(citations))

    # Resume из существующего файла
    done = {}
    if OUT.exists():
        try:
            done = json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            done = {}
    remaining = sorted(citations - set(done.keys()))

    for i, doc in enumerate(remaining):
        info = lens_lookup(doc)
        if info:
            done[doc] = info
        if (i + 1) % 20 == 0:
            logger.info("докачано %d/%d", i + 1, len(remaining))
            OUT.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(1.5)  # вежливость к API

    OUT.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding="utf-8")
    logger.info("Сохранено: %s (%d патентов)", OUT, len(done))


if __name__ == "__main__":
    main()
