#!/usr/bin/env python3
"""График выхода статей по годам: RCE (reactive co-evaporation) vs TLAG — OpenAlex.

МЕТОДОЛОГИЯ (уточнена 2026-08-31 после проверки полноты):
- Фильтр: title_and_abstract.search:"<метод>" — точный поиск по заголовку И абстракту
  (не fulltext! fulltext даёт шум: reactive co-evaporation=186, из них title+abstract=67)
- Локальный SC-фильтр (целые слова): отсекает не-сверхпроводящее
- RCE: title_and_abstract.search:"reactive co-evaporation" + SC → 51 работа
- TLAG: title_and_abstract.search:"transient liquid assisted growth" ∪
        title_and_abstract.search:"liquid assisted growth" + SC → 31 работа

Данные через прокси (локальный SOCKS-прокси) для обхода rate-limit OpenAlex.

Выход:
- data/raw/openalex/growth_methods_corpus.json — работы RCE + TLAG
- data/raw/openalex/growth_methods_counts.json  — агрегат по годам
- case_studies/002_rce_dr_sunam/plots/plot8_rcetlag_pubs.png — график
"""
from __future__ import annotations

import json
import re
import socket
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

import socks

socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9051, rdns=True)
socket.socket = socks.socksocket

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "growth_methods_corpus.json"
AGG = PROJECT_ROOT / "data" / "raw" / "openalex" / "growth_methods_counts.json"
PLOT_DIR = PROJECT_ROOT / "case_studies" / "002_rce_dr_sunam" / "plots"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"

# Метод -> (метка, цвет, запросы title_and_abstract)
METHODS = {
    "RCE co-evaporation": ("#d62728", ['"reactive co-evaporation"']),
    "TLAG": ("#1f77b4", ['"transient liquid assisted growth"', '"liquid assisted growth"']),
}

SC_RE = re.compile(
    r"\bREBCO\b|\bYBCO\b|\bGdBCO\b|\bSmBCO\b|\bEuBCO\b|\bNdBCO\b|coated conductor|coated conductors|"
    r"superconducting|superconductor|\bHTS\b|high.temperature superconducting|"
    r"Ba2Cu3O7|Ba₂Cu₃O₇|yttrium barium|rare.earth|REBa2Cu3O7|cuprate",
    re.I,
)
NON_SC_RE = re.compile(
    r"\bGaN\b|\bsilicon\b|\bSiC\b|perovskite solar|\bLiNi\b|\bbattery\b|\belectrode\b|"
    r"thermoelectric|\bsemiconductor\b|\bLED\b|laser diode|\bGaAs\b|\bInP\b|"
    r"metal halide|nanowire transistor|ferroelectr|solar cell",
    re.I,
)


def fetch(filter_str: str, per_page: int = 100, max_pages: int = 10) -> list[dict]:
    results, cursor, pages = [], "*", 0
    while cursor and pages < max_pages:
        params = {
            "filter": filter_str, "per-page": str(per_page), "cursor": cursor, "mailto": MAILTO,
            "select": "id,title,publication_year,abstract_inverted_index",
        }
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            print(f"  [err] {filter_str[:40]} p{pages}: {e}")
            time.sleep(15)
            continue
        results.extend(data.get("results", []))
        cursor = data.get("meta", {}).get("next_cursor")
        pages += 1
        time.sleep(0.8)
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
    return not NON_SC_RE.search(text) and bool(SC_RE.search(text))


def main():
    corpus = {}
    print("=== Сбор корпуса RCE vs TLAG (OpenAlex через прокси, title_and_abstract) ===")
    for label, (color, queries) in METHODS.items():
        for q in queries:
            filter_str = f"title_and_abstract.search:{q}"
            works = fetch(filter_str)
            kept = 0
            for w in works:
                if is_sc(w) and w["id"] not in corpus:
                    corpus[w["id"]] = {
                        "id": w["id"], "title": w.get("title"),
                        "year": w.get("publication_year"), "method": label,
                    }
                    kept += 1
            print(f"  → {label} [{q}]: {len(works)} получено, +{kept} SC")
            time.sleep(1)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(list(corpus.values()), f, ensure_ascii=False, indent=1)
    print(f"\nСохранено: {len(corpus)} работ → {OUT}")

    by_method_year = defaultdict(lambda: defaultdict(int))
    for w in corpus.values():
        by_method_year[w["method"]][w["year"] or 0] += 1

    all_years = sorted({y for d in by_method_year.values() for y in d if 1990 <= y <= 2026})
    print("\n=== Статьи по годам (title+abstract) ===")
    print(f"{'Метод':<22}" + "".join(f"{y % 100:>4}" for y in all_years))
    for label in METHODS:
        row = by_method_year[label]
        print(f"{label:<22}" + "".join(f"{row.get(y, 0):>4}" for y in all_years))

    agg = {
        "methods": list(METHODS.keys()),
        "years": all_years,
        "counts": {m: [by_method_year[m].get(y, 0) for y in all_years] for m in METHODS},
        "colors": {m: c for m, (c, _) in METHODS.items()},
        "total": {m: sum(by_method_year[m].values()) for m in METHODS},
        "methodology": "title_and_abstract.search + SC-фильтр (целые слова)",
    }
    with open(AGG, "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=1)
    print(f"Агрегат: {AGG}")


if __name__ == "__main__":
    main()
