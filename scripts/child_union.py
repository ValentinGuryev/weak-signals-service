#!/usr/bin/env python3
"""child_union.py — V2 (addendum №4 к протоколу 27.09): детский канал доставки
кандидатов для win100-окна.

Алгоритм (зафиксирован ДО в RANK_PROTOCOL_20260927.md, addendum №4):
  1) канал = реп-термины child-кластеров (все 9 доменов): rep ∈ top-40000 multi
     терминов candidates (воспроизведение отбора segment_topics), вектор из
     embed_cache.npy (без пересчёта);
  2) косинус запрос (query ∪ fanout-subqueries, макс по векторам) → порядок канала;
  3) frac(parent) = первая позиция его ребёнка / размер канала;
  4) rank_new = min(orig_rank, ceil(frac × (len(directions)+1))); orig=∞ если темы
     нет в directions (канал доставляет её из таксономии);
  5) выход: КОПИЯ run.json с directions = темы rank_new ≤ 100, отсортированные
     по rank_new (позиция в файле = win100-ранг для rank_directions_ngi).

Запуск: .venv/bin/python scripts/child_union.py --run <run.json> --out <out.json>
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
SEG_DIRS = sorted(Path("/mnt/e/openalex_derived").glob("termtech_*"))
TOP_N = 40_000        # как в segment_topics (--top 40000, multi, df desc)


def log(m: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def load_channel() -> tuple[np.ndarray, np.ndarray, list[str]]:
    """rep-вектора всех child-кластеров + parent_tid + имена репов.
    Источник связки rep→domain: webapp/data/children/children.parquet (store
    build_children_store), вектора: embed_cache каждого домена."""
    store_p = ROOT / "webapp/data/children/children.parquet"
    store = pd.read_parquet(store_p, columns=["parent_tid", "rep_term", "domain"])
    vecs, parents, names = [], [], []
    for domain, grp in store.groupby("domain"):
        d = Path("/mnt/e/openalex_derived") / f"termtech_{domain}"
        cand_p = d / "candidates_clean.parquet"
        cache_p = d / "segments" / "embed_cache.npy"
        if not (cand_p.exists() and cache_p.exists()):
            log(f"{domain}: НЕТ candidates/cache — пропуск")
            continue
        df = pd.read_parquet(cand_p, columns=["term", "n_tok", "df"])
        df = df[(df["n_tok"] >= 2)].sort_values("df", ascending=False) \
             .head(TOP_N).reset_index(drop=True)
        X = np.load(cache_p)
        assert len(X) == len(df), f"{domain}: X {len(X)} != terms {len(df)}"
        idx = {t: i for i, t in enumerate(df["term"].astype(str))}
        got = 0
        for rep, par in zip(grp["rep_term"].astype(str), grp["parent_tid"].astype(int)):
            i = idx.get(rep)
            if i is None:
                continue
            vecs.append(X[i]); parents.append(int(par)); names.append(rep); got += 1
        log(f"{domain}: {got}/{len(grp)} rep-векторов")
        del df, X
    return np.vstack(vecs), np.asarray(parents), names


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    run = json.loads(Path(a.run).read_text())
    dirs = run["directions"]
    n_dirs = len(dirs)
    orig = {int(c["topic_id"]): i + 1 for i, c in enumerate(dirs)}

    t0 = time.time()
    X, par_of, rep_names = load_channel()
    X = X / np.linalg.norm(X, axis=1, keepdims=True).clip(min=1e-9)
    log(f"канал: {len(X)} реп-терминов за {time.time()-t0:.0f}s")

    # запросы: query + fanout-subqueries (как ретривал), макс по векторам
    from vps_embed import E5Onnx, embed as e5_embed
    qs = [run.get("query", "")] + [s.get("text", "") for s in
                                   (run.get("fanout") or {}).get("subqueries") or []]
    model = E5Onnx()
    # та же обёртка, что в segment_topics (консистентность с embed_cache канала)
    Q = np.asarray(e5_embed(model, [q for q in qs if q]), dtype=np.float32)
    Q = Q / np.linalg.norm(Q, axis=1, keepdims=True).clip(min=1e-9)
    sim = (X @ Q.T).max(axis=1)                 # (N,)
    order = np.argsort(-sim)
    total = len(order)
    log(f"запросов {len(Q)}; top-5 канала: {[rep_names[i] for i in order[:5]]}")

    # frac(parent): первая позиция ребёнка в канале
    frac: dict[int, float] = {}
    for pos in range(total):
        p = int(par_of[order[pos]])
        if p not in frac:
            frac[p] = pos / total

    # rank_new по всем темам таксономии: для кандидатов min с orig, для
    # не-кандидатов — только канал (orig = ∞)
    scale = n_dirs + 1
    new_dirs = []
    for tid, fr in frac.items():
        r_new = min(orig.get(tid, 10**9), math.ceil(fr * scale))
        if r_new <= 100:
            new_dirs.append((r_new, tid))
    # темы с orig ≤ 100 сохраняем в любом случае (окно не сужаем)
    for tid, r in orig.items():
        if r <= 100:
            new_dirs.append((r, tid))
    # ранг = min по дублям
    best: dict[int, int] = {}
    for r, tid in new_dirs:
        best[tid] = min(best.get(tid, 10**9), r)
    merged = sorted(best.items(), key=lambda kv: (kv[1], kv[0]))
    log(f"directions: {n_dirs} → merged win100-окно {len(merged)} "
        f"(доставлено каналом: {sum(1 for t,_ in merged if t not in orig)})")

    out = dict(run)
    orig_map = {int(c["topic_id"]): c for c in dirs}
    # display_name обязателен для rank_directions (для новых тем — из таксономии)
    import pyarrow.parquet as pq
    tp = pq.read_table(ROOT / "webapp/data/taxonomy/topics.parquet",
                       columns=["id", "display_name"])
    tax = {int(str(i).rstrip("/").split("T")[-1]): str(n)
           for i, n in zip(tp["id"].to_pylist(), tp["display_name"].to_pylist())}
    out["directions"] = [
        dict(orig_map[tid]) if tid in orig_map else
        {"topic_id": tid, "display_name": tax.get(tid, f"T{tid}")}
        for tid, _ in merged]
    out["child_union"] = {"channel": len(X), "frac_parents": len(frac),
                          "n_dirs_new": len(merged)}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False))
    log(f"→ {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
