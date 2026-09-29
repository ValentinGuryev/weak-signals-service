#!/usr/bin/env python3
"""Красивые графики для образцового кейса IBAD-MgO (для жюри).

Четыре графика:
1. plot1_pubs_years.png — частота публикаций IBAD-MgO vs RABiTS vs ISD по годам (1997-2026)
   Строгий фильтр: технология прямо в заголовке (IBAD/RABiTS/ISD).
2. plot2_citation_graph.png — цитатный граф (S3): топ-статьи IBAD-MgO по цитируемости,
   рост цитируемости по годам (кумулятивная).
3. plot3_market_price.png — рынок REBCO $/кА·м: динамика цены (реперные точки).
4. plot4_semantic_shift.png — семантический сдвиг S2: прикладная vs лабораторная лексика
   в SNF-докладах по периодам (данные из src/semantic_shift_ibad.py).

Данные:
- data/raw/openalex/ibad_mgo_competitors.json (публикации IBAD/RABiTS/ISD)
- Экспертные/отраслевые реперные точки REBCO $/кА·м (пометка: верифицировать)
- Семантический сдвиг: посчитан src/semantic_shift_ibad.py (значения захардкожены ниже)

Выход: case_studies/001_ibad_mgo/plots/*.png
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OPENALEX = PROJECT_ROOT / "data" / "raw" / "openalex" / "ibad_mgo_competitors.json"
OUT = PROJECT_ROOT / "case_studies" / "001_ibad_mgo" / "plots"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.edgecolor": "#555",
    "axes.linewidth": 0.8,
    "figure.facecolor": "white",
})

# Палитра
C_IBAD = "#C0392B"   # красный — IBAD-MgO (герой)
C_RABITS = "#2471A3" # синий — RABiTS
C_ISD = "#7D3C98"    # фиолетовый — ISD
C_GOLD = "#B7950B"   # золото — рынок


STRICT_PATTERNS = {
    "ibad_mgo": re.compile(r"\bIBAD\b|ion[\s-]?beam[\s-]?assisted", re.I),
    "rabits": re.compile(r"\bRABiTS\b|rolling[\s-]?assisted", re.I),
    "isd": re.compile(r"\bISD\b|inclined substrate", re.I),
}


def load_competitors() -> dict:
    with open(OPENALEX) as f:
        return json.load(f)


def filter_strict(works: list[dict], comp: str) -> list[dict]:
    """Строгий фильтр: технология прямо в заголовке (IBAD/RABiTS/ISD).

    Широкий фильтр (слово «coated conductor») ловит всё поле сразу — все три
    технологии сливаются и график врёт (IBAD выглядит «как RABiTS»).
    Здесь — только статьи, где в заголовке есть сама технология.
    """
    pat = STRICT_PATTERNS[comp]
    return [w for w in works if pat.search(w.get("title", ""))]


def years_series(works: list[dict], y0: int = 1995, y1: int = 2026) -> dict[int, int]:
    c = Counter(w["year"] for w in works if w.get("year"))
    return {y: c.get(y, 0) for y in range(y0, y1 + 1)}


# ================= ГРАФИК 1: частота публикаций по годам =================

def plot_pubs_years():
    comps = load_competitors()
    fig, ax = plt.subplots(figsize=(11, 6))

    for comp, color, label in [("ibad_mgo", C_IBAD, "IBAD-MgO"),
                                ("rabits", C_RABITS, "RABiTS"),
                                ("isd", C_ISD, "ISD")]:
        works = filter_strict(comps[comp]["works"], comp)
        yrs = years_series(works)
        years = list(yrs.keys())
        vals = list(yrs.values())
        ax.bar(years, vals, color=color, alpha=0.75, label=label,
               width=0.55)
        # скользящее среднее
        if len(years) > 5:
            arr = np.array(vals, dtype=float)
            k = 3
            kernel = np.ones(k) / k
            sm = np.convolve(arr, kernel, mode="same")
            ax.plot(years, sm, color=color, lw=2.2, alpha=0.9)

    ax.set_ylabel("Публикации в год", fontsize=13)
    ax.set_title("Технологии текстурированных подложек для ВТСП-лент:\n"
                 "публикации с технологией в заголовке (OpenAlex, 1997-2026)",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=11, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.set_xlim(1995, 2027)
    ax.set_xlabel("Год", fontsize=12)

    # подпись о методе (честность)
    ax.text(0.99, 0.02,
            "Строгий фильтр: только статьи, где технология прямо в заголовке\n"
            "(IBAD / RABiTS / ISD). Широкий фильтр 'coated conductor' ловит всё поле сразу.",
            transform=ax.transAxes, fontsize=8, color="#999", va="bottom", ha="right")

    plt.tight_layout()
    out = OUT / "plot1_pubs_years.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"График 1 → {out}")


# ================= ГРАФИК 2: рождение темы (S3) =================

def plot_citation_graph():
    """Рождение темы IBAD-MgO: публикации + цитаты по годам.

    Панель (а): число публикаций IBAD-MgO по годам (рождение 1991-98,
    пик 2000-2012, зрелость/спад 2013+). Показывает «темы не было → родилась → росла».
    Панель (б): цитаты работ по году публикации (прокси; counts_by_year — TODO).
    """
    comps = load_competitors()
    works = filter_strict(comps["ibad_mgo"]["works"], "ibad_mgo")
    works = sorted(works, key=lambda w: w.get("year", 0))

    # По годам: число работ и сумма цитат
    years = sorted({w["year"] for w in works if w.get("year")})
    n_by_year = {y: 0 for y in years}
    c_by_year = {y: 0 for y in years}
    for w in works:
        y = w.get("year")
        if y:
            n_by_year[y] += 1
            c_by_year[y] += w.get("cited_by_count", 0)

    fig, (ax, ax2) = plt.subplots(
        1, 2, figsize=(13, 6), gridspec_kw={"width_ratios": [1.6, 1]})

    # (а) публикации по годам — рождение темы
    yrs = list(n_by_year.keys())
    vals = [n_by_year[y] for y in yrs]
    ax.bar(yrs, vals, color=C_IBAD, alpha=0.75, width=0.55, label="Публикации/год")
    # скользящее среднее (окно 3)
    arr = np.array(vals, dtype=float)
    sm = np.convolve(arr, np.ones(3) / 3, mode="same")
    ax.plot(yrs, sm, color="#7B241C", lw=2.5, label="Скользящее среднее (3 года)")

    # Аннотации фаз
    ax.axvspan(1991, 1998, color="#FADBD8", alpha=0.5, label="Зарождение (1991-98)")
    ax.axvspan(1999, 2012, color="#F5B7B1", alpha=0.4, label="Рост (1999-2012)")
    ax.axvspan(2013, 2026, color="#FDEDEC", alpha=0.5, label="Зрелость (2013+)")
    ax.annotate("Iijima 1991\n(первый IBAD)", xy=(1991, vals[0] + 0.3),
                xytext=(1994, max(vals) * 0.9), fontsize=9, color="#555",
                arrowprops=dict(arrowstyle="->", color="#888", lw=1))
    ax.annotate("Wang 1997\n(IBAD-MgO)", xy=(1997, n_by_year.get(1997, 0) + 0.3),
                xytext=(2000, max(vals) * 0.7), fontsize=9, color="#555",
                arrowprops=dict(arrowstyle="->", color="#888", lw=1))

    ax.set_xlabel("Год", fontsize=12)
    ax.set_ylabel("Публикации (IBAD-MgO в заголовке)", fontsize=11)
    ax.set_title("Рождение темы IBAD-MgO: публикации по годам\n"
                 "(темы не было → родилась → росла → зрелость)",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    # (б) цитаты: counts_by_year (реальные по годам получения) ИЛИ прокси
    root = Path(__file__).resolve().parent.parent.parent
    counts_file = root / "data/raw/openalex/ibad_counts_by_year.json"
    has_counts = counts_file.exists()
    if has_counts:
        try:
            counts = json.loads(counts_file.read_text(encoding="utf-8"))
            has_counts = len(counts) > 0
        except Exception:
            has_counts = False

    if has_counts:
        # РЕАЛЬНЫЕ цитаты по годам получения: суммируем counts_by_year по всем работам
        cite_by_calendar = {}
        for wid, cy in counts.items():
            for y, c in cy.items():
                cite_by_calendar[int(y)] = cite_by_calendar.get(int(y), 0) + c
        cyears = sorted(cite_by_calendar)
        cvals = [cite_by_calendar[y] for y in cyears]
        ax2.bar(cyears, cvals, color="#7B241C", alpha=0.8, width=0.6)
        cum = np.cumsum(cvals)
        ax2b = ax2.twinx()
        ax2b.plot(cyears, cum, color=C_IBAD, lw=2.5, marker="o", ms=4, label="Кумулятивно")
        ax2b.set_ylabel("Кумулятивные цитаты", fontsize=11)
        ax2.set_xlabel("Год", fontsize=12)
        ax2.set_ylabel("Цитаты, полученные в год (counts_by_year)", fontsize=10)
        ax2.set_title("Цитаты IBAD-MgO по годам ПОЛУЧЕНИЯ\n"
                     "(окно OpenAlex 2012-2026; пик 2016, далее плато)",
                      fontsize=11, fontweight="bold")
        # аннотация рождения
        first = next((y for y in cyears if cite_by_calendar[y] > 0), None)
        peak = max(cyears, key=lambda y: cite_by_calendar[y]) if cyears else None
        if first:
            ax2.annotate(f"первые цитаты {first}", xy=(first, cite_by_calendar[first]),
                         xytext=(first + 1, cite_by_calendar[peak] * 0.8),
                         fontsize=9, color="#7B241C",
                         arrowprops=dict(arrowstyle="->", color="#7B241C", lw=1))
        if peak:
            ax2.annotate(f"пик цитирования {peak}\n({cite_by_calendar[peak]} цит)",
                         xy=(peak, cite_by_calendar[peak]),
                         xytext=(peak - 6, cite_by_calendar[peak] * 0.85),
                         fontsize=9, color=C_IBAD,
                         arrowprops=dict(arrowstyle="->", color=C_IBAD, lw=1))
    else:
        # Прокси (нет counts_by_year)
        cvals = [c_by_year[y] for y in yrs]
        ax2.bar(yrs, cvals, color="#7B241C", alpha=0.8, width=0.55)
        cum = np.cumsum(cvals)
        ax2b = ax2.twinx()
        ax2b.plot(yrs, cum, color=C_IBAD, lw=2.5, marker="o", ms=4, label="Кумулятивно")
        ax2b.set_ylabel("Кумулятивные цитаты", fontsize=11)
        ax2.set_xlabel("Год", fontsize=12)
        ax2.set_ylabel("Цитаты работ года (сумма)", fontsize=10)
        ax2.set_title("Цитаты работ по году публикации\n(прокси; counts_by_year — ждём)",
                      fontsize=11, fontweight="bold")
        ax2.grid(axis="y", alpha=0.3)
        ax2b.legend(fontsize=8, loc="upper left")
        ax2.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    out = OUT / "plot2_citation_graph.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"График 2 → {out}")


# ================= ГРАФИК 3: рынок REBCO $/кА·м =================

def plot_market_price():
    """Динамика цены REBCO-лент в $/кА·м (реперные точки из SNF, 2026-08-30).

    Реальные данные из SNF-скана (rebco_price_snf.md): факты + цели + прогнозы.
    Источники: Selvamanickam CCA 2021, EUCAS 2013, manuscript 2014, ACCEPTED 2025.
    """
    # (год, цена $/кА·м, тип, подпись) — тип: 'факт' / 'цель' / 'прогноз'
    points = [
        (2010, 360, "факт", "CCA 2010 (Selvamanickam)"),
        (2011, 400, "факт", "YBCO tape (Century SC)"),
        (2013, 100, "цель", "EUROTAPES цель ~100€"),
        (2013, 100, "факт", "рынок $100/kAm"),
        (2014, 380, "факт", "350 €/кА·м (manuscript)"),
        (2021, 175, "факт", "реальность $150-200 (Selvamanickam)"),
        (2025, 90, "факт", "80-100 €/кА·м (обзор 2025)"),
        (2027, 50, "прогноз", "SuperLink цель 50€"),
    ]
    # факты — линия; цели/прогнозы — отдельные маркеры
    facts = [(y, p) for y, p, t, _ in points if t == "факт"]
    goals = [(y, p) for y, p, t, _ in points if t != "факт"]

    fig, ax = plt.subplots(figsize=(11, 6))
    fy = [x[0] for x in facts]; fp = [x[1] for x in facts]
    gy = [x[0] for x in goals]; gp = [x[1] for x in goals]
    ax.plot(fy, fp, color=C_GOLD, lw=3, marker="o", ms=8,
            markerfacecolor="white", markeredgecolor=C_GOLD, markeredgewidth=2,
            label="Факты (SNF)")
    ax.plot(gy, gp, "D--", color="#85929E", ms=8, label="Цели/прогнозы")
    ax.fill_between(fy, fp, alpha=0.12, color=C_GOLD)

    # аннотации
    for y, p, t, lab in points:
        dy = 40 if p < 200 else (60 if p < 350 else 80)
        ax.annotate(f"{p:.0f} $/кА·м", xy=(y, p), xytext=(y, p + dy),
                    ha="center", fontsize=9, color="#555",
                    arrowprops=dict(arrowstyle="-", color="#aaa", lw=0.8))
        ax.text(y, p - 25, lab, ha="center", fontsize=7, color="#999")

    ax.set_xlabel("Год", fontsize=13)
    ax.set_ylabel("Цена REBCO-ленты, $/кА·м", fontsize=13)
    ax.set_title("Стоимость REBCO-лент: реальные реперы из SNF (2010-2025)\n"
                 "×4 снижение (400→90), но цели (50) не достигнуты",
                 fontsize=14, fontweight="bold")
    ax.grid(alpha=0.3)
    ax.set_xlim(2008, 2029)
    ax.set_ylim(0, 480)
    ax.legend(fontsize=10, loc="upper right")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

    ax.text(0.98, 0.95, f"×{(400 / 90):.0f} дешевле\nза 14 лет",
            transform=ax.transAxes, ha="right", va="top", fontsize=13,
            fontweight="bold", color=C_GOLD,
            bbox=dict(boxstyle="round,pad=0.5", fc="#FFF8E1", ec=C_GOLD))

    ax.text(0.02, 0.02,
            "Данные: SNF-скан (Selvamanickam CCA 2021, EUCAS 2013, manuscript 2014, ACCEPTED 2025).\n"
            "Цены производители показывают графиками — это текстовые реперы, верифицировать по слайдам.\n"
            "См. signals/rebco_price_snf.md",
            transform=ax.transAxes, fontsize=8, color="#999", va="bottom")

    plt.tight_layout()
    out = OUT / "plot3_market_price.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"График 3 → {out}")


# ================= ГРАФИК 4: семантический сдвиг (S2) =================

# Данные из src/semantic_shift_ibad.py (SNF, на 1000 слов)
SEMANTIC_DATA = {
    "periods": ["2008-2010", "2011-2013", "2014-2016", "2017-2019", "2020-2022", "2023-2025"],
    "appl": [47.45, 36.86, 38.26, 30.13, 47.34, 58.45],   # прикладная лексика ‰
    "lab": [66.16, 52.96, 47.52, 35.20, 40.67, 31.03],    # лабораторная лексика ‰
    "docs": [54, 46, 76, 24, 37, 91],                     # докладов в периоде
}


def plot_semantic_shift():
    """Семантический сдвиг S2: «показали эффект» → «интегрировали в устройства»."""
    d = SEMANTIC_DATA
    x = np.arange(len(d["periods"]))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 6))
    b1 = ax.bar(x - width / 2, d["appl"], width, color=C_IBAD, alpha=0.85,
                label="Прикладная / системная лексика")
    b2 = ax.bar(x + width / 2, d["lab"], width, color="#85929E", alpha=0.85,
                label="Лабораторная лексика (лента, Ic, потери)")

    # разница Δ = appl − lab
    for i, (a, l) in enumerate(zip(d["appl"], d["lab"])):
        delta = a - l
        col = C_IBAD if delta >= 0 else "#85929E"
        ax.text(x[i], max(a, l) + 1.5, f"Δ{delta:+.0f}",
                ha="center", fontsize=11, fontweight="bold", color=col)

    ax.axhline(0, color="#888", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{p}\n({n} докл.)" for p, n in zip(d["periods"], d["docs"])])
    ax.set_ylabel("Частота лексики, ‰ (на 1000 слов)", fontsize=12)
    ax.set_title("Семантический сдвиг S2: «показали эффект на ленте» → «интегрировали в устройства»\n"
                 "(SNF-доклады по IBAD, 2008-2025)",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, 75)

    # аннотация кроссовера
    ax.annotate("Кроссовер ≈ 2017-2019\n(IBAD-MgO стал стандартом 2G HTS)",
                xy=(3, 36), xytext=(0.9, 58),
                fontsize=10, color="#555",
                arrowprops=dict(arrowstyle="->", color="#888", lw=1))

    ax.text(0.99, 0.02,
            "Источник: SNF-доклады по теме ibad_tapes (474 PDF).\n"
            "Метод: частота прикладной vs лабораторной лексики (см. src/semantic_shift_ibad.py)",
            transform=ax.transAxes, fontsize=8, color="#999", va="bottom", ha="right")

    plt.tight_layout()
    out = OUT / "plot4_semantic_shift.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"График 4 → {out}")


def plot_semantic_shift_v2():
    """Семантический сдвиг S2 v3: дискриминация АБСТРАКТОВ OpenAlex IBAD-корпуса.

    Полная база: 433 релевантные работы (1997-2026), 369 с абстрактами.
    Дискриминатор v2 → доля прикладных/фундаментальных по периодам.
    Источник: results/case_signals/ibad_abstracts_discrimination.json
    (НЕ SNF — чтобы избежать дублей с OpenAlex).
    """
    root = Path(__file__).resolve().parent.parent.parent
    disc = json.loads((root / "results/case_signals/ibad_abstracts_discrimination.json")
                      .read_text(encoding="utf-8"))
    bp = disc["by_period"]
    periods = list(bp.keys())
    n = [bp[p]["n"] for p in periods]
    appl = [100 * bp[p]["appl_share"] for p in periods]
    fund = [100 * bp[p]["fund_share"] for p in periods]
    mix = [100 * bp[p]["n_mix"] / bp[p]["n"] for p in periods]

    x = np.arange(len(periods))
    fig, ax = plt.subplots(figsize=(11, 6))
    b1 = ax.bar(x - 0.25, appl, 0.25, color=C_IBAD, alpha=0.85, label="Прикладные")
    b2 = ax.bar(x, fund, 0.25, color="#85929E", alpha=0.85, label="Фундаментальные")
    b3 = ax.bar(x + 0.25, mix, 0.25, color="#B0BEC5", alpha=0.7, label="Смешанные")

    # подписи n
    for i, nn in enumerate(n):
        ax.text(x[i], 104, f"n={nn}", ha="center", fontsize=8, color="#555")

    # доля прикладных поверх
    ax.plot(x, appl, "o-", color="#1A5276", lw=2, ms=5, label="Доля прикладных (тренд)")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{p}\n({n[i]} ст.)" for i, p in enumerate(periods)], fontsize=9)
    ax.set_ylabel("Доля абстрактов, %", fontsize=12)
    ax.set_title("Дискриминация абстрактов IBAD-корпуса OpenAlex (1997-2026)\n"
                 "Фундаментальные vs прикладные — доля прикладных стабильна (11-23%),\n"
                 "производственный сдвиг виден в SNF/патентах, а не в научных статьях",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, 110)

    ax.text(0.99, 0.02,
            "Данные: OpenAlex, 433 релевантных работы IBAD-семейства (1997-2026), 369 с абстрактами.\n"
            "Метод: semantic_shift_v2.classify_document (абстракт-режим, коррекция по заголовку).\n"
            "Вывод: научные статьи по IBAD остаются материаловедческими; производство — в SNF/патентах.",
            transform=ax.transAxes, fontsize=8, color="#999", va="bottom", ha="right")

    plt.tight_layout()
    out = OUT / "plot4_semantic_shift_v2.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"График 4 v2 → {out}")


def plot_knowledge_graph():
    """Граф знания S3: возникновение кластера цитирований IBAD (из referenced_works).

    Показывает появление кластера: работы-якоря (Wang 1997, Arendt 2004...) и как
    на них ссылаются последующие работы. Строится из ibad_references.json (докачивается
    openalex_counts_refs.py, когда OpenAlex снимет 429). Если данных нет — пропускаем.
    """
    root = Path(__file__).resolve().parent.parent.parent
    refs_file = root / "data/raw/openalex/ibad_references.json"
    corpus_file = root / "data/raw/openalex/ibad_abstracts_corpus.json"
    if not refs_file.exists():
        print("График 6 (граф знания): данных нет (ждём докачку counts_by_year/references)")
        return
    refs = json.loads(refs_file.read_text(encoding="utf-8"))
    corpus = json.loads(corpus_file.read_text(encoding="utf-8"))
    works = {w["id"]: w for w in corpus["works"]}
    print(f"График 6: {len(refs)} работ с references")

    try:
        import networkx as nx
    except ImportError:
        print("График 6: networkx недоступен — пропуск")
        return

    G = nx.DiGraph()
    # узлы: работы корпуса + их references (если в корпусе)
    for wid, wrefs in refs.items():
        if wid not in works:
            continue
        w = works[wid]
        G.add_node(wid, year=w.get("year"), title=w.get("title", "")[:40],
                   cites=w.get("cited_by_count", 0))
        for r in wrefs:
            if r in works:  # только связи внутри кластера
                G.add_edge(wid, r)

    if G.number_of_nodes() < 5:
        print(f"График 6: слишком мало узлов ({G.number_of_nodes()}) — пропуск")
        return

    # позиции: по году (x) и по цитируемости (y)
    pos = {}
    for n in G.nodes:
        y = G.nodes[n].get("year", 2000)
        c = G.nodes[n].get("cites", 0)
        pos[n] = (y + np.random.uniform(-0.3, 0.3), np.log1p(c))

    fig, ax = plt.subplots(figsize=(12, 7))
    years = [G.nodes[n].get("year", 2000) for n in G.nodes]
    cites = [np.log1p(G.nodes[n].get("cites", 0)) for n in G.nodes]
    colors = [plt.cm.Reds(0.3 + 0.7 * (c / max(cites))) for c in cites] if max(cites) > 0 else "#C0392B"

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.25, edge_color="#888", arrows=True, arrowsize=8)
    nodes = nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colors, node_size=120, alpha=0.8)
    labels = {n: f"{G.nodes[n]['year']}" for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=7)

    # якоря подписаны
    anchors = [n for n in G.nodes if "Wang" in G.nodes[n].get("title", "") or
               "Arendt" in G.nodes[n].get("title", "") or "Foltyn" in G.nodes[n].get("title", "")]
    for n in anchors:
        ax.annotate(G.nodes[n]["title"], xy=pos[n], xytext=(pos[n][0] + 0.5, pos[n][1] + 0.3),
                    fontsize=8, color="#C0392B",
                    arrowprops=dict(arrowstyle="->", color="#C0392B", lw=0.8))

    ax.set_xlabel("Год публикации", fontsize=12)
    ax.set_ylabel("log(1+цитаты)", fontsize=12)
    ax.set_title("Граф знания S3: кластер цитирований IBAD-MgO\n"
                 "(рождение кластера: якоря 1997-2004 → рост ссылок)",
                 fontsize=13, fontweight="bold")
    ax.grid(alpha=0.2)
    plt.tight_layout()
    out = OUT / "plot6_knowledge_graph.png"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"График 6 → {out}")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    plot_pubs_years()
    plot_citation_graph()
    plot_market_price()
    plot_semantic_shift()
    plot_semantic_shift_v2()
    plot_knowledge_graph()
    print("Все графики готовы.")
