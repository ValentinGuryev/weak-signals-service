#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Полный забег фарма-валидации (Этап 1): ~11 направлений.

Метод (из пилота): counts по ЯКОРНЫМ одобренным препаратам направления
(title_and_abstract, чисто) + корпус топ-работ. Для сигнала-2018 дополнительно
считаем термины направления (как в СП).

Выход: pharma_calibration/data/<dir>_v2.json на каждое направление +
features_table_pharma.csv (агрегат: сигнал-2018, рост, EScore-компоненты, исход).
"""
from __future__ import annotations

import csv
import json
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pharma_calibration" / "data"
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "research (mailto:research@example.com)"}

# direction -> конфиг. anchors: (препарат, термин_для_поиска, год_FDA)
# signal_terms: термины направления для сигнала-2018 (как в СП)
# expected: ожидаемый исход (для сверки, НЕ для модели)
DIRECTIONS = {
    "car_t": {
        "name": "CAR-T терапии",
        "promise_2018": "Kymriah/Yescarta одобрены 2017 — прорыв",
        "anchors": [("Kymriah", "tisagenlecleucel", 2017), ("Yescarta", "axicabtagene", 2017),
                    ("Breyanzi", "lisocabtagene", 2021), ("Carvykti", "ciltacabtagene", 2022)],
        "signal_terms": '"chimeric antigen receptor" AND (T-cell OR T cell) AND therapy',
        "expected": "✅",
    },
    "crispr_therapy": {
        "name": "CRISPR-терапии",
        "promise_2018": "революция с 2016, обещание Casgevy",
        "anchors": [("Casgevy", "exagamglogene", 2023), ("Lyfgenia", "lovotibeglogene", 2023)],
        "signal_terms": '"CRISPR" AND (therapeutic OR therapy OR "gene editing")',
        "expected": "🔶",
    },
    "microbiome_lbp": {
        "name": "Микробиом-терапии (LBP)",
        "promise_2018": "следующий рубеж ~2015",
        "anchors": [("Rebyota", "fecal microbiota", 2022), ("Vowst", "fecal microbiota spores", 2023)],
        "signal_terms": '"microbiome" AND ("live biotherapeutic" OR FMT OR therapeutic)',
        "expected": "❌",
    },
    "glp1": {
        "name": "GLP-1 (диабет/ожирение)",
        "promise_2018": "семейство GLP-1 растёт; ожирение — новая ниша",
        "anchors": [("Ozempic", "semaglutide", 2017), ("Wegovy", "semaglutide obesity", 2021),
                    ("Mounjaro", "tirzepatide", 2022)],
        "signal_terms": '"GLP-1" OR "glucagon-like peptide-1" AND (obesity OR diabetes)',
        "expected": "✅",
    },
    "adc": {
        "name": "ADC (antibody-drug conjugates)",
        "promise_2018": "зреющие; Enhertu — прорыв",
        "anchors": [("Adcetris", "brentuximab", 2011), ("Enhertu", "trastuzumab deruxtecan", 2019),
                    ("Padcev", "enfortumab", 2019)],
        "signal_terms": '"antibody-drug conjugate" OR "antibody drug conjugate"',
        "expected": "✅",
    },
    "anti_amyloid": {
        "name": "Анти-амилоид (Альцгеймер)",
        "promise_2018": "надежды на модифицирующие терапии",
        "anchors": [("Aduhelm", "aducanumab", 2021), ("Leqembi", "lecanemab", 2023)],
        "signal_terms": '"amyloid" AND (Alzheimer OR "beta-amyloid") AND (antibody OR immunotherapy)',
        "expected": "❌",
    },
    "aso": {
        "name": "ASO (антисмысловые олигонуклеотиды)",
        "promise_2018": "нишевой успех Spinraza",
        "anchors": [("Spinraza", "nusinersen", 2016), ("Exondys", "eteplirsen", 2016),
                    ("Amondys", "casimersen", 2021)],
        "signal_terms": '"antisense oligonucleotide" AND (therapy OR therapeutic)',
        "expected": "🔶",
    },
    "gene_therapy_aav": {
        "name": "Генная терапия (AAV, in vivo)",
        "promise_2018": "прорыв Luxturna/Zolgensma",
        "anchors": [("Luxturna", "voretigene", 2017), ("Zolgensma", "onasemnogene", 2019),
                    ("Hemgenix", "etranacogene", 2022)],
        "signal_terms": '"gene therapy" AND (AAV OR "adeno-associated")',
        "expected": "🔶",
    },
    "bispecific": {
        "name": "Биспецифичные антитела",
        "promise_2018": "перспективно в онкологии",
        "anchors": [("Blincyto", "blinatumomab", 2014), ("Hemlibra", "emicizumab", 2017),
                    ("Tecvayli", "teclistamab", 2022)],
        "signal_terms": '"bispecific antibody"',
        "expected": "✅",
    },
    "rlt": {
        "name": "Радиофармпрепараты (RLT)",
        "promise_2018": "ниша; Lutathera — первый",
        "anchors": [("Lutathera", "lutetium Lu 177 dotatate", 2018), ("Pluvicto", "lutetium Lu 177 vipivotide", 2022)],
        "signal_terms": '"radioligand therapy" OR "Lu-177" OR "lutetium-177" AND therapy',
        "expected": "🔶",
    },
}

MAX_WORKS = 120


def api_get(url: str) -> dict:
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            print(f"    retry {attempt+1}: {e}")
            time.sleep(2 + attempt * 3)
    return {}


def collect_anchors(direction: str, cfg: dict) -> dict:
    per_anchor, total_counts, works_by_id = {}, defaultdict(int), {}
    for anchor_name, anchor_term, fda_year in cfg["anchors"]:
        q = f'"{anchor_name}" OR "{anchor_term}"'
        enc = urllib.parse.quote(q)
        url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
               f",publication_year:2000-2026&group_by=publication_year&per-page=200")
        d = api_get(url)
        gb = {int(g["key"]): g["count"] for g in d.get("group_by", [])}
        per_anchor[anchor_name] = {"fda_year": fda_year, "counts": dict(sorted(gb.items()))}
        for y, c in gb.items():
            total_counts[y] += c
        if len(works_by_id) < MAX_WORKS:
            url2 = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
                    f",publication_year:2000-2026&per-page=40&sort=cited_by_count:desc")
            d2 = api_get(url2)
            for w in d2.get("results", []):
                wid = w["id"]
                if wid not in works_by_id and len(works_by_id) < MAX_WORKS:
                    works_by_id[wid] = {"id": wid, "title": w.get("title"),
                                        "year": w.get("publication_year"),
                                        "cited_by": w.get("cited_by_count")}
        time.sleep(0.8)
    return per_anchor, total_counts, works_by_id


def collect_signal(direction: str, cfg: dict) -> dict:
    """Сигнал-2018 по терминам направления (для EScore, без препаратных артефактов)."""
    q = cfg["signal_terms"]
    enc = urllib.parse.quote(q)
    # counts по годам 2000-2026 (для роста к 2018 и после)
    url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
           f",publication_year:2000-2026&group_by=publication_year&per-page=200")
    d = api_get(url)
    gb = {int(g["key"]): g["count"] for g in d.get("group_by", [])}
    return dict(sorted(gb.items()))


def main():
    rows = []
    for direction, cfg in DIRECTIONS.items():
        print(f"\n=== {cfg['name']} ===")
        per_anchor, total_counts, works = collect_anchors(direction, cfg)
        signal = collect_signal(direction, cfg)
        res = {
            "direction": direction, "name": cfg["name"], "promise_2018": cfg["promise_2018"],
            "expected": cfg["expected"], "signal_terms": cfg["signal_terms"],
            "anchors": per_anchor, "anchor_counts_by_year": dict(sorted(total_counts.items())),
            "signal_counts_by_year": signal,
            "corpus_size": len(works), "works": list(works.values()),
        }
        with open(OUT / f"{direction}_v2.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)

        def seg(c, a, b): return sum(v for y, v in c.items() if a <= y <= b)
        ac, sc = res["anchor_counts_by_year"], res["signal_counts_by_year"]
        # Компоненты для features: сигнал 2018 по терминам, рост, EScore
        sig2018 = seg(sc, 2016, 2018)
        sig1315 = seg(sc, 2013, 2015)
        growth = sig2018 / sig1315 if sig1315 else 0
        # новизна: год, когда термин-сигнал > 20/год (рождение)
        birth = next((y for y in sorted(sc) if sc[y] > 20), None)
        print(f"  сигнал-2018(термины)={sig2018} (13-15: {sig1315}) рост={growth:.1f} | рождение={birth} "
              f"| якоря до2026={seg(ac,2000,2026)}")
        rows.append({
            "direction": direction, "name": cfg["name"], "expected": cfg["expected"],
            "signal_2018": sig2018, "signal_2013_15": sig1315, "growth_to_2018": round(growth, 2),
            "term_birth": birth, "anchor_total": seg(ac, 2000, 2026),
            "anchor_2016_18": seg(ac, 2016, 2018), "anchor_2022_26": seg(ac, 2022, 2026),
        })
        time.sleep(0.8)

    # features_table_pharma.csv
    csv_path = ROOT / "pharma_calibration" / "features_table_pharma.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nГотово. features_table: {csv_path} ({len(rows)} направлений)")
    for r in rows:
        print(f"  {r['direction']:<18} {r['expected']} signal2018={r['signal_2018']} рост={r['growth_to_2018']} birth={r['term_birth']}")


if __name__ == "__main__":
    main()
