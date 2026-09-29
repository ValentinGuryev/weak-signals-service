#!/usr/bin/env python3
"""Lens-докачка патентов SMES и BESS (конкурент) за 2000-2020.

Стратегия (lens_strategy.md, санкция команды):
  S1: title:"SMES"                    2000-2020
  S2: title:"superconducting magnetic energy storage"  2000-2020
  B1: title:"battery energy storage"  2000-2020
  B2: title:"lithium-ion battery" + energy storage      2000-2020
  B3: title:"supercapacitor"/"ultracapacitor" + storage 2000-2020
Выход: data/raw/patents/topics/smes_lens.json, bess_lens.json
"""
from __future__ import annotations

import json
import os
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
    print("Нет LENS_TOKEN!")
    sys.exit(1)

# (название, ES-query-bool, target)
def title_phrase(phrase: str) -> dict:
    return {"bool": {"must": [{"match_phrase": {"title": phrase}}]}}

def title_phrase_and(phrase: str, extra: str) -> dict:
    return {"bool": {"must": [
        {"match_phrase": {"title": phrase}},
        {"match_phrase": {"title": extra}},
    ]}}

QUERIES = {
    # SMES
    "smes_abbr": (title_phrase("SMES"), 120, "SMES"),
    "smes_full": (title_phrase("superconducting magnetic energy storage"), 100, "SMES"),
    # BESS / конкуренты
    "bess": (title_phrase("battery energy storage"), 150, "BESS"),
    "liion_storage": (title_phrase_and("lithium-ion battery", "energy storage"), 80, "BESS"),
    "supercap": ({"bool": {"must": [
        {"bool": {"should": [
            {"match_phrase": {"title": "supercapacitor"}},
            {"match_phrase": {"title": "ultracapacitor"}},
        ]}},
        {"match_phrase": {"title": "energy storage"}},
    ]}}, 60, "BESS"),
}

# Окно дат
DATE_RANGE = {"gte": "2000-01-01", "lte": "2020-12-31"}


def lens_search(query: dict, offset: int, size: int = 50) -> dict | None:
    payload = {
        "query": query, "size": size, "offset": offset,
        "include": ["biblio.publication_reference", "biblio.application_reference",
                    "biblio.priority_claims", "biblio.invention_title", "biblio.parties", "abstract"],
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(LENS_API, data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            print(f"[lens] HTTP {e.code}")
            if e.code == 429:
                time.sleep(20)
            else:
                return None
        except Exception as e:
            print(f"[lens] ошибка: {str(e)[:80]}")
            if attempt == 2:
                return None
            time.sleep(5)
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
        "abstract": abstract,
        "assignee": ", ".join(applicants[:3]) if applicants else "",
        "priority_date": (biblio.get("priority_claims", {}).get("earliest_claim", {}).get("date") or "")[:10],
        "filing_date": (biblio.get("application_reference", {}).get("date") or "")[:10],
        "url": f"https://www.lens.org/lens/patent/{lens_id}" if lens_id else "",
        "topic": "",
    }


def in_window(rec: dict) -> bool:
    """Фильтр окна 2000-2020 по priority/filing/publication date."""
    for f in ("priority_date", "filing_date"):
        y = (rec.get(f) or "")[:4]
        if y and 2000 <= int(y) <= 2020:
            return True
    return False


def main() -> None:
    grouped = {"SMES": {}, "BESS": {}}
    for tag, (query, target, group) in QUERIES.items():
        print(f"\n=== {tag} (ищу до {target}) ===")
        got, offset, pages = 0, 0, 0
        while got < target and offset < 300 and pages < 5:
            resp = lens_search(query, offset)
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
                got += 1
            pages += 1
            offset += len(results)
            print(f"  offset {offset}: +{len(results)} (total={total}, в окне накоплено {got})")
            time.sleep(3)
        print(f"  Итог {tag}: {got} в окне 2000-2020")

    # Сохранение
    out_dir = PROJECT_ROOT / "data/raw/patents/topics"
    for group, pats in grouped.items():
        plist = list(pats.values())
        fname = "smes_lens.json" if group == "SMES" else "bess_lens.json"
        (out_dir / fname).write_text(json.dumps({
            "query": f"{group} patents 2000-2020 (Lens)",
            "downloaded": time.strftime("%Y-%m-%d"),
            "window": "2000-2020",
            "source": "lens.org",
            "patents": plist,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n{group}: {len(plist)} уникальных -> {out_dir / fname}")


if __name__ == "__main__":
    main()
