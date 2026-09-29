#!/usr/bin/env python3
"""Сбор корпуса JTWPA (OpenAlex) для кейса 007.

Тема: джозефсоновские проточные параметрические усилители (JTWPA) —
quantum-limited усилители СВЧ для чтения кубитов, аксионных поисков, радиоастрономии.

Классы (важно для терминологии, KNOWHOW §7 — все синонимы через OR):
  A) JTWPA-ядро (кейс):      josephson + (traveling|travelling) wave + parametric amplifier
  B) KITWPA/KIPA (сосед):    kinetic inductance + traveling wave + amplifier, БЕЗ josephson
  C) JPA (конкурент):        josephson + parametric amplifier, БЕЗ traveling wave (резонаторный)

OpenAlex нормализует traveling/travelling в поиске (проверено 2026-09-05: оба написания → 160).
Широкие запросы + строгий текстовый фильтр по классам (title + abstract).

Выход:
- data/raw/openalex/jtwpa_corpus.json   полные записи классов A+B (с авторами, §4.5)
- data/raw/openalex/jtwpa_counts.json   counts по годам: A, B, C (group_by)
+ паспорт данных в case_studies/007_jtwpa/signals/data_passports/
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
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "jtwpa_corpus.json"
AGG = PROJECT_ROOT / "data" / "raw" / "openalex" / "jtwpa_counts.json"

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"

# --- Широкие запросы (title_and_abstract.search; пробел = AND) -----------------
# Класс A: josephson + traveling wave + amplifier (любой порядок слов)
Q_CORE = [
    '"Josephson traveling-wave parametric amplifier"',
    '"Josephson travelling-wave parametric amplifier"',
    '"JTWPA"',
    '"TWPA" josephson',
    '"traveling-wave parametric amplifier" josephson',
    '"travelling-wave parametric amplifier" josephson',
    'josephson "traveling wave" amplifier',
    'josephson "travelling wave" amplifier',
]
# Класс B: kinetic-inductance проточные усилители (KITWPA/KIPA) — соседняя технология
Q_KIT = [
    '"kinetic inductance" "traveling-wave" amplifier',
    '"kinetic inductance" "travelling-wave" amplifier',
    '"KITWPA"',
    '"KIPA" superconducting amplifier',
]
# Класс C: резонаторные джозефсоновские параметрические усилители (JPA) — конкурент
Q_JPA = [
    '"Josephson parametric amplifier"',
    '"JPA" josephson',
    '"Josephson parametric converter"',
]

NON_SC_RE = re.compile(
    r"semiconductor|silicon photonics|\bHEMT\b|\bHFET\b|optical fiber|"
    r"laser|photodetector|optical parametric", re.I)

MAX_PAGES = 15  # 15*100 = 1500 работ на запрос — запас


def abstract_text(work: dict) -> str:
    inv = work.get("abstract_inverted_index") or {}
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def fetch(filter_str: str, select: str) -> list[dict]:
    """Полная пагинация по cursor. select — поля для работы."""
    results, cursor, pages = [], "*", 0
    while cursor and pages < MAX_PAGES:
        params = {"filter": filter_str, "per-page": "100", "cursor": cursor,
                  "mailto": MAILTO, "select": select}
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            msg = str(e)
            if "429" in msg:
                print(f"    429 — пауза 60с (упрёмся — переключиться на VPS-прокси)")
                time.sleep(60)
                continue
            print(f"    [err] p{pages}: {msg[:70]}")
            time.sleep(20)
            continue
        results.extend(data.get("results", []))
        cursor = data.get("meta", {}).get("next_cursor")
        pages += 1
        time.sleep(1.2)
    return results


def classify(text: str) -> str | None:
    """Класс A/B/C по тексту (title+abstract). Возвращает None если нерелевантно."""
    t = text.lower()
    if NON_SC_RE.search(t):
        return None
    has_jos = "josephson" in t
    has_tw = ("traveling" in t) or ("travelling" in t)
    has_amp = ("amplif" in t) or ("amplifier" in t)
    has_paramp = "parametric" in t
    has_kin = "kinetic inductance" in t
    if not has_amp:
        return None
    # A: джозефсоновский проточный параметрический усилитель
    if has_jos and has_tw and has_paramp:
        return "A"
    # B: проточный на кинетической индуктивности (KITWPA) — не джозефсоновский
    if has_kin and has_tw and not has_jos:
        return "B"
    # C: резонаторный JPA (без traveling wave)
    if has_jos and has_paramp and not has_tw:
        return "C"
    return None


def simplify(work: dict) -> dict:
    authors = []
    for a in (work.get("authorships") or []):
        au = a.get("author") or {}
        inst = (a.get("institutions") or [{}])[0]
        authors.append({
            "name": au.get("display_name"),
            "inst": (inst.get("display_name") if inst else None),
            "country": (inst.get("country_code") if inst else None),
        })
    return {
        "id": work["id"],
        "title": work.get("title"),
        "year": work.get("publication_year"),
        "cited_by": work.get("cited_by_count"),
        "authors": authors[:10],
        "source": ((work.get("primary_location") or {}).get("source") or {}).get("display_name"),
    }


SELECT = ("id,title,publication_year,cited_by_count,abstract_inverted_index,"
          "authorships,primary_location")


def main():
    corpus: dict[str, dict] = {}   # id -> {work..., class}
    class_count = defaultdict(int)

    print("=== Сбор корпуса JTWPA (OpenAlex), классы A/B ===")
    for q in Q_CORE + Q_KIT:
        works = fetch(f"title_and_abstract.search:{q}", SELECT)
        added_a = added_b = 0
        for w in works:
            text = f"{w.get('title') or ''} {abstract_text(w)}"
            cls = classify(text)
            if cls not in ("A", "B"):
                continue
            wid = w["id"]
            if wid in corpus:
                continue
            rec = simplify(w)
            rec["class"] = cls
            corpus[wid] = rec
            class_count[cls] += 1
            if cls == "A":
                added_a += 1
            else:
                added_b += 1
        print(f"  [{q[:55]}]: {len(works)} пол., +A={added_a} +B={added_b}")
        time.sleep(1.0)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(list(corpus.values()), f, ensure_ascii=False, indent=1)
    print(f"\nКорпус: A={class_count['A']}, B={class_count['B']} → {OUT}")

    # --- counts по годам для A/B (из корпуса) + C (отдельный запрос) -----------
    by_year = defaultdict(lambda: defaultdict(int))
    for w in corpus.values():
        y = w["year"] or 0
        if 2000 <= y <= 2026:
            by_year[w["class"]][y] += 1

    print("\n=== JTWPA (A) по годам ===")
    for y in sorted(by_year["A"]):
        print(f"  {y}: {by_year['A'][y]}")
    print("=== KITWPA (B) по годам ===")
    for y in sorted(by_year["B"]):
        print(f"  {y}: {by_year['B'][y]}")

    # Класс C (JPA) — только counts, отдельный лёгкий запрос
    c_counts = {}
    print("\n=== JPA (C) counts по годам (group_by) ===")
    for q in Q_JPA:
        params = {"filter": "title_and_abstract.search:" + q,
                  "group_by": "publication_year", "per-page": "50", "mailto": MAILTO}
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            print(f"  [err] {str(e)[:70]}")
            time.sleep(15)
            continue
        for g in data.get("group_by", []):
            y = int(g["key"])
            if 2000 <= y <= 2026 and g["count"] > c_counts.get(y, 0):
                c_counts[y] = g["count"]
        time.sleep(1.2)
    for y in sorted(c_counts):
        print(f"  {y}: {c_counts[y]}")

    agg = {
        "total_A": class_count["A"], "total_B": class_count["B"], "total_C": sum(c_counts.values()),
        "counts_A": {y: by_year["A"][y] for y in sorted(by_year["A"])},
        "counts_B": {y: by_year["B"][y] for y in sorted(by_year["B"])},
        "counts_C": {y: c_counts[y] for y in sorted(c_counts)},
    }
    with open(AGG, "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=1)

    # --- Паспорт (§4.5) ---
    passport = (PROJECT_ROOT / "case_studies" / "007_jtwpa" / "signals" / "data_passports"
                / "jtwpa_corpus.md")
    passport.parent.mkdir(parents=True, exist_ok=True)
    passport.write_text(
        f"# Паспорт: jtwpa_corpus.json\n\n"
        f"- **Файл:** `data/raw/openalex/jtwpa_corpus.json`\n"
        f"- **Скрипт:** `src/openalex_jtwpa.py`\n"
        f"- **Запросы:** title_and_abstract.search, 12 синонимов (8 core-JTWPA + 4 KITWPA)\n"
        f"- **Дата:** {time.strftime('%Y-%m-%d')}\n"
        f"- **Записей:** {len(corpus)} (A-JTWPA={class_count['A']}, B-KITWPA={class_count['B']})\n"
        f"- **Поля:** id, title, year, cited_by, class(A/B), authors (name/inst/country), source\n"
        f"- **Класс C (JPA, counts только):** jtwpa_counts.json → counts_C\n"
        f"- **Бюджет:** OpenAlex (~30-60 запросов, без лимита на число; прямой доступ)\n",
        encoding="utf-8",
    )
    print(f"\nПаспорт: {passport}")


if __name__ == "__main__":
    main()
