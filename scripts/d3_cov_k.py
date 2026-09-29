#!/usr/bin/env python3
"""D3 (28.09): достижимый потолок критерия — покрытие топ-K (15/30/50) под
каноном №13 (A) и лучшим projected-порядком (LaBSE:RRF60). Для пересмотра
критерия автором (данные, не подгонка)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "webapp"))

from eval_stage9 import load_oracles  # noqa: E402
import app as webapp  # noqa: E402
from rank_directions_ngi import GARBAGE_RE  # noqa: E402
import numpy as np  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

webapp.TOP_TOPICS = 10 ** 6
C = 60
TAX = Path("/home/user/projects/Hackathon/data/openalex_derived/taxonomy")
V = np.load(TAX / "topic_vectors_i2.npy")  # лучший вариант D2
LABSE = SentenceTransformer("sentence-transformers/LaBSE")


def cov(order, allowed_sets, k):
    s = {r["tid"] for r in order[:k]}
    return sum(1 for a in allowed_sets if s & a)


def main() -> int:
    oracles = load_oracles()
    print("| область | need | A@15 | A@30 | A@50 | C-labse@15 | C-labse@30 | C-labse@50 |")
    print("|---|---|---|---|---|---|---|---|")
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
        rel_rank = {r["tid"]: i + 1 for i, r in enumerate(
            sorted(kept, key=lambda r: (-r["rel"], r["tid"])))}
        qv = LABSE.encode([q], normalize_embeddings=True)[0]
        pos = {int(i): r + 1 for r, i in enumerate(np.argsort(-(V @ qv)))}
        g = lambda r: 1 if GARBAGE_RE.search(r["name"]) else 0  # noqa: E731
        A = sorted(kept, key=lambda r: (g(r), -r["rel"] / mx, -r["screen"], r["tid"]))
        Cc = sorted(kept, key=lambda r: (
            g(r),
            -(1 / (C + pos.get(webapp.TID2POS.get(r["tid"], -1), 10**6))
              + 1 / (C + rel_rank[r["tid"]])),
            -r["screen"], r["tid"]))
        print(f"| {slug} | {len(orc['targets'])} | "
              + " | ".join(str(cov(o, allowed_sets, k))
                           for o in (A, Cc) for k in (15, 30, 50))
              + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
