#!/usr/bin/env python3
"""hybrid_window.py — addendum №5 (27.09, вердикт «а»): гибридное окно
win100 ∪ top-30 по child_rel.

Входы: --run (оригинальный run.json), --probe (json от rank_directions
--relevance childall с child_rel в rows), --out (гибридный run.json).
Фикс: extras = 30 тем с max child_rel среди retr_rank > 100 (tie → меньший
orig-ранг); позиции: win100 = 1..100, extras = 101..130 (child_rel desc).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--probe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--top", type=int, default=30)
    a = ap.parse_args()

    run = json.loads(Path(a.run).read_text())
    dirs = run["directions"]
    orig = {int(c["topic_id"]): i + 1 for i, c in enumerate(dirs)}
    rec = {int(c["topic_id"]): c for c in dirs}

    probe = json.loads(Path(a.probe).read_text())
    # ключ 'all' (все строки окна, с child_rel), НЕ 'top' (дефект-фикс №2, 27.09)
    rows = probe.get("all") or probe.get("rows")
    cr = {}
    for r in rows:
        tid = int(r["topic_id"])
        if "child_rel" in r:
            cr[tid] = float(r["child_rel"])

    # extras: retr_rank > 100, есть child_rel, top-N по child_rel desc
    cand = [( -cr[t], orig[t], t) for t in cr if orig.get(t, 10**9) > 100]
    cand.sort()
    extras = [t for _, _, t in cand[:a.top]]

    win100 = [t for t in orig if orig[t] <= 100]
    win100.sort(key=lambda t: orig[t])
    merged = win100 + extras
    assert len(merged) == len(set(merged))

    out = dict(run)
    out["directions"] = [
        dict(rec[t]) if t in rec else {"topic_id": t} for t in merged
    ]
    out["hybrid_window"] = {"win100": len(win100), "extras": len(extras),
                            "extra_tids": extras}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False))
    top10 = [(t, round(cr.get(t, 0), 4)) for t in extras[:10]]
    print(f"окно: {len(win100)} win100 + {len(extras)} extras → {len(merged)}; "
          f"extras top: {top10}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
