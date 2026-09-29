#!/usr/bin/env python3
"""Дособор HTS-фильтры до ПОЛНОТЫ: пагинация A1 (510) + новые синонимичные слои.

План (~18 запросов):
  Pg: A1 страницы 6-13 (остаток до 510)           — 8 запросов
  N1 "superconducting RF filter" | "SRF filter"
  N2 "superconducting receive filter" | "HTS receive filter" | "superconducting receiver filter"
  N3 "superconducting notch filter" | "HTS notch filter"
  N4 "YBCO bandpass" | "bandpass filter superconducting" | "superconducting band-pass"
  N5 "HTSC filter" | "high-Tc filter" | "high Tc superconducting filter"
  N6 "高温超导滤波器" (CN-китайский термин)
  N7 "superconducting frequency-selective" | "superconducting frequency selective surface"
  N8 "duplexer" AND superconducting | "HTS duplexer"
  N9 "superconducting front-end" | "superconducting front end" | front-end receive filter
Выход: merge в data/raw/patents/cases/hts_filters.json
"""
from __future__ import annotations
import json, os, re, sys, time, urllib.request, urllib.error
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
    body={"query":esq,"include":INC,"size":size}
    if off: body["offset"]=off
    req=urllib.request.Request(API,data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {TOKEN}","Content-Type":"application/json"})
    r=urllib.request.urlopen(req,timeout=90)
    hdrs={k:v for k,v in r.headers.items() if "x-rate-limit" in k.lower()}
    return json.loads(r.read().decode()),hdrs
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
def rec(p,tag):
    pa=p.get("biblio",{}).get("parties",{})
    return {"source":"lens","query":tag,"publication_number":_num(p),
            "title":_txt(p.get("biblio",{}).get("invention_title")),
            "abstract":_txt(p.get("abstract")),
            "assignee":"; ".join(_txt(a.get("extracted_name",{}).get("value")) for a in (pa.get("applicants") or [])[:4]),
            "inventors":"; ".join(_txt(i.get("extracted_name",{}).get("value")) for i in (pa.get("inventors") or [])[:4]),
            "cited_by":(p.get("biblio",{}).get("cited_by",{}) or {}).get("count"),
            "year":_yr(p)}

A1={"bool":{"should":[mp("title","superconducting filter"),mp("abstract","superconducting filter"),
      mp("title","HTS filter"),mp("abstract","HTS filter"),
      mp("title","high temperature superconducting filter"),mp("abstract","high temperature superconducting filter")]}}

NEW={
 "N1_rf_filter":{"bool":{"should":[mp("title","superconducting RF filter"),mp("abstract","superconducting RF filter"),
    mp("title","superconducting radio frequency filter"),mp("abstract","superconducting radio frequency filter")]}},
 "N2_receive_filter":{"bool":{"should":[mp("title","superconducting receive filter"),mp("abstract","superconducting receive filter"),
    mp("title","HTS receive filter"),mp("abstract","HTS receive filter"),
    mp("title","superconducting receiver filter"),mp("abstract","superconducting receiver filter")]}},
 "N3_notch":{"bool":{"should":[mp("title","superconducting notch filter"),mp("abstract","superconducting notch filter"),
    mp("title","HTS notch filter"),mp("abstract","HTS notch filter")]}},
 "N4_bandpass":{"bool":{"should":[mp("title","YBCO bandpass"),mp("abstract","YBCO bandpass"),
    mp("title","bandpass filter superconducting"),mp("abstract","bandpass filter superconducting"),
    mp("title","superconducting band-pass"),mp("abstract","superconducting band-pass")]}},
 "N5_htsc":{"bool":{"should":[mp("title","HTSC filter"),mp("abstract","HTSC filter"),
    mp("title","high-Tc filter"),mp("abstract","high-Tc filter"),
    mp("title","high Tc superconducting filter"),mp("abstract","high Tc superconducting filter")]}},
 "N6_cn_term":{"bool":{"should":[mp("title","高温超导滤波器"),mp("abstract","高温超导滤波器")]}},
 "N7_fss":{"bool":{"should":[mp("title","superconducting frequency-selective surface"),mp("abstract","superconducting frequency-selective surface"),
    mp("title","superconducting frequency selective"),mp("abstract","superconducting frequency selective")]}},
 "N8_duplexer":{"bool":{"must":[{"bool":{"should":[mp("title","duplexer"),mp("abstract","duplexer")]}},
    {"bool":{"should":[mp("title","superconducting"),mp("abstract","superconducting")]}}]}},
 "N9_fronfend":{"bool":{"should":[mp("title","superconducting front-end"),mp("abstract","superconducting front-end"),
    mp("title","front-end receive filter"),mp("abstract","front-end receive filter")]}},
}

def main():
    rows=[]; last={}
    plan=[]
    for off in (200,240,280,320,360,400,440,480):
        plan.append((f"A1_p{off//40+1}",A1,off))
    for tag,q,_ in plan:  # пагинации A1
        pass
    # исполняем все
    for tag,q,off in plan:
        try: data,hdrs=call(q,off,40)
        except urllib.error.HTTPError as e:
            print(f"{tag}: HTTP {e.code}"); time.sleep(20 if e.code==429 else 0); continue
        except Exception as e: print(f"{tag}: ERR {str(e)[:60]}"); continue
        rs=[rec(p,tag) for p in (data.get("data") or data.get("results") or [])]
        rows+=rs; last=hdrs
        print(f"{tag}: total={data.get('total',0)}, +{len(rs)}")
        time.sleep(0.7)
    time.sleep(1)
    for tag,q in NEW.items():
        try: data,hdrs=call(q,0,40)
        except urllib.error.HTTPError as e:
            print(f"{tag}: HTTP {e.code}"); time.sleep(20 if e.code==429 else 0); continue
        except Exception as e: print(f"{tag}: ERR {str(e)[:60]}"); continue
        rs=[rec(p,tag) for p in (data.get("data") or data.get("results") or [])]
        rows+=rs; last=hdrs
        print(f"{tag}: total={data.get('total',0)}, +{len(rs)}")
        time.sleep(0.7)
    # merge
    mf=ROOT/"data/raw/patents/cases/hts_filters.json"
    d=json.loads(mf.read_text(encoding="utf-8"))
    have={p["publication_number"] for p in d["patents"]}
    new=0
    for r in rows:
        if r["publication_number"] in have: continue
        d["patents"].append(r); have.add(r["publication_number"]); new+=1
    d["limits"]=last
    d["full_sweep"]="2026-09-11 A1 p6-p13 + 9 новых слоёв"
    mf.write_text(json.dumps(d,ensure_ascii=False,indent=1),encoding="utf-8")
    print(f"\nдобавлено новых: {new}; ИТОГ в базе: {len(d['patents'])} (уникальных)")
    for k,v in last.items(): print(f"  {k}: {v}")
    with (ROOT/"results/runtime/api_budget.md").open("a") as f:
        f.write(f"\n| 2026-09-11 | HTS-фильтры полный дособор (lens_hts_filters_full.py: 8 пагинация + 9 слоёв, {17} запросов; +{new} новых) | Lens.org | 17 | Да (команда «как можно более полно собрать базу») |\n")

if __name__=="__main__": main()
