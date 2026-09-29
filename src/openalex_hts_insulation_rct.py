#!/usr/bin/env python3
"""Сбор корпуса статей по теплопроводящей изоляции + контролю R_ct (OpenAlex).

Тема (для кейса 004, NI-coils): конкурирующая технология — НЕ убирать изоляцию,
а сделать её теплопроводящей / контролировать контактное сопротивление.

Методология (по образцу openalex_growth_methods.py):
- filter: title_and_abstract.search:"<фраза>" — точный поиск по заголовку И абстракту;
- Локальный SC-фильтр (целые слова): отсекает не-сверхпроводящее;
- 4 подтемы:
  1. insulation_thermal — теплопроводящая изоляция (thermal conductivity + insulation + HTS)
  2. insulation_materials — изоляционные материалы для HTS (alumina/polyimide/kapton/epoxy + HTS)
  3. rct_contact — контактное сопротивление виток-виток (contact resistivity + REBCO/NI)
  4. rct_control — контроль R_ct (surface coating/oxide + REBCO)
- Выход: data/raw/openalex/hts_insulation_rct_corpus.json + counts по годам.

Внимание: OpenAlex rate-limit. Через SOCKS-прокси (как в growth_methods) или прямой доступ с паузами.
"""
from __future__ import annotations

import json
import re
import socket
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

import socks

# --- SOCKS-прокси прокси (недоступен 2026-09-01; прямой доступ работает) ---
# try:
#     socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9051, rdns=True)
#     socket.socket = socks.socksocket
#     print("[proxy] SOCKS-прокси 127.0.0.1:9051")
# except Exception as e:
#     print(f"[proxy] нет: {e}")
print("[proxy] прямой доступ (SOCKS-прокси недоступен)")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "hts_insulation_rct_corpus.json"
AGG = PROJECT_ROOT / "data" / "raw" / "openalex" / "hts_insulation_rct_counts.json"

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"

# Подтема -> (метка, список фраз для title_and_abstract.search)
TOPICS = {
    "insulation_thermal": (
        "Теплопроводящая изоляция HTS",
        [
            '"thermal conductivity" insulation superconducting coil',
            '"thermally conductive" insulation superconducting',
            'insulation "thermal conductivity" REBCO',
            'insulation "thermal conductivity" YBCO coil',
        ],
    ),
    "insulation_materials": (
        "Изоляционные материалы для HTS",
        [
            'alumina insulation superconducting magnet',
            'polyimide insulation superconducting coil',
            'kapton insulation REBCO coil',
            'epoxy insulation superconducting magnet "thermal conductivity"',
        ],
    ),
    "rct_contact": (
        "Контактное сопротивление виток-виток",
        [
            '"contact resistivity" REBCO coil',
            '"contact resistance" "no-insulation" REBCO',
            '"turn-to-turn" contact REBCO coil',
            '"contact resistivity" "coated conductor"',
        ],
    ),
    "rct_control": (
        "Контроль R_ct (покрытия/оксиды)",
        [
            '"surface coating" contact REBCO coil',
            'oxide layer "contact resistivity" superconducting',
            'coating "contact resistivity" REBCO',
            '"controlled contact" REBCO coil',
            '"contact resistivity" oxide REBCO',
            '"surface treatment" "contact resistivity" superconducting',
        ],
    ),
    "smart_insulation": (
        "Переключаемая изоляция (smart)",
        [
            'varistor insulation superconducting',
            'vanadium trioxide insulation REBCO',
            '"metal-to-insulator transition" REBCO insulation',
            '"smart insulation" superconducting coil',
            'V2O3 insulation superconducting',
        ],
    ),
}

SC_RE = re.compile(
    r"\bREBCO\b|\bYBCO\b|\bGdBCO\b|\bSmBCO\b|\bEuBCO\b|\bNdBCO\b|coated conductor|coated conductors|"
    r"superconducting|superconductor|\bHTS\b|high.temperature superconducting|"
    r"Ba2Cu3O7|Ba₂Cu₃O₇|yttrium barium|rare.earth|REBa2Cu3O7|cuprate|\bNI\b|\bMI\b|no.insulation|"
    r"varistor|vanadium trioxide|V2O3|V₂O₃|metal.to.insulator transition",
    re.I,
)
NON_SC_RE = re.compile(
    r"\bGaN\b|\bsilicon\b|\bSiC\b|perovskite solar|\bLiNi\b|\bbattery\b|\belectrode\b|"
    r"thermoelectric|\bsemiconductor\b|\bLED\b|laser diode|\bGaAs\b|\bInP\b|"
    r"metal halide|nanowire transistor|ferroelectr|solar cell|superconducting diode effect",
    re.I,
)


def fetch(filter_str: str, per_page: int = 100, max_pages: int = 5) -> list[dict]:
    results, cursor, pages = [], "*", 0
    while cursor and pages < max_pages:
        params = {
            "filter": filter_str, "per-page": str(per_page), "cursor": cursor, "mailto": MAILTO,
            "select": "id,title,publication_year,abstract_inverted_index,cited_by_count",
        }
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            print(f"  [err] {filter_str[:50]} p{pages}: {str(e)[:60]}")
            time.sleep(20)
            continue
        results.extend(data.get("results", []))
        cursor = data.get("meta", {}).get("next_cursor")
        pages += 1
        time.sleep(1.5)
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
    print("=== Сбор корпуса: теплопроводящая изоляция + контроль R_ct (OpenAlex) ===")
    for key, (label, queries) in TOPICS.items():
        for q in queries:
            filter_str = f"title_and_abstract.search:{q}"
            works = fetch(filter_str)
            kept = 0
            for w in works:
                if is_sc(w) and w["id"] not in corpus:
                    corpus[w["id"]] = {
                        "id": w["id"], "title": w.get("title"),
                        "year": w.get("publication_year"), "topic": key,
                        "cited_by": w.get("cited_by_count"),
                    }
                    kept += 1
            print(f"  → {label} [{q}]: {len(works)} получено, +{kept} SC")
            time.sleep(2)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(list(corpus.values()), f, ensure_ascii=False, indent=1)
    print(f"\nСохранено: {len(corpus)} работ → {OUT}")

    by_topic_year = defaultdict(lambda: defaultdict(int))
    for w in corpus.values():
        by_topic_year[w["topic"]][w["year"] or 0] += 1

    all_years = sorted({y for d in by_topic_year.values() for y in d if 1990 <= y <= 2026})
    print("\n=== Статьи по годам (title+abstract) ===")
    for key, (label, _) in TOPICS.items():
        row = by_topic_year[key]
        print(f"{label:<40}" + "".join(f"{row.get(y, 0):>4}" for y in all_years))

    agg = {
        "topics": {k: v[0] for k, v in TOPICS.items()},
        "years": all_years,
        "counts": {k: [by_topic_year[k].get(y, 0) for y in all_years] for k in TOPICS},
        "total": {k: sum(by_topic_year[k].values()) for k in TOPICS},
        "methodology": "title_and_abstract.search + SC-фильтр (целые слова); 4 подтемы",
    }
    with open(AGG, "w", encoding="utf-8") as f:
        json.dump(agg, f, ensure_ascii=False, indent=1)
    print(f"Агрегат: {AGG}")


if __name__ == "__main__":
    main()
