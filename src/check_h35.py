#!/usr/bin/env python3
"""Заход 4 — проверка H35 (Kleinberg 2002): burst-иерархия = каскад баз.

Кейс 011 (SRF/Nb3Sn): сравниваем burst-структуру pub (весь корпус), conf (конференционные
работы корпуса), патентов (Lens 79) и ядра Nb3Sn (208 работ) — иерархия уровней burst'ов
и каскад их начала по базам.

Реализация: автомат Клейнберга (Poisson-эмиссия, уровни 0..L с rate_j = lambda_0 * s^j,
стоимость перехода вверх gamma*ln(n) за уровень, DP-оптимизация последовательности состояний).

Данные: локальные (0 запросов к API). Окно для фич модели = <=2018 (см. выход отдельно).

2026-09-18
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
from scipy.special import gammaln

ROOT = Path(__file__).resolve().parent.parent

YEAR0 = 1965  # начало ряда (покрывает первые работы корпуса)
YEAR1 = 2026

BASE_DIRS = [
    "data/raw/openalex/srf_corpus.json",
    "data/raw/openalex/srf_nb3sn_subset.json",
    "data/raw/patents/cases/011_srf_cavities.json",
]


def load(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def series_from_works(works, year0=YEAR0, year1=YEAR1):
    """Счётчик работ по годам (массив year1-year0+1)."""
    counts = np.zeros(year1 - year0 + 1, dtype=int)
    for w in works:
        y = w.get("year")
        if y is None:
            continue
        try:
            y = int(y)
        except (TypeError, ValueError):
            continue
        if year0 <= y <= year1:
            counts[y - year0] += 1
    return counts


def kleinberg(counts, s=2.0, gamma=1.0, max_levels=10):
    """Burst-детекция Клейнберга.

    counts: массив числа событий на единицу времени (год).
    Возвращает: states (уровень 0..L на год), rates (rate каждого уровня).
    """
    T = len(counts)
    n = int(counts.sum())
    counts = np.asarray(counts, dtype=float)
    if n == 0:
        return np.zeros(T, dtype=int), np.array([0.0])
    lam0 = n / T
    c_max = counts.max()
    # число уровней: чтобы lambda_0*s^L покрыло максимум
    if lam0 > 0:
        L = int(np.ceil(math.log(max(1.0, c_max) / (lam0 * s)) / math.log(s))) + 1
    else:
        L = 1
    L = max(L, 2)
    L = min(L, max_levels)
    rates = lam0 * s ** np.arange(L + 1)

    logs = gammaln(counts + 1.0)
    E = np.zeros((T, L + 1))
    for j in range(L + 1):
        r = rates[j]
        E[:, j] = r - counts * np.log(max(r, 1e-12)) + logs

    jump = gamma * math.log(n + 1)
    C = np.zeros((L + 1, L + 1))
    for i in range(L + 1):
        for j in range(L + 1):
            if j > i:
                C[i, j] = (j - i) * jump

    dp = E[0].copy()
    parent = np.zeros((T, L + 1), dtype=int)
    for t in range(1, T):
        newdp = np.full(L + 1, np.inf)
        for j in range(L + 1):
            costs = dp + C[:, j]
            i_best = int(np.argmin(costs))
            parent[t, j] = i_best
            newdp[j] = costs[i_best] + E[t, j]
        dp = newdp
    states = np.zeros(T, dtype=int)
    j = int(np.argmin(dp))
    states[-1] = j
    for t in range(T - 1, 0, -1):
        j = parent[t, j]
        states[t - 1] = j
    return states, rates


def bursts_from_states(states, year0):
    """Список burst'ов: [{'start','end','level','len'}] — уровни >= 1, склеивая соседние."""
    bursts = []
    t = 0
    T = len(states)
    while t < T:
        if states[t] >= 1:
            t0 = t
            while t < T and states[t] >= 1:
                t += 1
            bursts.append(
                {
                    "start": year0 + t0,
                    "end": year0 + t - 1,
                    "level": int(states[t0 : t + 1].max()) if t < T else int(states[t0:t].max()),
                    "len": t - t0,
                }
            )
        else:
            t += 1
    return bursts


def hist_levels(states):
    uniq, cnts = np.unique(states, return_counts=True)
    return {int(u): int(c) for u, c in zip(uniq, cnts)}


