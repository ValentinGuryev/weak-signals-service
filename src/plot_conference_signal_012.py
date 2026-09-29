#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 012: конференционный сигнал (S1c) — кабельные доклады SNF/ASC/TASC по годам.

Источники (без API):
  1) literature/ кейса 012 — 21 доклад (только выжимки с годом в имени);
  2) results/snf_index/index.csv — 62 кабельных доклада (33 с годом).
Итог: сводный счёт по годам, пунктир окна 2018, аннотации ключевых событий.
"""
from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
LIT = ROOT / "case_studies/012_dc_hvdc_cables/literature"
IDX = ROOT / "results/snf_index/index.csv"
OUT = ROOT / "case_studies/012_dc_hvdc_cables/plots/conference_signal.png"

ANNO = {
    2013: "KEPCO 80 кВ, СПб старт, ASC2012",
    2015: "CAS Xiao DC-сеть, Roadmap ASC",
    2016: "Sytnikov AC/DC тесты",
    2020: "Shingal 1-й комм., ComEd",
    2021: "СПб full-scale 2.4 км",
    2024: "SuperRail квалиф., Шанхай 1.2 км",
    2025: "СПб ввод в сеть (TASC)",
}


def main() -> None:
    # 1) literature доклады кейса
    lit = Counter()
    for p in LIT.glob("*.md"):
        m = re.match(r"\((\d{4})\)", p.name)
        if m:
            lit[int(m.group(1))] += 1

    # 2) SNF-индекс
    snf = Counter()
    pat = re.compile(r"\b(cable|transmission|cable conductor|dc power|power grid|current lead|fault current|HVDC|HTS cable|superconducting power)\b", re.I)
    seen = set()
    with open(IDX, encoding="utf-8", errors="replace") as f:
        for x in csv.DictReader(f):
            t = x.get("title") or ""
            if pat.search(t):
                k = t.strip().lower()[:50]
                if k in seen:
                    continue
                seen.add(k)
                yr = x.get("year") or ""
                if yr.isdigit():
                    snf[int(yr)] += 1

    # сводный счёт (объединение; литература даёт приоритет, но не двойной счёт с индексом — 
    # индекс-хиты включают и доклады кейса; берём max по каждому году как оценку присутствия)
    years = list(range(1998, 2027))
    both = Counter(lit)
    for y in snf:
        both[y] = max(both.get(y, 0), snf[y])

    fig, ax = plt.subplots(figsize=(12, 6))
    vals = [both.get(y, 0) for y in years]
    ax.bar(years, vals, color="#1f77b4", alpha=0.85)
    ax.axvline(2018 - 0.5, color="red", ls="--", lw=1.5)
    ax.text(2018.3, max(vals) * 0.95, "окно 2018", color="red", fontsize=10)

    for y, lab in ANNO.items():
        if both.get(y):
            ax.annotate(lab, (y, both[y]), textcoords="offset points",
                        xytext=(0, 8), ha="center", fontsize=7.5, rotation=90, color="#333333")

    ax.set_xlabel("Год")
    ax.set_ylabel("Кабельных докладов (SNF/ASC/TASC)")
    ax.set_title("Кейс 012: конференционный сигнал — HTS-кабельные доклады по годам")
    ax.set_xticks(range(1998, 2027, 2))
    ax.grid(axis="y", alpha=0.3)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"График → {OUT}")
    print("\nСводный счёт по годам (max(lit, snf)):")
    for y in years:
        if both.get(y):
            print(f"  {y}: {both[y]}")


if __name__ == "__main__":
    main()