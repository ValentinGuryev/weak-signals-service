#!/usr/bin/env python3
"""Lens ПОЛНЫЙ СБОР Этапа 2 (2026-09): uhf_nmr, current_leads, cryo_cmos + тема datacenter.

Экономия запросов: cryo_cmos широкий слой ограничен 200 записями; МАКСИМАЛЬНО size=100.
Остаток Lens ~37/1000 (по заголовкам 2026-09-11). Дедуп L1+L2, релеванс-авто, паспорта.
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
def AND(*items): return {"bool":{"must":list(items)}}
def bool_should(*items): return {"bool":{"should":list(items)}}

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

def fetch_all(tag, q, case, max_pages=None):
    rows=[]; last={}; size=100
    for _ in range(2):
        offset=0; pages=0
        try:
            data, hdrs = call(q, 0, size)
        except urllib.error.HTTPError as e:
            if e.code==400 and size==100:
                size=40; continue
            raise
        total=data.get("total",0)
        rows += [rec(p,tag,case) for p in (data.get("data") or data.get("results") or [])]
        last=hdrs; pages+=1
        while len(rows) < total and (max_pages is None or pages < max_pages):
            offset += size
            try:
                data, hdrs = call(q, offset, size)
            except urllib.error.HTTPError as e:
                if e.code==429: time.sleep(30); continue
                raise
            chunk=[rec(p,tag,case) for p in (data.get("data") or data.get("results") or [])]
            if not chunk: break
            rows += chunk; last=hdrs; pages+=1; time.sleep(1.2)
        return rows, last, total
    return rows, last, total

# ---------- ЗАПРОСЫ ----------
CASES = {
 "uhf_nmr": {
   "L1_nmr_magnet": AND(bool_should(mp("title","NMR magnet"),mp("abstract","NMR magnet")),
        bool_should(mp("title","superconducting"),mp("abstract","superconducting"),
                    mp("title","HTS"),mp("abstract","HTS"))),
   "L2_insert": AND(OR("HTS insert","high temperature superconducting insert","superconducting insert"),
        bool_should(mp("abstract","NMR"),mp("title","NMR"),mp("title","magnet"),mp("abstract","magnet"))),
 },
 "current_leads": {
   "L1_core": OR("superconducting current lead","superconducting current leads",
                 "HTS current lead","HTS current leads","superconducting current-lead"),
   "L2_classic": OR("vapor cooled lead","vapour cooled lead","gas cooled current lead"),
 },
 "cryo_cmos": {
   "L1_core": OR("cryogenic CMOS","cryo-CMOS","cryo CMOS"),
   "L2_qubit_context": AND(bool_should(mp("title","CMOS"),mp("abstract","CMOS")),
        bool_should(mp("title","cryogenic"),mp("abstract","cryogenic"),
                    mp("title","qubit"),mp("abstract","qubit"),
                    mp("abstract","quantum"),mp("abstract","4 K"))),
 },
 "sc_datacenter": {
   "D1_dc": AND(OR("datacenter","data center","data-centre","datacentre"),
        bool_should(mp("abstract","superconducting"),mp("abstract","superconductor"),
                    mp("abstract","HTS"),mp("abstract","cryogenic"))),
   "D2_hv": OR("high voltage superconductor","superconducting power distribution",
               "cryogenic power distribution","cryo power delivery"),
 },
}

# max_pages для экономии: cryo_cmos L2 — 200 записей
LIMITS = {("cryo_cmos","L2_qubit_context"): 2}

def relevance(case, r):
    t=f"{r.get('title','')} {r.get('abstract','')}".lower()
    if case=="uhf_nmr":
        ok = bool(re.search(r'nmr|nuclear magnetic resonance', t)) and bool(re.search(r'superconduct|magnet|insert|shield|persistent', t))
        return ok and not re.search(r'semiconductor|\bcmos\b|laser\b|optical fiber|fibre optic|\bpet\b', t)
    if case=="current_leads":
        ok = bool(re.search(r'current \w*lead|cooled lead', t)) and bool(re.search(r'superconduct|hts\b|rebco|bscco|magnet', t))
        return ok and not re.search(r'semiconductor|\bcmos\b|battery\b|solar', t)
    if case=="cryo_cmos":
        ok = bool(re.search(r'\bcmos\b', t)) and bool(re.search(r'cryo|cryogenic|qubit|quantum|4 k|77 k|millikelvin', t))
        return ok and not re.search(r'semiconductor fab|wafer fab|photolith|etch|implant process', t)
    if case=="sc_datacenter":
        ok = bool(re.search(r'datacenter|data center|datacentre|data-centre|campus', t)) and bool(re.search(r'superconduct|hts\b|cryogenic|cryo', t))
        return ok and not re.search(r'drug|pharma|semiconductor fab', t)
    return True

def norm_title(t):
    t=re.sub(r'[^a-z0-9 ]',' ',t.lower())
    return re.sub(r'\s+',' ',t).strip()[:60]

def main():
    last={}; total_req=0
    for case, qs in CASES.items():
        rows=[]; tot=0
        for tag, q in qs.items():
            mp_ = LIMITS.get((case,tag))
            for attempt in range(3):
                try:
                    r, hdrs, total = fetch_all(tag, q, case, max_pages=mp_)
                    total_req+=1; last=hdrs; rows+=r; tot+=total
                    lim = f" (лимит {mp_} стр.)" if mp_ else ""
                    print(f"  [{case}][{tag}] total={total}, собрано {len(r)}{lim}")
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
        for r in ded: r["invention"]= r in inv
        res={"case":case,"date":"2026-09-11","query_plan":list(qs.keys()),
             "raw":len(rows),"uniq":len(ded),
             "relevant_count":sum(1 for r in ded if r["relevant"]),
             "inventions":len(inv),"patents":ded,"limits":last}
        outp=ROOT/f"data/raw/patents/cases/{case}.json"
        outp.write_text(json.dumps(res,ensure_ascii=False,indent=1),encoding="utf-8")
        print(f"  ⭐ {case}: raw={len(rows)} uniq={len(ded)} релев.={res['relevant_count']} изобрет.={len(inv)} → {outp.name}")
    print(f"\nВсего запросов: {total_req}")
    for k,v in last.items(): print(f"  {k}: {v}")

if __name__=="__main__": main()