#!/usr/bin/env python3
"""Lens: патентная база СП-моторов для авиации (кейс 008) — ужатый план v2.

План: case_studies/008_sc_aircraft_motors/lens_strategy.md (5 логических, ~10-15 API-вызовов).
Запросы:
  Q1 core: superconducting (motor/machine/generator/propulsion/field winding) + aircraft/aero/flight
  Q2 cryo: cryogenic + electric propulsion/motor + aircraft
  Q3 giants: Airbus/RR/Boeing/GE/Safran/Siemens + superconducting/cryogenic
  Q4 competitors: cryogenic motor / cryo-Al / PM motor + aircraft (не-СП)
  Q5 academy: MIT/Illinois/FSU/Ohio State/Strathclyde/HIT + superconducting
ЖЁСТКИЙ лимит: 15 API-вызовов (санкция команды).
Выход:
  data/raw/patents/cases/008_sc_aircraft.json       — ядро (Q1+Q2-CORE)
  data/raw/patents/cases/008_sc_aircraft_competitors.json — Q4 (крио-медь/PM)
  data/raw/patents/cases/008_sc_aircraft_players.json     — Q3+Q5 (гиганты+академия)
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
MAX_CALLS = 15  # жёсткий лимит
DATE_RANGE = {"gte": "1990-01-01", "lte": "2026-12-31"}  # шире окна (патенты 90-х по СП-моторам есть)


def mp(field: str, phrase: str) -> dict:
    return {"match_phrase": {field: phrase}}


def m(field: str, term: str) -> dict:
    return {"match": {field: term}}


def should(entries: list) -> dict:
    return {"bool": {"should": entries}}


# --- 5 логических запросов ---
def q_core():
    """Ядро: СП-концепт + авиа-контекст."""
    sc_concepts = should([
        mp("abstract", "superconducting motor"), mp("abstract", "superconducting machine"),
        mp("abstract", "superconducting generator"), mp("abstract", "superconducting propulsion"),
        mp("abstract", "superconducting field winding"), mp("abstract", "high temperature superconducting"),
    ])
    avia = should([
        m("abstract", "aircraft"), m("abstract", "aero"), m("abstract", "flight"),
        m("abstract", "aviation"), m("abstract", "propulsion"),
    ])
    return {"bool": {"must": [sc_concepts, avia]}}


def q_cryo():
    """Широкий: крио-электрическая авиация."""
    cryo = should([
        mp("abstract", "cryogenic electric propulsion"), mp("abstract", "cryogenic electric motor"),
        mp("abstract", "cryogenic motor"), m("abstract", "cryogenic"),
    ])
    avia = should([
        m("abstract", "aircraft"), m("abstract", "aero"), m("abstract", "flight"), m("abstract", "aviation"),
    ])
    return {"bool": {"must": [cryo, avia]}}


def q_giants():
    """Авиа-гиганты + СП/крио."""
    giants = should([
        m("applicants", "Airbus"), m("applicants", "Rolls-Royce"), m("applicants", "Rolls Royce"),
        m("applicants", "Boeing"), m("applicants", "General Electric"), m("applicants", "Safran"),
        m("applicants", "Siemens"),
    ])
    sc = should([m("abstract", "superconducting"), m("abstract", "cryogenic")])
    return {"bool": {"must": [giants, sc]}}


def q_competitors():
    """Конкуренты (не-СП): крио-медь/PM + авиа."""
    comp = should([
        mp("abstract", "cryogenic motor"), mp("abstract", "cryo-cooled motor"),
        mp("abstract", "cryogenic aluminum"), mp("abstract", "permanent magnet motor"),
        mp("abstract", "permanent magnet machine"),
    ])
    avia = should([
        m("abstract", "aircraft"), m("abstract", "aero"), m("abstract", "flight"), m("abstract", "aviation"),
    ])
    return {"bool": {"must": [comp, avia]}}


def q_academy():
    """Академия/центры + СП/авиа."""
    acad = should([
        m("applicants", "Massachusetts Institute"), m("applicants", "University of Illinois"),
        m("applicants", "Florida State"), m("applicants", "Ohio State"),
        m("applicants", "Strathclyde"), m("applicants", "Harbin Institute"),
        m("applicants", "University of Cambridge"), m("applicants", "University of Oxford"),
    ])
    sc = should([m("abstract", "superconducting"), m("abstract", "aircraft"), m("abstract", "cryogenic")])
    return {"bool": {"must": [acad, sc]}}


QUERIES = [
    ("core", q_core(), "CORE"),
    ("cryo", q_cryo(), "CRYO"),
    ("giants", q_giants(), "GIANTS"),
    ("competitors", q_competitors(), "COMPET"),
    ("academy", q_academy(), "ACAD"),
]


def lens_search(query: dict, offset: int, size: int = 50) -> dict | None:
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


def in_window(rec: dict) -> bool:
    for f in ("publication_date", "priority_date", "filing_date"):
        y = (rec.get(f) or "")[:4]
        if y and 1990 <= int(y) <= 2026:
            return True
    return False


def main() -> None:
    grouped = defaultdict(dict)
    calls = 0
    print("=== Lens: СП-авиамоторы (кейс 008, план v2, лимит 15) ===", flush=True)
    for tag, query, group in QUERIES:
        print(f"\n=== {tag} (group={group}) ===", flush=True)
        got, offset, pages = 0, 0, 0
        # на каждый запрос максимум 3 страницы, но общий лимит 15 вызовов
        while got < 100 and offset < 200 and pages < 4 and calls < MAX_CALLS:
            resp = lens_search(query, offset)
            calls += 1
            print(f"  [вызов {calls}/{MAX_CALLS}] offset {offset}", flush=True)
            if not resp:
                break
            results = resp.get("data", []) or []
            total = resp.get("total", 0)
            if not results:
                break
            for p in results:
                rec = extract(p)
                if not rec:
                    continue
                if not in_window(rec):
                    continue
                rec["topic"] = tag
                grouped[group][rec["publication_number"]] = rec
            pages += 1
            offset += len(results)
            got = sum(1 for v in grouped[group].values() if v["topic"] == tag)
            print(f"    обработано {len(results)} (total={total}, {tag}-уник={got})", flush=True)
            time.sleep(3)
        print(f"  Итог {tag}: {got} уникальных", flush=True)

    # ---- сборка по файлам ----
    out_dir = PROJECT_ROOT / "data/raw/patents/cases"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ядро = CORE (+ CRYO со СП после проверки — пока просто CORE+CRYO)
    core = {}
    for g in ("CORE", "CRYO"):
        core.update(grouped[g])
    core_list = list(core.values())
    f1 = out_dir / "008_sc_aircraft.json"
    f1.write_text(json.dumps({
        "query": "SC aircraft motors (Lens, план v2 Q1 core + Q2 cryo)",
        "downloaded": time.strftime("%Y-%m-%d"),
        "window": "1990-2026",
        "source": "lens.org",
        "note": "ядро superconducting+aircraft + cryo-электрическая авиация, дедуп по publication_number",
        "patents": core_list,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    comp_list = list(grouped["COMPET"].values())
    f2 = out_dir / "008_sc_aircraft_competitors.json"
    f2.write_text(json.dumps({
        "query": "cryogenic motor / PM motor aircraft (Lens, Q4)",
        "downloaded": time.strftime("%Y-%m-%d"),
        "window": "1990-2026",
        "source": "lens.org",
        "note": "конкуренты не-СП: cryogenic motor, cryo-Al, PM motor + aircraft",
        "patents": comp_list,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    players = {}
    for g in ("GIANTS", "ACAD"):
        players.update(grouped[g])
    players_list = list(players.values())
    f3 = out_dir / "008_sc_aircraft_players.json"
    f3.write_text(json.dumps({
        "query": "aviation giants + academy + SC/cryo (Lens, Q3+Q5)",
        "downloaded": time.strftime("%Y-%m-%d"),
        "window": "1990-2026",
        "source": "lens.org",
        "note": "assignee-анализ: авиа-гиганты и академия с СП/крио",
        "patents": players_list,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- паспорт ----
    passport = PROJECT_ROOT / "case_studies/008_sc_aircraft_motors/signals/data_passports/patents_sc_aircraft.md"
    passport.parent.mkdir(parents=True, exist_ok=True)
    passport.write_text(
        "# Паспорт: патентные базы СП-авиамоторов (кейс 008)\n\n"
        f"- **Файлы:** `008_sc_aircraft.json` ({len(core_list)}), "
        f"`008_sc_aircraft_competitors.json` ({len(comp_list)}), "
        f"`008_sc_aircraft_players.json` ({len(players_list)})\n"
        f"- **Скрипт:** `src/lens_sc_aircraft.py`\n"
        f"- **Запросы:** 5 логических (core/cryo/giants/competitors/academy), окно 1990-2026\n"
        f"- **Дата:** {time.strftime('%Y-%m-%d')}\n"
        f"- **API-вызовов:** {calls} (лимит 15)\n"
        f"- **Поля:** publication_number, title, abstract, assignee, priority/filing/publication_date, url\n"
        f"- **Бюджет:** Lens ~481 до, лог results/runtime/api_budget.md\n",
        encoding="utf-8",
    )

    # ---- api_budget ----
    budget_log = PROJECT_ROOT / "results/runtime/api_budget.md"
    if budget_log.exists():
        with budget_log.open("a", encoding="utf-8") as f:
            f.write(f"\n| 2026-09-07 | 008 Lens выполнен (план v2, {calls} вызовов) | {calls} | ~481→~{481-calls} | Да |\n")

    print(f"\nСохранено: {f1} ({len(core_list)}), {f2} ({len(comp_list)}), {f3} ({len(players_list)})")
    print(f"API-вызовов: {calls}/{MAX_CALLS}")


if __name__ == "__main__":
    main()
