#!/usr/bin/env python3
"""Фазы тренда для RCE/TLAG (кейс 002, S3).

Адаптация src/trend_phases_fluxpump.py под rce_tlag корпус:
- Ядро = работы с наибольшим числом ВХОДЯЩИХ ссылок внутри корпуса.
- Серия f(y) = число ссылок на ядро работами, опубликованными в год y.
- Развитие = ускоренный рост (Δ² > 0) до пика; Состоялся = год пика.

Данные: data/raw/openalex/rce_tlag_references.json + rce_tlag_corpus.json
Выход: results/case_signals/trend_phases_rce_tlag.json + график.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REFS = PROJECT_ROOT / "data/raw/openalex/rce_tlag_references.json"
CORPUS = PROJECT_ROOT / "data/raw/openalex/rce_tlag_corpus.json"
OUT_JSON = PROJECT_ROOT / "results/case_signals/trend_phases_rce_tlag.json"
OUT_PNG = PROJECT_ROOT / "case_studies/002_rce_dr_sunam/plots/plot_s3_trend_phases.png"


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
        return {"birth": None, "development": [], "established": None, "series": {}}
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
    refs = json.loads(REFS.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    ws = corpus if isinstance(corpus, list) else corpus.get("works", [])
    works = {w["id"]: w for w in ws}

    # Топики
    topics = {}
    for w in ws:
        t = w.get("topic", "?")
        topics.setdefault(t, []).append(w["id"])

    all_results = {}
    for topic, tids in topics.items():
        inc = Counter()
        for wid in tids:
            for r in refs.get(wid, []):
                if r in tids:
                    inc[r] += 1
        top = inc.most_common(8)
        tag = {"RCE/co-evap": "rce", "TLAG": "tlag"}.get(topic, "other")
        if not top or tag == "other":
            continue
        print(f"\n===== {topic} ({tag}) — {len(tids)} работ =====")
        results = []
        for wid, n_in in top:
            w = works[wid]
            year = w.get("year")
            title = w.get("title", "")[:65]
            cite_series = Counter()
            for cid in tids:
                if wid in refs.get(cid, []) and works[cid].get("year"):
                    cite_series[works[cid]["year"]] += 1
            ph = phases_for(dict(cite_series))
            results.append({
                "work_id": wid, "title": title, "year_pub": year,
                "incoming": n_in, "phases": ph,
            })
            dev = f"{ph['development'][0]}-{ph['development'][-1]}" if ph["development"] else "—"
            print(f"  Ядро [{year}]: {title}")
            print(f"    входящих: {n_in} | первая ссылка {ph['first_cite']} | "
                  f"развитие {dev} | состоялся ~{ph['established']}")
        all_results[tag] = results

    OUT_JSON.write_text(json.dumps(all_results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT_JSON}")

    # График
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for ax, (tag, results) in zip(axes, all_results.items()):
        for r in results[:4]:
            series = r["phases"]["series"]
            if not series:
                continue
            yrs = sorted(series)
            ax.plot(yrs, [series[y] for y in yrs], marker="o", linewidth=2,
                    label=f"{r['year_pub']}: {r['title'][:28]}")
        ax.set_title(f"{'RCE co-evap' if tag=='rce' else 'TLAG'} — ссылки на ядра по годам",
                     fontsize=11, fontweight="bold")
        ax.set_xlabel("год публикации цитирующей работы")
        ax.set_ylabel("число ссылок на ядро")
        ax.legend(fontsize=7); ax.grid(alpha=0.3)
    plt.suptitle("S3 кейс 002: фазы тренда RCE vs TLAG (зарождение → развитие → состоялся)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
    print(f"График: {OUT_PNG}")


if __name__ == "__main__":
    main()
