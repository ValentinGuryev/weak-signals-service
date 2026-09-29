#!/usr/bin/env python3
"""Lens РАЗВЕДКА Этапа 1 (2026-09): counts-проверка терминов для 4 кейсов.

Кейсы: sc_dc_cables, sfcl, iron_pnictides+chalcogenides, sc_induction_heaters.
Правила: разведка = 2 запроса/кейс (ядро + CN/JP-слой); БЕЗ записи полных баз
(полный сбор — отдельно, после санкции автора). Остаток по X-RateLimit-заголовкам.
"""
from __future__ import annotations
import json, re, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = ""
env = ROOT / ".env"
if env.exists():
    for line in env.read_text().splitlines():
        if line.startswith("LENS_TOKEN="):
            TOKEN = line.split("=",1)[1].strip(); break
if not TOKEN:
    print("Нет LENS_TOKEN!"); sys_exit = True
    raise SystemExit("Нет LENS_TOKEN!")

API = "https://api.lens.org/patent/search"
INC = ["biblio.publication_reference","biblio.priority_claims",
       "biblio.invention_title","biblio.parties"]

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

def _yr(p):
    pc=p.get("biblio",{}).get("priority_claims",{})
    if isinstance(pc,dict):
        ec=pc.get("earliest_claim")
        if isinstance(ec,dict) and isinstance(ec.get("date"),str) and ec["date"][:4].isdigit():
            return int(ec["date"][:4])
    pub=p.get("biblio",{}).get("publication_reference",{})
    if isinstance(pub,dict):
        d=pub.get("date")
        if isinstance(d,str) and d[:4].isdigit(): return int(d[:4])
    return None

def _jur(p):
    for src in ("publication_reference","application_reference"):
        x=p.get("biblio",{}).get(src)
        if isinstance(x,dict) and x.get("jurisdiction"): return x["jurisdiction"]
    return "?"

def _assignees(p):
    pa=p.get("biblio",{}).get("parties",{})
    out=[]
    for a in (pa.get("applicants") or [])[:5]:
        n=_txt((a.get("extracted_name") or {}).get("value"))
        if n: out.append(n)
    return "; ".join(out[:3])

CASES = {
 "sc_dc_cables": {
   "R1_core": {"bool":{"should":[
        mp("title","superconducting DC cable"),mp("abstract","superconducting DC cable"),
        mp("title","DC HTS cable"),mp("abstract","DC HTS cable"),
        mp("title","HVDC superconducting cable"),mp("abstract","HVDC superconducting cable"),
        mp("title","superconducting DC transmission"),mp("abstract","superconducting DC transmission")]}},
   "R3_cn": {"bool":{"should":[mp("title","超导直流电缆"),mp("abstract","超导直流电缆")]}},
 },
 "sfcl": {
   "R1_core": {"bool":{"should":[
        mp("title","superconducting fault current limiter"),mp("abstract","superconducting fault current limiter"),
        mp("title","SFCL"),mp("abstract","SFCL")]}},
   "R3_cn": {"bool":{"should":[mp("title","超导故障限流器"),mp("abstract","超导故障限流器"),
        mp("title","超导限流器"),mp("abstract","超导限流器")]}},
 },
 "iron_based": {
   "R1_core": {"bool":{"should":[
        mp("title","iron-based superconductor"),mp("abstract","iron-based superconductor"),
        mp("title","pnictide superconductor"),mp("abstract","pnictide superconductor"),
        mp("title","iron pnictide"),mp("abstract","iron pnictide")]}},
   "R3_cn": {"bool":{"should":[mp("title","铁基超导"),mp("abstract","铁基超导")]}},
 },
 "sc_induction_heaters": {
   "R1_core": {"bool":{"should":[
        mp("title","superconducting induction heater"),mp("abstract","superconducting induction heater"),
        mp("abstract","induction heating superconducting")]}},
   "R3_jp": {"bool":{"should":[mp("title","超伝導誘導加熱"),mp("abstract","超伝導誘導加熱")]}},
 },
}

