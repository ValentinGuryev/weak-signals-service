#!/usr/bin/env python3
"""D2 (28.09, диагноз ДО addendum №15): проекция покрытия топ-15 под разными
ПОРЯДКАМИ на тех же метриках (позиционная проекция — как L0 «при K=400»).

Варианты векторов: e5m / e5m-alias(i2) / LaBSE / LaBSE-i2 — плюс порядки:
A = канон №13 (rel), B = чистый вектор-ранг, C = RRF60(вектор, rel) + screen.
NOT_IN_WIN_K цели недостижимы для любого порядка (это канал child-доставки).

Запуск: .venv/bin/python scripts/d2_order_projection.py
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

import numpy as np  # noqa: E402

webapp.TOP_TOPICS = 10 ** 6
C = 60  # RRF-константа — та же, что в замороженном fanout-конфиге
TAX = Path("/home/user/projects/Hackathon/data/openalex_derived/taxonomy")

VECTORS: dict[str, np.ndarray] = {
    "e5m": webapp.VECTORS,
    "e5m_i2": np.load(TAX / "topic_vectors_e5m_i2.npy"),
    "labse": np.load(TAX / "topic_vectors.npy"),
    "labse_i2": np.load(TAX / "topic_vectors_i2.npy"),
}
_labse = None


def embed(q: str, kind: str) -> np.ndarray:
    global _labse
    if kind.startswith("e5"):
        return webapp.e5_embed([q])[0]
    if _labse is None:
        from sentence_transformers import SentenceTransformer
        import torch
        torch.set_num_threads(8)
        _labse = SentenceTransformer("sentence-transformers/LaBSE")
    return _labse.encode([q], normalize_embeddings=True)[0]


def main() -> int:
    oracles = load_oracles()
    hdr = "| область | reachable | A:№13 |" + "".join(
        f" {v}:B | {v}:C |" for v in VECTORS)
    print(hdr)
    print("|---" * (3 + 2 * len(VECTORS)) + "|")
    for slug, orc in oracles.items():
        q = json.loads((ROOT / "results" / "qa_areas9" / f"{slug}.json").read_text())["query"]
        cand, model, run = webapp.retrieve(q)
        qt = webapp.qtokens(q)
        qt_exp = qt + [t for t in webapp.qtokens(" ".join(
            str(webapp.TOPICS.iloc[i]["display_name"]) for i in cand[:30]
            if not GARBAGE_RE.search(str(webapp.TOPICS.iloc[i]["display_name"])))) if t not in qt]
        kept = webapp.screen_rows(cand, qt_exp)

        allowed = set()
        for t in orc["targets"]:
            allowed |= {int(x) for x in t["allowed"]}
        n_targets = len(orc["targets"])
        reachable_tg = sum(1 for t in orc["targets"]
                           if any(r["tid"] in {int(x) for x in t["allowed"]} for r in kept))

        mx = max((r["rel"] for r in kept), default=1.0) or 1.0
        rel_rank = {r["tid"]: i + 1 for i, r in enumerate(
            sorted(kept, key=lambda r: (-r["rel"], r["tid"])))}
        garbage_flag = lambda r: 1 if GARBAGE_RE.search(r["name"]) else 0  # noqa: E731

        def cov15(order):
            s = {r["tid"] for r in order[:15]}
            return sum(1 for t in orc["targets"] if s & {int(x) for x in t["allowed"]})

        A = sorted(kept, key=lambda r: (garbage_flag(r), -r["rel"] / mx, -r["screen"], r["tid"]))
        cells = []
        for kind, V in VECTORS.items():
            qv = embed(q, kind)
            e5r = np.argsort(-(V @ qv))
            pos = {int(i): r + 1 for r, i in enumerate(e5r)}
            B = sorted(kept, key=lambda r: (garbage_flag(r),
                                            pos.get(webapp.TID2POS.get(r["tid"], -1), 10**6),
                                            -r["screen"], r["tid"]))
            rrf = {r["tid"]: 1 / (C + pos.get(webapp.TID2POS.get(r["tid"], -1), 10**6))
                   + 1 / (C + rel_rank[r["tid"]]) for r in kept}
            Cc = sorted(kept, key=lambda r: (garbage_flag(r), -rrf[r["tid"]], -r["screen"], r["tid"]))
            cells += [cov15(B), cov15(Cc)]
        print(f"| {slug} | {reachable_tg}/{n_targets} | {cov15(A)} | "
              + " | ".join(str(x) for x in cells) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
