#!/usr/bin/env python3
"""Дискриминация абстрактов OpenAlex IBAD-корпуса: фундаментальные vs прикладные.

Кейс 001_ibad_mgo, S2. Применяем улучшенный дискриминатор (classify_document с
коррекцией по заголовку) к АБСТРАКТАМ релевантных работ (1997-2026).

Выход: results/case_signals/ibad_abstracts_discrimination.json + печать
  {by_year: {year: {n, n_appl, n_fund, n_mix, appl_share, fund_share}},
   by_period: {...3-летние периоды...},
   works: [{... + verdict}]}
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from semantic_shift_v2 import classify_document

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "ibad_abstracts_corpus.json"
OUT = PROJECT_ROOT / "results" / "case_signals" / "ibad_abstracts_discrimination.json"

PERIODS = {"1997-2000": (1997, 2000), "2001-2004": (2001, 2004),
           "2005-2008": (2005, 2008), "2009-2012": (2009, 2012),
           "2013-2016": (2013, 2016), "2017-2020": (2017, 2020),
           "2021-2024": (2021, 2024), "2025-2026": (2025, 2026)}


def period_of(year: int) -> str | None:
    for p, (a, b) in PERIODS.items():
        if a <= year <= b:
            return p
    return None


def main() -> None:
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    works = data["works"]
    print(f"Корпус: {len(works)} работ, с абстрактами {data['with_abstract']}")

    # Дискриминация по абстрактам
    results = []
    for w in works:
        abstract = w.get("abstract") or ""
        if len(abstract) < 40:
            # нет абстракта — пропускаем (не можем дискриминировать)
            continue
        r = classify_document(abstract)
        results.append({**w, "verdict": r["verdict"],
                        "n_paras": r["n"], "eng_p": r["eng_p"], "eff_p": r["eff_p"]})
    print(f"Дискриминировано по абстрактам: {len(results)}")

    # По годам
    by_year = {}
    for y in sorted(set(w["year"] for w in results)):
        ws = [w for w in results if w["year"] == y]
        n_appl = sum(1 for w in ws if w["verdict"] == "applied")
        n_fund = sum(1 for w in ws if w["verdict"] == "fundamental")
        n_mix = sum(1 for w in ws if w["verdict"] == "mixed")
        by_year[y] = {"n": len(ws), "n_appl": n_appl, "n_fund": n_fund, "n_mix": n_mix,
                      "appl_share": n_appl / len(ws), "fund_share": n_fund / len(ws)}

    # По периодам
    by_period = {}
    for p, (a, b) in PERIODS.items():
        ws = [w for w in results if a <= w["year"] <= b]
        if not ws:
            by_period[p] = {"n": 0}
            continue
        n_appl = sum(1 for w in ws if w["verdict"] == "applied")
        n_fund = sum(1 for w in ws if w["verdict"] == "fundamental")
        n_mix = sum(1 for w in ws if w["verdict"] == "mixed")
        by_period[p] = {"n": len(ws), "n_appl": n_appl, "n_fund": n_fund, "n_mix": n_mix,
                        "appl_share": n_appl / len(ws), "fund_share": n_fund / len(ws),
                        "appl_pct": 100 * n_appl / len(ws), "fund_pct": 100 * n_fund / len(ws)}

    print(f"\n=== Доля прикладных абстрактов по периодам (IBAD-корпус OpenAlex) ===")
    print(f"{'период':<10} {'статей':>5} {'прикл%':>7} {'фунд%':>7} {'смеш%':>6}")
    for p in PERIODS:
        d = by_period[p]
        if not d.get("n"):
            print(f"{p:<10} {'—':>5}")
            continue
        print(f"{p:<10} {d['n']:>5} {d['appl_pct']:>6.1f}% {d['fund_pct']:>6.1f}% "
              f"{100*d['n_mix']/d['n']:>5.1f}%")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "method": "ibad_abstracts_discrimination",
        "note": "Дискриминатор v2 применён к абстрактам OpenAlex (1997-2026), не к полным текстам.",
        "n_total": len(works), "n_with_abstract": len(results),
        "by_year": by_year, "by_period": by_period,
        "works": results,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT}")


if __name__ == "__main__":
    main()
