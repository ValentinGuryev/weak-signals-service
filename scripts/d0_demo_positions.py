#!/usr/bin/env python3
"""D0-диагноз (28.09, ДО addendum №15): где теряются цели ДЕМО-конвейера №13.

Для каждого запроса области: позиция каждой allowed-темы оракула в кандидатах e5
(retr_rank), статус фильтров screen (серии/birth) и итоговая позиция в отсортированном
kept (ключ №13). Ответ на вопрос ветки (б): цели ОТСУТСТВУЮТ в окне WIN_K,
ОТСЕЧЕНЫ фильтрами или ЕСТЬ, но ранжируются ниже топ-15?

Запуск: .venv/bin/python scripts/d0_demo_positions.py
Выход: компактная таблица по 6 областям (цель = лучшая позиция среди allowed).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "webapp"))

from eval_stage9 import load_oracles  # noqa: E402

import app as webapp  # noqa: E402  (data читаются при импорте)
from rank_directions_ngi import GARBAGE_RE  # noqa: E402

webapp.TOP_TOPICS = 10 ** 6  # не обрезаем kept — нам ВСЕ позиции


def diagnose(slug: str, orc: dict, q: str) -> None:
    cand, model, run = webapp.retrieve(q)
    assert run is None, "D0 гоняется на каноне №13 (WEBAPP_BATCH выключен)"
    pos_in_cand = {idx: r for r, idx in enumerate(cand, 1)}
    qt = webapp.qtokens(q)
    qt_exp = qt + [t for t in webapp.qtokens(" ".join(
        str(webapp.TOPICS.iloc[i]["display_name"]) for i in cand[:30]
        if not GARBAGE_RE.search(str(webapp.TOPICS.iloc[i]["display_name"])))) if t not in qt]
    kept = webapp.screen_rows(cand, qt_exp)          # полный kept (без обрезки)
    order_pos = {r["tid"]: i + 1 for i, r in enumerate(kept)}

    # диагностика dropped/вне окна — реплика фильтров screen_rows
    def why(tid: int) -> str:
        i = webapp.TID2POS.get(tid)
        if i is None:
            return "NOT_IN_TAXONOMY"
        if i not in pos_in_cand:
            return f"NOT_IN_WIN_K(e5rank>{webapp.WIN_K})"
        ser = webapp.NGI_SERIES.get(tid, {})
        n_late = sum(ser.get(y, 0) for y in (2023, 2024, 2025))
        n_early = sum(ser.get(y, 0) for y in (2021, 2022))
        if n_late == 0 and n_early == 0:
            return "DROP_NO_SERIES"
        if webapp.birth_of(tid) is None:
            return "DROP_NO_BIRTH"
        return "IN_KEPT?"

    buckets = {"<=15": 0, "16-30": 0, "31-100": 0, "101-300": 0, ">300": 0,
               "NOT_IN_WIN_K": 0, "DROP": 0, "NOT_IN_TAXONOMY": 0}
    det = []
    for t in orc["targets"]:
        allowed = [int(x) for x in t["allowed"]]
        best_pos = None
        for tid in allowed:
            if tid in order_pos:
                p = order_pos[tid]
                best_pos = p if best_pos is None else min(best_pos, p)
        if best_pos is not None:
            b = ("<=15" if best_pos <= 15 else "16-30" if best_pos <= 30 else
                 "31-100" if best_pos <= 100 else "101-300" if best_pos <= 300 else ">300")
            det.append((t.get("n"), f"pos={best_pos}"))
        else:
            # ни одна allowed не в kept → почему первая allowed
            r0 = why(allowed[0])
            b = "NOT_IN_WIN_K" if r0.startswith("NOT_IN_WIN_K") else (
                "NOT_IN_TAXONOMY" if r0 == "NOT_IN_TAXONOMY" else "DROP")
            det.append((t.get("n"), r0))
        buckets[b] += 1
    print(f"\n## {slug} («{q}», model={model}) — kept={len(kept)}, win_k={webapp.WIN_K}")
    print("  " + " ".join(f"{k}={v}" for k, v in buckets.items() if v))
    print("  " + ", ".join(f"#{n}:{s}" for n, s in det))


def main() -> int:
    oracles = load_oracles()
    queries = {p.stem.replace(".json", ""): None
               for p in (ROOT / "results" / "qa_areas9").glob("*.json")}
    import json
    area_query = {k: json.loads((ROOT / "results" / "qa_areas9" / f"{k}.json").read_text())["query"]
                  for k in queries}
    for slug, orc in oracles.items():
        q = area_query.get(slug)
        if not q:
            continue
        diagnose(slug, orc, q)
    return 0


if __name__ == "__main__":
    sys.exit(main())
