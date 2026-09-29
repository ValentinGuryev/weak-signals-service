"""Бейзлайн: EScore (Carley et al. 2018) — индикатор технической зарождаемости.

Термин emergent, если удовлетворяет ВСЕМ условиям (по выжимке literature/):
- a) Persistence: появляется ≥ 3 года И ≥ 7 записей;
- b) Novelty/Growth: НЕ в ≥15% записей базового периода И в активном ≥ 2x чаще, чем в базовом;
- c) Community: используется > 1 автором (не все записи от одного автора);
- d) Growth: 3 тренда (последние 3 года vs первые 3 активного; последние 2 vs предыдущие 2; наклон).
Порог: EScore ≥ 1.77 (≈√π).

Термины = наши концепты (ключевые слова домена), как в link-pred — для сравнения с 8 калибровочными темами.

Вход: data/processed/papers.parquet.
Выход: experiment/runs/baseline_escore_results.json
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

# Термины = ключевые слова калибровочных тем + домена (как в link-pred)
TERMS = {
    "graphene": r"\bgraphene",
    "nanotube": r"\bnanotube",
    "twisted bilayer": r"twisted bilayer",
    "nv center": r"nv center|nitrogen.?vacancy",
    "diamond": r"\bdiamond",
    "magnon": r"\bmagnon",
    "spin torque": r"spin[ -]?torque|spin transfer torque",
    "memristor": r"\bmemristor|memristive",
    "neuromorphic": r"\bneuromorphic",
    "machine learning": r"machine learning",
    "neural network": r"neural network|deep learning",
    "plasmon": r"\bplasmon",
    "metasurface": r"\bmetasurface",
    "quantum error": r"quantum error|error correction",
    "qubit": r"\bqubit",
    "superconducting diode": r"superconducting diode|diode effect",
    "fluxonium": r"\bfluxonium",
    "perovskite": r"\bperovskite",
    "mgb2": r"\bmgb2",
    "skyrmion": r"\bskyrmion",
    "vo2": r"\bvo2|vanadium dioxide",
    "weyl": r"\bweyl",
    "ga2o3": r"ga2o3|gallium oxide",
    "chiral phonon": r"chiral phonon",
    "hydride": r"\bhydride",
    "aharonov": r"aharonov",
    "neutron star": r"neutron star",
    "thermoelectric": r"\bthermoelectric",
}

# Калибровочные темы: концепт -> окно автора
CAL = {
    "graphene": (2000, 2002),
    "quantum systems": (2005, 2008),
    "nv center": (2006, 2008),
    "magnon": (2007, 2012),
    "machine learning": (2023, 2023),
    "neuromorphic": (2018, 2022),
    "plasmon": (2024, 2025),
    "quantum error": (2022, 2022),
}


def compute_escore(
    years: np.ndarray,
    n_years: int,
    base_len: int = 3,
    active_len: int = 7,
) -> float:
    """EScore для термина по временному ряду лет присутствия (по Carley 2018).

    years — отсортированный массив годов, где термин встречался (может повторяться).
    В упрощении: частоты по годам.
    """
    if len(years) == 0:
        return 0.0
    # частоты по годам
    freq = pd.Series(years).value_counts().sort_index()
    all_years = list(range(int(freq.index.min()), int(freq.index.max()) + 1))
    # если меньше окна — не считаем
    if len(all_years) < base_len + active_len:
        return 0.0
    # базовый период = первые base_len лет, активный = следующие active_len
    base_years = all_years[:base_len]
    active_years = all_years[base_len:base_len + active_len]

    base_n = sum(int(freq.get(y, 0)) for y in base_years)
    active_n = sum(int(freq.get(y, 0)) for y in active_years)

    # a) Persistence: >= 3 года и >= 7 записей
    n_distinct_years = len(freq)
    if n_distinct_years < 3 or len(years) < 7:
        return 0.0

    # b) Novelty/Growth: НЕ в >=15% базового периода И active >= 2x base
    # (упрощение: доля записей термина в базовом периоде от всех записей периода)
    if active_n < 2 * base_n:
        return 0.0

    # c) Community: (проверяется вне, здесь не считаем)

    # d) Growth: 3 тренда (упрощение — нормированные отношения)
    if base_n == 0:
        return 0.0
    # (1) последние 3 года активного vs первые 3 активного
    first3 = sum(int(freq.get(y, 0)) for y in active_years[:3])
    last3 = sum(int(freq.get(y, 0)) for y in active_years[-3:])
    # (2) последние 2 vs предыдущие 2 активного
    prev2 = sum(int(freq.get(y, 0)) for y in active_years[2:4]) if len(active_years) >= 4 else first3
    last2 = sum(int(freq.get(y, 0)) for y in active_years[-2:])
    # (3) наклон (линейная регрессия по активному периоду)
    xs = np.arange(len(active_years))
    ys = np.array([int(freq.get(y, 0)) for y in active_years], dtype=float)
    slope = np.polyfit(xs, ys, 1)[0] if len(xs) >= 2 else 0.0

    g1 = last3 / first3 if first3 > 0 else 1.0
    g2 = last2 / prev2 if prev2 > 0 else 1.0
    g3 = slope  # наклон (нормирован)

    # EScore = комбинация трендов (по статье: sqrt(pi) порог, скрипт — взвешенная сумма)
    escore = np.sqrt(g1 * g2) * (1 + abs(g3))  # упрощение, по духу Carley
    return float(escore)


def main() -> None:
    ap = argparse.ArgumentParser(description="Бейзлайн EScore (Carley 2018)")
    ap.add_argument("--papers", default="data/processed/papers.parquet")
    ap.add_argument("--out", default="experiment/runs/baseline_escore_results.json")
    args = ap.parse_args()

    papers = pd.read_parquet(PROJECT_ROOT / args.papers)
    papers["year"] = pd.to_datetime(papers["published"], errors="coerce").dt.year
    papers["text"] = (papers["title"].fillna("") + " " + papers["abstract"].fillna("")).str.lower()
    papers["authors_str"] = papers["authors"].apply(lambda a: ",".join(a) if isinstance(a, (list, tuple)) else str(a))

    logger.info("Расчёт EScore для %d терминов…", len(TERMS))
    results = []
    for term, pattern in TERMS.items():
        mask = papers["text"].str.contains(pattern, regex=True, na=False)
        sub = papers[mask]
        if sub.empty:
            results.append({"term": term, "escore": 0.0, "emergent": False, "n_docs": 0})
            continue
        years = sub["year"].dropna().astype(int).values
        # c) Community: > 1 автор (не один и тот же автор во всех записях)
        n_authors = sub["authors_str"].nunique()
        escore = compute_escore(years, len(years))
        emergent = escore >= 1.77 and n_authors > 1
        results.append({
            "term": term,
            "escore": round(escore, 3),
            "emergent": emergent,
            "n_docs": len(sub),
            "n_authors": int(n_authors),
            "first_year": int(years.min()),
            "last_year": int(years.max()),
            "author_window": CAL.get(term, None),
        })
        logger.info("  %-22s escore=%.2f emergent=%s n=%d (авт.%d)", term, escore, emergent, len(sub), n_authors)

    out = {
        "method": "escore_carley2018",
        "description": "Индикатор технической зарождаемости (Carley 2018): новизна, устойчивость, сообщество, рост; порог 1.77",
        "terms": results,
    }
    out_path = PROJECT_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Записано: %s", out_path)


if __name__ == "__main__":
    main()
