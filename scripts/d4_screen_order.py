#!/usr/bin/env python3
"""D4 (28.09): проверка ГИПОТЕЗЫ автора — порядок по novelty×growth×impact (screen)
на демо-кандидатах (WIN_K=1200, после фильтров). Покрытие топ-K + топ-15 имена.

Контекст: №10 (batch, полное окно) и бейзлайн win100 (демо) провалили screen-порядок;
на демо-окне 1200 с текущими данными Т12/M13 порядок НЕ замерялся.
Запуск: .venv/bin/python scripts/d4_screen_order.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "webapp"))

from eval_stage9 import load_oracles  # noqa: E402
import app as webapp  # noqa: E402
from rank_directions_ngi import GARBAGE_RE  # noqa: E402

webapp.TOP_TOPICS = 10 ** 6


def cov(order, allowed_sets, k):
    s = {r["tid"] for r in order[:k]}
    return sum(1 for a in allowed_sets if s & a)


def main() -> int:
    oracles = load_oracles()
    print("| область | need | screen@15 | screen@30 | screen@50 | (для сравнения №13@15) |")
    print("|---|---|---|---|---|---|")
    for slug, orc in oracles.items():
        q = json.loads((ROOT / "results" / "qa_areas9" / f"{slug}.json").read_text())["query"]
        cand, model, run = webapp.retrieve(q)
        qt = webapp.qtokens(q)
        qt_exp = qt + [t for t in webapp.qtokens(" ".join(
            str(webapp.TOPICS.iloc[i]["display_name"]) for i in cand[:30]
            if not GARBAGE_RE.search(str(webapp.TOPICS.iloc[i]["display_name"])))) if t not in qt]
        kept = webapp.screen_rows(cand, qt_exp)
        allowed_sets = [{int(x) for x in t["allowed"]} for t in orc["targets"]]
        mx = max((r["rel"] for r in kept), default=1.0) or 1.0
        g = lambda r: 1 if GARBAGE_RE.search(r["name"]) else 0  # noqa: E731
        # чистый NGI-screen (гипотеза автора): с мусорным флагом и без
        S = sorted(kept, key=lambda r: (g(r), -r["screen"], r["tid"]))
        A = sorted(kept, key=lambda r: (g(r), -r["rel"] / mx, -r["screen"], r["tid"]))
        print(f"| {slug} | {len(orc['targets'])} | {cov(S, allowed_sets, 15)} | "
              f"{cov(S, allowed_sets, 30)} | {cov(S, allowed_sets, 50)} | "
              f"{cov(A, allowed_sets, 15)} |")
        if slug in ("industrial", "infra"):
            print(f"  топ-15 {slug} по screen: " + " | ".join(
                r["name"][:34] for r in S[:15]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
