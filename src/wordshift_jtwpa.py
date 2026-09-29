#!/usr/bin/env python3
"""S2 для кейса 007 (JTWPA): wordshift-анализ семантики по периодам.

Адаптация wordshift_snspd.py под JTWPA. Ищем 4 типа сдвигов (CASE_BUILDING_GUIDE ШАГ 4б):
1. смена термина (JPA → JTWPA/TWPA, travelling/traveling);
2. смена архитектуры/материала (Josephson junction chain → SNAIL/kinetic inductance; Nb/Al);
3. сдвиг фокуса (qubit readout → axion/radar/multiplex/scalable — диверсификация применений);
4. «открытие → инжиниринг» (discovery-лексика убывает, design/fabricate/integrate растёт).

Данные: data/raw/openalex/jtwpa_corpus.json (A-ядро 265) + jtwpa_full.json (abstracts).
Выход: results/case_signals/wordshift_trends_jtwpa.json
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

CORPUS = PROJECT_ROOT / "data/raw/openalex/jtwpa_corpus.json"
FULL = PROJECT_ROOT / "data/raw/openalex/jtwpa_full.json"
OUT = PROJECT_ROOT / "results/case_signals/wordshift_trends_jtwpa.json"

# Периоды: JTWPA родился 2010-2015, взрыв 2021+
PERIODS = {"2010-2014": (2010, 2014), "2015-2017": (2015, 2017),
           "2018-2020": (2018, 2020), "2021-2023": (2021, 2023), "2024-2026": (2024, 2026)}

# Словарь-таргет: маркеры по группам (стемминг упрощённый — ищем подстроки корней)
TARGETS = {
    # --- 1. Терминология ---
    "term_jpa": ["josephson parametric amplifier", "jpa"],
    "term_jtwpa": ["josephson traveling", "josephson travelling", "jtwpa", "traveling wave parametric", "travelling wave parametric"],
    "term_twpa": ["twpa", "traveling wave", "travelling wave"],
    # --- 2. Архитектура/материал ---
    "arch_junction_chain": ["junction chain", "series array", "chain of josephson", "josephson junction array"],
    "arch_snail": ["snail", "superconducting nonlinear asymmetric"],
    "arch_kinetic": ["kinetic inductance"],
    "arch_squid": ["squid"],
    "mat_al": ["aluminum", "aluminium"],
    "mat_nbn": ["nbn", "niobium nitride"],
    "mat_nbtin": ["nbtin", "titanium nitride", "tin"],
    # --- 3. Фокус/применения ---
    "app_qubit": ["qubit", "transmon", "readout", "circuit qed"],
    "app_axion": ["axion", "haloscope", "dark matter"],
    "app_radar": ["radar", "quantum illumination"],
    "app_multiplex": ["multiplex", "scalable", "large scale", "scale up"],
    "app_squeeze": ["squeez"],
    "app_astro": ["radioastronom", "telescope", "mkid", "detector array"],
    # --- 4. Открытие → инжиниринг ---
    "phase_discovery": ["demonstrate", "demonstration", "first", "proof", "novel", "observe", "discover", "show"],
    "phase_eng": ["design", "fabricat", "manufactur", "integrat", "optimiz", "engineer", "chip", "wafer", "process", "automated", "product", "commercial"],
}


def clean_text(t: str) -> str:
    t = t.lower()
    t = re.sub(r"[^a-z0-9\s-]", " ", t)
    return re.sub(r"\s+", " ", t)


def analyze():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    full = json.loads(FULL.read_text(encoding="utf-8"))
    A = [w for w in corpus if w["class"] == "A"]

    # texts по периодам
    texts_by_period = defaultdict(list)
    for w in A:
        y = w.get("year") or 0
        ab = full.get(w["id"], {}).get("abstract", "") or ""
        if not ab:
            continue
        for pname, (lo, hi) in PERIODS.items():
            if lo <= y <= hi:
                texts_by_period[pname].append(clean_text(w.get("title", "") + " " + ab))
                break

    periods = sorted(texts_by_period.keys())
    print(f"Периоды: {periods}")
    for p in periods:
        n = len(texts_by_period[p])
        nw = sum(len(t.split()) for t in texts_by_period[p])
        print(f"  {p}: работ {n}, слов {nw}")

    # частота таргетов на 1000 слов
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
