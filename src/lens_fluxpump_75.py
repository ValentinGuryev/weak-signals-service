#!/usr/bin/env python3
"""Расширение патентной базы flux pump — 5 запросов (по плану patent_75_percent_plan.md).

Q1: assignee-фильтр гигантов (Fujikura/Sumitomo/Toshiba/Hitachi/GA/AMSC) + flux pump
Q2: assignee Cambridge/Coombs/Geng + flux pump
Q3: "flux pumping" (без SC-требования)
Q4: "magnetic flux pump" / "superconducting pump"
Q5: "superconducting dynamo" / "HTS dynamo"

Жёсткий бюджет: 5 запросов (по 1 на каждый, size=50, offset=0).
Мерж с существующей базой + дедупликация + фильтр релевантности.
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

OUT_FILE = PROJECT_ROOT / "data" / "raw" / "patents" / "topics" / "flux_pump_lens_clean.json"
PAGE_SIZE = 50
BUDGET = 5  # жёсткий бюджет

ASSIGNEE_FIELD = "biblio.parties.applicants.extracted_name.value"

# 5 запросов
QUERIES = [
    # Q1: гиганты + flux pump
    {"bool": {"must": [
        {"bool": {"should": [
            {"match": {ASSIGNEE_FIELD: "Fujikura"}},
            {"match": {ASSIGNEE_FIELD: "Sumitomo"}},
            {"match": {ASSIGNEE_FIELD: "Toshiba"}},
            {"match": {ASSIGNEE_FIELD: "Hitachi"}},
            {"match": {ASSIGNEE_FIELD: "General Atomics"}},
            {"match": {ASSIGNEE_FIELD: "AMSC"}},
        ]}},
        {"bool": {"should": [
            {"match_phrase": {"title": "flux pump"}},
            {"match_phrase": {"title": "flux pumping"}},
            {"match_phrase": {"abstract": "flux pump"}},
            {"match_phrase": {"abstract": "flux pumping"}},
        ]}},
    ]}},
    # Q2: Cambridge/Coombs/Geng + flux pump
    {"bool": {"must": [
        {"bool": {"should": [
            {"match": {ASSIGNEE_FIELD: "Cambridge"}},
            {"match": {ASSIGNEE_FIELD: "Coombs"}},
            {"match": {ASSIGNEE_FIELD: "Geng"}},
        ]}},
        {"bool": {"should": [
            {"match_phrase": {"title": "flux pump"}},
            {"match_phrase": {"title": "flux pumping"}},
            {"match_phrase": {"abstract": "flux pump"}},
            {"match_phrase": {"abstract": "flux pumping"}},
        ]}},
    ]}},
    # Q3: flux pumping (без SC)
    {"bool": {"should": [
        {"match_phrase": {"title": "flux pumping"}},
        {"match_phrase": {"abstract": "flux pumping"}},
    ]}},
    # Q4: magnetic flux pump / superconducting pump
    {"bool": {"should": [
        {"match_phrase": {"title": "magnetic flux pump"}},
        {"match_phrase": {"abstract": "magnetic flux pump"}},
        {"match_phrase": {"title": "superconducting pump"}},
        {"match_phrase": {"abstract": "superconducting pump"}},
    ]}},
    # Q5: superconducting dynamo / HTS dynamo
    {"bool": {"should": [
        {"match_phrase": {"title": "superconducting dynamo"}},
        {"match_phrase": {"abstract": "superconducting dynamo"}},
        {"match_phrase": {"title": "HTS dynamo"}},
        {"match_phrase": {"abstract": "HTS dynamo"}},
        {"match_phrase": {"title": "high temperature superconducting dynamo"}},
        {"match_phrase": {"abstract": "high temperature superconducting dynamo"}},
    ]}},
]

# Фильтры (как в основном скрипте)
FP_RE = re.compile(r"flux[\s-]?pump|fluxpump|dynamo|rectifier", re.I)
SC_RE = re.compile(r"superconduct|coated[\s-]?conductor|\bhts\b|\brebco\b|\bybco\b|flux[\s-]?flow|persistent", re.I)
NON_RE = re.compile(r"\bGaN\b|\bsilicon\b|\bSiC\b|perovskite|\bbattery\b|\belectrode\b|\bsemiconductor\b|\bLED\b|solar cell|\bquantum\b|\bqubit\b|dynamo.electric machine|rotor of.*dynamo|stator.*dynamo", re.I)
TAG_RE = re.compile(r"<[^>]+>")


def relevant(title: str, abstract: str) -> bool:
    t = TAG_RE.sub("", f"{title} {abstract}").lower()
    if NON_RE.search(t):
        return False
    return bool(FP_RE.search(t)) and bool(SC_RE.search(t))


def lens_search(query: dict) -> dict | None:
    payload = {
        "query": query, "size": PAGE_SIZE, "offset": 0,
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
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            logger.warning("[lens] 429 — пауза 15 сек")
            time.sleep(15)
            return None
        logger.warning("[lens] HTTP %d", e.code)
        return None
    except Exception as e:
        logger.warning("[lens] ошибка: %s", str(e)[:80])
        return None


def extract(p: dict) -> dict | None:
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
    # Загружаем существующую базу
    existing = []
    if OUT_FILE.exists():
        try:
            d = json.loads(OUT_FILE.read_text(encoding="utf-8"))
            existing = d.get("patents", [])
        except Exception:
            existing = []
    logger.info("Существующая база: %d патентов", len(existing))
    seen = {p["publication_number"] for p in existing}
    all_pats = list(existing)

    used = 0
    for qi, query in enumerate(QUERIES):
        if used >= BUDGET:
            break
        data = lens_search(query)
        used += 1
        logger.info("[Q%d] запросов %d/%d", qi + 1, used, BUDGET)
        if not data:
            continue
        total = data.get("total", 0)
        items = data.get("data", [])
        new_cnt = 0
        for p in items:
            ep = extract(p)
            if not ep or ep["publication_number"] in seen:
                continue
            if relevant(ep["title"], ep["abstract"]):
                seen.add(ep["publication_number"])
                all_pats.append(ep)
                new_cnt += 1
        logger.info("    → +%d новых (всего %d, total=%d)", new_cnt, len(all_pats), total)
        time.sleep(2)

    # Окно
    in_window = []
    for p in all_pats:
        pd = p.get("priority_date") or ""
        y = int(pd[:4]) if len(pd) >= 4 and pd[:4].isdigit() else 0
        if 2006 <= y <= 2026:
            in_window.append(p)

    logger.info("ИТОГО: %d патентов, в окне: %d, запросов: %d/%d",
                len(all_pats), len(in_window), used, BUDGET)

    result = {
        "query": "5-запросное расширение (гиганты + flux pumping + magnetic flux pump + dynamo)",
        "window": "2006-2026",
        "downloaded": len(all_pats),
        "in_window": len(in_window),
        "requests_used": used,
        "source": "lens.org",
        "patents": all_pats,
    }
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Сохранено: %s (%d)", OUT_FILE, len(all_pats))

    # Итоговая статистика
    from collections import Counter
    geo = Counter(p["publication_number"].split("_")[0] for p in in_window)
    print("\n=== География (окно) ===")
    for k, v in geo.most_common():
        print(f"  {k}: {v}")

    # Игроки
    def norm(a):
        a = a.upper()
        for key, name in [
            ("SICHUAN", "Sichuan Univ"), ("NORTH CHINA", "N China Elec Power"),
            ("VICTORIA", "Victoria Link (NZ)"), ("SIEMENS", "Siemens"),
            ("HUNAN", "Hunan Univ"), ("NORTHEASTERN", "Northeastern Univ"),
            ("FUTONG", "Futong Group"), ("HTS 110", "HTS 110 (NZ)"),
            ("HOFFMANN", "Hoffmann"), ("POOKE", "Pooke"), ("COOMBS", "Coombs"),
            ("KOREA ADVANCED", "KAIST"), ("CHANGWON", "Changwon"), ("KOREA BASIC", "KBSI"),
            ("JEJU", "Jeju"), ("SHANGHAI", "Shanghai Jiao Tong"),
            ("FUJIKURA", "Fujikura (JP)"), ("FURUKAWA", "Furukawa (JP)"),
            ("SUMITOMO", "Sumitomo (JP)"), ("TOSHIBA", "Toshiba (JP)"),
            ("HITACHI", "Hitachi (JP)"), ("GENERAL ATOMICS", "General Atomics (US)"),
            ("AMSC", "AMSC (US)"), ("GRID LOGIC", "Grid Logic (US)"), ("EMERSON", "Emerson"),
            ("MITSUBISHI", "Mitsubishi (JP)"), ("CAMBRIDGE", "Cambridge"),
            ("HOLCOMB", "Grid Logic (US)"),
        ]:
            if key in a:
                return name
        return a.split(",")[0][:30] if a else "(нет)"

    players = Counter(norm(p["assignee"]) for p in in_window)
    print("\n=== Игроки (окно) ===")
    for k, v in players.most_common(25):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
