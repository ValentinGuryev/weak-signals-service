#!/usr/bin/env python3
"""Lens: патентная база кейса HTS-фильтры (сверхпроводящие ВЧ-фильтры для телекома/космоса).

Термины (Р1-урок: синонимия!):
  A1 "superconducting filter" | "HTS filter" | "high temperature superconducting filter"
  A2 "YBCO filter" | "superconducting microwave filter" | "superconducting bandpass" | "superconducting preselect"
  A3 "superconducting power extractor" | "superconducting duplexer" (старые телеком-термины)
  B1 игроки (термин-проверка): Tsinghua / Zongyi / Tianjin Hi-Tech / Conductus по тексту
Выход: data/raw/patents/cases/hts_filters.json
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
            TOKEN = line.split("=",1)[1].strip(); break
if not TOKEN:
    print("Нет LENS_TOKEN!"); sys.exit(1)

API = "https://api.lens.org/patent/search"
INC = ["biblio.publication_reference","biblio.application_reference","biblio.priority_claims",
       "biblio.invention_title","biblio.parties","biblio.cited_by","abstract"]

def mp(f,p): return {"match_phrase": {f: p}}
def m(f,t): return {"match": {f: t}}

def call(esq, size=40):
    body = {"query": esq, "include": INC, "size": size}
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=90)
    hdrs = {k:v for k,v in r.headers.items() if "x-rate-limit" in k.lower()}
    return json.loads(r.read().decode()), hdrs

def _txt(x):
    if not x: return ""
    if isinstance(x,str): return x
    if isinstance(x,list): return " ".join(_txt(i) for i in x)
    if isinstance(x,dict): return _txt(x.get("text") or x.get("value") or "")
    return str(x)

def _num(p):
    a=p.get("biblio",{}).get("application_reference",{})
    if isinstance(a,list): a=a[0] if a else {}
    if isinstance(a,dict) and a.get("doc_number"): return f"{a.get('jurisdiction','')}_{a.get('doc_number')}"
    pc=p.get("biblio",{}).get("priority_claims",{})
    if isinstance(pc,dict):
        for c in pc.get("claims",[]) or []:
            if isinstance(c,dict) and c.get("doc_number"): return f"{c.get('jurisdiction','')}_{c.get('doc_number')}"
    return ""

def _yr(p):
    pc=p.get("biblio",{}).get("priority_claims",{})
    if isinstance(pc,dict):
        dt=(pc.get("earliest_claim") or {}).get("date") if isinstance(pc.get("earliest_claim"),dict) else None
        if isinstance(dt,str) and dt[:4].isdigit(): return int(dt[:4])
    return None

def rec(p, tag):
    pa=p.get("biblio",{}).get("parties",{})
    return {"source":"lens","query":tag,"publication_number":_num(p),
            "title":_txt(p.get("biblio",{}).get("invention_title")),
            "abstract":_txt(p.get("abstract")),
            "assignee":"; ".join(_txt(a.get("extracted_name",{}).get("value")) for a in (pa.get("applicants") or [])[:4]),
            "inventors":"; ".join(_txt(i.get("extracted_name",{}).get("value")) for i in (pa.get("inventors") or [])[:4]),
            "cited_by":(p.get("biblio",{}).get("cited_by",{}) or {}).get("count"),
            "year":_yr(p)}

QUERIES = {
  "A1_sc_hts_filter": {"bool":{"should":[mp("title","superconducting filter"),mp("abstract","superconducting filter"),
        mp("title","HTS filter"),mp("abstract","HTS filter"),
        mp("title","high temperature superconducting filter"),mp("abstract","high temperature superconducting filter")]}},
  "A2_ybco_mw_filter": {"bool":{"should":[mp("title","YBCO filter"),mp("abstract","YBCO filter"),
        mp("title","superconducting microwave filter"),mp("abstract","superconducting microwave filter"),
        mp("title","superconducting bandpass"),mp("abstract","superconducting bandpass"),
        mp("title","superconducting preselect"),mp("abstract","superconducting preselect"),
        mp("title","superconducting duplexer"),mp("abstract","superconducting duplexer")]}},
  "A3_power_extractor": {"bool":{"should":[mp("title","superconducting power extractor"),mp("abstract","superconducting power extractor"),
        mp("title","power extraction filter superconducting"),mp("abstract","power extraction filter superconducting"),
        mp("title","HTS receive filter"),mp("abstract","HTS receive filter")]}},
  "B1_players": {"bool":{"must":[{"bool":{"should":[mp("title","superconducting"),mp("abstract","superconducting"),mp("title","HTS"),mp("abstract","HTS")]}}],
        "should":[mp("abstract","Tsinghua"),mp("abstract","Zongyi"),mp("abstract","Tianjin"),mp("abstract","Conductus"),
                  mp("abstract","STI"),mp("abstract","preselect filter")],"minimum_should_match":1}},
}

def main():
    rows=[]; last={}
    for i,(tag,q) in enumerate(QUERIES.items(),1):
        try:
            data, hdrs = call(q, 40)
        except urllib.error.HTTPError as e:
            print(f"[{i}/4] {tag}: HTTP {e.code}")
            if e.code==429: time.sleep(25)
            continue
        except Exception as e:
            print(f"[{i}/4] {tag}: ERR {str(e)[:80]}"); continue
        tot=data.get("total",0); rs=[rec(p,tag) for p in (data.get("data") or data.get("results") or [])]
        rows+=rs; last=hdrs
        print(f"[{i}/4] {tag}: total={tot}, +{len(rs)}")
        time.sleep(0.8)
    # дедуп
    seen=set(); uniq=[]
    for r in rows:
        k=r["publication_number"] or f"T:{str(r['title'])[:40].lower()}"
        if k in seen: continue
        seen.add(k); uniq.append(r)
    res={"case":"hts_filters","date":"2026-09-11","raw":len(rows),"uniq":len(uniq),
         "patents":uniq,"limits":last}
    outp=ROOT/"data/raw/patents/cases/hts_filters.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(res,ensure_ascii=False,indent=1),encoding="utf-8")
    print(f"\nИТОГ: raw={len(rows)}, uniq={len(uniq)} → {outp}")
    for k,v in last.items(): print(f"  {k}: {v}")
    with (ROOT/"results/runtime/api_budget.md").open("a") as f:
        f.write(f"\n| 2026-09-11 | Кейс HTS-фильтры: Lens патенты (lens_hts_filters.py, 4 лог. запроса; {len(rows)} raw / {len(uniq)} уник.) | Lens.org | 4 | Да (явная команда «сделать патентный сигнал») |\n")

if __name__=="__main__": main()