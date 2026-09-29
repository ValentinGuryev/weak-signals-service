#!/usr/bin/env python3
"""Дособор патентов HTS-фильтры (пагинация A1/A2; ~5 запросов).
"""
from __future__ import annotations
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = ""
for line in (ROOT/".env").read_text().splitlines():
    if line.startswith("LENS_TOKEN="):
        TOKEN = line.split("=",1)[1].strip(); break
if not TOKEN: print("Нет LENS_TOKEN!"); sys.exit(1)

API="https://api.lens.org/patent/search"
INC=["biblio.publication_reference","biblio.application_reference","biblio.priority_claims",
     "biblio.invention_title","biblio.parties","biblio.cited_by","abstract"]
def mp(f,p): return {"match_phrase":{f:p}}
def call(esq,off,size=40):
    body={"query":esq,"include":INC,"size":size,"offset":off}
    req=urllib.request.Request(API,data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {TOKEN}","Content-Type":"application/json"})
    r=urllib.request.urlopen(req,timeout=90)
    hdrs={k:v for k,v in r.headers.items() if "x-rate-limit" in k.lower()}
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
def rec(p,tag):
    pa=p.get("biblio",{}).get("parties",{})
    return {"source":"lens","query":tag,"publication_number":_num(p),
            "title":_txt(p.get("biblio",{}).get("invention_title")),
            "abstract":_txt(p.get("abstract")),
            "assignee":"; ".join(_txt(a.get("extracted_name",{}).get("value")) for a in (pa.get("applicants") or [])[:4]),
            "year":_yr(p)}

A1={"bool":{"should":[mp("title","superconducting filter"),mp("abstract","superconducting filter"),
      mp("title","HTS filter"),mp("abstract","HTS filter"),
      mp("title","high temperature superconducting filter"),mp("abstract","high temperature superconducting filter")]}}
A2={"bool":{"should":[mp("title","YBCO filter"),mp("abstract","YBCO filter"),
      mp("title","superconducting microwave filter"),mp("abstract","superconducting microwave filter")]}}

def main():
    rows=[]; last={}
    plan=[("A1_p2",A1,40),("A1_p3",A1,80),("A1_p4",A1,120),("A1_p5",A1,160),("A2_p2",A2,40)]
    for tag,q,off in plan:
        try:
            data,hdrs=call(q,off,40)
        except urllib.error.HTTPError as e:
            print(f"{tag}: HTTP {e.code}"); time.sleep(20 if e.code==429 else 0); continue
        except Exception as e:
            print(f"{tag}: ERR {str(e)[:70]}"); continue
        rs=[rec(p,tag) for p in (data.get("data") or data.get("results") or [])]
        rows+=rs; last=hdrs
        print(f"{tag}: total={data.get('total',0)}, +{len(rs)}")
        time.sleep(0.8)
    # merge в основной файл
    main_file=ROOT/"data/raw/patents/cases/hts_filters.json"
    d=json.loads(main_file.read_text(encoding="utf-8"))
    have={p["publication_number"] for p in d["patents"]}
    new=0
    for r in rows:
        if r["publication_number"] in have: continue
        d["patents"].append(r); have.add(r["publication_number"]); new+=1
    d["raw"]=len(d["patents"])  # уник
    d["limits"]=last
    d["topup"]="2026-09-11 пагинация A1 p2-p5, A2 p2"
    main_file.write_text(json.dumps(d,ensure_ascii=False,indent=1),encoding="utf-8")
    print(f"\nдобавлено новых: {new}; всего в базе: {len(d['patents'])}")
    for k,v in last.items(): print(f"  {k}: {v}")
    with (ROOT/"results/runtime/api_budget.md").open("a") as f:
        f.write(f"\n| 2026-09-11 | HTS-фильтры дособор (lens_hts_filters_topup.py, 5 запросов пагинация) | Lens.org | 5 | Да (в рамках задачи патентного сигнала) |\n")

if __name__=="__main__": main()
