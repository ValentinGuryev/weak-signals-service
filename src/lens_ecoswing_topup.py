#!/usr/bin/env python3
"""ТОП-АП патентной базы кейса 010 (EcoSwing) — ~20 запросов (лимит: сжечь, но не перебор).

Слои:
  P-A4  добить пагинацию A4 (superconducting generator + wind, 25 ост.)
  P-B1/B2 добить пагинацию классов машин/генераторов (по 2 страницы)
  P-C  новые термины ядра (wind farm / wind powered / wind energy / REBCO wind / HTS wind machine)
  P-D  азиатские ключи (CN 超导风电, KR 초전도 풍력)
  P-E  компоненты (field coil + wind, cooling + wind, cryogenic + wind)
  P-V  верификация игроков через термины (Envision, DTU, HTS generator wind, offshore wind + SC)
Выход: data/raw/patents/cases/010_sc_wind_topup.json (merge потом)
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

def mp(f, p): return {"match_phrase": {f: p}}
def m(f, t): return {"match": {f: t}}
def must_any(*pairs):
    return {"bool": {"should": [ {"bool":{"must":list(pairs)}} ], "must": list(pairs)} }

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
    return ""
def _yr(p):
    pc=p.get("biblio",{}).get("priority_claims",{})
    if isinstance(pc,dict):
        dt=(pc.get("earliest_claim") or {}).get("date") if isinstance(pc.get("earliest_claim"),dict) else None
        if isinstance(dt,str) and dt[:4].isdigit(): return int(dt[:4])
    return None

def rec(p, tag, qy=""):
    pa=p.get("biblio",{}).get("parties",{})
    return {"source":"lens","query":tag,"publication_number":_num(p),
            "title":_txt(p.get("biblio",{}).get("invention_title")),
            "abstract":_txt(p.get("abstract")),
            "assignee":"; ".join(_txt(a.get("extracted_name",{}).get("value")) for a in (pa.get("applicants") or [])[:4]),
            "inventors":"; ".join(_txt(i.get("extracted_name",{}).get("value")) for i in (pa.get("inventors") or [])[:4]),
            "cited_by":(p.get("biblio",{}).get("cited_by",{}) or {}).get("count"),
            "year":_yr(p),"query_extra":qy}

# P-A4 пагинация (2 стр): superconducting generator AND wind/offshore в title
A4 = {"bool":{"must":[
        {"bool":{"should":[mp("title","superconducting generator"),mp("abstract","superconducting generator")]}},
        {"bool":{"should":[mp("title","wind"),mp("title","turbine"),mp("title","offshore")],"minimum_should_match":1}}]}}

# P-B класс
B1 = {"bool":{"should":[mp("title","superconducting electrical machine"),mp("abstract","superconducting electrical machine"),
        mp("title","superconducting machine"),mp("abstract","superconducting machine")]}}
B2 = {"bool":{"should":[mp("title","superconducting generator"),mp("abstract","superconducting generator")]}}

C = {
 "C1_sc_wind_farm": {"bool":{"should":[mp("title","superconducting wind farm"),mp("abstract","superconducting wind farm")]}},
 "C2_sc_wind_powered": {"bool":{"should":[mp("title","superconducting wind powered"),mp("abstract","superconducting wind powered")]}},
 "C3_sc_wind_energy_system": {"bool":{"should":[mp("title","superconducting wind energy system"),mp("abstract","superconducting wind energy system"),
    mp("title","superconducting wind power system"),mp("abstract","superconducting wind power system")]}},
 "C4_rebco_wind": {"bool":{"should":[mp("title","REBCO wind"),mp("abstract","REBCO wind"),mp("title","YBCO wind"),mp("abstract","YBCO wind")]}},
 "C5_hts_wind_machine": {"bool":{"should":[mp("title","HTS wind machine"),mp("abstract","HTS wind machine"),
    mp("title","high temperature superconducting wind machine"),mp("abstract","high temperature superconducting wind machine")]}},
}
D = {
 "D1_cn_sc_wind": {"bool":{"should":[mp("title","超导风电"),mp("abstract","超导风电")]}},
 "D2_kr_sc_wind": {"bool":{"should":[mp("title","초전도 풍력"),mp("abstract","초전도 풍력")]}},
}
E = {
 "E1_field_coil_wind": {"bool":{"must":[mp("title","superconducting field coil"),mp("title","wind")],"minimum_should_match":2}},
 "E2_cooling_wind": {"bool":{"must":[mp("title","superconducting generator"),mp("title","cooling")],"minimum_should_match":2,
    "should":[mp("abstract","wind"),mp("title","wind")],"minimum_should_match":1}},
 "E3_cryogenic_wind": {"bool":{"must":[mp("title","cryogenic"),mp("title","superconducting")],
    "should":[mp("title","wind turbine"),mp("abstract","wind")],"minimum_should_match":1}},
}
V = {
 "V1_envision": {"bool":{"should":[mp("title","Envision"),mp("abstract","Envision")],
   "must":[{"bool":{"should":[mp("title","superconducting"),mp("abstract","superconducting")]}}]}},
 "V2_dtu_dk": {"bool":{"should":[mp("title","Technical University of Denmark"),
    mp("abstract","Technical University of Denmark")]}},
 "V3_hts_gen_wind": {"bool":{"should":[mp("abstract","HTS generator for wind"),mp("abstract","HTS wind turbine generator"),
    mp("abstract","high temperature superconducting generator wind")]}},
 "V4_offshore_sc": {"bool":{"must":[
    {"bool":{"should":[mp("title","offshore wind"),mp("abstract","offshore wind")]}},
    {"bool":{"should":[mp("title","superconducting"),mp("title","HTS")]}}]}},
}

PLAN = {}
PLAN.update({"A4_p1": (A4, 0), "A4_p2": (A4, 40)})
PLAN.update({"B1_p2": (B1, 40), "B1_p3": (B1, 80), "B2_p2": (B2, 40), "B2_p3": (B2, 80)})
for k,q in {**C, **D, **E, **V}.items(): PLAN[k] = (q, 0)

def main():
    all_rows=[]; last_hdrs={}
    for i,(tag,(q,off)) in enumerate(PLAN.items(),1):
        try:
            data, hdrs = call(q, off, 40)
        except urllib.error.HTTPError as e:
            print(f"[{i}/{len(PLAN)}] {tag}: HTTP {e.code} — СТОП (429/лимит)")
            if e.code==429: time.sleep(25)
            continue
        except Exception as e:
            print(f"[{i}/{len(PLAN)}] {tag}: ERR {str(e)[:80]}"); continue
        tot=data.get("total",0); rows=[rec(p,tag) for p in (data.get("data") or data.get("results") or [])]
        all_rows.extend(rows); last_hdrs=hdrs
        print(f"[{i}/{len(PLAN)}] {tag}: total={tot}, +{len(rows)}")
        time.sleep(0.7)
    # дедуп
    seen=set(); uniq=[]
    for r in all_rows:
        k=r["publication_number"] or f"T:{str(r['title'])[:40].lower()}"
        if k in seen: continue
        seen.add(k); uniq.append(r)
    out=ROOT/"data/raw/patents/cases/010_sc_wind_topup.json"
    out.write_text(json.dumps({"case":"010","date":"2026-09-11","raw":len(all_rows),"uniq":len(uniq),
        "patents":uniq,"limits":last_hdrs}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nИТОГ topup: raw={len(all_rows)}, uniq={len(uniq)} → {out}")
    for k,v in last_hdrs.items(): print(f"  {k}: {v}")

if __name__=="__main__": main()
