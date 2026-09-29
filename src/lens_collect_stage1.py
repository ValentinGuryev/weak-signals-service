#!/usr/bin/env python3
"""Lens ПОЛНЫЙ СБОР Этапа 1 (2026-09): патентные базы 4 кейсов.

Кейсы: sc_dc_cables, sfcl, iron_based (пниктиды+халькогениды), sc_induction_heaters.
Термины — по результатам разведки (lens_explore_stage1.py, v1+v2).
Дедуп L1 (pub num) + L2 (assignee+norm title = изобретение); релеванс-авто (аудит вручную потом);
паспорт .md; лог api_budget. Пагинация size=100 (fallback 40).
"""
from __future__ import annotations
import json, re, time, urllib.request, urllib.error, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN = ""
for line in (ROOT/".env").read_text().splitlines():
    if line.startswith("LENS_TOKEN="):
        TOKEN = line.split("=",1)[1].strip(); break
if not TOKEN:
    print("Нет LENS_TOKEN!"); sys.exit(1)

API = "https://api.lens.org/patent/search"
INC = ["biblio.publication_reference","biblio.application_reference","biblio.priority_claims",
       "biblio.invention_title","biblio.parties","biblio.cited_by","abstract"]

def mp(f,p): return {"match_phrase": {f: p}}
def OR(*phrases):
    s=[]
    for p in phrases:
        s.append(mp("title",p)); s.append(mp("abstract",p))
    return {"bool":{"should":s}}
def AND(*must_items):
    return {"bool":{"must":list(must_items)}}
def bool_should(*items):
    return {"bool":{"should":list(items)}}

def call(esq, offset=0, size=100):
    body = {"query": esq, "include": INC, "size": size}
    if offset: body["offset"] = offset
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=120)
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
    return "; ".join(out[:4])

def rec(p, tag, case):
    return {"source":"lens","case":case,"query":tag,
            "publication_number":_num(p),
            "title":_txt(p.get("biblio",{}).get("invention_title")),
            "abstract":_txt(p.get("abstract")),
            "assignee":_assignees(p),
            "year":_yr(p), "jurisdiction":_jur(p),
            "cited_by":(p.get("biblio",{}).get("cited_by",{}) or {}).get("count")}

def fetch_all(tag, q, case):
    rows=[]; last={}; size=100
    for _ in range(2):
        offset=0
        try:
            data, hdrs = call(q, 0, size)
        except urllib.error.HTTPError as e:
            if e.code==400 and size==100:
                size=40; continue
            raise
        total=data.get("total",0)
        rows += [rec(p,tag,case) for p in (data.get("data") or data.get("results") or [])]
        last=hdrs
        while len(rows) < total:
            offset += size
            try:
                data, hdrs = call(q, offset, size)
            except urllib.error.HTTPError as e:
                if e.code==429: time.sleep(30); continue
                raise
            chunk=[rec(p,tag,case) for p in (data.get("data") or data.get("results") or [])]
            if not chunk: break
            rows += chunk; last=hdrs; time.sleep(1.2)
        return rows, last, total
    return rows, last, total

# ---------- ЗАПРОСЫ ПО КЕЙСАМ ----------
CASES_QUERIES = {
 "sc_dc_cables": {
   "L1_core": AND(OR("superconducting DC cable","DC HTS cable","HVDC superconducting cable",
                     "superconducting DC transmission")),
   "L2_sc_cable_dc": AND(OR("superconducting cable"),
        bool_should(mp("title","direct current"),mp("abstract","direct current"),
                    mp("title","DC cable"),mp("abstract","DC cable"),
                    mp("title","DC transmission"),mp("abstract","DC transmission"),
                    mp("title","HVDC"),mp("abstract","HVDC"))),
   "L3_mgb2_dc": AND(OR("MgB2"),
        bool_should(mp("abstract","direct current"),mp("abstract","DC cable"),
                    mp("abstract","DC transmission"),mp("abstract","DC"))),
 },
 "sfcl": {
   "L1_core": OR("superconducting fault current limiter","SFCL"),
   "L2_dc_sfcl": AND(OR("fault current limiter"),
        bool_should(mp("abstract","superconducting"),mp("abstract","HTS")),
        bool_should(mp("abstract","DC"),mp("abstract","direct current"))),
 },
 "iron_based": {
   "L1_core": OR("iron-based superconductor","pnictide superconductor","iron pnictide"),
   "L2_formulas": AND(
        bool_should(mp("abstract","BaFe2As2"),mp("abstract","SmFeAsO"),
                    mp("abstract","LiFeAs"),mp("abstract","KFe2As2"),
                    mp("abstract","FeSe"),mp("abstract","FeTe")),
        bool_should(mp("abstract","superconductor"),mp("abstract","superconducting"))),
 },
 "sc_induction_heaters": {
   "L1_and": AND(OR("induction heating","induction heater"),
        bool_should(mp("title","superconducting"),mp("abstract","superconducting"),
                    mp("title","HTS"),mp("abstract","HTS"))),
   "L2_sc_magnet": AND(OR("induction heating","induction heater"),
        OR("superconducting magnet")),
 },
}

