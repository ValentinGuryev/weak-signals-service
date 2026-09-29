#!/usr/bin/env python3
"""Фазы тренда для ядер кластера IBAD: зарождение / развитие / состоялся.

Методика (по решению команды):
- Ядро = работы с наибольшим числом ВХОДЯЩИХ ссылок внутри корпуса (сетевой анализ).
- Для каждого ядра строим серию f(y) = число ссылок на ядро по годам публикации
  цитирующих работ (из ibad_references.json).
- Развитие = УСКОРЕННЫЙ рост: вторая производная Δ²(y) = Δ(y) - Δ(y-1) > 0,
  где Δ(y) = f(y) - f(y-1) (первая производная / рост).
- Фазы:
  * Зарождение: год первой ссылки на ядро (и год публикации ядра).
  * Развитие: годы, где Δ > 0 И Δ² > 0 (рост растёт).
  * Состоялся: первый год после развития, где ускорение закончилось
    (Δ² ≤ 0 после пика ускорения) — тема устоялась, на ядро ссылаются как на факт.

Дополнительно: counts_by_year (2012-2026) — пик цитирования для кросс-проверки.

Выход: results/case_signals/trend_phases.json + печать + график plot7.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REFS = PROJECT_ROOT / "data/raw/openalex/ibad_references.json"
CORPUS = PROJECT_ROOT / "data/raw/openalex/ibad_abstracts_corpus.json"
COUNTS = PROJECT_ROOT / "data/raw/openalex/ibad_counts_by_year.json"
OUT_JSON = PROJECT_ROOT / "results" / "case_signals" / "trend_phases.json"
OUT_PNG = PROJECT_ROOT / "case_studies" / "001_ibad_mgo" / "plots" / "plot7_trend_phases.png"


def smooth(series: dict[int, int], window: int = 3) -> dict[int, float]:
    """Скользящее среднее по годам."""
    years = sorted(series)
    out = {}
    for i, y in enumerate(years):
        lo = max(0, i - window // 2)
        hi = min(len(years), i + window // 2 + 1)
        vals = [series[years[j]] for j in range(lo, hi)]
        out[y] = sum(vals) / len(vals)
    return out


def phases_for(series: dict[int, int]) -> dict:
    """Фазы по серии ссылок на ядро по годам.

    series: {year: число ссылок на ядро работами, опубликованными в этот год}

    Развитие = ускоренный рост (Δ² > 0) НА ГЛАВНОЙ ФАЗЕ РОСТА:
    берём участок до глобального пика серии и ищем там годы с Δ>0 И Δ²>0.
    Состоялся = год после пика, где рост остановился.
    """
    if not series:
        return {"birth": None, "development": [], "established": None, "series": {}}
    years = sorted(series)
    first_cite = min(years)  # год первой ссылки на ядро
    # сглаженная серия
    s = smooth(series)
    syears = sorted(s)
    # глобальный пик сглаженной серии
    peak_year = max(syears, key=lambda y: s[y])
    peak_idx = syears.index(peak_year)
    # фаза роста: от первой ссылки до пика
    growth = syears[: peak_idx + 1]
    # первая и вторая производные на фазе роста
    d1 = {}
    d2 = {}
    for i in range(1, len(syears)):
        y, yp = syears[i], syears[i - 1]
        d1[y] = s[y] - s[yp]
    for i in range(1, len(syears)):
        y, yp = syears[i], syears[i - 1]
        if yp in d1 and y in d1:
            d2[y] = d1[y] - d1[yp]
    # Развитие: Δ > 0 И Δ² > 0, только до пика
    dev_years = [y for y in growth if y in d1 and y in d2
                 and d1[y] > 0 and d2[y] > 0]
    # Состоялся: год пика (тема устоялась, дальше ссылки как на факт)
    established = peak_year
    return {
        "first_cite": first_cite,
        "peak_year": peak_year,
        "development": dev_years,
        "established": established,
        "series": series,
    }


def main() -> None:
    refs = json.loads(REFS.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    works = {w["id"]: w for w in corpus["works"]}
    counts = json.loads(COUNTS.read_text(encoding="utf-8"))

    # Входящие ссылки (ядро кластера)
    incoming = Counter()
    for wid, rlist in refs.items():
        for r in rlist:
            if r in works:
                incoming[r] += 1

    # Топ-10 ядер
    top = incoming.most_common(10)
    print(f"=== Фазы тренда для ядер кластера IBAD (топ-{len(top)}) ===\n")
    results = []
    for wid, n_in in top:
        w = works[wid]
        year = w.get("year")
        title = w.get("title", "")[:60]
        # серия: годы публикации работ, ссылающихся на ядро
        cite_series = Counter()
        for cid, rlist in refs.items():
            if wid in rlist and cid in works:
                cite_series[works[cid]["year"]] += 1
        ph = phases_for(dict(cite_series))
        # counts_by_year пик (для кросс-проверки, 2012+)
        cy = counts.get(wid, {})
        peak_cite = max(cy, key=lambda k: cy[k]) if cy else None
        results.append({
            "work_id": wid, "title": title, "year_pub": year,
            "incoming": n_in, "phases": ph,
            "counts_peak": peak_cite,
        })
        dev = f"{ph['development'][0]}-{ph['development'][-1]}" if ph["development"] else "—"
        print(f"Ядро: [{year}] {title}")
        print(f"  входящих ссылок: {n_in}")
        print(f"  Зарождение: публикация {year}, первая ссылка {ph['first_cite']}")
        print(f"  Развитие (ускоренный рост Δ²>0): {dev} ({len(ph['development'])} лет)")
        print(f"  Состоялся: ~{ph['established']}")
        print(f"  (кросс-проверка counts_by_year пик: {peak_cite})")
        print()

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Сохранено: {OUT_JSON}")

    # ===== АГРЕГАЦИЯ ПО ВСЕМ ЯДРАМ (плотная кривая) =====
    # Все ссылки на топ-ядра вместе → гладкая серия по годам
    top_ids = {w for w, _ in top}
    agg_series = Counter()
    for cid, rlist in refs.items():
        if cid not in works:
            continue
        hits = top_ids & set(rlist)
        if hits:
            agg_series[works[cid]["year"]] += len(hits)
    agg_ph = phases_for(dict(agg_series))
    print("\n=== АГРЕГИРОВАННЫЙ КЛАСТЕР (все ссылки на топ-10 ядер) ===")
    print(f"Всего ссылок на ядра: {sum(agg_series.values())}")
    print(f"Зарождение: первая ссылка на ядро {agg_ph['first_cite']}")
    dev = agg_ph["development"]
    print(f"Развитие (ускоренный рост Δ²>0): {dev[0]}-{dev[-1]}" if dev else "Развитие: —")
    print(f"Пик ссылок на ядра (состоялся): ~{agg_ph['established']}")
    print("\nСерия ссылок на ядра по годам:")
    for y in sorted(agg_series):
        print(f"  {y}: {agg_series[y]}")

    # counts_by_year для кросс-проверки (окно 2012-2026)
    cy_total = Counter()
    for wid, cy in counts.items():
        for y, c in cy.items():
            cy_total[int(y)] += c
    cy_peak = max(cy_total, key=lambda y: cy_total[y]) if cy_total else None
    cy_years = sorted(cy_total)
    print(f"\n[кросс-проверка] counts_by_year (окно {cy_years[0]}-{cy_years[-1]}, OpenAlex):")
    print(f"  пик цитирования: {cy_peak} ({cy_total[cy_peak]} цит/год), диапазон {min(cy_total.values())}-{max(cy_total.values())}")
    print(f"  ОГОВОРКА: окно начинается с {cy_years[0]} — ускоренный рост 1999-2006 виден"
          f" только в references, не в counts_by_year.")

    # Сохраним агрегацию
    agg_entry = {"aggregated": {"series": dict(agg_series), "phases": agg_ph}}
    results.append(agg_entry)
    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")

    # График: серия ссылок на каждое ядро (нормированная) + фазы
    # (только записи с 'phases' — не агрегированная)
    core_results = [r for r in results if "phases" in r]
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(results)))
    for i, res in enumerate(core_results):
        s = res["phases"]["series"]
        years = sorted(s)
        vals = [s[y] for y in years]
        if not vals:
            continue
        # нормируем к макс
        mx = max(vals)
        norm = [v / mx for v in vals]
        label = f"[{res['year_pub']}] {res['title'][:30]}"
        ax.plot(years, norm, "o-", lw=1.8, ms=4, color=colors[i], label=label, alpha=0.85)
        # отметим фазы
        dev = res["phases"]["development"]
        est = res["phases"]["established"]
        if dev:
            ax.axvspan(dev[0], dev[-1], color=colors[i], alpha=0.08)
        if est:
            ax.axvline(est, color=colors[i], lw=1, ls=":", alpha=0.6)

    ax.set_xlabel("Год публикации цитирующих работ", fontsize=12)
    ax.set_ylabel("Нормированные ссылки на ядро", fontsize=12)
    ax.set_title("Фазы тренда IBAD-MgO: зарождение → развитие (Δ²>0) → состоялся\n"
                 "(затенение = развитие, пунктир = состоялся)",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=7, loc="upper right", ncol=2)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"График: {OUT_PNG}")


if __name__ == "__main__":
    main()
