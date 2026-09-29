#!/usr/bin/env python3
"""Патентная база flux pump через Lens.org — бюджет 7 запросов.

План (7 запросов максимум):
  1-4. Основной запрос "flux pump" + superconducting (abstract), size=50,
       offset 0/50/100/150 → покрывает все ~182 патента
  5.   count для доп. запроса "flux pump" + dynamo (size=0)
  6-7. доп. запрос dynamo (offset 0, при необходимости 50)

Пост-фильтр (локально, 0 запросов):
  - маркер: flux pump / flux-pump / fluxpump
  - SC: superconducting / HTS / REBCO / YBCO / coated conductor / dynamo / flux flow
  - окно: priority_date 2006-2026 (репрезентативная база для кейса)

Выход: data/raw/patents/topics/flux_pump_lens.json
Запуск: LENS_TOKEN=xxx .venv/bin/python src/lens_fluxpump_patents.py
"""
from __future__ import annotations

import json
import logging
import os
import re
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
    logger.error("Нет LENS_TOKEN в env!")
    sys.exit(1)

OUT_DIR = PROJECT_ROOT / "data" / "raw" / "patents" / "topics"
OUT_NAME = "flux_pump_lens.json"
PAGE_SIZE = 50
BUDGET = 7  # жёсткий бюджет запросов

# Основной запрос: "flux pump" + superconducting в abstract
QUERY_MAIN = {
    "bool": {"must": [
        {"match_phrase": {"abstract": "flux pump"}},
        {"match": {"abstract": "superconducting"}},
    ]}
}
# Доп. запрос: dynamo-тип без слова superconducting
QUERY_DYNAMO = {
    "bool": {"must": [
        {"match_phrase": {"abstract": "flux pump"}},
        {"match": {"abstract": "dynamo"}},
    ]}
}

# Пост-фильтр
FP_RE = re.compile(r"flux[\s-]?pump|fluxpump", re.I)
SC_RE = re.compile(r"superconduct|coated[\s-]?conductor|\bhts\b|\brebco\b|\bybco\b|dynamo|flux[\s-]?flow", re.I)
NON_RE = re.compile(r"\bGaN\b|\bsilicon\b|\bSiC\b|perovskite|\bbattery\b|\bsemiconductor\b|\bLED\b|solar cell", re.I)
TAG_RE = re.compile(r"<[^>]+>")


def relevant(title: str, abstract: str) -> bool:
    t = TAG_RE.sub("", f"{title} {abstract}").lower()
    if NON_RE.search(t):
        return False
    return bool(FP_RE.search(t)) and bool(SC_RE.search(t))


