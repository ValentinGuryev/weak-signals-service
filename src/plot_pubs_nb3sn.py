#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011 (ТРЕНД Nb3Sn SRF): пересборка публикационного сигнала под новое видение.

ЗАДАЧА (решение команды): тренд кейса — Nb3Sn SRF (замена ниобия), а НЕ SRF вообще.
Nb SRF — зрелая конкурирующая технология (контроль). Публикационный сигнал пересобирается
ИЗ УЖЕ СУЩЕСТВУЮЩЕГО корпуса srf_corpus.json (7579 работ) — НОВЫХ API-запросов НЕ нужно:
запрос №3 паспорта «Nb3Sn cavity/Nb3Sn SRF/niobium-tin cavity» был сделан при сборе 2026-09-11.

Извлечение: подмножество работ, где Nb3Sn/niobium-tin встречается в ТИТУЛЕ (ядро, 208 шт.)
или в абстракте (полное, 327 шт.). Контрольная группа Nb-spec: литлогика по title.

Выход (данные + сигнал, НЕ только график):
  data/raw/openalex/srf_nb3sn_subset.json        — извлечённое подмножество (ядро+полное)
  case_studies/011_srf_cavities/plots/pubs_nb3sn_by_year.png — график динамики
  case_studies/011_srf_cavities/signals/publication_signal.md — анализ сигнала (генерируется частично)

Расход API: 0 новых запросов.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/raw/openalex/srf_corpus.json"
SUB = ROOT / "data/raw/openalex/srf_nb3sn_subset.json"
OUT = ROOT / "case_studies/011_srf_cavities/plots/pubs_nb3sn_by_year.png"

PAT = re.compile(r"nb\s*3\s*sn|niobium[\s-]?tin|niob[\s-]?tin|b3sn", re.I)
PAT_NB_ONLY = re.compile(r"\bniobium\b|\bNb\b", re.I)


def cite(w):
    cb = w.get("cited_by")
    return cb.get("count") if isinstance(cb, dict) else (cb or 0)


def main() -> None:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    works = d["works"]
    print("всего в корпусе:", len(works))

    core, full = [], []
    for w in works:
        t = w.get("title") or ""
        a = w.get("abstract") or ""
        if PAT.search(t):
            core.append(w)
            full.append(w)          # ядро ⊂ полное
        elif PAT.search(a):
            full.append(w)

    # дедуп на всякий случай
    seen, full2 = set(), []
    for w in full:
        i = w.get("id")
        if i in seen:
            continue
        seen.add(i)
        full2.append(w)
    full = full2

    print(f"Nb3Sn в титуле (ядро): {len(core)} | в титуле+абстракте (полное): {len(full)}")

    # контроль: ниобиевые работы (Nb в title, БЕЗ Nb3Sn) — зрелая технология
    nb = [w for w in works
          if PAT_NB_ONLY.search(w.get("title") or "") and not PAT.search(w.get("title") or "")]
    print(f"контроль Nb (Nb в title, без Nb3Sn): {len(nb)}")

    # динамика
    def years(wlist):
        return Counter(w.get("year") for w in wlist if w.get("year"))

    yc_core, yc_full, yc_nb = years(core), years(full), years(nb)
    lo = min([min(yc_full), min(yc_nb)] + [2010])
    hi = max([max(yc_full), max(yc_nb)] + [2026])
    years_r = range(lo, hi + 1)
    c_full = [yc_full.get(y, 0) for y in years_r]
    c_core = [yc_core.get(y, 0) for y in years_r]
    c_nb = [yc_nb.get(y, 0) for y in years_r]

    # 3-летнее сглаживание (урок «эхо» датировки)
    def smooth(v):
        out = []
        for i in range(len(v)):
            a = v[max(0, i - 1):i + 2]
            out.append(sum(a) / len(a))
        return out

    sm_full = smooth(c_full)
    sm_nb = smooth(c_nb)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    ax = axes[0]
    ax.bar([y for y in years_r], c_full, color="#d62728", alpha=0.85, label="Nb3Sn (title+abstract)")
    ax.bar([y for y in years_r], c_core, color="#ff7f0e", alpha=0.85, label="Nb3Sn (title-ядро)")
    ax.axvline(2018, color="black", ls="--", lw=1.2)
    ax.text(2018.2, max(c_full) * 0.92, "окно 2018", fontsize=9, rotation=90, va="top")
    ax.set_title(f"ТРЕНД Nb3Sn SRF: {len(full)} работ (полное), {len(core)} в титуле\n"
                 f"зарождение 2015 (proof-of-principle), рост 2017-18, всплеск 2023-25", fontsize=10)
    ax.set_xlabel("год"); ax.set_ylabel("работ"); ax.grid(alpha=0.3); ax.legend(fontsize=8)

    ax = axes[1]
    ax.plot(years_r, sm_full, color="#d62728", lw=2, label="Nb3Sn SRF (сглаж.)")
    ax.plot(years_r, sm_nb, color="#1f77b4", lw=2, ls="--", label="Nb SRF (контроль, сглаж.)")
    for y, lbl in [(2015, "PoP Cornell"), (2018, "окно"), (2022, "Snowmass"), (2023, "всплеск")]:
        ax.axvline(y, color="gray", ls=":", lw=0.8)
        ax.text(y, max(sm_full + sm_nb) * 0.97, lbl, fontsize=7, ha="center", color="gray")
    ax.set_title("Сглаженный тренд: Nb3Sn растёт на фоне зрелой Nb-технологии\n"
                 "(Nb — контроль: зрелый, НЕ тренд)", fontsize=10)
    ax.set_xlabel("год"); ax.set_ylabel("работ/год (сглаж.)"); ax.grid(alpha=0.3); ax.legend(fontsize=8)

    fig.suptitle("S1a — Кейс 011: публикационный сигнал ТРЕНДА Nb3Sn SRF (по новому видению)", fontsize=13)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    print("saved:", OUT)

    # сохраняем подмножество отдельно (без API)
    SUB.write_text(json.dumps({
        "case": "011_srf_cavities",
        "signal": "publications (тренд Nb3Sn SRF)",
        "date": "2026-09-12",
        "method": "фильтрация существующего srf_corpus.json (БЕЗ новых API-запросов)",
        "source_corpus": "data/raw/openalex/srf_corpus.json",
        "pattern": str(PAT.pattern),
        "n_core_title": len(core),
        "n_full_title_abstract": len(full),
        "n_control_nb": len(nb),
        "works_core": [{"id": w.get("id"), "title": w.get("title"), "year": w.get("year"),
                        "cited_by": cite(w)} for w in core],
        "works_full_noncore": [{"id": w.get("id"), "title": w.get("title"), "year": w.get("year"),
                                "cited_by": cite(w)} for w in full if w not in core],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved:", SUB)

    # сводка для сигнала
    print("\n== Динамика Nb3Sn (полное) ==")
    for y in sorted(yc_full):
        if y >= 2008:
            print(f"  {y}: {yc_full[y]}")
    print("\nТОП-10 по цитированию (полное):")
    for w in sorted(full, key=lambda w: -cite(w))[:10]:
        print(f"  [{w.get('year')}] c={cite(w)} | {(w.get('title') or '')[:90]}")


if __name__ == "__main__":
    main()