#!/usr/bin/env python3
"""CORDIS-гранты для кейса 008 (СП-авиамоторы) — термины от ПРОБЛЕМЫ.

Вопрос: кто финансировал СП-авиамоторы/крио-пропульсию через гранты ЕС?
(и конкуренты: обычные электромоторы, водород-эл. авиация)
CORDIS API бесплатен, без ключа. contentType=project фильтр.
Выход: data/raw/grants_foreign/cordis_sc_aircraft_results.json
"""
import json, time, urllib.parse, urllib.request

CORDIS_URL = "https://cordis.europa.eu/api/search/results"
# Термины: ядро (СП-мотор/крио) + конкуренты (электромотор, водород)
KEYWORDS = [
    # ядро — СП-моторы/крио-пропульсия для авиации
    '"superconducting motor" aircraft', '"superconducting machine" aviation',
    '"superconducting propulsion" aircraft', 'cryogenic electric propulsion aircraft',
    '"cryogenic motor" aircraft', 'cryo-electric aircraft',
    # известные проекты
    'ASuMED', 'HIVOMOT', 'FAME megawatt engines',
    # конкуренты (драйверы поля)
    '"electric propulsion" aircraft motor', 'hydrogen-electric aircraft propulsion',
]

def search(q, page=0):
    params = {"q": q, "page": page, "pageSize": 50}
    url = CORDIS_URL + "?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120 Safari/537.36",
               "Accept": "application/json"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.load(r)
    except Exception as e:
        print(f"  ERR {q}: {e}")
        return None

def main():
    out = {}
    for kw in KEYWORDS:
        d = search(kw)
        if not d:
            continue
        total = d.get("total", 0)
        results = d.get("results", [])
        projects = []
        for r in results:
            if r.get("contentType") != "project":
                continue
            projects.append({
                "id": r.get("id"), "title": r.get("title"),
                "acronym": r.get("acronym"), "programme": r.get("programme"),
                "funding": r.get("totalCost"), "euContribution": r.get("ecMaxContribution"),
                "startDate": r.get("startDate"), "endDate": r.get("endDate"),
                "status": r.get("status"), "countries": [c.get("name") for c in (r.get("countries") or [])],
                "summary": (r.get("summary") or "")[:400],
            })
        out[kw] = {"total_raw": total, "projects": projects}
        print(f"{kw}: raw={total}, projects={len(projects)}")
        for p in projects[:5]:
            print(f"   {p['id']} | {p['acronym']} | {p['title'][:60]} | {p.get('startDate','')[:4]}-{p.get('endDate','')[:4]} | {p['status']}")
        time.sleep(3)
    json.dump(out, open("data/raw/grants_foreign/cordis_sc_aircraft_results.json", "w"), ensure_ascii=False, indent=1)
    print("\nСохранено: data/raw/grants_foreign/cordis_sc_aircraft_results.json")

if __name__ == "__main__":
    main()
