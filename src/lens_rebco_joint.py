#!/usr/bin/env python3
"""Разведка патентной базы соединений REBCO — план joint_patent_plan.md (8 запросов).

Фаза 1 — Термины:
  Q1: "superconducting joint" + (REBCO OR "coated conductor" OR HTS)
  Q2: "superconducting splice" + (REBCO OR "coated conductor")
  Q3: "intermediate grown superconducting" OR "iGS" + (REBCO OR joint)
  Q4: "persistent current" + (REBCO OR "coated conductor") + (joint OR magnet)
Фаза 2 — Игроки:
  Q5: assignee (Sumitomo OR Fujikura OR Toshiba OR Hitachi) + (joint OR splice OR persistent)
  Q6: assignee (RIKEN OR NIMS OR AIST OR "Korea" OR KJoins) + (joint OR splice)
Фаза 3 — Альтернативы:
  Q7: "joint-less" OR "jointless" + (REBCO OR coil OR magnet)
  Q8: "resistance-free" + (joint OR connection) + superconducting

Пост-фильтр: joint/splice/iGS/persistent + REBCO/coated conductor/YBCO/GdBCO.
Окно: priority_date 2006-2026.
Выход: data/raw/patents/topics/rebco_joint_lens.json
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

OUT_FILE = PROJECT_ROOT / "data" / "raw" / "patents" / "topics" / "rebco_joint_lens.json"
PAGE_SIZE = 50
BUDGET = 10  # жёсткий бюджет

ASSIGNEE_FIELD = "biblio.parties.applicants.extracted_name.value"
INVENTOR_FIELD = "biblio.parties.inventors.extracted_name.value"

# Термины для Q3 (iGS) — ищем в title/abstract
IGS_Q = {"bool": {"should": [
    {"match_phrase": {"abstract": "intermediate grown superconducting"}},
    {"match_phrase": {"title": "intermediate grown superconducting"}},
    {"match_phrase": {"abstract": "iGS joint"}},
    {"match_phrase": {"title": "iGS joint"}},
]}}

# Термины joint/splice для игроков
JS_Q = {"bool": {"should": [
    {"match_phrase": {"title": "superconducting joint"}},
    {"match_phrase": {"title": "joint"}},
    {"match_phrase": {"title": "splice"}},
    {"match_phrase": {"title": "persistent"}},
    {"match_phrase": {"abstract": "superconducting joint"}},
    {"match_phrase": {"abstract": "splice"}},
]}}

QUERIES = [
    # Q1: superconducting joint + REBCO/CC/HTS
    {"bool": {"must": [
        {"match_phrase": {"abstract": "superconducting joint"}},
        {"bool": {"should": [
            {"match": {"abstract": "REBCO"}},
            {"match_phrase": {"abstract": "coated conductor"}},
            {"match": {"abstract": "HTS"}},
            {"match": {"abstract": "YBCO"}},
            {"match": {"abstract": "GdBCO"}},
        ]}},
    ]}},
    # Q2: superconducting splice + REBCO/CC
    {"bool": {"must": [
        {"bool": {"should": [
            {"match_phrase": {"abstract": "superconducting splice"}},
            {"match_phrase": {"title": "superconducting splice"}},
        ]}},
        {"bool": {"should": [
            {"match": {"abstract": "REBCO"}},
            {"match_phrase": {"abstract": "coated conductor"}},
            {"match": {"abstract": "YBCO"}},
        ]}},
    ]}},
    # Q3: iGS
    {"bool": {"must": [
        IGS_Q,
        {"bool": {"should": [
            {"match": {"abstract": "REBCO"}},
            {"match_phrase": {"abstract": "coated conductor"}},
            {"match": {"abstract": "YBCO"}},
            {"match_phrase": {"abstract": "joint"}},
        ]}},
    ]}},
    # Q4: persistent current + REBCO/CC + joint/magnet
    {"bool": {"must": [
        {"match_phrase": {"abstract": "persistent current"}},
        {"bool": {"should": [
            {"match": {"abstract": "REBCO"}},
            {"match_phrase": {"abstract": "coated conductor"}},
        ]}},
        {"bool": {"should": [
            {"match": {"abstract": "joint"}},
            {"match": {"abstract": "magnet"}},
        ]}},
    ]}},
    # Q5: японские гиганты + joint/splice/persistent
    {"bool": {"must": [
        {"bool": {"should": [
            {"match": {ASSIGNEE_FIELD: "Sumitomo"}},
            {"match": {ASSIGNEE_FIELD: "Fujikura"}},
            {"match": {ASSIGNEE_FIELD: "Toshiba"}},
            {"match": {ASSIGNEE_FIELD: "Hitachi"}},
        ]}},
        JS_Q,
    ]}},
    # Q6: лаборатории/Корея + joint/splice
    {"bool": {"must": [
        {"bool": {"should": [
            {"match": {ASSIGNEE_FIELD: "RIKEN"}},
            {"match": {ASSIGNEE_FIELD: "NIMS"}},
            {"match": {ASSIGNEE_FIELD: "AIST"}},
            {"match": {ASSIGNEE_FIELD: "Korea"}},
            {"match": {ASSIGNEE_FIELD: "KJoins"}},
        ]}},
        JS_Q,
    ]}},
    # Q7: joint-less / jointless + REBCO/coil/magnet
    {"bool": {"must": [
        {"bool": {"should": [
            {"match_phrase": {"title": "joint-less"}},
            {"match_phrase": {"title": "jointless"}},
            {"match_phrase": {"abstract": "joint-less"}},
            {"match_phrase": {"abstract": "jointless"}},
        ]}},
        {"bool": {"should": [
            {"match": {"abstract": "REBCO"}},
            {"match_phrase": {"abstract": "coated conductor"}},
            {"match": {"abstract": "coil"}},
            {"match": {"abstract": "magnet"}},
            {"match": {"abstract": "superconduct"}},
        ]}},
    ]}},
    # Q8: resistance-free + joint/connection + superconducting
    {"bool": {"must": [
        {"bool": {"should": [
            {"match_phrase": {"abstract": "resistance-free"}},
            {"match_phrase": {"title": "resistance-free"}},
        ]}},
        {"bool": {"should": [
            {"match": {"abstract": "joint"}},
            {"match": {"abstract": "connection"}},
        ]}},
        {"match": {"abstract": "superconduct"}},
    ]}},
]

# Пост-фильтр: соединение REBCO (не NbTi/MgB2/Bi-2212!)
JOINT_RE = re.compile(r"joint|splice|iGS|persistent|connection", re.I)
REBCO_RE = re.compile(r"REBCO|coated[\s-]?conductor|YBCO|GdBCO|SmBCO|EuBCO|RE-?123|rare[\s-]?earth", re.I)
SC_RE = re.compile(r"superconduct|HTS|persistent|flux", re.I)
NON_RE = re.compile(r"\bGaN\b|\bsilicon\b|\bSiC\b|perovskite|\bbattery\b|\belectrode\b|\bsemiconductor\b|\bLED\b|solar cell|\bquantum\b|\bqubit\b|NbTi|MgB2|Bi-?2212|Bi-?2223|niobium|magnesium diboride", re.I)
TAG_RE = re.compile(r"<[^>]+>")


def relevant(title: str, abstract: str) -> bool:
    t = TAG_RE.sub("", f"{title} {abstract}").lower()
    if NON_RE.search(t):
        return False
    # Должно быть: joint-контекст И REBCO И superconducting
    if not JOINT_RE.search(t):
        return False
    if not REBCO_RE.search(t):
        return False
    return bool(SC_RE.search(t))


def lens_search(query: dict, offset: int = 0) -> dict | None:
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
        "tech": "rebco_joint",
        "url": url,
    }


def main() -> None:
    all_pats: list[dict] = []
    seen: set[str] = set()
    used = 0

    for qi, query in enumerate(QUERIES):
        if used >= BUDGET:
            logger.warning("Бюджет исчерпан (%d)", used)
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
        # Вторая страница, если total > 50 и есть бюджет
        if total > PAGE_SIZE and used < BUDGET:
            data2 = lens_search(query, PAGE_SIZE)
            used += 1
            if data2:
                for p in data2.get("data", []):
                    ep = extract(p)
                    if not ep or ep["publication_number"] in seen:
                        continue
                    if relevant(ep["title"], ep["abstract"]):
                        seen.add(ep["publication_number"])
                        all_pats.append(ep)
                        new_cnt += 1
                logger.info("    [p2] +%d (всего %d, total=%d)", new_cnt, len(all_pats), data2.get("total", 0))
        time.sleep(2)

    # Окно 2006-2026
    in_window = []
    for p in all_pats:
        pd = p.get("priority_date") or ""
        y = int(pd[:4]) if len(pd) >= 4 and pd[:4].isdigit() else 0
        if 2006 <= y <= 2026:
            in_window.append(p)

    logger.info("ИТОГО: %d патентов, в окне 2006-2026: %d, запросов: %d/%d",
                len(all_pats), len(in_window), used, BUDGET)

    result = {
        "query": "REBCO соединения: joint/splice/iGS/persistent/jointless/resistance-free (8 запросов)",
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

    # Статистика
    from collections import Counter
    geo = Counter(p["publication_number"].split("_")[0] for p in in_window)
    print("\n=== География (окно) ===")
    for k, v in geo.most_common():
        print(f"  {k}: {v}")
    years = Counter(p["priority_date"][:4] for p in in_window if p.get("priority_date"))
    print("\n=== По годам (окно) ===")
    for y in range(2006, 2027):
        if years.get(str(y)):
            print(f"  {y}: {years.get(str(y), 0)}")

    # Игроки
    def norm(a):
        a = a.upper()
        for key, name in [
            ("SUMITOMO", "Sumitomo (JP)"), ("FUJIKURA", "Fujikura (JP)"),
            ("TOSHIBA", "Toshiba (JP)"), ("HITACHI", "Hitachi (JP)"),
            ("RIKEN", "RIKEN (JP)"), ("NIMS", "NIMS (JP)"), ("AIST", "AIST (JP)"),
            ("KOREA", "Korea"), ("KJOINS", "KJoins (KR)"),
            ("SICHUAN", "Sichuan Univ"), ("NORTH CHINA", "N China Elec Power"),
            ("SIEMENS", "Siemens"), ("VICTORIA", "Victoria Link"),
            ("BROOKHAVEN", "Brookhaven"), ("MIT", "MIT"), ("FSU", "FSU/NHMFL"),
            ("NATIONAL HIGH", "NHMFL"), ("TOKYO", "Tokyo"),
            ("KYOTO", "Kyoto"), ("TSUKUBA", "Tsukuba"),
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
