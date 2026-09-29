#!/usr/bin/env python3
"""Фазы тренда / ядра кластера для JTWPA (кейс 007, S3).

Адаптация src/trend_phases_snspd.py под jtwpa-корпус (класс A + B):
- Ядро = работы с наибольшим числом ВХОДЯЩИХ ссылок внутри корпуса (A+B);
- Серия f(y) = число ссылок на ядро работами, опубликованными в год y;
- Развитие = ускоренный рост (Δ² > 0) до пика; Состоялся = год пика.

Данные: data/raw/openalex/jtwpa_full.json (refs) + jtwpa_corpus.json
Выход: results/case_signals/trend_phases_jtwpa.json + plots/plot_s3_trend_phases.png
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REFS = PROJECT_ROOT / "data/raw/openalex/jtwpa_full.json"
CORPUS = PROJECT_ROOT / "data/raw/openalex/jtwpa_corpus.json"
OUT_JSON = PROJECT_ROOT / "results/case_signals/trend_phases_jtwpa.json"
OUT_PNG = PROJECT_ROOT / "case_studies/007_jtwpa/plots/plot_s3_trend_phases.png"


def smooth(series: dict, window: int = 3) -> dict:
    years = sorted(series)
    out = {}
    for i, y in enumerate(years):
        lo = max(0, i - window // 2)
        hi = min(len(years), i + window // 2 + 1)
        vals = [series[years[j]] for j in range(lo, hi)]
        out[y] = sum(vals) / len(vals)
    return out


def phases_for(series: dict) -> dict:
    if not series:
        return {"first_cite": None, "peak_year": None, "development": [], "established": None, "series": {}}
    years = sorted(series)
    first_cite = min(years)
    s = smooth(series)
    syears = sorted(s)
    peak_year = max(syears, key=lambda y: s[y])
    peak_idx = syears.index(peak_year)
    growth = syears[: peak_idx + 1]
    d1, d2 = {}, {}
    for i in range(1, len(syears)):
        d1[syears[i]] = s[syears[i]] - s[syears[i - 1]]
    for i in range(1, len(syears)):
        if syears[i - 1] in d1 and syears[i] in d1:
            d2[syears[i]] = d1[syears[i]] - d1[syears[i - 1]]
    dev_years = [y for y in growth if y in d1 and y in d2 and d1[y] > 0 and d2[y] > 0]
    return {"first_cite": first_cite, "peak_year": peak_year,
            "development": dev_years, "established": peak_year, "series": series}


def main() -> None:
    raw_refs = json.loads(REFS.read_text(encoding="utf-8"))
    refs = {wid: v.get("referenced_works", []) for wid, v in raw_refs.items()}
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    ws = corpus if isinstance(corpus, list) else corpus.get("works", [])
    works = {w["id"]: w for w in ws}
    print(f"Корпус: {len(works)} работ, с refs: {len(refs)}")

    # Входящие ссылки внутри корпуса
    incoming = Counter()
    for wid, rlist in refs.items():
        for r in rlist:
            if r in works:
                incoming[r] += 1
    print(f"Внутренних ссылок: {sum(incoming.values())}, уникальных цитируемых: {len(incoming)}")

    top = incoming.most_common(12)
    print(f"\n=== Фазы тренда для ядер кластера JTWPA (топ-{len(top)}) ===\n")
    results = []
    for wid, n_in in top:
        w = works[wid]
        year = w.get("year")
        title = (w.get("title") or "")[:70]
        cite_series = Counter()
        for cid, rlist in refs.items():
            if wid in rlist and cid in works and works[cid].get("year"):
                cite_series[works[cid]["year"]] += 1
        ph = phases_for(dict(cite_series))
        results.append({
            "work_id": wid, "title": title, "year_pub": year,
            "incoming": n_in, "cls": w.get("class"), "phases": ph,
        })
        dev = f"{ph['development'][0]}-{ph['development'][-1]}" if ph["development"] else "—"
        print(f"Ядро [{year}] ({w.get('class')}): {title}")
        print(f"  входящих: {n_in} | первая ссылка {ph['first_cite']} | "
              f"развитие {dev} | состоялся ~{ph['established']}")
        print()

    OUT_JSON.write_text(json.dumps({"jtwpa": results}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Сохранено: {OUT_JSON}")

    # График: динамика ссылок на топ-ядра (до 6)
    fig, ax = plt.subplots(figsize=(12.5, 6.5))
    for r in results[:6]:
        series = r["phases"]["series"]
        if not series:
            continue
        yrs = sorted(series)
        ax.plot(yrs, [series[y] for y in yrs], marker="o", linewidth=2,
                label=f"{r['year_pub']}: {r['title'][:38]}")
    ax.set_title("JTWPA: ссылки на ядра кластера по годам (S3)", fontsize=12, fontweight="bold")
    ax.set_xlabel("год публикации цитирующей работы")
    ax.set_ylabel("число ссылок на ядро")
    ax.legend(fontsize=7.5); ax.grid(alpha=0.3)
    fig.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
    print(f"График: {OUT_PNG}")


if __name__ == "__main__":
    main()
