#!/usr/bin/env python3
"""D1 (28.09, ДО addendum №15): из чего складывается топ-15 и чем цели проигрывают.

По industrial/infra/fintech: топ-20 kept (rel_norm, screen, child_rel, e5-ранг)
плюс 6 лучших целей с теми же метриками. child_rel = макс IDF-покрытие qt_exp
профилем ребёнка (механика compute_child_rel раннера, но на лексике демо №13).

Запуск: .venv/bin/python scripts/d1_top_vs_targets.py
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "webapp"))

from eval_stage9 import load_oracles  # noqa: E402
import app as webapp  # noqa: E402
from rank_directions_ngi import GARBAGE_RE  # noqa: E402

webapp.TOP_TOPICS = 10 ** 6
AREAS = ["industrial", "infra", "fintech"]


def child_rel_all(rows, qt):
    """child_rel для всех rows (IDF — тот же, что у rel; механика раннера 352-365).
    _prof в kept уже pop'нут — пересобираем профиль на лету."""
    for r in rows:
        r["_prof"] = webapp.profile(r["tid"], r["name"])
    n = max(len(rows), 1)
    df = {t: sum(1 for r in rows if t in r["_prof"]) for t in qt}
    idf = {t: math.log((n + 1) / (df[t] + 1)) + 1.0 for t in qt}
    total = sum(idf.values()) or 1.0
    for r in rows:
        best = 0.0
        for prof in webapp.CHILDREN.get(r["tid"], []):
            s = sum(idf[t] for t in qt if t in prof["profile"])
            best = max(best, s / total)
        r["crel"] = best


def main() -> int:
    oracles = load_oracles()
    for slug in AREAS:
        orc = oracles[slug]
        q = json.loads((ROOT / "results" / "qa_areas9" / f"{slug}.json").read_text())["query"]
        cand, model, run = webapp.retrieve(q)
        qt = webapp.qtokens(q)
        qt_exp = qt + [t for t in webapp.qtokens(" ".join(
            str(webapp.TOPICS.iloc[i]["display_name"]) for i in cand[:30]
            if not GARBAGE_RE.search(str(webapp.TOPICS.iloc[i]["display_name"])))) if t not in qt]
        kept = webapp.screen_rows(cand, qt_exp)
        child_rel_all(kept, qt_exp)
        mx = max((r["rel"] for r in kept), default=1.0) or 1.0

        # e5-ранг (для сравнения семантики)
        import numpy as np
        qv = webapp.e5_embed([q])[0]
        sim = webapp.VECTORS @ qv
        e5rank = {int(i): r + 1 for r, i in enumerate(np.argsort(-sim)[: webapp.WIN_K])}

        allowed = set()
        for t in orc["targets"]:
            allowed |= {int(x) for x in t["allowed"]}
        tid2pos = {r["tid"]: i + 1 for i, r in enumerate(kept)}

        print(f"\n## {slug} («{q}») — qt_exp={qt_exp[:14]}{'…' if len(qt_exp) > 14 else ''}")
        print("  ТОП-20 (непокрытые * = мусор вне regex?):")
        for r in kept[:20]:
            flag = "+" if r["tid"] in allowed else " "
            print(f"   {flag} p={tid2pos[r['tid']]:<3} rel={r['rel']/mx:.2f} "
                  f"scr={r['screen']:.3f} crel={r.get('crel', 0):.2f} "
                  f"e5={e5rank.get(webapp.TID2POS.get(r['tid'], -1), '-'):>5} {r['name'][:58]}")
        best = sorted((r for r in kept if r["tid"] in allowed),
                      key=lambda r: tid2pos[r["tid"]])[:8]
        print("  ЛУЧШИЕ ЦЕЛИ:")
        for r in best:
            print(f"   + p={tid2pos[r['tid']]:<3} rel={r['rel']/mx:.2f} "
                  f"scr={r['screen']:.3f} crel={r.get('crel', 0):.2f} "
                  f"e5={e5rank.get(webapp.TID2POS.get(r['tid'], -1), '-'):>5} {r['name'][:58]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
