"""Бейзлайн: Small 2014 — Emergence Potential (EP).

Emergence Potential = вознаграждение за новые статьи − штраф за старые:
  EP(тема, год y) = (статьи темы в новых co-citation thread-ах года y)
                    − (статьи темы во все годы до y−3)

Адаптация к нашим данным (arXiv без co-citation):
  EP(термин, y) = (статьи термина за последние 2 года [новые])
                  − (статьи термина старше 3 лет назад [старые])
Ранжирование по EP в каждый год; детекция = первый год, где EP > 0 и термин в топ-N.

Вход: data/processed/papers.parquet.
Выход: experiment/runs/baseline_small_results.json
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


def emergence_potential(freq: dict[int, int], y: int, new_win: int = 2, old_cut: int = 3) -> float:
    """EP(термин, y) = статьи за последние new_win лет − статьи старше old_cut лет назад от y."""
    recent = sum(c for yy, c in freq.items() if y - new_win + 1 <= yy <= y)
    old = sum(c for yy, c in freq.items() if yy < y - old_cut + 1)
    return recent - old


def detect_small(freq: dict[int, int], top_n: int = 10, min_ep: float = 0.0) -> int | None:
    """Первый год, где EP > 0 (и не в самом начале, чтобы убрать краевой эффект)."""
    years = sorted(freq)
    if not years:
        return None
    start = years[0]
    for y in years:
        if y < start + 3:  # пропускаем первые 3 года (нужна база для "старых" статей)
            continue
        ep = emergence_potential(freq, y)
        if ep > min_ep:
            return y
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Бейзлайн Small 2014 (Emergence Potential)")
    ap.add_argument("--papers", default="data/processed/papers.parquet")
    ap.add_argument("--out", default="experiment/runs/baseline_small_results.json")
    args = ap.parse_args()

    papers = pd.read_parquet(PROJECT_ROOT / args.papers)
    papers["year"] = pd.to_datetime(papers["published"], errors="coerce").dt.year.astype("Int64")
    papers["text"] = (papers["title"].fillna("") + " " + papers["abstract"].fillna("")).str.lower()

    results = []
    for term, pattern in TERMS.items():
        mask = papers["text"].str.contains(pattern, regex=True, na=False)
        sub = papers[mask].dropna(subset=["year"])
        freq = sub["year"].astype(int).value_counts().sort_index().to_dict()
        det = detect_small(freq) if freq else None
        results.append({
            "term": term,
            "detect_year": det,
            "frequency_by_year": {int(y): int(c) for y, c in sorted(freq.items())},
            "n_docs": int(len(sub)),
            "author_window": CAL.get(term, None),
        })
        logger.info("  %-22s детекция=%s n=%d", term, det, len(sub))

    out = {
        "method": "small2014_emergence_potential",
        "description": "Small 2014: EP = статьи(последние 2 года) − статьи(старше 3 лет), детекция при EP>0",
        "terms": results,
    }
    out_path = PROJECT_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Записано: %s", out_path)


if __name__ == "__main__":
    main()
