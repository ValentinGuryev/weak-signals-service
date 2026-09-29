#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011: ценз-счётчики проблемных формулировок (ШАГ 2 GUIDE — «от проблемы»).

Только meta.count (per-page=1, БЕЗ скачивания) — разведка, §8.1 исключение.
Цель: оценить размер поля по НОВЫМ формулировкам (ни разу не использованным в сборе srf_corpus).
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


QUERIES = [
    # --- A. Проблема ускорительной физики (формулировки от задачи, не от технологии) ---
    ("A1 high gradient", '"high gradient" AND ("linac" OR "accelerator" OR "cavity")'),
    ("A2 wall loss", '"wall loss" AND ("cavity" OR "radiofrequency" OR "RF")'),
    ("A3 RF-loss cavity", '"RF loss" AND ("cavity" OR "linac")'),
    ("A4 duty cycle", '"duty cycle" AND ("linac" OR "accelerator" OR "klystron")'),
    ("A5 cryoplant", '"cryoplant" OR "cryogenic plant"'),
    ("A6 compact accel", '"compact accelerator"'),
    ("A7 accelerating gradient", '"accelerating gradient"'),
    ("A8 energy efficiency accel", '"energy efficiency" AND ("accelerator" OR "linac")'),
    ("A9 AC power linac", '"AC power" AND ("linac" OR "accelerator")'),
    # --- B. Нормальнопроводящие (NC) альтернативы ---
    ("B1 normal conducting", '"normal conducting" AND ("linac" OR "accelerator" OR "cavity" OR "structure")'),
    ("B2 copper cavity", '"copper" AND ("accelerating structure" OR "RF cavity")'),
    ("B3 CLIC", '"CLIC" AND ("collider" OR "accelerator" OR "structure")'),
    ("B4 two-beam", '"two-beam accelerator"'),
    # --- C. Новые технологии ускорения (не-структуры RF) ---
    ("C1 dielectric laser", '"dielectric laser acceleration" OR "dielectric laser accelerator"'),
    ("C2 dielectric wakefield", '"dielectric wakefield"'),
    ("C3 plasma wakefield", '"plasma wakefield acceleration"'),
    ("C4 laser wakefield", '"laser wakefield acceleration"'),
    ("C5 THz accelerator", '"THz" AND ("accelerator" OR "linac") AND ("structure" OR "cavity")'),
    # --- D. Драйверы-применения (что требует полостей) ---
    ("D1 cryomodule-accel", '"cryomodule" AND ("linac" OR "accelerator" OR "XFEL" OR "ILC")'),
    ("D2 ERL", '"energy recovery linac"'),
    ("D3 ILC/FCC/CEPC", '"International Linear Collider" OR ("FCC" AND "cavity") OR ("CEPC" AND ("cavity" OR "SRF"))'),
    ("D4 XFEL", '"XFEL" AND ("cavity" OR "linac" OR "accelerator")'),
    # --- E. Материальные дыры (ценз 2026-09-13: MgB2 105 vs 67; NbN 152 vs 65; NbTiN 101 vs 41) ---
    ("E1 MgB2 SRF", '"MgB2" AND ("radiofrequency" OR "SRF" OR "RF cavity")'),
    ("E2 NbN film SRF", '"NbN" AND ("SRF" OR "superconducting RF" OR "RF cavity")'),
    ("E3 NbTiN film SRF", '"NbTiN" AND ("cavity" OR "SRF" OR "radiofrequency")'),
    ("E4 SIS multilayer", '"SIS multilayer"'),
    ("E5 Nb3Sn wire", '"Nb3Sn" AND ("wire" OR "conductor" OR "magnet")'),
]

print(f"{'метка':24} {'count':>9}")
for label, q in QUERIES:
    c = count(q)
    print(f"{label:24} {c:>9,}")
    time.sleep(1.3)