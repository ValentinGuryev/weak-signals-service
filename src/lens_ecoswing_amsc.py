#!/usr/bin/env python3
"""Точечная проверка AMSC + расширение ядра патентной базы кейса 010 (EcoSwing).

Пакет 1 (AMSC, ~6 запросов):
  AM1 "American Superconductor" (title|abstract) — алиас компании
  AM2 "AMSC" + wind/turbine (title|abstract)
  AM3 "superconductive wind turbine" (старое написание! в 70-х было superconductive)
  AM4 "superconductive wind" в любой позиции
  AM5 "HTS wind" + generator/coil (широкая компонентная)
Выход: data/raw/patents/cases/010_sc_wind_amsc.json
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOKEN = os.environ.get("LENS_TOKEN", "")
if not TOKEN:
    for line in (PROJECT_ROOT / ".env").read_text().splitlines():
        if line.startswith("LENS_TOKEN="):
            TOKEN = line.split("=", 1)[1].strip(); break
if not TOKEN:
    print("Нет LENS_TOKEN!"); sys.exit(1)

LENS_API = "https://api.lens.org/patent/search"
INCLUDE = ["biblio.publication_reference", "biblio.application_reference", "biblio.priority_claims",
           "biblio.invention_title", "biblio.parties", "biblio.cited_by", "abstract"]


def mp(field, phrase): return {"match_phrase": {field: phrase}}
def m(field, term): return {"match": {field: term}}


def search(esq, size=25, offset=0):
    body = {"query": esq, "include": INCLUDE, "size": size, "offset": offset}
    req = urllib.request.Request(LENS_API, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        headers = {k: v for k, v in r.headers.items() if "x-rate-limit" in k.lower()}
        return json.loads(r.read().decode()), headers


def _text(x):
    if x is None: return ""
    if isinstance(x, str): return x
    if isinstance(x, list): return " ".join(_text(i) for i in x)
    if isinstance(x, dict): return _text(x.get("text") or x.get("value") or "")
    return str(x)


def _pubnum(pat):
    app = pat.get("biblio", {}).get("application_reference", {})
    if isinstance(app, list): app = app[0] if app else {}
    if isinstance(app, dict) and app.get("doc_number"):
        return f"{app.get('jurisdiction','')}_{app.get('doc_number')}"
    return ""


def _year(pat):
    pc = pat.get("biblio", {}).get("priority_claims", {})
    if isinstance(pc, dict):
        dt = (pc.get("earliest_claim") or {}).get("date") if isinstance(pc.get("earliest_claim"), dict) else None
        if dt and isinstance(dt, str): return int(dt[:4])
        for c in pc.get("claims", []) or []:
            if isinstance(c, dict) and c.get("date"): return int(c["date"][:4])
    return None


def rec(pat, tag):
    parties = pat.get("biblio", {}).get("parties", {})
    applicants = "; ".join(_text(a.get("extracted_name", {}).get("value")) for a in (parties.get("applicants") or [])[:4])
    inv = "; ".join(_text(i.get("extracted_name", {}).get("value")) for i in (parties.get("inventors") or [])[:4])
    num = _pubnum(pat)
    return {"source": "lens", "query": tag, "publication_number": num,
            "title": _text(pat.get("biblio", {}).get("invention_title")),
            "abstract": _text(pat.get("abstract")), "assignee": applicants, "inventors": inv,
            "cited_by": (pat.get("biblio", {}).get("cited_by", {}) or {}).get("count"),
            "year": _year(pat)}


QUERIES = {
    "AM1_american_superconductor": {"bool": {"should": [
        mp("title", "American Superconductor"), mp("abstract", "American Superconductor")]}},
    "AM2_amsc_wind": {"bool": {"must": [m("title", "AMSC")],
                                "should": [mp("title", "wind"), mp("abstract", "wind")],
                                "minimum_should_match": 1}},
    "AM3_superconductive_wind_turbine": {"bool": {"should": [
        mp("title", "superconductive wind turbine"), mp("abstract", "superconductive wind turbine")]}},
    "AM4_superconductive_wind": {"bool": {"should": [
        mp("title", "superconductive wind"), mp("abstract", "superconductive wind")]}},
    "AM5_hts_wind_generator": {"bool": {"should": [
        mp("title", "HTS wind generator"), mp("abstract", "HTS wind generator")]}},
    "AM6_sc_wind_energy": {"bool": {"should": [
        mp("title", "superconducting wind energy"), mp("abstract", "superconducting wind energy"),
        mp("title", "superconducting wind power"), mp("abstract", "superconducting wind power")]}},
}


def main():
    all_rows = []
    limits = []
    for tag, esq in QUERIES.items():
        try:
            data, hdrs = search(esq, size=25)
        except Exception as e:  # noqa: BLE001
            print(f"--- {tag}: ERR {str(e)[:90]}")
            continue
        total = data.get("total", 0)
        rows = [rec(p, tag) for p in (data.get("data") or data.get("results") or [])]
        all_rows.extend(rows)
        print(f"--- {tag}: total={total}, получено={len(rows)}")
        limits.append({"query": tag, "headers": hdrs})
        time.sleep(0.8)

    # дедуп по публикации
    seen, uniq = set(), []
    for r in all_rows:
        key = r["publication_number"] or f"T:{r['title'][:40].lower()}"
        if key in seen: continue
        seen.add(key); uniq.append(r)

    out = PROJECT_ROOT / "data/raw/patents/cases/010_sc_wind_amsc.json"
    out.write_text(json.dumps({"case": "010", "downloaded": "2026-09-11",
                               "raw": len(all_rows), "uniq": len(uniq),
                               "patents": uniq}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nИТОГ: raw={len(all_rows)}, uniq={len(uniq)} → {out}")
    if limits:
        last = limits[-1]["headers"]
        for k, v in last.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()