#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 012: график грантового сигнала HTS-DC кабелей.

Данные — из signals/grant_signal.md (локально, без API):
  - по годам старта проектов
  - цвет = тип финансирования: конкурсный грант / гос. прямое / корпоративное+гос.заказ
  - врезка = география (страна/регион главных инициатор)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "case_studies/012_dc_hvdc_cables/plots/grants_hts_dc.png"

# (год_старта, название, тип, регион)
# типы: G = конкурсный грант, S = гос. прямое/программное, C = корпоративное+гос.заказ
GRANTS = [
    (2008, "LIPA HTS cable (US/AMSC) пилот", "C", "США"),
    (2013, "СПб 2.4 км HTS DC (ФСК ЕЭС) нач.", "S", "Россия"),
    (2013, "80 kV/500 МВт DC (KEPCO/KERI)", "S", "Корея"),
    (2013, "KEPCO/Ishikari DC (Япония)", "S", "Япония"),
    (2016, "Shingal 23 кВ (KEPCO+LS) — старт", "S", "Корея"),
    (2018, "NSF: Air-Core СК-генераторы", "G", "США"),
    (2019, "Ishikari 100 км дизайн (<50 кВ/500 МВт)", "S", "Япония"),
    (2020, "ComEd/AMSC Чикаго (первый постоянный US)", "C", "США"),
    (2021, "Shanghai 1.2 км 35 кВ (Xuhui)", "S", "Китай"),
    (2022, "SCARLET (EU MVDC MgB2)", "G", "ЕС"),
    (2023, "SUBRACABLE (EIC, Дания)", "G", "ЕС"),
    (2023, "NSF SBIR: HTS-wire production", "G", "США"),
    (2023, "SuperRail (SNCF+Nexans) квалификация", "C", "Франция"),
    (2024, "CABLEGNOSIS (Греция, Horizon)", "G", "ЕС"),
    (2024, "MVDC MgB2 hybrid (EU)", "G", "ЕС"),
    (2026, "MW-class EV fast-charging (Турция)", "G", "ЕС/Турция"),
    (2026, "VEIR (US венчур, ЦОД-кабели)", "C", "США"),
]

COL = {"G": "#1f77b4", "S": "#d62728", "C": "#ff7f0e"}
LBL = {"G": "конкурсный грант (Horizon/EIC/NSF)", "S": "гос. прямое/программное", "C": "корпоративное + гос. заказ"}


def main() -> None:
    by_year = {}
    for y, name, typ, _geo in GRANTS:
        by_year.setdefault(y, []).append((name, typ))

    years = sorted(by_year)
    fig = plt.figure(figsize=(13, 7))
    ax = fig.add_subplot(111)

    # stacked bars по типам
    y0 = [0 for _ in years]
    for typ in ("G", "S", "C"):
        vals = [sum(1 for _, t in by_year[y] if t == typ) for y in years]
        ax.bar(years, vals, bottom=y0, color=COL[typ], label=LBL[typ], alpha=0.85)
        y0 = [a + b for a, b in zip(y0, vals)]

    # подписи проектов: <=2 на год — имена; >2 — краткие имена + "+N"
    for y in years:
        stack = 0
        items = by_year[y]
        show = items[:2]
        rest = len(items) - len(show)
        for name, typ in show:
            ax.annotate(name.split(" (")[0][:24], (y, stack + 0.5), ha="center",
                        va="center", fontsize=6.5, color=COL[typ], rotation=90)
            stack += 1
        if rest:
            ax.annotate(f"+{rest}", (y, stack + 0.7), ha="center", va="center",
                        fontsize=8, color="#333333")

    ax.set_xlabel("Год старта проекта")
    ax.set_ylabel("Новых проектов/грантов")
    ax.set_title("Кейс 012: грантовый сигнал HTS-DC кабелей — старты по годам и типу финансирования")
    ax.set_xticks(years)
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.axvline(2018, color="red", ls="--", lw=1.2)
    ax.text(2018.15, max(y0 or [1]) * 0.93, "окно 2018", color="red", fontsize=9)

    # врезка: география
    ax2 = fig.add_axes([0.68, 0.68, 0.28, 0.26])
    from collections import Counter
    geo = Counter(g for _y, _n, _t, g in GRANTS)
    geol = {k: v for k, v in geo.items()}
    ax2.pie(list(geol.values()), labels=[f"{k}\n{v}" for k, v in geol.items()],
            colors=plt.cm.tab20.colors[:len(geol)], startangle=90, textprops={"fontsize": 7})
    ax2.set_title("География инициатив", fontsize=9)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"График → {OUT}")
    print(f"\nПроектов: {len(GRANTS)}")
    for typ in ("G", "S", "C"):
        n = sum(1 for _, _, t, _ in GRANTS if t == typ)
        print(f"  {LBL[typ]}: {n}")
    print("\nГеография:", dict(geol))


if __name__ == "__main__":
    main()