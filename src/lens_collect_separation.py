#!/usr/bin/env python3
"""Lens ПОЛНЫЙ СБОР кейса sc_magnetic_separation (2026-09).

Разведка (L1/L3) + полный сбор (L1, L2, L3). Экономия: size=100, лимит страниц,
слои с total=0 пропускаются. Остаток ~24/1000 (X-RateLimit).
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

CASE="sc_magnetic_separation"
QUERIES = {
  "L1_phrase": OR("superconducting magnetic separation","superconducting magnetic separator",
                  "superconducting separator"),
  "L2_any":    AND(OR("magnetic separation","magnetic separator","HGMS",
                      "high gradient magnetic separator","magnetic separator device"),
                   bool_should(mp("title","superconducting"),mp("abstract","superconducting"),
                               mp("title","HTS"),mp("abstract","HTS"),
                               mp("title","superconductor"),mp("abstract","superconductor"))),
  "L3_cn_jp":  OR("超导磁分离","超导磁选","超電導磁気分離","超伝導磁気分離"),
}
# разведка: L1 + L3; L3 берём сразу если >0; L2 только если L1 мал/нужна полнота
RECON = ["L1_phrase","L3_cn_jp"]

def relevance(r):
    t=f"{r.get('title','')} {r.get('abstract','')}".lower()
    ok = bool(re.search(r'magnetic separat|magnetic separato|hgms|high.*gradient magnetic|magnet separator', t)) \
         and bool(re.search(r'superconduct|hts\b|superconductor', t))
    bad = re.search(r'semiconductor|\bcmos\b|solar cell|\bled\b|fuel cell|drug|\bMRI\b|mri\b', t)
    return ok and not bad

def norm_title(t):
    t=re.sub(r'[^a-z0-9 ]',' ',t.lower())
    return re.sub(r'\s+',' ',t).strip()[:60]

def main():
    last={}; total_req=0
    # 1) разведка
    print("=== РАЗВЕДКА ===")
    recon_tot={}
    for tag in RECON:
        try:
            data, hdrs = call(QUERIES[tag])
            total_req+=1; last=hdrs
            recon_tot[tag]=data.get("total",0)
            print(f"  [{tag}] total={recon_tot[tag]}")
            time.sleep(1.2)
        except Exception as e:
            print(f"  [{tag}] ERR {str(e)[:80]}"); recon_tot[tag]=None
    # 2) сбор: L1 всегда; L3 если >0; L2 если нужно (L3 мал или 0 → берём L2 для полноты)
    collect_tags = ["L1_phrase"]
    if recon_tot.get("L3_cn_jp"): collect_tags.append("L3_cn_jp")
    if (recon_tot.get("L3_cn_jp") or 0) < 40: collect_tags.append("L2_any")
    print(f"=== СБОР (слои: {collect_tags}) ===")
    rows=[]
    for tag in collect_tags:
        for attempt in range(3):
            try:
                r, hdrs, total = fetch_all(tag, QUERIES[tag], CASE)
                total_req+=1; last=hdrs; rows+=r
                print(f"  [{tag}] total={total}, собрано {len(r)}")
                time.sleep(1.5)
                break
            except urllib.error.HTTPError as e:
                print(f"  [{tag}] HTTP {e.code} (попытка {attempt+1})")
                if e.code==429: time.sleep(30)
            except Exception as e:
                print(f"  [{tag}] ERR {str(e)[:100]} (попытка {attempt+1})"); time.sleep(5)
    # 3) дедуп + релевантность + изобретения
    seen=set(); ded=[]
    for r in rows:
        k=r["publication_number"] or f"T:{norm_title(r['title'])}"
        if k in seen: continue
        seen.add(k); r["relevant"]=relevance(r); ded.append(r)
    fam=set(); inv=[]
    for r in sorted(ded, key=lambda x:-(x["year"] or 0)):
        key=(r["assignee"].split(";")[0].strip().lower(), norm_title(r["title"]))
        if key in fam: continue
        fam.add(key); inv.append(r)
    for r in ded: r["invention"]= r in inv
    res={"case":CASE,"date":"2026-09-11","query_plan":list(QUERIES.keys()),
         "raw":len(rows),"uniq":len(ded),
         "relevant_count":sum(1 for r in ded if r["relevant"]),
         "inventions":len(inv),"patents":ded,"limits":last}
    outp=ROOT/f"data/raw/patents/cases/{CASE}.json"
    outp.write_text(json.dumps(res,ensure_ascii=False,indent=1),encoding="utf-8")
    print(f"\n⭐ {CASE}: raw={len(rows)} uniq={len(ded)} релев.={res['relevant_count']} изобрет.={len(inv)} → {outp.name}")
    print(f"Всего запросов (разведка+сбор с пагинацией): ~{total_req}+")
    for k,v in last.items(): print(f"  {k}: {v}")

if __name__=="__main__": main()