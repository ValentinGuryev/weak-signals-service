#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H1-check: слабый сигнал = низкая частота × высокий рост (Ebadi/Yoon).

Считает по локальным OpenAlex-корпусам кейсов:
  - частоту ~2018 (2016-2018)
  - рост к 2018 (2016-18 / 2014-15) и дальний (2016-18 / 2010-12)
  - профиль волн W1(2014-16) W2(2017-19) W3(2020-22) W4(2023-26) — устойчивость роста
Сверяет с меткой исхода из features_table.csv. Результат — results/hypothesis_H1_check.md
(документ написан вручную; этот скрипт воспроизводит таблицу §2).

Запуск: .venv/bin/python src/check_h1.py
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPENALEX = ROOT / "data" / "raw" / "openalex"
FEATURES = ROOT / "results" / "features_table.csv"

# кейс -> (файл корпуса, topic-фильтр или None)
CASES = {
    "003_flux_pump": ("fluxpump_vs_joint_corpus.json", "Flux pump (CC)"),
    "003_joint_control": ("fluxpump_vs_joint_corpus.json", "Сверхпроводящее соединение"),
    "004_ni_coils": ("ni_coils_corpus.json", None),
    "005_smes": ("smes_vs_bess_counts.json", "SMES"),  # special: counts-файл
    "002_rce_dr_sunam": ("rce_tlag_corpus.json", "RCE/co-evap"),
    "007_jtwpa": ("jtwpa_corpus.json", None),
    "001_ibad_mgo": ("ibad_abstracts_corpus.json", None),
    "006_snspd": ("snspd_corpus.json", None),
    "008_sc_aircraft_motors": ("sc_aircraft_motors_corpus.json", None),
}


def load_works(fname: str, topic: str | None) -> list[dict]:
    """Достаёт список работ из corpus/counts json."""
    d = json.load(open(OPENALEX / fname, encoding="utf-8"))
    if fname == "smes_vs_bess_counts.json":
        # counts-файл: {counts: {SMES: {year: n}}}
        if topic == "SMES":
            raw = d["counts"]["SMES"]
            return [{"year": int(y), "topic": topic} for y, n in raw.items() for _ in range(n)]
        return []
    if isinstance(d, list):
        works = d
    elif isinstance(d, dict) and isinstance(d.get("works"), list):
        works = d["works"]
    else:
        works = []
        for k in d:
            if isinstance(d[k], list) and d[k] and isinstance(d[k][0], dict) and "year" in d[k][0]:
                works = d[k]
                break
    if topic:
        works = [w for w in works if w.get("topic") == topic]
    return works


def yearly(works: list[dict]) -> dict[int, int]:
    c: Counter = Counter()
    for w in works:
        y = w.get("year")
        if y is None:
            continue
        try:
            c[int(y)] += 1
        except (TypeError, ValueError):
            continue
    return dict(c)


def seg(s: dict[int, int], a: int, b: int) -> int:
    return sum(s.get(y, 0) for y in range(a, b + 1))


def load_label() -> dict[str, str]:
    """Метка исхода из features_table.csv (колонки case_id, label_2026)."""
    labels: dict[str, str] = {}
    with open(FEATURES, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cid = row["case_id"].strip()
            lab = row.get("label_2026", "").strip()
            labels[cid] = {  # нормализация к символам
                "1": "✅", "0": "❌", "в_развитии": "🔶",
            }.get(lab, lab)
    return labels


def main() -> None:
    labels = load_label()
    print(f"{'case':<22}{'метка':<5}{'N16-18':>7}{'N14-15':>7}{'рост15→18':>10}"
          f"{'N10-12':>7}{'рост11→18':>10} | {'W1':>4}{'W2':>5}{'W3':>5}{'W4':>5}"
          f"{'W3/W2':>7}")
    for case, (fname, topic) in CASES.items():
        s = yearly(load_works(fname, topic))
        n18 = seg(s, 2016, 2018)
        n15 = seg(s, 2014, 2015)
        n11 = seg(s, 2010, 2012)
        w1, w2, w3, w4 = seg(s, 2014, 2016), seg(s, 2017, 2019), seg(s, 2020, 2022), seg(s, 2023, 2026)
        r15 = n18 / n15 if n15 else float("nan")
        r11 = n18 / n11 if n11 else float("nan")
        rw = w3 / w2 if w2 else float("nan")
        lab = labels.get(case, "?")
        print(f"{case:<22}{lab:<5}{n18:>7}{n15:>7}{r15:>9.1f}x{n11:>7}{r11:>9.1f}x | "
              f"{w1:>4}{w2:>5}{w3:>5}{w4:>5}{rw:>6.2f}")


if __name__ == "__main__":
    main()
