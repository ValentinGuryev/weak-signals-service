#!/usr/bin/env python3
"""Пересчёт impact — ВАРИАНТ B (решение, сессия «2-3 часа»).

Правило подбора k (объявлено ДО прогона):
  impact = 1 − exp(−x/k),  x = max(IMPACT[linked]) из кэша тем.
  Якорь: impact(p50(сырого)) = 0.70  →  k = p50 / (−ln(0.3)) = p50 / 1.20397.
  Ожидание (расчёт на развёрнутых 160k): p5≈0.21, p50=0.70, p75≈0.84;
  медиана score_ngi 0.61 → ≈0.45; влияние impact на балл ×3.3 (вариант B).

Отличие от recalibrate_impact.py (В3, ночь: якорь p5=0.5): там k=p5/ln2 —
насыщение p50=0.95+ осталось, автор счёл влияние impact слабым.

Запуск:
  .venv/bin/python scripts/recalibrate_impact_v2.py --in webapp/data/cards/tech_cards.parquet
Выход: тот же файл (in-place) + results/runtime/impact_recalib_v2_report.md.
"""
import argparse
import json
import math
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
IMPACT_PARQUET = ROOT / "webapp/data/ngi/topic_ngi_cache_impact.parquet"
ANCHOR_Q, ANCHOR_V = 0.50, 0.70          # объявлено ДО прогона (вариант B)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp",
                    default=str(ROOT / "webapp/data/cards/tech_cards.parquet"))
    args = ap.parse_args()
    t0 = time.time()

    imp = pd.read_parquet(IMPACT_PARQUET)
    IMPACT = dict(zip(imp.tid.astype(int), imp.impact.astype(float)))
    del imp

    df = pd.read_parquet(args.inp)
    raw = []
    for s in df["linked_json"]:
        try:
            tids = [int(t) for t in json.loads(s)] if isinstance(s, str) and s else []
        except json.JSONDecodeError:
            tids = []
        vals = [IMPACT[t] for t in tids if t in IMPACT]
        raw.append(max(vals) if vals else 0.0)
    raw = pd.Series(raw, index=df.index, dtype=float)
    pos = raw[raw > 0]
    if len(pos) == 0:
        raise SystemExit("нет ни одного сырого impact > 0 — нечего нормировать")

    p50 = float(pos.quantile(ANCHOR_Q))
    k = p50 / (-math.log(1.0 - ANCHOR_V))
    old = df["impact"].astype(float).copy()
    new = (1.0 - np_exp(raw / k))
    df["impact"] = new.round(6)
    df["score_ngi"] = (
        df["novelty"].astype(float) * df["growth_n"].astype(float) * df["impact"]
    ).round(4)
    df.to_parquet(args.inp, index=False)

    def pct(s):
        return {q: round(float(s.quantile(q / 100)), 3)
                for q in (0, 5, 25, 50, 75, 95, 99)}

    lines = [
        f"# impact recalibration v2 (вариант B) — {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"- файл: `{args.inp}`; строк: {len(df):,}",
        f"- якорь (объявлен ДО прогона): impact(p{ANCHOR_Q*100:.0f} сырого) = {ANCHOR_V}",
        f"- **k = p50/(-ln0.3) = {p50:.0f}/1.20397 = {k:.1f}**",
        f"- сырой max(IMPACT): {pct(pos)}",
        f"- impact БЫЛО: {pct(old)}",
        f"- impact СТАЛО: {pct(new)}",
        f"- score_ngi СТАЛО: {pct(df['score_ngi'])}",
        f"- время: {time.time()-t0:.0f} с",
    ]
    rep = ROOT / "results/runtime/impact_recalib_v2_report.md"
    rep.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def np_exp(x):
    import numpy as np
    return np.exp(-x.astype(float))


if __name__ == "__main__":
    main()
