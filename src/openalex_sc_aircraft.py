#!/usr/bin/env python3
"""Сбор корпуса OpenAlex для кейса 008 (СП-авиадвигатели) — оптимизированный (полный select).

Тема: сверхпроводящие (ВТСП) двигатели/генераторы для авиации (propulsion).
Вопрос: был ли это зарождающийся тренд в 2018 (гонка E-Fan X/ASuMED) и состоялся ли к 2026?

Классы:
  core  = сверхпроводящий мотор/машина/пропульсия в АВИАЦИИ (кейс)
  (electric/cryogenic — конкуренты, только counts)
Полный select: абстракты (S2) + referenced_works (S3) + authorships (гео) одним проходом.
"""
import sys, json, re, time, urllib.parse, urllib.request
from collections import Counter
from pathlib import Path

CASE = "sc_aircraft_motors"
TOPIC = "сверхпроводящие двигатели для авиации"

# Ядро: сверхпроводящий + мотор/машина + авиация (кавычки = точные фразы)
Q_CORE = [
    '"superconducting motor" (aircraft OR aviation OR aerospace OR flight)',
    '"superconducting machine" (aircraft OR aviation OR aerospace)',
    '"superconducting propulsion" (aircraft OR aviation OR aerospace)',
    '"high temperature superconducting" (motor OR machine OR propulsion) (aircraft OR aviation OR aerospace)',
    '"superconducting" (motor OR machine) "electric aircraft"',
]
# Конкуренты/альтернативы — только counts (group_by), работы НЕ качаем
Q_COUNTS = [
    '"electric aircraft" motor',
    '"electric propulsion" aircraft motor',
    'cryogenic (motor OR machine) aircraft',
    '"hydrogen" OR "fuel cell" aircraft propulsion',
]

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
SELECT = ("id,title,publication_year,cited_by_count,abstract_inverted_index,"
          "referenced_works,authorships,primary_location,concepts")
MAX_PAGES = 40

def abstract_text(w):
    inv = w.get("abstract_inverted_index") or {}
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))

def classify(text):
    """core = сверхпроводящий + (мотор/машина/пропульсия) + авиация. None = шум."""
    t = text.lower()
    sc = re.search(r'superconduct|hts|mgb2|rebco|ybco', t)
    if not sc: return None
    mot = re.search(r'\bmotor\b|\bmachine\b|\bpropulsion\b|\bgenerator\b|\bmotor\b', t)
    if not mot: return None
    av = re.search(r'aircraft|aviation|aerospace|\bflight\b|\baero\b', t)
    if not av: return None
    # исключить не-авиационные (судовые и т.п.), если авиация не главная — оставляем, помечаем
    return 'core'

def simplify(w):
    auths = []
    for a in (w.get("authorships") or []):
        au = a.get("author") or {}
        inst = (a.get("institutions") or [{}])[0]
        auths.append({"name": au.get("display_name"), "country": inst.get("country_code"),
                      "inst": inst.get("display_name")})
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    return {"id": w.get("id"), "title": w.get("title"), "year": w.get("publication_year"),
            "cited_by": w.get("cited_by_count"), "abstract": abstract_text(w),
            "referenced_works": w.get("referenced_works") or [], "authors": auths,
            "source": src.get("display_name"), "doi": loc.get("doi")}

def fetch(filter_str):
    results, cursor, pages = [], "*", 0
    while cursor and pages < MAX_PAGES:
        params = {"filter": filter_str, "per-page": "100", "cursor": cursor,
                  "mailto": MAILTO, "select": SELECT}
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
            results.extend(data.get("results", []))
            cursor = data.get("meta", {}).get("next_cursor")
            pages += 1
            time.sleep(0.4)
        except Exception as e:
            print(f"  ! fetch: {e}", file=sys.stderr); time.sleep(8)
    return results

def counts_by_year(query):
    params = {"filter": "title_and_abstract.search:" + query,
              "group_by": "publication_year", "per-page": "50", "mailto": MAILTO}
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=60) as r:
            return {g["key"]: g["count"] for g in (json.load(r).get("group_by") or [])}
    except Exception as e:
        print(f"  ! counts: {e}", file=sys.stderr); return {}

OUT = Path("data/raw/openalex")
def main():
    works, seen = [], set()
    for q in Q_CORE:
        print(f"\n[core] {q}")
        for w in fetch(f'title_and_abstract.search:{q}'):
            text = f"{w.get('title') or ''} {abstract_text(w)}"
            if not classify(text): continue
            if w.get("id") in seen: continue
            seen.add(w.get("id")); works.append(simplify(w))
    print(f"\nЯдро: {len(works)} работ")
    with open(OUT/f"{CASE}_corpus.json","w") as f:
        json.dump({"query_core": Q_CORE, "topic": TOPIC, "works": works}, f, ensure_ascii=False, indent=1)
    # counts
    counts = {}
    cy = Counter()
    for q in Q_CORE[:2]:
        for y,c in counts_by_year(q).items(): cy[y] = max(cy[y], c)
    counts["core"] = dict(sorted(cy.items()))
    for i,q in enumerate(Q_COUNTS):
        counts[f"q{i}"] = counts_by_year(q); time.sleep(0.4)
    with open(OUT/f"{CASE}_counts.json","w") as f:
        json.dump(counts, f, ensure_ascii=False, indent=1)
    print("Counts сохранены")
    # паспорт
    with open(OUT/f"{CASE}_passport.md","w") as f:
        f.write(f"# Паспорт: корпус {CASE}\n- Тема: {TOPIC}\n- Запросы: {Q_CORE}\n- Работ: {len(works)}\n- select: {SELECT}\n- Дата: {time.strftime('%Y-%m-%d')}\n")
    print("Паспорт сохранён")

if __name__ == "__main__":
    main()
