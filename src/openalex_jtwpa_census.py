#!/usr/bin/env python3
"""Докачка корпуса JTWPA (кейс 007) до ПОЛНОГО покрытия ценза.

Проблема: корпус A=186, а ценз всего пространства "traveling-wave parametric amplifier"
+ josephson даёт 224. Разница ~38 — работы, где слово "josephson" НЕ в тексте, но это
Джозефсоновские TWPA (SQUID-based, SNAIL, superinductor, "TWPA" в контексте кубитов).
Чтобы публикационный сигнал НАДЁЖНО покрывал конкурентов, докачиваем и классифицируем
ВСЕ работы ценза TWPA (442) с сохранением класса:
  A_josephson / A_squid / A_snail / B_kinetic / OTHER (шум/нерелевантно) / APPL (применение без ядра)

Выход: data/raw/openalex/jtwpa_census.json — полный классифицированный ценз.
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "jtwpa_census.json"

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
SEL = "id,title,publication_year,cited_by_count,abstract_inverted_index,primary_location"


def abstracts(w: dict) -> str:
    inv = w.get("abstract_inverted_index") or {}
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def fetch(fs: str, max_pages: int = 8) -> list[dict]:
    results, cursor, pages = [], "*", 0
    while cursor and pages < max_pages:
        params = {"filter": fs, "per-page": "100", "cursor": cursor, "mailto": MAILTO, "select": SEL}
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        for att in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=45) as r:
                    d = json.load(r)
                results.extend(d.get("results", []))
                cursor = d.get("meta", {}).get("next_cursor")
                pages += 1
                break
            except Exception as e:
                time.sleep(40 if "429" in str(e) else 12)
        else:
            break
        time.sleep(1.0)
    return results


NON_SC = re.compile(
    r"plasma|whistler|ion-ring|topological|optical fiber|semiconductor laser|"
    r"travelling wave tube|klystron|magnetron|laser plasma", re.I)


def classify(w: dict) -> str:
    t = ((w.get("title") or "") + " " + abstracts(w)).lower()
    if NON_SC.search(t):
        return "NONSC"
    jos = "josephson" in t or "jj" in t.split()
    squid = "squid" in t
    snail = "snail" in t or "superconducting nonlinear asymmetric" in t
    kin = "kinetic inductance" in t
    has_tw = ("traveling" in t) or ("travelling" in t)
    has_par = "parametric" in t
    has_amp = ("amplif" in t) or ("amplifier" in t)
    if not has_amp:
        return "NONSC" if not has_par else "APPL"
    if has_par and has_tw:
        if jos or squid:
            return "A_josephson" if jos else "A_squid"
        if snail:
            return "A_snail"
        if kin:
            return "B_kinetic"
        # TWPA без явного типа — смотрим: возможно KIT без слов или неясно
        return "TWPA_unspecified"
    if jos and has_par:  # резонаторный JPA
        return "C_JPA_res"
    if kin and ("amplif" in t):
        return "B_kinetic"
    if squid and "amplif" in t:
        return "A_squid"
    return "APPL"


def main():
    print("=== Ценз TWPA: сбор и классификация ===")
    seen = {}
    for q in ('"traveling-wave parametric amplifier"', '"travelling-wave parametric amplifier"'):
        for w in fetch("title_and_abstract.search:" + q):
            seen[w["id"]] = w
    # + резонаторные JPA (Josephson parametric amplifier) — тоже конкуренты
    for w in fetch('"Josephson parametric amplifier"', max_pages=8):
        if w["id"] not in seen:
            seen[w["id"]] = w
    print(f"Всего уникальных в цензе: {len(seen)}")

    classes = defaultdict(list)
    for w in seen.values():
        c = classify(w)
        y = w.get("publication_year") or 0
        if 2007 <= y <= 2026:
            classes[c].append(w)
    for c in sorted(classes):
        print(f"  {c:18s} {len(classes[c])}")

    # --- сохранить ---
    out = {"total": len(seen),
           "classes": {c: [{"id": w["id"], "title": w.get("title"), "year": w.get("publication_year"),
                            "cited_by": w.get("cited_by_count"),
                            "source": ((w.get("primary_location") or {}).get("source") or {}).get("display_name")}
                           for w in ws] for c, ws in classes.items()}}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT}")


if __name__ == "__main__":
    main()