# ---------- РЕЛЕВАНС-АВТО (финальный аудит вручную, паттерн 011) ----------
def relevance(case, r):
    t=f"{r.get('title','')} {r.get('abstract','')}".lower()
    if case=="sc_dc_cables":
        ok = bool(re.search(r'superconduct|hts\b|mgb2', t)) and bool(re.search(r'cable|transmission|direct current|\bdc\b|hvdc', t))
        return ok and not re.search(r'semiconductor|\bcmos\b|integrated circuit|\bled\b', t)
    if case=="sfcl":
        ok = bool(re.search(r'superconduct|sfcl|hts', t)) and bool(re.search(r'fault|current limit|limiter', t))
        return ok and not re.search(r'semiconductor substrate|plasma|wafer|etch|implant', t)
    if case=="iron_based":
        ok = bool(re.search(r'iron.based|pnictide|feas|fese|fete|bafe|smfeaso|lifeas|superconduct', t))
        return ok and not re.search(r'drug|pharma|battery\b|solar cell|\bled\b', t)
    if case=="sc_induction_heaters":
        ok = bool(re.search(r'induction heat', t)) and bool(re.search(r'superconduct|hts\b', t))
        return ok and not re.search(r'high.?throughput screening|semiconductor', t)
    return True

def norm_title(t):
    t=re.sub(r'[^a-z0-9 ]',' ',t.lower())
    return re.sub(r'\s+',' ',t).strip()[:60]

def main():
    # самопроверка структуры запросов
    for case,qs in CASES_QUERIES.items():
        for tag,q in qs.items():
            json.dumps(q)  # бросит исключение при битой структуре
    print("Структура запросов OK")
    last={}; total_req=0
    for case, qs in CASES_QUERIES.items():
        rows=[]; tot=0
        for tag, q in qs.items():
            for attempt in range(3):
                try:
                    r, hdrs, total = fetch_all(tag, q, case)
                    total_req+=1; last=hdrs; rows+= r; tot+=total
                    print(f"  [{case}][{tag}] total={total}, собрано {len(r)}")
                    time.sleep(1.5)
                    break
                except urllib.error.HTTPError as e:
                    print(f"  [{case}][{tag}] HTTP {e.code} (попытка {attempt+1})")
                    if e.code==429: time.sleep(30)
                except Exception as e:
                    print(f"  [{case}][{tag}] ERR {str(e)[:120]} (попытка {attempt+1})"); time.sleep(5)
        seen=set(); ded=[]
        for r in rows:
            k=r["publication_number"] or f"T:{norm_title(r['title'])}"
            if k in seen: continue
            seen.add(k); r["relevant"]=relevance(case,r); ded.append(r)
        fam=set(); inv=[]
        for r in sorted(ded, key=lambda x:-(x["year"] or 0)):
            key=(r["assignee"].split(";")[0].strip().lower(), norm_title(r["title"]))
            if key in fam: continue
            fam.add(key); inv.append(r)
        for r in ded:
            r["invention"]=bool(r in inv)
        res={"case":case,"date":"2026-09-11","query_plan":list(qs.keys()),
             "raw":len(rows),"uniq":len(ded),
             "relevant_count":sum(1 for r in ded if r["relevant"]),
             "inventions":len(inv),"patents":ded,"limits":last}
        outp=ROOT/f"data/raw/patents/cases/{case}.json"
        outp.write_text(json.dumps(res,ensure_ascii=False,indent=1),encoding="utf-8")
        print(f"  ⭐ {case}: raw={len(rows)} uniq={len(ded)} релев.={res['relevant_count']} изобретений={len(inv)} → {outp}")
    print(f"\nВсего запросов: {total_req}")
    for k,v in last.items(): print(f"  {k}: {v}")

if __name__=="__main__": main()