def lens_search(query: dict, offset: int) -> tuple[dict | None, int]:
    """Один запрос Lens. Возвращает (json, кол-во запросов)."""
    payload = {
        "query": query, "size": PAGE_SIZE, "offset": offset,
        "include": [
            "biblio.publication_reference", "biblio.application_reference",
            "biblio.priority_claims", "biblio.invention_title",
            "biblio.parties", "abstract",
        ],
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(LENS_API, data=body, headers={
        "Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode()), 1
    except urllib.error.HTTPError as e:
        if e.code == 429:
            logger.warning("[lens] 429 — пауза 15 сек")
            time.sleep(15)
            return None, 0
        logger.warning("[lens] HTTP %d", e.code)
        return None, 1
    except Exception as e:
        logger.warning("[lens] ошибка: %s", str(e)[:80])
        return None, 1


def extract(p: dict) -> dict | None:
    """Извлечь патент в совместимый с ibad формат."""
    lens_id = p.get("lens_id") or ""
    biblio = p.get("biblio", {})
    pr = biblio.get("publication_reference", {})
    jur = pr.get("jurisdiction") or ""
    doc = pr.get("doc_number") or ""
    kind = pr.get("kind") or ""
    pdate = pr.get("date") or ""
    if not (jur and doc):
        return None
    doc_key = f"{jur}_{doc}_{kind}_{pdate}" if kind else f"{jur}_{doc}"
    title = ""
    for t in biblio.get("invention_title", []):
        if t.get("lang") == "en" or t.get("text"):
            title = t.get("text", "")
            break
    abstract = ""
    for a in p.get("abstract", []) or []:
        if a.get("lang") == "en":
            abstract = a.get("text", "")
            break
    priority_date = ""
    pc = biblio.get("priority_claims", {})
    earliest = pc.get("earliest_claim", {}).get("date") or ""
    if earliest:
        priority_date = earliest[:10]
    filing_date = ""
    ar = biblio.get("application_reference", {})
    if ar.get("date"):
        filing_date = ar["date"][:10]
    applicants = []
    for ap in biblio.get("parties", {}).get("applicants", []):
        name = ap.get("extracted_name", {}).get("value", "")
        if name:
            applicants.append(name)
    assignee = ", ".join(applicants[:3]) if applicants else ""
    inventors = []
    for inv in biblio.get("parties", {}).get("inventors", []):
        name = inv.get("extracted_name", {}).get("value", "")
        if name:
            inventors.append(name)
    url = f"https://www.lens.org/lens/patent/{lens_id}" if lens_id else ""
    return {
        "publication_number": doc_key,
        "title": title,
        "abstract": abstract,
        "assignee": assignee,
        "priority_date": priority_date,
        "filing_date": filing_date,
        "inventor": ", ".join(inventors[:5]) if inventors else "",
        "tech": "flux_pump",
        "url": url,
    }


def main() -> None:
    all_pats: list[dict] = []
    seen: set[str] = set()
    used = 0

    # Основной запрос: листаем страницы до total
    total_main = None
    offset = 0
    while used < BUDGET:
        data, n = lens_search(QUERY_MAIN, offset)
        used += n
        if not data:
            break
        total_main = data.get("total", 0)
        items = data.get("data", [])
        if not items:
            break
        for p in items:
            ep = extract(p)
            if not ep or ep["publication_number"] in seen:
                continue
            if relevant(ep["title"], ep["abstract"]):
                seen.add(ep["publication_number"])
                all_pats.append(ep)
        logger.info("  [main] offset %d → %d релевантных (total=%d, запросов %d/%d)",
                    offset, len(all_pats), total_main, used, BUDGET)
        if offset + PAGE_SIZE >= total_main:
            break
        offset += PAGE_SIZE
        time.sleep(2)

    # Доп. запрос: dynamo (если бюджет позволяет)
    if used < BUDGET:
        data, n = lens_search(QUERY_DYNAMO, 0)
        used += n
        if data:
            total_dyn = data.get("total", 0)
            for p in data.get("data", []):
                ep = extract(p)
                if not ep or ep["publication_number"] in seen:
                    continue
                if relevant(ep["title"], ep["abstract"]):
                    seen.add(ep["publication_number"])
                    all_pats.append(ep)
            logger.info("  [dynamo] → %d релевантных (total=%d, запросов %d/%d)",
                        len(all_pats), total_dyn, used, BUDGET)
            time.sleep(2)
            # Вторая страница dynamo
            if used < BUDGET and total_dyn > PAGE_SIZE:
                data2, n2 = lens_search(QUERY_DYNAMO, PAGE_SIZE)
                used += n2
                if data2:
                    for p in data2.get("data", []):
                        ep = extract(p)
                        if not ep or ep["publication_number"] in seen:
                            continue
                        if relevant(ep["title"], ep["abstract"]):
                            seen.add(ep["publication_number"])
                            all_pats.append(ep)
                    logger.info("  [dynamo p2] → %d релевантных (запросов %d/%d)",
                                len(all_pats), used, BUDGET)

    # Фильтр окна 2006-2026 (репрезентативная база)
    in_window = []
    out_window = []
    for p in all_pats:
        pd = p.get("priority_date") or ""
        y = int(pd[:4]) if len(pd) >= 4 and pd[:4].isdigit() else 0
        if 2006 <= y <= 2026:
            in_window.append(p)
        else:
            out_window.append(p)

    logger.info("Итого: %d релевантных (запросов %d/%d), в окне 2006-2026: %d, вне: %d",
                len(all_pats), used, BUDGET, len(in_window), len(out_window))

    # Сохранение
    result = {
        "query": '"flux pump" superconducting + dynamo',
        "window": "2006-2026",
        "downloaded": len(all_pats),
        "in_window": len(in_window),
        "requests_used": used,
        "source": "lens.org",
        "patents": all_pats,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    f = OUT_DIR / OUT_NAME
    f.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Сохранено: %s (%d патентов)", f, len(all_pats))

    # Годовая статистика
    from collections import Counter
    years = Counter(int(p["priority_date"][:4]) for p in in_window if p.get("priority_date"))
    print("\n=== Патенты flux pump по годам (2006-2026) ===")
    for y in range(2006, 2027):
        print(f"  {y}: {years.get(y, 0)}")


if __name__ == "__main__":
    main()
