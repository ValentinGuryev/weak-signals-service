#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 012: корпус проблемы «подземные линии в мегаполисах → сверхпроводящие DC-кабели».

ШАГ 2 GUIDE — «от проблемы»: формулируем запросы из саМой проблемы (городские ЛЭП, уход под землю)
и конкурентов (AC-ВТСП, медь+криоохлаждение, традиционные XLPE/GIL, HVDC, DC-распределение в ЦОД).

Таксономия (7 групп конкурентов + тренд):
  HTS-DC   — сверхпроводящие DC-кабели (ТРЕНД)
  HTS-AC   — сверхпроводящие AC-кабели (компетент 1)
  CU-CRYO  — медь + криогенное охлаждение (компетент 2, вопрос автора «может медь просто азотом охлаждать»)
  CU-DC    — обычные медные DC-линии / XLPE / HVDC (компетент 3)
  GIL      — газоизолированные линии (компетент 4)
  URBAN    — проблема: городские ЛЭП, подземные коридоры, right-of-way (рамка проблемы)
  DATACENTER — питание дата-центров DC (новая ниша спроса)

MERGE-идемпотентно (как 011), 429→backoff 30/60/120.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/raw/openalex/dc_cables_problem.json"
HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
MAX_PAGES = 25

SELECT = ("id,doi,title,display_name,publication_year,cited_by_count,publication_date,"
          "abstract_inverted_index,authorships,referenced_works,type,concepts")

# (group, label, query) — запросы от проблемы
QUERIES = [
    # ── ТРЕНД: сверхпроводящие HTS DC-кабели ──
    ("HTS-DC", "t1 hts dc cable", '"superconducting" AND "DC cable"'),
    ("HTS-DC", "t2 hts power cable", '"high temperature superconducting" AND ("power cable" OR "cable")'),
    ("HTS-DC", "t3 hts dc transmission", '"superconducting" AND ("DC transmission" OR "dc link" OR "dc power")'),
    ("HTS-DC", "t4 hts line city", '"superconducting" AND "cable line" AND ("city" OR "urban" OR "grid")'),
    ("HTS-DC", "t5 hts current lead", '"superconducting" AND "fault current" AND ("cable" OR "line")'),

    # ── КОМПЕТЕНТ 1: AC сверхпроводящие кабели ──
    ("HTS-AC", "a1 hts ac cable", '"superconducting" AND "AC cable"'),
    ("HTS-AC", "a2 hts ac line", '"superconducting" AND ("AC transmission" OR "AC power cable")'),
    ("HTS-AC", "a3 hts fault current limiter", '"superconducting fault current limiter"'),
    ("HTS-AC", "a4 ampa/lip/tesla", '"AmpaCity" OR "HTS cable" AND "Albany"'),

    # ── КОМПЕТЕНТ 2: медь + криоохлаждение (вопрос автора) ──
    ("CU-CRYO", "c1 cryocable", '"cryogenic cable" AND ("copper" OR "aluminum" OR "conductor")'),
    ("CU-CRYO", "c2 cold conductor", '"cryogenically cooled" AND ("cable" OR "transmission line" OR "conductor")'),
    ("CU-CRYO", "c3 copper LN2", '"liquid nitrogen" AND ("cable" OR "transmission") AND ("copper" OR "aluminum")'),
    ("CU-CRYO", "c4 superconducting vs copper", '"superconducting" AND "copper" AND ("loss" OR "efficiency" OR "compact")'),

    # ── КОМПЕТЕНТ 3: обычные медные DC / XLPE / HVDC ──
    ("CU-DC", "d1 xlpe underground", '"XLPE" AND ("cable" OR "underground" OR "transmission")'),
    ("CU-DC", "d2 hvdc underground", '"HVDC" AND ("underground" OR "city" OR "space")'),
    ("CU-DC", "d3 hvdc transmission", '"HVDC" AND ("transmission" OR "line")'),
    ("CU-DC", "d4 copper loss", '"power loss" AND ("cable" OR "transmission line") AND ("city" OR "underground")'),

    # ── КОМПЕТЕНТ 4: газоизолированные линии (GIL) ──
    ("GIL", "g1 gil", '"gas-insulated" AND ("line" OR "transmission" OR "cable")'),
    ("GIL", "g2 gil hvdc", '"gas insulated line"'),

    # ── ПРОБЛЕМА: городские ЛЭП, подземные коридоры ──
    ("URBAN", "u1 urban grid", '"urban" AND ("power grid" OR "distribution" OR "transmission") AND "cable"'),
    ("URBAN", "u2 underground line", '"underground" AND ("power line" OR "cable" OR "transmission")'),
    ("URBAN", "u3 right of way", '"right of way" AND ("power" OR "transmission" OR "cable")'),
    ("URBAN", "u4 substation city", '"substation" AND ("city" OR "urban") AND ("capacity" OR "expansion")'),

    # ── НИША: питание дата-центров (новый драйвер) ──
    ("DATACENTER", "e1 dc data center", '"data center" AND ("DC power" OR "380 V" OR "800 V" OR "distribution")'),
    ("DATACENTER", "e2 hvdc data center", '"HVDC" AND ("data center" OR "hyperscaler")'),
    ("DATACENTER", "e3 datacenter efficiency", '"data center" AND ("efficiency" OR "power delivery") AND ("DC" OR "voltage")'),
    ("DATACENTER", "e4 dc microgrid", '"data center" AND "microgrid" AND "DC"'),
]


