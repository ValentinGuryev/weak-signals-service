#!/usr/bin/env python3
"""Lens: патентная база кейса 011 (SRF-резонаторы / сверхпроводящие ВЧ-полости).

План (~6 логических запросов; остаток Lens ~152/мес на 2026-09-11, сброс 2026-09-30):
  A1 "superconducting RF cavity" | "SRF cavity" | "SRF cavities"   (ядро)
  A2 "niobium cavity" | "niobium SRF" | "Nb cavity"               (материал)
  A3 "superconducting accelerator cavity" | "superconducting cavity accelerator"
  B1 "Nb3Sn cavity" | "Nb3Sn SRF" | "niobium-tin cavity"          (ветка)
  B2 "superconducting RF" + (accelerator | linac) — компонентный слой
  C1  верификация: "SRF" + (Fermilab|JLab|KEK|CERN|Cornell) в тексте (игроки-академия)
Выход: data/raw/patents/cases/011_srf_cavities.json
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

def call(esq, offset=0, size=40):
    body = {"query": esq, "include": INC, "size": size}
    if offset: body["offset"] = offset
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
  "A1_srf_cavity": {"bool":{"should":[mp("title","superconducting RF cavity"),mp("abstract","superconducting RF cavity"),
        mp("title","SRF cavity"),mp("abstract","SRF cavity"),mp("title","SRF cavities"),mp("abstract","SRF cavities")]}},
  "A2_niobium_cavity": {"bool":{"should":[mp("title","niobium cavity"),mp("abstract","niobium cavity"),
        mp("title","niobium SRF"),mp("abstract","niobium SRF")]}},
  "A3_sc_accel_cavity": {"bool":{"should":[mp("title","superconducting accelerator cavity"),mp("abstract","superconducting accelerator cavity"),
        mp("abstract","superconducting accelerating cavity")]}},
  "B1_nb3sn_cavity": {"bool":{"should":[mp("title","Nb3Sn cavity"),mp("abstract","Nb3Sn cavity"),
        mp("title","Nb3Sn SRF"),mp("abstract","Nb3Sn SRF"),mp("title","niobium-tin cavity"),mp("abstract","niobium-tin cavity")]}},
  "B2_sc_rf_accel": {"bool":{"must":[{"bool":{"should":[mp("title","superconducting RF"),mp("abstract","superconducting RF")]
        ,"minimum_should_match":1}}],
        "should":[mp("title","accelerator"),mp("abstract","accelerator"),mp("title","linac"),mp("abstract","linac")],
        "minimum_should_match":1}},
  "C1_players": {"bool":{"must":[{"bool":{"should":[mp("title","SRF"),mp("abstract","SRF"),mp("title","superconducting cavity"),mp("abstract","superconducting cavity")]}}],
        "should":[mp("abstract","Fermilab"),mp("abstract","Fermilab"),mp("abstract","Jefferson Lab"),mp("abstract","KEK"),
                  mp("abstract","CERN"),mp("abstract","Cornell"),mp("abstract","FNAL")], "minimum_should_match":1}},
}

def main():
    rows=[]; last={}
    for i,(tag,q) in enumerate(QUERIES.items(),1):
        try:
            data, hdrs = call(q, 0, 40)
        except urllib.error.HTTPError as e:
            print(f"[{i}/{len(QUERIES)}] {tag}: HTTP {e.code} — пропуск")
            if e.code==429: time.sleep(25)
            continue
        except Exception as e:
            print(f"[{i}/{len(QUERIES)}] {tag}: ERR {str(e)[:80]}"); continue
        tot=data.get("total",0); rs=[rec(p,tag) for p in (data.get("data") or data.get("results") or [])]
        rows+=rs; last=hdrs
        print(f"[{i}/{len(QUERIES)}] {tag}: total={tot}, +{len(rs)}")
        time.sleep(0.8)
    # дедуп + релевантность
    def rel(p):
        t=f"{p.get('title','')} {p.get('abstract','')}".lower()
        if not re.search(r'srf|superconducting (rf|radio|accelerator|cavity)|niobium|nb3sn|niobium.tin', t): return False
        if re.search(r'optical|photonic|laser|fibre|fiber|quantum|microwave oven|cook', t): return False
        return True
    seen=set(); out=[]
    for r in rows:
        k=r["publication_number"] or f"T:{str(r['title'])[:40].lower()}"
        if k in seen: continue
        seen.add(k); r["relevant"]=rel(r); out.append(r)
    res={"case":"011_srf_cavities","date":"2026-09-11","query_plan":list(QUERIES.keys()),
         "raw":len(rows),"uniq":len(out),
         "relevant_count":sum(1 for r in out if r["relevant"]),"patents":out,"limits":last}
    outp=ROOT/"data/raw/patents/cases/011_srf_cavities.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(res,ensure_ascii=False,indent=1),encoding="utf-8")
    print(f"\nИТОГ: raw={len(rows)}, uniq={len(out)}, релев.={res['relevant_count']} → {outp}")
    for k,v in last.items(): print(f"  {k}: {v}")
    # api_budget
    with (ROOT/"results/runtime/api_budget.md").open("a") as f:
        f.write(f"\n| 2026-09-11 | Кейс 011 SRF: Lens патенты (lens_srf.py, {len(QUERIES)} лог. запросов; "
                f"{len(rows)} raw / {len(out)} уник. / {res['relevant_count']} релев.) | Lens.org | {len(QUERIES)} | Да (команда «Сделай lens запросы») |\n")

if __name__=="__main__": main()