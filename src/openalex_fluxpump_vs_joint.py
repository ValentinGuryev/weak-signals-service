#!/usr/bin/env python3
"""Сравнение динамики публикаций: flux pump на CC vs сверхпроводящее соединение ВТСП-2G.

Экспертная гипотеза (пользователь): flux pump ценен, ПОКА нет сверхпроводящего
соединения ВТСП-2G. Если соединение удастся — ценность насоса упадёт.
Сравниваем динамику публикаций по двум темам (OpenAlex через прокси).

Тема 1 (flux pump): title_and_abstract "flux pump" + coated conductor/HTS
Тема 2 (соединение): title_and_abstract "superconducting joint" + REBCO/coated conductor/HTS tape

Выход:
- data/raw/openalex/fluxpump_vs_joint_corpus.json — работы обеих тем
- data/raw/openalex/fluxpump_vs_joint_counts.json  — агрегат по годам
- case_studies/003_flux_pump_space/plots/plot9_fluxpump_vs_joint.png — график
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
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "fluxpump_vs_joint_corpus.json"
AGG = PROJECT_ROOT / "data" / "raw" / "openalex" / "fluxpump_vs_joint_counts.json"
PLOT_DIR = PROJECT_ROOT / "case_studies" / "003_flux_pump_space" / "plots"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"

# Темы: (метка, цвет, запросы title_and_abstract)
TOPICS = {
    "Flux pump (CC)": ("#1f77b4", [
        '"flux pump" coated conductor',
        '"flux pump" HTS',
        '"flux pumping" coated conductor',
    ]),
    "Сверхпроводящее соединение": ("#d62728", [
        '"superconducting joint" REBCO',
        '"superconducting joint" coated conductor',
        '"superconducting joint" HTS tape',
    ]),
}

# SC-фильтр: тема должна быть про сверхпроводимость
SC_RE = re.compile(
    r"superconduct|HTS|REBCO|YBCO|coated conductor|coated conductors|flux pump|"
    r"magnet|persistent|joint|splice",
    re.I,
)
NON_SC_RE = re.compile(
    r"\bGaN\b|\bsilicon\b|\bSiC\b|perovskite solar|\bLiNi\b|\bbattery\b|\belectrode\b|"
    r"thermoelectric|\bsemiconductor\b|\bLED\b|laser diode|\bGaAs\b|\bInP\b|"
    r"metal halide|nanowire transistor|ferroelectr|solar cell|blood|medical imaging device",
    re.I,
)


def fetch(filter_str: str, per_page: int = 100, max_pages: int = 8) -> list[dict]:
    results, cursor, pages = [], "*", 0
    while cursor and pages < max_pages:
        params = {
            "filter": filter_str, "per-page": str(per_page), "cursor": cursor, "mailto": MAILTO,
            "select": "id,title,publication_year,abstract_inverted_index",
        }
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=35) as r:
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
    print("=== Сбор корпуса: flux pump vs сверхпроводящее соединение (OpenAlex через прокси) ===")
    for label, (color, queries) in TOPICS.items():
        for q in queries:
            filter_str = f"title_and_abstract.search:{q}"
            works = fetch(filter_str)
            kept = 0
            for w in works:
                if is_sc(w) and w["id"] not in corpus:
                    corpus[w["id"]] = {
                        "id": w["id"], "title": w.get("title"),
                        "year": w.get("publication_year"), "topic": label,
                    }
                    kept += 1
            print(f"  → {label} [{q}]: {len(works)} получено, +{kept}")
            time.sleep(1)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(list(corpus.values()), f, ensure_ascii=False, indent=1)
    print(f"\nСохранено: {len(corpus)} работ → {OUT}")

    by_topic_year = defaultdict(lambda: defaultdict(int))
    for w in corpus.values():
        by_topic_year[w["topic"]][w["year"] or 0] += 1

    all_years = sorted({y for d in by_topic_year.values() for y in d if 1985 <= y <= 2026})
    print("\n=== Публикации по годам ===")
    print(f"{'Тема':<28}" + "".join(f"{y % 100:>4}" for y in all_years))
    for label in TOPICS:
        row = by_topic_year[label]
        print(f"{label:<28}" + "".join(f"{row.get(y, 0):>4}" for y in all_years))

    agg = {
        "topics": list(TOPICS.keys()),
        "years": all_years,
        "counts": {t: [by_topic_year[t].get(y, 0) for y in all_years] for t in TOPICS},
        "colors": {t: c for t, (c, _) in TOPICS.items()},
        "total": {t: sum(by_topic_year[t].values()) for t in TOPICS},
    }
    with open(AGG, "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=1)
    print(f"Агрегат: {AGG}")


if __name__ == "__main__":
    main()
