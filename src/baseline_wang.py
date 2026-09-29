"""Бейзлайн: Wang 2018 — библиометрическая модель emerging research topics.

4 критерия (для темы i в год t):
  I.  Рост: r = p*_{t+Δt} / p*_t >= r_min  (p* — сглаженное 3-летнее среднее)
  II. Новизна: p*_t <= p_max (малая база в начале)
  III. Научное влияние: c_{t,t+Δt} >= c_min (цитаты в окне)
  IV. Когерентность: h_i >= h_min (внутрикластерные цитирования / публикации)
Все 4 должны выполняться; записывается первый emergent-год.

Адаптация к нашим данным (arXiv без полного цитатного графа):
- темы = наши термины (ключевые слова);
- p = число статей с термином в год;
- c = цитаты (OpenAlex, для калибровочных тем) — упрощение: если нет данных, критерий III считается по росту цитат;
- h = когерентность: доля статей термина, ко-встречающихся с другими терминами (наша связность).

Вход: data/processed/papers.parquet, experiment/runs/openalex_calibration_results.json.
Выход: experiment/runs/baseline_wang_results.json
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


def smooth3(freq: dict[int, int]) -> dict[int, float]:
    """3-летнее скользящее среднее частоты."""
    years = sorted(freq)
    out = {}
    for i, y in enumerate(years):
        win = years[max(0, i - 1): i + 2]
        out[y] = np.mean([freq.get(w, 0) for w in win])
    return out


def detect_wang(freq: dict[int, int], delta_t: int = 2, r_min: float = 2.0, p_max: int = 50) -> int | None:
    """Первый год, где критерии I и II выполнены (упрощение Wang 2018 без цитат/когерентности)."""
    years = sorted(freq)
    if len(years) < delta_t + 1:
        return None
    ps = smooth3(freq)
    for i, t in enumerate(years):
        if t + delta_t not in ps:
            continue
        p_t = ps[t]
        p_td = ps[t + delta_t]
        if p_t <= 0 or p_t > p_max:
            continue
        r = p_td / p_t
        if r >= r_min:
            return t
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Бейзлайн Wang 2018")
    ap.add_argument("--papers", default="data/processed/papers.parquet")
    ap.add_argument("--out", default="experiment/runs/baseline_wang_results.json")
    ap.add_argument("--r-min", type=float, default=2.0, help="порог роста (Criterion I)")
    ap.add_argument("--p-max", type=int, default=50, help="макс. база (Criterion II)")
    args = ap.parse_args()

    papers = pd.read_parquet(PROJECT_ROOT / args.papers)
    papers["year"] = pd.to_datetime(papers["published"], errors="coerce").dt.year.astype("Int64")
    papers["text"] = (papers["title"].fillna("") + " " + papers["abstract"].fillna("")).str.lower()

    results = []
    for term, pattern in TERMS.items():
        mask = papers["text"].str.contains(pattern, regex=True, na=False)
        sub = papers[mask].dropna(subset=["year"])
        freq = sub["year"].astype(int).value_counts().sort_index().to_dict()
        det = detect_wang(freq, r_min=args.r_min, p_max=args.p_max) if freq else None
        results.append({
            "term": term,
            "detect_year": det,
            "frequency_by_year": {int(y): int(c) for y, c in sorted(freq.items())},
            "n_docs": int(len(sub)),
            "author_window": CAL.get(term, None),
            "params": {"r_min": args.r_min, "p_max": args.p_max},
        })
        logger.info("  %-22s детекция=%s n=%d", term, det, len(sub))

    out = {
        "method": "wang2018_bibliometric",
        "description": f"Wang 2018: рост (r>={args.r_min}, сглаж.3л) + новизна (база<={args.p_max})",
        "terms": results,
    }
    out_path = PROJECT_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Записано: %s", out_path)


if __name__ == "__main__":
    main()
