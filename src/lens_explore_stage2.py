#!/usr/bin/env python3
"""Lens РАЗВЕДКА Этапа 2 (2026-09): counts-проверка терминов для 3 кейсов.

Кейсы: uhf_nmr, current_leads, cryo_cmos. Остаток Lens ~43/1000 (по заголовкам).
Разведка = 2 запроса/кейс; БЕЗ записи полных баз.
"""
from __future__ import annotations
import json, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = ""
for line in (ROOT/".env").read_text().splitlines():
    if line.startswith("LENS_TOKEN="):
        TOKEN = line.split("=",1)[1].strip(); break
if not TOKEN:
    raise SystemExit("Нет LENS_TOKEN!")

API = "https://api.lens.org/patent/search"
INC = ["biblio.publication_reference","biblio.priority_claims","biblio.invention_title","biblio.parties"]

def mp(f,p): return {"match_phrase": {f: p}}
def OR(*phrases):
    s=[]
    for p in phrases:
        s.append(mp("title",p)); s.append(mp("abstract",p))
    return {"bool":{"should":s}}
def AND(*items): return {"bool":{"must":list(items)}}
def bool_should(*items): return {"bool":{"should":list(items)}}

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
        dt=(pc.get("earliest_claim") or {}).get("date") if isinstance(pc.get("earliest_claim"),dict) else None
        if isinstance(dt,str) and dt[:4].isdigit(): return int(dt[:4])
    pub=p.get("biblio",{}).get("publication_reference",{})
    if isinstance(pub,dict) and isinstance(pub.get("date"),str) and pub["date"][:4].isdigit():
        return int(pub["date"][:4])
    return None

def _jur(p):
    x=p.get("biblio",{}).get("publication_reference",{})
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
 "uhf_nmr": {
   "R1_nmr_magnet": AND(bool_should(mp("title","NMR magnet"),mp("abstract","NMR magnet")),
        bool_should(mp("title","superconducting"),mp("abstract","superconducting"),
                    mp("title","HTS"),mp("abstract","HTS"))),
   "R2_numeric": AND(bool_should(mp("title","NMR"),mp("abstract","NMR")),
        bool_should(mp("abstract","1.2 GHz"),mp("abstract","1.1 GHz"),mp("abstract","900 MHz"),
                    mp("abstract","21.1 T"),mp("abstract","28.2 T"),mp("abstract","21.5 T"))),
 },
 "current_leads": {
   "R1_core": OR("superconducting current lead","superconducting current leads",
                 "HTS current lead","HTS current leads","superconducting current-lead"),
   "R2_classic": OR("vapor cooled lead","vapour cooled lead","gas cooled current lead"),
 },
 "cryo_cmos": {
   "R1_core": OR("cryogenic CMOS","cryo-CMOS","cryo CMOS"),
   "R2_qubit": AND(bool_should(mp("title","CMOS"),mp("abstract","CMOS")),
        bool_should(mp("title","cryogenic"),mp("abstract","cryogenic"),
                    mp("title","qubit"),mp("abstract","qubit"),
                    mp("abstract","quantum"),mp("abstract","4 K"))),
 },
}

def report(data):
    total=data.get("total",0)
    rs=data.get("data") or data.get("results") or []
    yrs={}; jurs={}; apps={}
    for p in rs:
        y=_yr(p)
        if y: yrs[y]=yrs.get(y,0)+1
        j=_jur(p); jurs[j]=jurs.get(j,0)+1
        a=_assignees(p)
        if a:
            apps[a.split(";")[0].strip()]=apps.get(a.split(";")[0].strip(),0)+1
    print(f"  total={total} (в выборке {len(rs)})")
    if yrs: print(f"  годы: {', '.join(f'{y}:{c}' for y,c in sorted(yrs.items())[-10:]) }")
    if jurs: print(f"  юрисд.: {', '.join(f'{j}:{c}' for j,c in sorted(jurs.items(), key=lambda x:-x[1])[:6])}")
    if apps: print(f"  заявители: {', '.join(f'{a} ({c})' for a,c in sorted(apps.items(), key=lambda x:-x[1])[:8])}")

def main():
    last={}; n=0
    for case, qs in CASES.items():
        print(f"\n===== {case} =====")
        for tag, q in qs.items():
            for attempt in range(3):
                try:
                    data, hdrs = call(q)
                    n+=1; last=hdrs
                    print(f"[{tag}] ", end=""); report(data)
                    break
                except urllib.error.HTTPError as e:
                    print(f"[{tag}] HTTP {e.code} (попытка {attempt+1})")
                    if e.code==429: time.sleep(30)
                except Exception as e:
                    print(f"[{tag}] ERR {str(e)[:100]} (попытка {attempt+1})"); time.sleep(3)
    print(f"\nВсего запросов Этап 2 разведка: {n}")
    for k,v in last.items(): print(f"  {k}: {v}")

if __name__=="__main__": main()