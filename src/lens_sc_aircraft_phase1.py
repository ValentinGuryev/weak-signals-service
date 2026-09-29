#!/usr/bin/env python3
"""Lens: Фаза 1 докачки патентной базы СП-авиамоторов (кейс 008).

План: case_studies/008_sc_aircraft_motors/lens_gap_analysis.md (v3, Фаза 1 = 6 запросов).
Слой A (ядро, докачка): A1 superconducting motor+aircraft (offset 50+), A2 stator/rotor,
                        A3 machine/generator.
Слой B (assignee): B1 Rolls-Royce, B2 NASA, B3 академия/пром (Siemens/HIT/Beihang/MIT/...).
Добавляет к существующей базе data/raw/patents/cases/008_sc_aircraft.json.
НЕ цепляет конкурентов (крио-медь/PM — ошибка v2).
Выход: дополненный 008_sc_aircraft.json + лог.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOKEN = os.environ.get("LENS_TOKEN", "")
if not TOKEN:
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("LENS_TOKEN="):
                TOKEN = line.split("=", 1)[1].strip()
                break
if not TOKEN:
    print("Нет LENS_TOKEN!")
    sys.exit(1)

LENS_API = "https://api.lens.org/patent/search"
MAX_CALLS = 10  # жёсткий лимит на Фазу 1
DATE_RANGE = {"gte": "1990-01-01", "lte": "2026-12-31"}
CASE_FILE = PROJECT_ROOT / "data/raw/patents/cases/008_sc_aircraft.json"


def mp(field, phrase):
    return {"match_phrase": {field: phrase}}


def m(field, term):
    return {"match": {field: term}}


def should(entries):
    return {"bool": {"should": entries}}


def avia():
    return should([m("abstract", "aircraft"), m("abstract", "aero"), m("abstract", "flight"),
                   m("abstract", "aviation"), m("abstract", "airplane")])


def q_a1():
    """Ядро: superconducting motor + авиа (offset 50+ — долистать хвост)."""
    return {"bool": {"must": [
        mp("abstract", "superconducting motor"),
        should([m("abstract", "aircraft"), m("abstract", "aero"), m("abstract", "flight"),
                m("abstract", "aviation"), m("abstract", "propulsion")]),
    ]}}


def q_a2():
    """Компонентные: superconducting + stator/rotor/field winding + авиа."""
    return {"bool": {"must": [
        m("abstract", "superconducting"),
        should([mp("abstract", "stator"), mp("abstract", "rotor"), mp("abstract", "field winding")]),
        avia(),
    ]}}


def q_a3():
    """Машины/генераторы: superconducting machine/generator + авиа."""
    return {"bool": {"must": [
        should([mp("abstract", "superconducting machine"), mp("abstract", "superconducting generator")]),
        avia(),
    ]}}


def q_b1_rr():
    """Rolls-Royce + СП/мотор/электрика."""
    return {"bool": {"must": [
        should([m("applicants", "Rolls-Royce"), m("applicants", "Rolls Royce")]),
        should([m("abstract", "superconducting"), m("abstract", "motor"), m("abstract", "electric propulsion")]),
    ]}}


def q_b2_nasa():
    """NASA/US Gov + СП/крио + мотор."""
    return {"bool": {"must": [
        should([m("applicants", "NASA"), m("applicants", "National Aeronautics"),
                m("applicants", "Administrator"), m("applicants", "United States of America")]),
        should([m("abstract", "superconducting"), m("abstract", "cryogenic")]),
        should([m("abstract", "motor"), m("abstract", "machine"), m("abstract", "generator")]),
    ]}}


def q_b3_acad():
    """Академия/пром (Siemens/HIT/Beihang/MIT/Illinois/FSU/Strathclyde) + СП."""
    return {"bool": {"must": [
        should([m("applicants", "Siemens"), m("applicants", "Harbin"), m("applicants", "Beihang"),
                m("applicants", "Massachusetts"), m("applicants", "Illinois"), m("applicants", "Florida State"),
                m("applicants", "Strathclyde"), m("applicants", "Beijing University")]),
        should([m("abstract", "superconducting"), m("abstract", "cryogenic")]),
        should([m("abstract", "motor"), m("abstract", "machine"), m("abstract", "aircraft")]),
    ]}}


# (tag, query_fn, max_pages)
PHASE1 = [
    ("a1_core_motor", q_a1, 3),    # долистать до 150 (было total 153)
    ("a2_stator_rotor", q_a2, 2),
    ("a3_machine_gen", q_a3, 2),
    ("b1_rollsroyce", q_b1_rr, 2),
    ("b2_nasa", q_b2_nasa, 2),
    ("b3_academy", q_b3_acad, 2),
]


def lens_search(query, offset, size=50):
    payload = {
        "query": query, "size": size, "offset": offset,
        "date_filter": {"field": "publication_date", "from": DATE_RANGE["gte"], "to": DATE_RANGE["lte"]},
        "include": ["biblio.publication_reference", "biblio.application_reference",
                    "biblio.priority_claims", "biblio.invention_title", "biblio.parties", "abstract"],
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(LENS_API, data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            print(f"[lens] HTTP {e.code}", flush=True)
            if e.code == 429:
                time.sleep(25)
            else:
                return None
        except Exception as e:
            print(f"[lens] ошибка: {str(e)[:80]}", flush=True)
            if attempt == 2:
                return None
            time.sleep(6)
    return None


def extract(p):
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
    applicants = []
    for ap in biblio.get("parties", {}).get("applicants", []):
        name = ap.get("extracted_name", {}).get("value", "")
        if name:
            applicants.append(name)
    return {
        "publication_number": doc_key,
        "title": title,
        "abstract": abstract[:1500],
        "assignee": ", ".join(applicants[:3]) if applicants else "",
        "priority_date": (biblio.get("priority_claims", {}).get("earliest_claim", {}).get("date") or "")[:10],
        "filing_date": (biblio.get("application_reference", {}).get("date") or "")[:10],
        "publication_date": pdate[:10],
        "url": f"https://www.lens.org/lens/patent/{lens_id}" if lens_id else "",
        "topic": "",
    }


def in_window(rec):
    for f in ("publication_date", "priority_date", "filing_date"):
        y = (rec.get(f) or "")[:4]
        if y and 1990 <= int(y) <= 2026:
            return True
    return False


def main():
    # загрузить текущую базу
    case = json.loads(CASE_FILE.read_text(encoding="utf-8"))
    existing = {p["publication_number"]: p for p in case["patents"]}
    print(f"Текущая база: {len(existing)} патентов")

    calls = 0
    new_by_tag = defaultdict(list)
    for tag, query_fn, max_pages in PHASE1:
        query = query_fn()
        print(f"\n=== {tag} ===", flush=True)
        got, offset, pages = 0, 0, 0
        while got < 100 and offset < 200 and pages < max_pages and calls < MAX_CALLS:
            resp = lens_search(query, offset)
            calls += 1
            print(f"  [вызов {calls}/{MAX_CALLS}] offset {offset}", flush=True)
            if not resp:
                break
            results = resp.get("data", []) or []
            total = resp.get("total", 0)
            if not results:
                print(f"    пусто (total={total})", flush=True)
                break
            added = 0
            for p in results:
                rec = extract(p)
                if not rec or not in_window(rec):
                    continue
                if rec["publication_number"] in existing:
                    continue  # уже есть
                rec["topic"] = tag
                existing[rec["publication_number"]] = rec
                new_by_tag[tag].append(rec)
                added += 1
            print(f"    +{added} новых (total={total})", flush=True)
            pages += 1
            offset += len(results)
            time.sleep(3)
        print(f"  Итог {tag}: +{len(new_by_tag[tag])} новых", flush=True)

    case["patents"] = list(existing.values())
    case["note"] = case.get("note", "") + " + Фаза 1 докачка (A1-A3, B1-B3)"
    CASE_FILE.write_text(json.dumps(case, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n=== ИТОГ Фазы 1: база {len(existing)} патентов, вызовов {calls} ===")
    for tag, lst in new_by_tag.items():
        print(f"  {tag}: +{len(lst)}")
        # показать assignees новых
        from collections import Counter
        ass = Counter(p.get("assignee", "?") for p in lst if p.get("assignee"))
        for a, c in ass.most_common(5):
            print(f"      {c} | {a[:60]}")

    # лог бюджета
    budget_log = PROJECT_ROOT / "results/runtime/api_budget.md"
    if budget_log.exists():
        with budget_log.open("a", encoding="utf-8") as f:
            f.write(f"\n| 2026-09-07 | 008 Lens Фаза 1 выполнена | {calls} | ~467→~{467-calls} | Да |\n")


if __name__ == "__main__":
    main()
