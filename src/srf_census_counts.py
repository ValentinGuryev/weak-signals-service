#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011: внешний ценз полноты SRF-корпуса (разведка счётчиками OpenAlex).

Только meta.count (per-page=1, БЕЗ скачивания записей) — разведка, §8.1 исключение.
Сверяет: размер поля SRF (знаменатель) и Nb3Sn-подмножества (числитель) против корпуса.

Выход: печать таблицы; лог — results/runtime/api_budget.md (добавляется вручную).
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"


def count(q: str) -> int:
    enc = urllib.parse.quote(q)
    url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
           f"&per-page=1&mailto={MAILTO}")
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                return int(json.load(r)["meta"]["count"])
        except Exception as e:  # noqa: BLE001
            print(f"    retry {attempt + 1}: {e}")
            time.sleep(2 + attempt * 3)
    return -1


# (метка, запрос) — запросы в SYNTAX как в скрипте сбора (title_and_abstract.search)
QUERIES = [
    # --- базовые (исходные запросы корпуса, сверка размера) ---
    ("Q1 SRF core", '"superconducting radio frequency" OR "superconducting RF" OR "SRF cavity" OR "SRF cavities"'),
    ("Q2 SRF accel", '"SRF accelerator" OR "superconducting accelerator cavity" OR "superconducting RF cavity"'),
    ("Q3 niobium", '"niobium cavity" OR "niobium SRF" OR "niobium superconducting cavity"'),
    ("Q4 nb3sn", '"Nb3Sn cavity" OR "Nb3Sn SRF" OR "niobium-tin cavity"'),
    ("Q5 generic", '"superconducting cavity" AND ("accelerator" OR "CERN" OR "Fermilab" OR "JLab" OR "KEK")'),
    # --- расширение знаменателя (поле SRF, другие формулировки) ---
    ("D1 RF-superconductivity", '"RF superconductivity" OR "radiofrequency superconductivity"'),
    ("D2 spelled-out", '"superconducting radiofrequency"'),
    ("D3 cryomodule", '"cryomodule" AND ("superconducting" OR "SRF")'),
    ("D4 sc-linac", '"superconducting linac"'),
    ("D5 cavity-SC-bare", '"cavity" AND "superconductor" AND ("accelerator" OR "RF")'),
    # --- числитель: Nb3Sn во всём поле ---
    ("N1 nb3sn+cavity", '"Nb3Sn" AND ("cavity" OR "cavities")'),
    ("N2 nb3sn+SRF", '"Nb3Sn" AND ("SRF" OR "superconducting RF")'),
    ("N3 niobium-tin+cavity", '"niobium tin" AND ("cavity" OR "cavities")'),
    ("N4 niobium-tin+SRF", '"niobium tin" AND ("SRF" OR "superconducting RF")'),
    # --- конкуренты: размер их подполей в SRF ---
    ("C1 MgB2+cavity", '"MgB2" AND ("cavity" OR "cavities")'),
    ("C2 NbN+SC+cavity", '"NbN" AND "superconducting" AND ("cavity" OR "cavities")'),
    ("C3 NbTiN+cavity", '"NbTiN" AND ("cavity" OR "cavities" OR "SRF")'),
    ("C4 SIS-multilayer", '"SIS multilayer" AND ("cavity" OR "SRF")'),
    ("C5 V3Si+cavity", '"V3Si" AND ("cavity" OR "cavities")'),
]

for label, q in QUERIES:
    c = count(q)
    print(f"{label:22} {c:>7,}")
    time.sleep(1.5)