def api_get(url: str) -> dict:
    for attempt, wait in [(1, 30), (2, 60), (3, 120)]:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            print(f"    retry {attempt}: {e} — жду {wait}s", flush=True)
            time.sleep(wait)
    return {}


def parse_work(w: dict, group: str) -> dict:
    inv = w.get("abstract_inverted_index")
    abstract = None
    if inv:
        pos = {}
        for word, idxs in inv.items():
            for i in idxs:
                pos[i] = word
        abstract = " ".join(pos[i] for i in sorted(pos))
    authors = []
    for a in (w.get("authorships") or []):
        au = a.get("author") or {}
        inst = ((a.get("institutions") or [{}])[0] or {}).get("display_name")
        authors.append({"name": au.get("display_name"), "institution": inst})
    return {
        "id": w.get("id"), "doi": w.get("doi"), "title": w.get("title") or w.get("display_name"),
        "year": w.get("publication_year"), "date": w.get("publication_date"),
        "cited_by": w.get("cited_by_count"), "abstract": abstract,
        "authors": authors, "references": w.get("referenced_works"),
        "type": w.get("type"),
        "concepts": [c.get("display_name") for c in (w.get("concepts") or [])],
        "group": group,
    }


def save(works: dict) -> None:
    ws = sorted(works.values(), key=lambda w: (w["year"] or 0))
    out = {
        "case": "012_dc_hvdc_cables", "signal": "s1a_publications_problem",
        "date": "2026-09-14",
        "method": "OpenAlex title_and_abstract.search от проблемы (7 групп конкурентов), cursor, "
                   "дедуп по id, MERGE-идемпотентно + сохранение после каждого запроса; backoff 30/60/120",
        "queries": [{"group": g, "label": l, "query": q} for g, l, q in QUERIES],
        "n_works": len(ws), "works": ws,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)


def main():
    supp = {}
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        for w in old["works"]:
            supp[w["id"]] = w
    seen = set(supp)
    print(f"seen: {len(seen)} работ в существующем корпусе", flush=True)

    for group, label, q in QUERIES:
        enc = urllib.parse.quote(q)
        cursor = "*"
        pages = 0
        zero_pages = 0
        n_new = 0
        print(f"=== [{group}] {label} …", flush=True)
        while cursor and pages < MAX_PAGES:
            url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
                   f"&per-page=200&select={SELECT}&cursor={cursor}&mailto={MAILTO}")
            d = api_get(url)
            results = d.get("results", [])
            if not results:
                break
            add = 0
            for w in results:
                wid = w.get("id")
                if wid and wid not in seen:
                    seen.add(wid)
                    supp[wid] = parse_work(w, group)
                    add += 1
            n_new += add
            pages += 1
            cursor = d.get("meta", {}).get("next_cursor")
            zero_pages = zero_pages + 1 if add == 0 else 0
            print(f"    стр.{pages}: +{add} (по {label}: {n_new}; всего {len(supp)})", flush=True)
            time.sleep(2.0)
            if zero_pages >= 3:
                print("    → перекрыто, ранняя остановка", flush=True)
                break
        print(f"  ИТОГО [{group}] {label}: +{n_new}", flush=True)
        save(supp)  # ⚠️ прогресс-сохранение после каждого запроса

    print(f"\nГотово: корпус {len(supp)} работ → {OUT}", flush=True)


if __name__ == "__main__":
    main()