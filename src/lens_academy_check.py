#!/usr/bin/env python3
"""Lens: проверка патентования академии для кейса 008 (3 запроса, санкция).

Гипотеза: западная/японская академия публикует (Strathclyde 72, Kyushu 73, Tokyo 43,
Cambridge 47, Florida State 35, Illinois-CHEETA 29 в корпусе 008), но НЕ поймана в патентной базе.
Вопрос: патентуют ли университеты авиа-СП (или патенты ушли подрядчикам / их нет)?

Запросы:
  L1 UK-академия: Strathclyde/Glasgow/Cambridge/Bath/Manchester + superconducting/motor/aircraft
  L2 US-академия: Florida State/Ohio State/Illinois/MIT + superconducting motor/aircraft
  L3 JP-академия: Kyushu/Tokyo/Kyoto + superconducting motor

Выход: results/case_signals/lens_academy_check.json (временный, потом в data/raw).
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
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
DATE_RANGE = {"gte": "1990-01-01", "lte": "2026-12-31"}


def mp(field, phrase):
    return {"match_phrase": {field: phrase}}


def m(field, term):
    return {"match": {field: term}}


def should(entries):
    return {"bool": {"should": entries}}


def q_uk():
    return {"bool": {"must": [
        should([m("applicants", "Strathclyde"), m("applicants", "Glasgow"),
                m("applicants", "Cambridge"), m("applicants", "Bath"),
                m("applicants", "Manchester"), m("applicants", "Nottingham")]),
        should([m("abstract", "superconducting"), m("abstract", "cryogenic")]),
        should([m("abstract", "motor"), m("abstract", "machine"), m("abstract", "aircraft")]),
    ]}}


def q_us():
    return {"bool": {"must": [
        should([m("applicants", "Florida State"), m("applicants", "Ohio State"),
                m("applicants", "Illinois"), m("applicants", "Massachusetts"),
                m("applicants", "Virginia Tech"), m("applicants", "Purdue")]),
        should([m("abstract", "superconducting"), m("abstract", "cryogenic")]),
        should([m("abstract", "motor"), m("abstract", "machine"), m("abstract", "aircraft")]),
    ]}}


def q_jp():
    return {"bool": {"must": [
        should([m("applicants", "Kyushu"), m("applicants", "Tokyo"),
                m("applicants", "Kyoto"), m("applicants", "Tohoku"),
                m("applicants", "Nagoya")]),
        should([m("abstract", "superconducting"), m("abstract", "cryogenic"), mp("abstract", "超電導")]),
        should([m("abstract", "motor"), m("abstract", "machine"), m("abstract", "aircraft"), mp("abstract", "モータ")]),
    ]}}


QUERIES = [
    ("uk_academy", q_uk, "UK (Strathclyde/Glasgow/Cambridge/Bath/Manchester)"),
    ("us_academy", q_us, "US (Florida State/Ohio State/Illinois/MIT)"),
    ("jp_academy", q_jp, "JP (Kyushu/Tokyo/Kyoto/Tohoku/Nagoya)"),
]


def lens_search(query, offset, size=50):
    payload = {
        "query": query, "size": size, "offset": offset,
        "date_filter": {"field": "publication_date", "from": DATE_RANGE["gte"], "to": DATE_RANGE["lte"]},
        "include": ["biblio.publication_reference", "biblio.priority_claims",
                    "biblio.invention_title", "biblio.parties", "abstract"],
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
    applicants = []
    for ap in biblio.get("parties", {}).get("applicants", []):
        name = ap.get("extracted_name", {}).get("value", "")
        if name:
            applicants.append(name)
    return {
        "publication_number": doc_key,
        "title": title,
        "assignee": ", ".join(applicants[:4]) if applicants else "",
        "publication_date": pdate[:10],
        "topic": "",
    }


def main():
    calls = 0
    result = {}
    print("=== Lens: проверка академии (кейс 008) ===", flush=True)
    for tag, query_fn, label in QUERIES:
        query = query_fn()
        print(f"\n=== {tag} ({label}) ===", flush=True)
        resp = lens_search(query, 0)
        calls += 1
        if not resp:
            print("  ошибка/нет ответа", flush=True)
            result[tag] = {"error": True}
            continue
        total = resp.get("total", 0)
        results = resp.get("data", []) or []
        recs = []
        for p in results:
            rec = extract(p)
            if rec:
                recs.append(rec)
        print(f"  total={total}, получено {len(recs)}", flush=True)
        result[tag] = {"total": total, "works": recs}
        time.sleep(3)

    # Сохранить (данные — в data/raw, вне git)
    out_dir = PROJECT_ROOT / "data/raw/openalex"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "008_lens_academy_check.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {out}")
    print(f"Вызовов: {calls}")

    # Лог бюджета
    budget_log = PROJECT_ROOT / "results/runtime/api_budget.md"
    if budget_log.exists():
        with budget_log.open("a", encoding="utf-8") as f:
            f.write(f"\n| 2026-09-08 | 008 Lens академия выполнен | {calls} | ~457→~{457-calls} | Да |\n")


if __name__ == "__main__":
    main()
