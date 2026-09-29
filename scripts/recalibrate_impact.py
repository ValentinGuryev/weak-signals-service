#!/usr/bin/env python3
"""Этап В3 (ночь 29.09): перенормировка impact — снятие насыщения у единицы.

решение команды: «перенормируй impact … подбери подэкспоненциальную
константу так чтобы impact менялся в более широких диапазонах, скажем от 0.5
до 1, а не был сгруппирован вблизи единицы».

Данные (смоук 29.09 00:1x, 100 648 карточек): канон k=40 даёт impact ≡ 1.0
(в tech_ngi тоже 96.3% = 1.0); сырой max(IMPACT[linked]) имеет p5=1832,
p50=4527, p95=8206 (диапазон ×4.5 между p5 и p95 — одна константа тянет).

Правило подбора (объявлено ДО прогона, детерминировано):
  k = p5(сырого) / ln2  →  impact(p5) = 0.5;  impact = 1 − exp(−x/k).
  Ожидаемый разброс по смоуку: p0≈0.37, p5=0.50, p50≈0.82, p95≈0.95.
  score_ngi пересчитывается = novelty × growth × impact.

Запуск (после сборки карточек, ДО дедупа — дедуп выбирает хранителя по score_ngi):
  .venv/bin/python scripts/recalibrate_impact.py --in data/openalex_derived/tech_cards_v1.parquet
Выход: тот же файл (in-place) + results/runtime/impact_recalib_report.md.
"""
import argparse
import json
import math
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
IMPACT_PARQUET = ROOT / "webapp/data/ngi/topic_ngi_cache_impact.parquet"


def raw_impact(row, IMPACT: dict) -> float:
    if not isinstance(row.linked_json, str) or not row.linked_json:
        return 0.0
    tids = [int(t) for t in json.loads(row.linked_json)]
    vals = [IMPACT[t] for t in tids if t in IMPACT]
    return max(vals) if vals else 0.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp",
                    default=str(ROOT / "data/openalex_derived/tech_cards_v1.parquet"))
    ap.add_argument("--inplace", action="store_true", default=True)
    args = ap.parse_args()
    t0 = time.time()

    imp = pd.read_parquet(IMPACT_PARQUET)
    IMPACT = dict(zip(imp.tid.astype(int), imp.impact.astype(int)))
    del imp

    df = pd.read_parquet(args.inp)
    ok = df["status"] == "ok"
    raw = df.loc[ok].apply(lambda r: raw_impact(r, IMPACT), axis=1)
    pos = raw[raw > 0]
    if len(pos) == 0:
        raise SystemExit("нет ни одного сырого impact > 0 — нечего нормировать")
    p5 = float(pos.quantile(0.05))
    k = p5 / math.log(2.0)

    old = df.loc[ok, "impact"]
    new = pos.map(lambda x: 1.0 - math.exp(-x / k))
    df.loc[new.index, "impact"] = new          # индексы строк OK (map по term был багом)
    df.loc[ok, "score_ngi"] = (
        df.loc[ok, "novelty"] * df.loc[ok, "growth_n"] * df.loc[ok, "impact"]
    ).round(4)

    df.to_parquet(args.inp, index=False)

    def pct(s):
        return {q: round(float(s.quantile(q / 100)), 3)
                for q in (0, 5, 25, 50, 75, 95, 99)}

    lines = [
        f"# impact recalibration — {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"- файл: `{args.inp}`; карточек OK: {int(ok.sum()):,}",
        f"- **k = p5(сырого)/ln2 = {p5:.0f}/{math.log(2):.4f} = {k:.1f}**",
        f"- сырой max(IMPACT) percentile: {pct(pos)}",
        f"- impact БЫЛО (канон k=40): {pct(old)}",
        f"- impact СТАЛО: {pct(df.loc[ok, 'impact'])}",
        f"- score_ngi СТАЛО: {pct(df.loc[ok, 'score_ngi'])}",
        f"- время: {time.time()-t0:.0f} с",
    ]
    rp = ROOT / "results/runtime/impact_recalib_report.md"
    rp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
