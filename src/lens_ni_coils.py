#!/usr/bin/env python3
"""Докачка патентов NI-coils / MI-coils (кейс 004) через Lens.org API.

7 запросов (бюджет пользователя 2026-09-01):
  1. ni_core:  "no-insulation" AND (coil OR magnet)
  2. pi:       "partially insulated" AND superconducting
  3. mi:       "metal-insulation" OR "metal as insulation"
  4. quench:   "no-insulation" AND (quench OR protection)
  5. selfprot: "self-protecting" AND superconducting coil
  6. apps:     "no-insulation" AND (MRI OR NMR OR fusion OR accelerator)
  7. rebco:    "no-insulation" AND REBCO

Токен: LENS_TOKEN из .env
Сохранение: data/raw/patents/topics/ni_coils_lens_clean.json
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LENS_API = "https://api.lens.org/patent/search"

env_path = PROJECT_ROOT / ".env"
TOKEN = os.environ.get("LENS_TOKEN", "")
if not TOKEN and env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.startswith("LENS_TOKEN="):
            TOKEN = line.split("=", 1)[1].strip()
            break
if not TOKEN:
    print("Нет LENS_TOKEN! (env или .env)")
    sys.exit(1)

OUT = PROJECT_ROOT / "data/raw/patents/topics/ni_coils_lens_clean.json"

QUERIES = {
    "ni_core": (
        {"bool": {"must": [
            {"match_phrase": {"title": "no-insulation"}},
            {"bool": {"should": [
                {"match": {"title": "coil"}}, {"match": {"title": "magnet"}},
                {"match": {"abstract": "coil"}}, {"match": {"abstract": "magnet"}},
            ]}},
        ]}},
        120,
    ),
    "pi": (
        {"bool": {"must": [
            {"match_phrase": {"abstract": "partially insulated"}},
            {"match": {"abstract": "superconduct"}},
        ]}},
        60,
    ),
    "mi": (
        {"bool": {"should": [
            {"match_phrase": {"abstract": "metal-insulation"}},
            {"match_phrase": {"abstract": "metal as insulation"}},
            {"match_phrase": {"title": "metal-insulation"}},
        ]}},
        80,
    ),
    "quench": (
        {"bool": {"must": [
            {"match_phrase": {"abstract": "no-insulation"}},
            {"bool": {"should": [
                {"match": {"abstract": "quench"}}, {"match": {"abstract": "protection"}},
            ]}},
        ]}},
        80,
    ),
    "selfprot": (
        {"bool": {"must": [
            {"match_phrase": {"abstract": "self-protecting"}},
            {"match": {"abstract": "superconduct"}},
        ]}},
        40,
    ),
    "apps": (
        {"bool": {"must": [
            {"match_phrase": {"abstract": "no-insulation"}},
            {"bool": {"should": [
                {"match": {"abstract": "MRI"}}, {"match": {"abstract": "NMR"}},
                {"match": {"abstract": "fusion"}}, {"match": {"abstract": "accelerator"}},
            ]}},
        ]}},
        60,
    ),
    "rebco": (
        {"bool": {"must": [
            {"match_phrase": {"abstract": "no-insulation"}},
            {"match": {"abstract": "REBCO"}},
        ]}},
        60,
    ),
}

SC_RE = re.compile(r"superconduct|rebco|ybco|gdbco|hts|magnet|coil", re.I)
NI_RE = re.compile(r"no[\s-]?insulat|partial[\s-]?insulat|metal[\s-]?insulat|metal as insulat|self[\s-]?protect", re.I)


def relevant(title: str, abstract: str, tag: str) -> bool:
    t = f"{title} {abstract}".lower()
    if not SC_RE.search(t):
        return False
    if tag in ("ni_core", "quench", "apps", "rebco"):
        return bool(NI_RE.search(t))
    if tag == "pi":
        return bool(re.search(r"partial[\s-]?insulat", t))
    if tag == "mi":
        return bool(re.search(r"metal[\s-]?insulat|metal as insulat", t))
    if tag == "selfprot":
        return bool(re.search(r"self[\s-]?protect", t))
    return False


def lens_search(query: dict, offset: int, size: int = 50) -> dict | None:
    payload = {
        "query": query,
        "size": size,
        "offset": offset,
        "include": [
            "biblio.publication_reference",
            "biblio.application_reference",
            "biblio.priority_claims",
            "biblio.invention_title",
            "biblio.parties",
            "abstract",
        ],
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        LENS_API, data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print(f"[lens] HTTP {e.code} — токен невалиден")
            return None
        if e.code == 429:
            print("[lens] HTTP 429 — пауза 20 сек")
            time.sleep(20)
            return None
        print(f"[lens] HTTP {e.code}")
        return None
    except Exception as e:
        print(f"[lens] ошибка: {str(e)[:80]}")
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
    return {
        "publication_number": doc_key,
        "title": title,
        "abstract": abstract,
        "assignee": ", ".join(applicants[:3]) if applicants else "",
        "priority_date": priority_date,
        "filing_date": filing_date,
        "url": f"https://www.lens.org/lens/patent/{lens_id}" if lens_id else "",
    }


def main() -> None:
    all_pats = {}
    for tag, (query, target) in QUERIES.items():
        print(f"\n=== {tag}: ищу до {target} ===")
        got, offset = 0, 0
        pages = 0
        while got < target and offset < 300 and pages < 4:
            resp = lens_search(query, offset)
            if not resp:
                break
            total = resp.get("total", 0)
            results = resp.get("data", []) or resp.get("results", []) or []
            if not results:
                break
            found = 0
            for p in results:
                rec = extract(p)
                if not rec:
                    continue
                if relevant(rec["title"], rec["abstract"], tag):
                    rec["topic"] = tag
                    all_pats[rec["publication_number"]] = rec
                    found += 1
            got += found
            pages += 1
            print(f"  offset {offset}: +{found} релевантных (total={total})")
            offset += len(results)
            time.sleep(4)
        print(f"  Итог {tag}: {got} релевантных")

    pats = list(all_pats.values())
    print(f"\n=== ИТОГО уникальных: {len(pats)} ===")
    OUT.write_text(json.dumps({
        "query": "NI/MI coils (кейс 004)",
        "downloaded": time.strftime("%Y-%m-%d"),
        "with_abstract": sum(1 for p in pats if p["abstract"]),
        "patents": pats,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Сохранено: {OUT}")

    from collections import Counter
    for tag, n in Counter(p["topic"] for p in pats).most_common():
        print(f"  {tag}: {n}")
    print("\n=== Примеры ===")
    for p in pats[:15]:
        print(f"  {p['publication_number']} | {(p['title'] or '')[:50]} | {p.get('assignee','')[:28]} | {p.get('priority_date','')}")


if __name__ == "__main__":
    main()
