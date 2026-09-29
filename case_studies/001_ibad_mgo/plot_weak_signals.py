#!/usr/bin/env python3
"""Динамика «слабых сигналов» IBAD: появление и рост новых терминов по годам.

Слабый сигнал = термин, впервые появившийся в корпусе IBAD в год Y и растущий далее.
Курируемый список СМЫСЛОВЫХ сигналов (вручную отобраны из биграмм, без мусора).

Выход: case_studies/001_ibad_mgo/plots/plot8_weak_signals.png
       + печать хронологии.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CORPUS = PROJECT_ROOT / "data/raw/openalex/ibad_abstracts_corpus.json"
OUT = PROJECT_ROOT / "case_studies" / "001_ibad_mgo" / "plots"

# Смысловые «слабые сигналы» (биграммы-маркеры эволюции технологии)
# {термин: (год появления, подпись)}
SIGNALS = [
    ("ysz buffer", 1997, "IBAD-YSZ буфер"),
    ("cube texture", 2000, "Кубическая текстура (RABiTS)"),
    ("seed layers", 2001, "Сид-слои буферов"),
    ("self-epitaxial", 2004, "Само-эпитаксия MgO"),
    ("fabrication rate", 2004, "Скорость производства"),
    ("artificial pinning", 2006, "Искусственный пиннинг"),
    ("mgo buffer", 2006, "MgO буфер"),
    ("doped ybco", 2012, "Легированный YBCO"),
    ("lanthanum zirconate", 2012, "La2Zr2O7 (LZO) буфер"),
    ("bso-doped gdbco", 2014, "BSO-легированный GdBCO"),
    ("planarization layer", 2014, "Планаризация (CSD)"),
    ("magnetic pinning", 2016, "Магнитный пиннинг"),
    ("fesexte thin", 2016, "Fe(Se,Te) плёнки"),
    ("bzo nanostructure", 2021, "BZO наноструктуры"),
    ("epi-mgo layer", 2023, "Эпитаксиальный MgO слой"),
    ("ibad-mgo layer", 2023, "IBAD-MgO слой"),
    ("josephson junction", 2026, "Джозефсоновские переходы"),
]


def bigrams(text: str) -> list[str]:
    words = re.findall(r"[a-z][a-z\-]{2,}", text.lower())
    return [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]


def bg_contains(term: str) -> callable:
    """Проверка биграммы на термин (с учётом дефисов)."""
    t = term.replace("-", "")
    return lambda bg: bg.replace("-", "") == t or bg.replace("-", "").startswith(t)


def main() -> None:
    d = json.loads(CORPUS.read_text(encoding="utf-8"))
    works = [w for w in d["works"] if w.get("abstract") and w.get("year")]

    # год -> счётчик биграмм
    year_bg = defaultdict(Counter)
    for w in works:
        y = w["year"]
        for bg in bigrams(w["abstract"]):
            year_bg[y][bg] += 1

    # нормализация на число работ в год (‰ от абстрактов)
    n_by_year = Counter(w["year"] for w in works)

    years_all = sorted(n_by_year)
    fig, ax = plt.subplots(figsize=(13, 7))

    colors = plt.cm.viridis(np.linspace(0.05, 0.95, len(SIGNALS)))
    print("=== Слабые сигналы IBAD (появление и рост) ===\n")
    for (term, birth, label), color in zip(SIGNALS, colors):
        matcher = bg_contains(term)
        series = []
        xs = []
        for y in years_all:
            c = sum(cnt for bg, cnt in year_bg[y].items() if matcher(bg))
            n = n_by_year[y]
            norm = 1000 * c / n if n else 0
            if norm > 0 or y >= birth - 1:
                xs.append(y)
                series.append(norm)
        # только если термин реально встречался
        if max(series) == 0:
            continue
        ax.plot(xs, series, "o-", lw=2, ms=4, color=color, alpha=0.85,
                label=f"{label} ({birth})")
        # отметка рождения
        ax.axvline(birth, color=color, lw=0.6, ls=":", alpha=0.4)
        print(f"  {birth}: {label} [{term}]")

    ax.set_xlabel("Год", fontsize=12)
    ax.set_ylabel("Вхождения на 1000 абстрактов (норм.)", fontsize=11)
    ax.set_title("Слабые сигналы IBAD-MgO: появление и рост смысловых терминов\n"
                 "(нормировано на число работ в год)",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=8, loc="upper left", ncol=2)
    ax.grid(alpha=0.3)
    ax.set_xlim(1995, 2027)

    ax.text(0.99, 0.02,
            "Слабый сигнал = термин впервые появился в году Y и рос далее.\n"
            "Данные: OpenAlex, корпус IBAD (427 работ, 365 с абстрактами).",
            transform=ax.transAxes, fontsize=8, color="#999", va="bottom", ha="right")

    plt.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "plot8_weak_signals.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"\nГрафик: {out}")


if __name__ == "__main__":
    main()
