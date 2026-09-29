#!/usr/bin/env python3
"""S2 для кейса 008 (СП-авиамоторы): wordshift-анализ семантики по периодам.

Адаптация wordshift_jtwpa.py под 008. Гипотезы сдвига:
1. Архитектура: hybrid (СП-ротор/DC-поле) → fully-SC / air-core (Ainslie 2016 развилка);
2. Энергоноситель: появление водородной лексики (LH2/cryo/hydrogen/fuel cell) — синхронно с
   переломом 2020 и водородной волной 2023+;
3. «Демонстратор/гонка» → «дизайн/оптимизация/потери» (открытие → инжиниринг);
4. Конкуренты в лексике: permanent magnet / cryo-copper/aluminum появляются в абстрактах core;
5. Материал: REBCO vs MgB2 (какой проводник доминирует в авиа-лексике).

Данные: data/raw/openalex/sc_aircraft_motors_corpus.json (453, полный select — abstract уже внутри).
Выход: results/case_signals/wordshift_trends_sc_aircraft.json
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS = PROJECT_ROOT / "data/raw/openalex/sc_aircraft_motors_corpus.json"
OUT = PROJECT_ROOT / "results/case_signals/wordshift_trends_sc_aircraft.json"

# Периоды (2014-2016 мал — объединяем с до-2013)
PERIODS = {"до2014": (0, 2013), "2014-2016": (2014, 2016), "2017-2019": (2017, 2019),
           "2020-2022": (2020, 2022), "2023-2026": (2023, 2026)}

# Словарь-таргет: маркеры по группам (подстроки корней)
TARGETS = {
    # --- 1. Архитектура ---
    "arch_hybrid_partial": ["hybrid", "partially superconducting", "partial superconducting", "dc field", "field winding"],
    "arch_fully_sc": ["fully superconducting", "all-superconducting", "fully sc", "air-core", "air core", "fully hts"],
    "arch_partial_sc": ["partially superconducting", "partial superconducting", "partially sc"],
    # --- 2. Энергоноситель/платформа ---
    "plat_hydrogen": ["hydrogen", "lh2", "liquid hydrogen", "h2"],
    "plat_cryo": ["cryogenic", "cryo", "cryocool", "cryostat"],
    "plat_fuelcell": ["fuel cell", "fuel-cell", "pemfc", "sofc"],
    "plat_battery": ["battery", "lithium", "li-ion"],
    # --- 3. Фаза: демонстратор → инжиниринг ---
    "phase_demo_gonka": ["demonstrat", "first", "proof", "novel", "concept", "feasib", "test"],
    "phase_eng": ["design", "optimiz", "fabricat", "manufactur", "integrat", "model", "simulat", "analys", "loss", "efficien", "weight", "mass"],
    # --- 4. Конкуренты в лексике ---
    "comp_pm": ["permanent magnet", "pm machine", "pm motor", "rare earth"],
    "comp_cryo_cu": ["cryogenic copper", "cryo-copper", "cryogenic aluminum", "cryo-aluminum", "cryo-aluminium", "hyper-al"],
    "comp_turbine": ["turbine", "turbofan", "turboelectric", "gas turbine"],
    "comp_saf": ["sustainable aviation fuel", "saf", "biofuel", "bio-fuel"],
    # --- 5. Материал проводника ---
    "mat_rebco": ["rebco", "ybco", "coated conductor", "rare earth barium", "2g hts"],
    "mat_mgb2": ["mgb2", "magnesium diboride"],
    "mat_bscco": ["bscco", "bi-2212", "bi2212", "bi-2223"],
    # --- 6. Проблема/метрика ---
    "metric_power_density": ["power density", "kw/kg", "w/kg", "specific power", "power-to-weight"],
    "metric_loss": ["ac loss", "ac-loss", "losses"],
    "metric_weight": ["weight", "lightweight", "mass reduction", "lighter"],
}


def clean_text(t: str) -> str:
    t = t.lower()
    t = re.sub(r"[^a-z0-9\s-]", " ", t)
    return re.sub(r"\s+", " ", t)


def analyze():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    works = corpus["works"] if isinstance(corpus, dict) else corpus

    texts_by_period = defaultdict(list)
    for w in works:
        y = w.get("year") or 0
        ab = w.get("abstract") or ""
        if not ab:
            continue
        for pname, (lo, hi) in PERIODS.items():
            if lo <= y <= hi:
                texts_by_period[pname].append(clean_text(f"{w.get('title') or ''} {ab}"))
                break

    periods = sorted(texts_by_period.keys())
    print(f"Периоды: {periods}")
    for p in periods:
        n = len(texts_by_period[p])
        nw = sum(len(t.split()) for t in texts_by_period[p])
        print(f"  {p}: работ {n}, слов {nw}")

    result = {}
    for group, patterns in TARGETS.items():
        freqs = []
        for p in periods:
            texts = texts_by_period.get(p, [])
            total_words = sum(len(t.split()) for t in texts)
            if total_words == 0:
                freqs.append(0.0)
                continue
            cnt = 0
            for t in texts:
                for pat in patterns:
                    cnt += len(re.findall(re.escape(pat), t))
            freqs.append(1000.0 * cnt / total_words)
        result[group] = dict(zip(periods, freqs))

    OUT.write_text(json.dumps({"periods": periods, "targets": result}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT}")
    print("\n=== Частоты на 1000 слов по периодам ===")
    for group, freqs in result.items():
        line = " | ".join(f"{p}: {v:.2f}" for p, v in freqs.items())
        print(f"{group:20s} {line}")


if __name__ == "__main__":
    analyze()
