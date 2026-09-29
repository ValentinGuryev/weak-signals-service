#!/usr/bin/env python3
"""Lens: патентная база кейса MgB2-МРТ (калибровочный «УСПЕХ», кейс ещё не начат).

Логика сигнала (термины-синонимы через OR!):
  A1 MgB2 AND МРТ                  — ядро: патенты на MgB2-МРТ
  A2 MgB2 AND (wire|coil|lena) AND magnet — магнитостроение
  A3 MgB2 AND (cryocooler|без гелия) AND МРТ — «сухая» тема (без жидкого гелия)
  A4 игроки (Paramed/ASG/Columbus/Hyper Tech/MetOx) AND MgB2 — терминология игроков
  A5 MgB2 в TITLE (широкий фон)   — весь патентный ландшафт MgB2
  A6 MgB2 AND magnet (без МРТ)    — фон магнитов
Выход: data/raw/patents/cases/mgb2_mri.json
"""
from __future__ import annotations
import json, os, re, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = ""
env = ROOT / ".env"
if env.exists():
    for line in env.read_text().splitlines():
        if line.startswith("LENS_TOKEN="):
            TOKEN = line.split("=", 1)[1].strip(); break
if not TOKEN:
    print("Нет LENS_TOKEN!"); sys.exit(1)

API = "https://api.lens.org/patent/search"
INC = ["biblio.publication_reference","biblio.application_reference","biblio.priority_claims",
       "biblio.invention_title","biblio.parties","biblio.cited_by","abstract"]

def mp(f, p): return {"match_phrase": {f: p}}

def call(esq, size=40):
    body = {"query": esq, "include": INC, "size": size}
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=90)
    hdrs = {k: v for k, v in r.headers.items() if "x-rate-limit" in k.lower()}
    return json.loads(r.read().decode()), hdrs

def _txt(x):
    if not x: return ""
    if isinstance(x, str): return x
    if isinstance(x, list): return " ".join(_txt(i) for i in x)
    if isinstance(x, dict): return _txt(x.get("text") or x.get("value") or "")
    return str(x)

def _num(p):
    a = p.get("biblio", {}).get("application_reference", {})
    if isinstance(a, list): a = a[0] if a else {}
    if isinstance(a, dict) and a.get("doc_number"): return f"{a.get('jurisdiction','')}_{a.get('doc_number')}"
    pc = p.get("biblio", {}).get("priority_claims", {})
    if isinstance(pc, dict):
        for c in pc.get("claims", []) or []:
            if isinstance(c, dict) and c.get("doc_number"): return f"{c.get('jurisdiction','')}_{c.get('doc_number')}"
    return ""

def _yr(p):
    pc = p.get("biblio", {}).get("priority_claims", {})
    if isinstance(pc, dict):
        dt = (pc.get("earliest_claim") or {}).get("date") if isinstance(pc.get("earliest_claim"), dict) else None
        if isinstance(dt, str) and dt[:4].isdigit(): return int(dt[:4])
    return None

def rec(p, tag):
    pa = p.get("biblio", {}).get("parties", {})
    return {"source": "lens", "query": tag, "publication_number": _num(p),
            "title": _txt(p.get("biblio", {}).get("invention_title")),
            "abstract": _txt(p.get("abstract")),
            "assignee": "; ".join(_txt(a.get("extracted_name", {}).get("value")) for a in (pa.get("applicants") or [])[:4]),
            "inventors": "; ".join(_txt(i.get("extracted_name", {}).get("value")) for i in (pa.get("inventors") or [])[:4]),
            "cited_by": (p.get("biblio", {}).get("cited_by", {}) or {}).get("count"),
            "year": _yr(p)}

def OR(terms):
    """terms: список (поле, фраза) -> bool should"""
    return {"bool": {"should": [mp(f, t) for f, t in terms], "minimum_should_match": 1}}

MGB2 = [("title", "MgB2"), ("abstract", "MgB2"), ("title", "Mg-B2"), ("abstract", "Mg-B2"),
        ("title", "magnesium diboride"), ("abstract", "magnesium diboride"),
        ("title", "magnesium-diboride"), ("abstract", "magnesium-diboride")]
