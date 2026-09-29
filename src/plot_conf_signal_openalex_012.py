#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 012: конференционный сигнал (S1c) — conference-paper из корпуса OpenAlex.

Источник: data/raw/openalex/dc_cables_problem.json, type=conference-paper (10 932 работ,
уже в корпусе, 0 новых API-запросов). Показывает: DC-конференции растут/держатся,
AC-конференции обваливаются после 2020 — согласовано с публикационным сигналом.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/raw/openalex/dc_cables_problem.json"
OUT = ROOT / "case_studies/012_dc_hvdc_cables/plots/conference_signal_openalex.png"

YEARS = range(2002, 2027)


def main() -> None:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    conf = [w for w in d["works"] if w.get("type") == "conference-paper"]

    fig, (ax, axb) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                  gridspec_kw={"height_ratios": [2, 1]})

    for g, col, lab in [("HTS-DC", "#2ca02c", "ВТСП DC-линии (ядро)"),
                        ("HTS-AC", "#d62728", "ВТСП AC-линии")]:
        c = Counter(w["year"] for w in conf if w.get("group") == g and isinstance(w.get("year"), int))
        vals = [c.get(y, 0) for y in YEARS]
        ax.plot(YEARS, vals, marker="o", ms=3, color=col, lw=2.2, label=lab)
        ax.fill_between(YEARS, vals, color=col, alpha=0.12)

    ax.axvline(2018, color="red", ls="--", lw=1.5)
    ax.text(2018.2, ax.get_ylim()[1], "окно 2018", color="red", fontsize=10)
    ax.set_ylabel("Конф. публикаций")
    ax.set_title("Кейс 012: конференционный сигнал (OpenAlex conference-paper) — HTS кабели")
    ax.legend(fontsize=10, loc="upper left")
    ax.grid(alpha=0.3)

    # нижняя: доля DC среди конф-публикаций
    sdc, sac = [], []
    for y in YEARS:
        dc = sum(1 for w in conf if w.get("group") == "HTS-DC" and w.get("year") == y)
        ac = sum(1 for w in conf if w.get("group") == "HTS-AC" and w.get("year") == y)
        sdc.append(dc); sac.append(ac)
    share = [100 * a / max(a + b, 1) for a, b in zip(sdc, sac)]
    axb.plot(YEARS, share, color="#2ca02c", lw=2.2, marker="s", ms=3)
    axb.axhline(50, color="gray", ls=":", lw=1)
    axb.axvline(2018, color="red", ls="--", lw=1.5)
    axb.text(2018.2, axb.get_ylim()[1], "окно 2018", color="red", fontsize=9)
    axb.fill_between(YEARS, 50, share, where=[s >= 50 for s in share], color="#2ca02c", alpha=0.15)
    axb.set_ylabel("Доля DC среди конф., %")
    axb.set_ylim(0, 100)
    axb.grid(alpha=0.3)
    axb.set_xlabel("Год")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"График → {OUT}")
    print("\nКлючевые точки (доля DC среди конф. ВТСП):")
    for y in (2014, 2016, 2018, 2020, 2022, 2024, 2025):
        idx = YEARS.index(y)
        print(f"  {y}: DC={sdc[idx]} AC={sac[idx]} → доля DC={share[idx]:.0f}%")


if __name__ == "__main__":
    main()