def main():
    out = {}

    # ---- загрузка баз ----
    corpus = load(ROOT / BASE_DIRS[0])
    works = corpus["works"]
    out["corpus"] = {
        "n_works": len(works),
        "n_with_year": sum(1 for w in works if w.get("year") is not None),
        "queries": corpus.get("queries"),
    }
    series_pubs_all = series_from_works(works)
    series_pubs_conf = series_from_works([w for w in works if (w.get("type") or "").startswith("conference")])
    series_pubs_nonconf = series_from_works([w for w in works if not (w.get("type") or "").startswith("conference")])

    nb = load(ROOT / BASE_DIRS[1])
    core = nb.get("works_core", [])
    full_nc = nb.get("works_full_noncore", [])
    series_nb3sn = series_from_works(core + full_nc)
    series_nb3sn_core = series_from_works(core)
    out["nb3sn"] = {
        "n_core": len(core),
        "n_full_noncore": len(full_nc),
        "n_core_title": nb.get("n_core_title"),
        "n_full_title_abstract": nb.get("n_full_title_abstract"),
        "n_control_nb": nb.get("n_control_nb"),
    }

    pat = load(ROOT / BASE_DIRS[2])
    patents = pat.get("patents", [])
    series_patents = series_from_works(patents)
    out["patents"] = {"raw": pat.get("raw"), "uniq": pat.get("uniq"),
                      "relevant_count": pat.get("relevant_count"), "n_loaded": len(patents)}

    # Nb3Sn-специфичные патенты (по паспорту: подграф-фильтр nb3sn/niobium-tin)
    import re
    NB3SN_RE = re.compile(r"nb\s*3\s*sn|niobium[\s-]?tin|b3sn|tin\s*cavity", re.I)
    nb3sn_patents = [p for p in patents if NB3SN_RE.search((p.get("title") or "") + " " + (p.get("abstract") or ""))]
    series_patents_nb3sn = series_from_works(nb3sn_patents)
    out["patents_nb3sn"] = {
        "n": len(nb3sn_patents),
        "years": {int(p.get("year")): 1 for p in nb3sn_patents} if nb3sn_patents else {},
    }

    # Nb3Sn-conf слой (srf_nb3sn_conf_subset) — для каскада conf-подслоя
    conf_sub = load(ROOT / "data/raw/conferences/srf_nb3sn_conf_subset.json")
    conf_works = conf_sub.get("works_title", [])
    by_year = conf_sub.get("by_year", {})
    series_conf_nb3sn = np.zeros(YEAR1 - YEAR0 + 1, dtype=int)
    for y, n in by_year.items():
        if YEAR0 <= int(y) <= YEAR1:
            series_conf_nb3sn[int(y) - YEAR0] = int(n)
    out["conf_nb3sn"] = {"n": len(conf_works), "by_year": by_year}

    years = list(range(YEAR0, YEAR1 + 1))

    # ---- burst-детекция по каждой базе ----
    bases = {
        "pubs_corpus_all": ("Публикации SRF, весь корпус (n=%d)" % len(works), series_pubs_all),
        "pubs_conf": ("Конференционные работы SRF (n=%d)" % series_pubs_conf.sum(), series_pubs_conf),
        "pubs_nonconf": ("Не-конференционные публикации SRF (n=%d)" % series_pubs_nonconf.sum(), series_pubs_nonconf),
        "nb3sn_core_full": ("Nb3Sn ядро+полные (n=%d)" % (len(core) + len(full_nc)), series_nb3sn),
        "nb3sn_core": ("Nb3Sn ядро по титулам (n=%d)" % len(core), series_nb3sn_core),
        "patents_011": ("Патенты кейса 011 (n=%d)" % len(patents), series_patents),
        "patents_011_nb3sn": ("Nb3Sn-специф. патенты (n=%d)" % len(nb3sn_patents), series_patents_nb3sn),
        "conf_nb3sn": ("Nb3Sn-конференц. работы (n=%d)" % series_conf_nb3sn.sum(), series_conf_nb3sn),
    }

    results = {}
    for name, (label, ser) in bases.items():
        states, rates = kleinberg(ser)
        bursts = bursts_from_states(states, YEAR0)
        results[name] = {
            "label": label,
            "total": int(ser.sum()),
            "nonzero_years": int((ser > 0).sum()),
            "levels_hist": hist_levels(states),
            "n_bursts": len(bursts),
            "bursts": bursts,
            # окно фич <=2018: активность burst'ов, начавшихся до/в 2018
            "bursts_le2018": [b for b in bursts if b["start"] <= 2018 and b["level"] >= 1],
            "max_level_overall": max((b["level"] for b in bursts), default=0),
        }
        print(f"\n=== {name} ({label}) ===")
        print("  counts:", " ".join(f"{y}:{int(c)}" for y, c in zip(years, ser) if c > 0))
        print("  levels (лет в состоянии):", results[name]["levels_hist"])
        for b in bursts:
            print(f"  burst {b['start']}-{b['end']} level={b['level']} len={b['len']}")

    # ---- каскад: первое значимое начало burst'а по базам (окно feature <=2018 vs 2019+) ----
    cascade = {}
    for name in ["nb3sn_core_full", "conf_nb3sn", "patents_011_nb3sn", "pubs_corpus_all", "pubs_conf", "patents_011"]:
        bl = results[name]["bursts"]
        first_ge1 = next((b["start"] for b in bl if b["level"] >= 1), None)
        first_ge2 = next((b["start"] for b in bl if b["level"] >= 2), None)
        first_ge3 = next((b["start"] for b in bl if b["level"] >= 3), None)
        cascade[name] = {"first_burst": first_ge1, "first_level2": first_ge2, "first_level3": first_ge3,
                         "max_level": results[name]["max_level_overall"]}
        print(f"\nКаскад {name}: первый burst={first_ge1}, lvl2={first_ge2}, lvl3={first_ge3}, max_level={cascade[name]['max_level']}")

    # ---- выравнивание burst-периодов 2018-2026 ----
    both = next((b for b in results["pubs_corpus_all"]["bursts"] if b["start"] >= 2015), None)
    print(f"\nКрупный burst pubs_corpus_all после 2015: {both}")

    out["series"] = {name: {name2: int(v) for name2, v in zip([str(y) for y in years], ser)}
                     for name, (label, ser) in bases.items()}
    out["results"] = results
    out["cascade"] = cascade

    with open(ROOT / "results" / "h35_stats.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("\nSaved results/h35_stats.json")


if __name__ == "__main__":
    main()