MRI = [("title", "MRI"), ("abstract", "MRI"), ("title", "magnetic resonance imaging"), ("abstract", "magnetic resonance imaging"),
       ("title", "magnetic resonance"), ("abstract", "magnetic resonance")]
WIRE = [("title", "wire"), ("abstract", "wire"), ("title", "coil"), ("abstract", "coil"),
        ("title", "conductor"), ("abstract", "conductor"), ("title", "tape"), ("abstract", "tape")]
MAGNET = [("title", "magnet"), ("abstract", "magnet")]
CRYO = [("title", "cryocooler"), ("abstract", "cryocooler"), ("title", "cryogen free"), ("abstract", "cryogen free"),
        ("title", "cryogen-free"), ("abstract", "cryogen-free"), ("title", "dry magnet"), ("abstract", "dry magnet"),
        ("title", "helium-free"), ("abstract", "helium-free"), ("title", "no liquid helium"), ("abstract", "no liquid helium")]

QUERIES = {
  "A1_mgb2_and_mri": {"bool": {"must": [OR(MGB2), OR(MRI)]}},
  "A2_mgb2_wire_and_magnet": {"bool": {"must": [OR(MGB2), OR(WIRE), OR(MAGNET)]}},
  "A3_mgb2_cryogenfree_mri": {"bool": {"must": [OR(MGB2), OR(CRYO), OR(MRI)]}},
  "A4_players_mgb2": {"bool": {"must": [OR([("abstract", "Paramed Medical"), ("abstract", "ASG Superconductors"),
                                           ("abstract", "Columbus Superconductors"), ("abstract", "Hyper Tech"),
                                           ("abstract", "MetOx")]), OR(MGB2)]}},
  "A5_mgb2_title_all": OR([("title", "MgB2"), ("title", "Mg-B2"), ("title", "magnesium diboride"), ("title", "magnesium-diboride")]),
  "A6_mgb2_magnet": {"bool": {"must": [OR(MGB2), OR(MAGNET)]}},
}

def main():
    rows = []; last = {}
    sizes = {"A5_mgb2_title_all": 100}
    for i, (tag, q) in enumerate(QUERIES.items(), 1):
        try:
            data, hdrs = call(q, sizes.get(tag, 40))
        except urllib.error.HTTPError as e:
            print(f"[{i}/{len(QUERIES)}] {tag}: HTTP {e.code}")
            if e.code == 429: time.sleep(25)
            continue
        except Exception as e:
            print(f"[{i}/{len(QUERIES)}] {tag}: ERR {str(e)[:80]}"); continue
        tot = data.get("total", 0); rs = [rec(p, tag) for p in (data.get("data") or data.get("results") or [])]
        rows += rs; last = hdrs
        print(f"[{i}/{len(QUERIES)}] {tag}: total={tot}, +{len(rs)}")
        time.sleep(0.9)
    seen = set(); uniq = []
    for r in rows:
        k = r["publication_number"] or f"T:{str(r['title'])[:40].lower()}"
        if k in seen: continue
        seen.add(k); uniq.append(r)
    res = {"case": "mgb2_mri", "date": "2026-09-11", "raw": len(rows), "uniq": len(uniq),
           "patents": uniq, "limits": last}
    outp = ROOT / "data/raw/patents/cases/mgb2_mri.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nИТОГ: raw={len(rows)}, uniq={len(uniq)} → {outp}")
    for k, v in last.items(): print(f"  {k}: {v}")
    with (ROOT / "results/runtime/api_budget.md").open("a") as f:
        f.write(f"\n| 2026-09-11 | Кейс MgB2-МРТ: Lens патенты (lens_mgb2_mri.py, {len(QUERIES)} лог. запросов; "
                f"{len(rows)} raw / {len(uniq)} уник.) | Lens.org | {len(QUERIES)} | Да (команда «Давай про МРТ на MgB2» 2026-09-11) |\n")

if __name__ == "__main__":
    main()