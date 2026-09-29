"""Докачка абстрактов 18 патентов (17 CN + PsiQuantum) из очереди.

Стратегия: XHR даёт snippet (фрагмент), HTML-страница даёт полный abstract.
1. Для каждого патента: Google Patents HTML → abstract (section itemprop="abstract").
2. Fallback: XHR → snippet.
Обновляет data/raw/patents/superconducting_diode_patents.json (поле abstract + snippet).
"""
from __future__ import annotations

import json
import logging
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

PATS_FILE = PROJECT_ROOT / "data" / "raw" / "patents" / "superconducting_diode_patents.json"

# 18 патентов из очереди (по номеру)
QUEUE = [
    "US20260107697A1", "CN121038588A", "CN121442959B", "CN120435217A",
    "CN120124571A", "CN120529823A", "CN121908810A", "CN121793636A",
    "CN119866171A", "CN121034796A", "CN121908809A", "CN120614742A",
    "CN119965802A", "CN121127118A", "CN120640508A", "CN121483794A",
    "CN121815950A", "CN120527113A",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36",
}


def fetch_html(pub: str, lang: str = "en") -> str | None:
    url = f"https://patents.google.com/patent/{pub}/{lang}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        logger.warning("HTML %s: %s", pub, str(e)[:80])
        return None


def extract_abstract(html: str) -> str | None:
    """Извлечь abstract из section itemprop='abstract'."""
    m = re.search(r'<section itemprop="abstract"[^>]*>(.*?)</section>', html, re.S)
    if not m:
        return None
    text = re.sub(r"<[^>]+>", " ", m.group(1))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:2000] or None


def fetch_snippet(pub: str) -> str | None:
    """Fallback: XHR snippet."""
    url = "https://patents.google.com/xhr/query?url=" + urllib.parse.quote(f"q={pub}&num=1", safe="")
    headers = {**HEADERS, "Accept": "application/json"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode())
        for c in d.get("results", {}).get("cluster", []):
            for res in c.get("result", []):
                if res.get("patent", {}).get("publication_number") == pub:
                    return (res["patent"].get("snippet") or "")[:2000]
    except Exception as e:
        logger.warning("XHR %s: %s", pub, str(e)[:80])
    return None


def main() -> None:
    data = json.loads(PATS_FILE.read_text(encoding="utf-8"))
    by_num = {p["publication_number"]: p for p in data["patents"]}

    ok, fail = 0, 0
    for pub in QUEUE:
        # найти патент по подстроке номера (в базе номера могут быть с <b> тегами)
        target = next((p for p in by_num.values() if pub.replace("<b>", "").replace("</b>", "") in p["publication_number"].replace("<b>", "").replace("</b>", "")), None)
        if target is None:
            logger.warning("Нет в базе: %s", pub)
            continue
        # 1) HTML abstract
        html = fetch_html(pub)
        abstract = extract_abstract(html) if html else None
        src = "html"
        # 2) fallback: snippet (XHR)
        if not abstract:
            abstract = fetch_snippet(pub)
            src = "xhr_snippet"
        if abstract:
            target["abstract"] = abstract
            target["abstract_source"] = src
            ok += 1
            logger.info("  %s → %s (%d симв.)", pub, src, len(abstract))
        else:
            fail += 1
            logger.warning("  %s → НЕТ abstract", pub)
        time.sleep(6)  # пауза против rate-limit

    # сохранить (только очередь, не перезаписывая остальные)
    data["patents"] = list(by_num.values())
    PATS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Итог: %d/18 с abstract (fail=%d) → %s", ok, fail, PATS_FILE)


if __name__ == "__main__":
    main()
