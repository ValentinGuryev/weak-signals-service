#!/usr/bin/env python3
"""Сбор корпуса SNSPD (OpenAlex) для кейса 006.

Тема: сверхпроводниковые нанодетекторы одиночных фотонов (SNSPD).
Синонимы (см. KNOWHOW §7 — передавать все через OR):
  - "superconducting nanowire single photon detector", SNSPD
  - "superconducting nanowire single-photon"
  - "nanowire superconducting single photon"

Собираем по title_and_abstract.search, с фильтром по сверхпроводимости.
Выход: data/raw/openalex/snspd_corpus.json (полные записи с авторами, §4.5)
+ паспорт данных.
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
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "snspd_corpus.json"
AGG = PROJECT_ROOT / "data" / "raw" / "openalex" / "snspd_counts.json"

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"

QUERIES = [
    '"superconducting nanowire single-photon detector"',
    '"superconducting nanowire single photon detector"',
    '"superconducting nanowire single-photon detectors"',
    '"nanowire superconducting single photon"',
    '"SNSPD"',
    '"superconducting nanowire" photon detection',
]

NON_SC_RE = re.compile(
    r"\bGaN\b|\bsilicon photonics\b|semiconductor nanowire|"
    r"\bSiPM\b|perovskite|quantum dot.*laser|\bLED\b", re.I)


def fetch(filter_str: str, per_page: int = 100, max_pages: int = 10) -> list[dict]:
    results, cursor, pages = [], "*", 0
    while cursor and pages < max_pages:
        params = {
            "filter": filter_str, "per-page": str(per_page), "cursor": cursor, "mailto": MAILTO,
            # Полные записи с авторами (правило §4.5)
            "select": "id,title,publication_year,abstract_inverted_index,cited_by_count,"
                      "authorships,primary_location",
        }
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            print(f"  [err] p{pages}: {str(e)[:70]}")
            time.sleep(20)
            continue
        results.extend(data.get("results", []))
        cursor = data.get("meta", {}).get("next_cursor")
        pages += 1
        time.sleep(1.2)
    return results


def abstract_text(work: dict) -> str:
    inv = work.get("abstract_inverted_index") or {}
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def is_sc(work: dict) -> bool:
    text = f"{work.get('title') or ''} {abstract_text(work)}"
    return not NON_SC_RE.search(text)


def main():
    corpus = {}
    print("=== Сбор корпуса SNSPD (OpenAlex) ===")
    for q in QUERIES:
        filter_str = f"title_and_abstract.search:{q}"
        works = fetch(filter_str)
        added = 0
        for w in works:
            if w["id"] in corpus:
                continue
            # строгий отбор: в title/abstract должно быть про сверхпроводящую nanowire
            text = f"{w.get('title') or ''} {abstract_text(w)}".lower()
            if not is_sc(w):
                continue
            # упрощённые авторы
            authors = []
            for a in (w.get("authorships") or []):
                au = a.get("author") or {}
                inst = (a.get("institutions") or [{}])[0]
                authors.append({
                    "name": au.get("display_name"),
                    "inst": (inst.get("display_name") if inst else None),
                    "country": (inst.get("country_code") if inst else None),
                })
            corpus[w["id"]] = {
                "id": w["id"],
                "title": w.get("title"),
                "year": w.get("publication_year"),
                "cited_by": w.get("cited_by_count"),
                "authors": authors[:10],
                "source": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
            }
            added += 1
        print(f"  [{q[:60]}]: {len(works)} получено, +{added} SC")
        time.sleep(1.5)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(list(corpus.values()), f, ensure_ascii=False, indent=1)

    # Агрегат по годам
    by_year = defaultdict(int)
    for w in corpus.values():
        by_year[w["year"] or 0] += 1
    years = sorted(y for y in by_year if 2000 <= y <= 2026)
    print("\n=== Публикации по годам ===")
    for y in years:
        print(f"  {y}: {by_year[y]}")

    agg = {"total": len(corpus), "counts_by_year": {y: by_year[y] for y in years}}
    with open(AGG, "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=1)

    # Паспорт (§4.5)
    passport = PROJECT_ROOT / "case_studies" / "006_snspd" / "signals" / "data_passports" / "snspd_corpus.md"
    passport.parent.mkdir(parents=True, exist_ok=True)
    passport.write_text(
        f"# Паспорт: snspd_corpus.json\n\n"
        f"- **Файл:** `data/raw/openalex/snspd_corpus.json`\n"
        f"- **Скрипт:** `src/openalex_snspd.py`\n"
        f"- **Запросы:** title_and_abstract.search, 6 синонимов (SNSPD, superconducting nanowire single-photon...)\n"
        f"- **Дата:** {time.strftime('%Y-%m-%d')}\n"
        f"- **Записей:** {len(corpus)}\n"
        f"- **Поля:** id, title, year, cited_by, authors (name/inst/country), source\n"
        f"- **Бюджет:** OpenAlex (~10-30 запросов, без лимита на число)\n",
        encoding="utf-8",
    )
    print(f"\nСохранено: {len(corpus)} работ → {OUT}\nПаспорт: {passport}")


if __name__ == "__main__":
    main()