def report(data, tag):
    total=data.get("total",0)
    rs=data.get("data") or data.get("results") or []
    yrs={}; jurs={}; apps={}
    for p in rs:
        y=_yr(p)
        if y: yrs[y]=yrs.get(y,0)+1
        j=_jur(p); jurs[j]=jurs.get(j,0)+1
        a=_assignees(p)
        if a:
            first=a.split(";")[0].strip()
            apps[first]=apps.get(first,0)+1
    top_y=sorted(yrs.items(), key=lambda x:-x[1])[:8]
    top_j=sorted(jurs.items(), key=lambda x:-x[1])[:6]
    top_a=sorted(apps.items(), key=lambda x:-x[1])[:8]
    print(f"  total={total}  (в выборке {len(rs)})")
    if top_y: print(f"  годы(приоритет): {', '.join(f'{y}:{c}' for y,c in top_y)}")
    if top_j: print(f"  юрисдикции: {', '.join(f'{j}:{c}' for j,c in top_j)}")
    if top_a: print(f"  заявители: {', '.join(f'{a} ({c})' for a,c in top_a)}")

def main():
    last={}; total_req=0
    for case, qs in CASES.items():
        print(f"\n===== {case} =====")
        for tag, q in qs.items():
            # 429-защита: до 3 попыток
            for attempt in range(3):
                try:
                    data, hdrs = call(q)
                    total_req+=1; last=hdrs
                    print(f"[{tag}] ", end="")
                    report(data, tag)
                    break
                except urllib.error.HTTPError as e:
                    print(f"[{tag}] HTTP {e.code} (попытка {attempt+1})")
                    if e.code==429: time.sleep(30)
                except Exception as e:
                    print(f"[{tag}] ERR {str(e)[:100]} (попытка {attempt+1})"); time.sleep(3)
    print(f"\nВсего запросов Lens: {total_req}")
    for k,v in last.items(): print(f"  {k}: {v}")

# ---------- РАЗВЕДКА v2 (доп., по команде автора) ----------
V2 = {
 "dc_cables_v2": {
   "V2R1_sc_cable_dc": {"bool":{"must":[{"bool":{"should":[
        mp("title","superconducting cable"),mp("abstract","superconducting cable")]}}],
        "should":[mp("title","direct current"),mp("abstract","direct current"),
                  mp("title","DC cable"),mp("abstract","DC cable"),
                  mp("title","DC transmission"),mp("abstract","DC transmission"),
                  mp("title","HVDC"),mp("abstract","HVDC")],"minimum_should_match":1}},
   "V2R2_hvdc_sc": {"bool":{"should":[
        mp("abstract","HVDC superconducting"),mp("title","HVDC superconducting cable"),
        mp("abstract","high voltage direct current superconducting")]}},
 },
 "heaters_v2": {
   "V2R1_and": {"bool":{"must":[
        {"bool":{"should":[mp("title","induction heating"),mp("abstract","induction heating"),
                           mp("title","induction heater"),mp("abstract","induction heater")]}},
        {"bool":{"should":[mp("title","superconducting"),mp("abstract","superconducting"),
                           mp("title","HTS"),mp("abstract","HTS")]}}]}},
   "V2R2_sc_magnet": {"bool":{"must":[
        {"bool":{"should":[mp("title","induction heating"),mp("abstract","induction heating"),
                           mp("title","induction heater"),mp("abstract","induction heater")]}},
        {"bool":{"should":[mp("title","superconducting magnet"),mp("abstract","superconducting magnet")]}}]}},
 },
}

def run_v2():
    last={}; total_req=0
    for case, qs in V2.items():
        print(f"\n===== {case} =====")
        for tag, q in qs.items():
            for attempt in range(3):
                try:
                    data, hdrs = call(q)
                    total_req+=1; last=hdrs
                    print(f"[{tag}] ", end="")
                    report(data, tag)
                    break
                except urllib.error.HTTPError as e:
                    print(f"[{tag}] HTTP {e.code} (попытка {attempt+1})")
                    if e.code==429: time.sleep(30)
                except Exception as e:
                    print(f"[{tag}] ERR {str(e)[:100]} (попытка {attempt+1})"); time.sleep(3)
    print(f"\nВсего запросов v2: {total_req}")
    for k,v in last.items(): print(f"  {k}: {v}")

if __name__=="__main__":
    run_v2()
