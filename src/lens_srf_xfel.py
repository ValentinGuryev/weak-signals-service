#!/usr/bin/env python3
"""Кейс 011 SRF: точечный патентный чек XFEL/DESY (разрешение команды).

Вопрос: есть ли патенты European XFEL / DESY-семейства / FEL-полостей под другими терминами?
Запросы (3):
  X1 "European XFEL" | "XFEL" | "X-ray free-electron laser" (+ cavity/accelerator)
  X2 "DESY" (+ superconducting | cavity | linac)
  X3 "free electron laser" AND "superconducting cavity" | "superconducting RF"
Выход: data/raw/patents/cases/011_srf_xfel_check.json
"""
from __future__ import annotations
import json, os, sys, time, urllib.request, urllib.error
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

def call(esq, size=25):
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
            "assignee":"; ".join(_txt(a.get("extracted_name",{}).get("value")) for a in (pa.get("applicants") or [])[:5]),
            "inventors":"; ".join(_txt(i.get("extracted_name",{}).get("value")) for i in (pa.get("inventors") or [])[:4]),
            "year":_yr(p)}

QUERIES = {
  "X1_xfel": {"bool":{"should":[mp("title","XFEL"),mp("abstract","XFEL"),
        mp("title","European XFEL"),mp("abstract","European XFEL"),
        mp("title","X-ray free electron laser"),mp("abstract","X-ray free-electron laser")]}},
  "X2_desy": {"bool":{"must":[{"bool":{"should":[mp("abstract","DESY"),mp("title","DESY")]}},
     {"bool":{"should":[mp("abstract","cavity"),mp("abstract","superconducting"),mp("abstract","linac"),
                        mp("abstract","accelerator")],"minimum_should_match":1}}]}},
  "X3_fel_sc_cavity": {"bool":{"must":[{"bool":{"should":[mp("abstract","free electron laser"),mp("abstract","free-electron laser")]}},
     {"bool":{"should":[mp("abstract","superconducting cavity"),mp("abstract","superconducting RF"),
                        mp("abstract","SRF cavity")],"minimum_should_match":1}}]}},
}

def main():
    rows=[]; last={}
    for i,(tag,q) in enumerate(QUERIES.items(),1):
        try:
            data, hdrs = call(q, 25)
        except urllib.error.HTTPError as e:
            print(f"[{i}/3] {tag}: HTTP {e.code}")
            if e.code==429: time.sleep(25)
            continue
        except Exception as e:
            print(f"[{i}/3] {tag}: ERR {str(e)[:80]}"); continue
        tot=data.get("total",0); rs=[rec(p,tag) for p in (data.get("data") or data.get("results") or [])]
        rows+=rs; last=hdrs
        print(f"[{i}/3] {tag}: total={tot}, +{len(rs)}")
        time.sleep(0.8)
    res={"case":"011_srf_cavities","xfel_check":True,"date":"2026-09-11",
         "raw":len(rows), "patents":rows, "limits":last}
    outp=ROOT/"data/raw/patents/cases/011_srf_xfel_check.json"
    outp.write_text(json.dumps(res,ensure_ascii=False,indent=1),encoding="utf-8")
    print(f"\nИТОГ: {len(rows)} записей → {outp}")
    for k,v in last.items(): print(f"  {k}: {v}")
    with (ROOT/"results/runtime/api_budget.md").open("a") as f:
        f.write(f"\n| 2026-09-11 | Кейс 011 SRF: точечный чек XFEL/DESY (lens_srf_xfel.py, 3 запроса) | Lens.org | 3 | Да (команда «да запускай» 2026-09-11) |\n")

if __name__=="__main__": main()