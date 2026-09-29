"""Бейзлайн: Co-word maps (Leydesdorff & Nerghes 2016) — рост частоты ключевых слов.

Суть: co-word подход отслеживает частоту/ко-встречаемость терминов по времени;
термин «emerging», если его частота растёт от базового периода.
Упрощение для сравнения с 8 калибровочными темами:
- для каждого термина считаем частоту по годам;
- детекция = первый год, где частота >= 2x средней базовой (первые 3 года) 
  И сохраняется >= 2x ещё 2 года подряд (устойчивый рост).

Вход: data/processed/papers.parquet.
Выход: experiment/runs/baseline_coword_results.json
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


def detect_growth(freq: dict[int, int], base_len: int = 3, growth_x: float = 2.0, sustain: int = 2) -> int | None:
    """Первый год устойчивого роста частоты термина.

    freq: {год: частота}. Базовый = первые base_len лет (минимум 1).
    Детекция: год, где freq >= growth_x * base_mean, и следующие sustain лет тоже >= growth_x * base_mean.
    """
    years = sorted(freq)
    if len(years) < base_len + sustain:
        return None
    base_years = years[:base_len]
    base_mean = max(1.0, np.mean([freq[y] for y in base_years]))
    thr = growth_x * base_mean
    for i in range(base_len, len(years) - sustain + 1):
        y = years[i]
        if all(freq.get(years[i + k], 0) >= thr for k in range(sustain)):
            return y
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Бейзлайн co-word (рост частоты терминов)")
    ap.add_argument("--papers", default="data/processed/papers.parquet")
    ap.add_argument("--out", default="experiment/runs/baseline_coword_results.json")
    args = ap.parse_args()

    papers = pd.read_parquet(PROJECT_ROOT / args.papers)
    papers["year"] = pd.to_datetime(papers["published"], errors="coerce").dt.year.astype("Int64")
    papers["text"] = (papers["title"].fillna("") + " " + papers["abstract"].fillna("")).str.lower()

    results = []
    for term, pattern in TERMS.items():
        mask = papers["text"].str.contains(pattern, regex=True, na=False)
        sub = papers[mask].dropna(subset=["year"])
        freq = sub["year"].astype(int).value_counts().sort_index().to_dict()
        det = detect_growth(freq) if freq else None
        results.append({
            "term": term,
            "detect_year": det,
            "frequency_by_year": {int(y): int(c) for y, c in sorted(freq.items())},
            "n_docs": int(len(sub)),
            "author_window": CAL.get(term, None),
        })
        logger.info("  %-22s детекция=%s n=%d", term, det, len(sub))

    out = {
        "method": "coword_leydesdorff2016",
        "description": "Co-word maps: рост частоты ключевых слов (>=2x от базового, устойчиво 2 года)",
        "terms": results,
    }
    out_path = PROJECT_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Записано: %s", out_path)


if __name__ == "__main__":
    main()
