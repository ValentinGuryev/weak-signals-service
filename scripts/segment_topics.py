#!/usr/bin/env python3
"""segment_topics.py — тонкая сегментация: child-темы из termtech-кандидатов.

Идея (путь 1, решение автора 26-27.09): NJ-добрые n-граммы → эмбеддинг e5 →
кластеризация по косинусу → child-темы с parent'ом из таксономии 4516.
Результат — материал для обхода потолка гранулярности (проблема П1) и честного
фильтра мусора (узкие темы вместо generic-родителей).

Этапы:
  1) кандидаты (df>=20, n_tok>=2) → top-N по df (память/CPU-бюджет);
  2) эмбеддинг e5-small ONNX (переиспользование scripts/vps_embed.py);
  3) косинус ≥ --cos, топ-20 соседей/строку → scipy CSR → connected_components;
  4) parent = argmax косинуса(rep-термин, topic_vectors_e5m[4516]);
  5) выход: child_topics.parquet + segment_report.md.

Ресурсы: ~0.5-1.5 ГБ RAM, CPU-bound ( embeddings ~50-150 терм/с ).
Есть guard: ждёт MemAvailable >= --min-avail-mb перед тяжёлыми шагами.

Запуск:
  .venv/bin/python scripts/segment_topics.py \
    --cand /mnt/e/openalex_derived/termtech_biomed/candidates_clean.parquet \
    --out  /mnt/e/openalex_derived/termtech_biomed/segments \
    --name biomed [--top 40000] [--cos 0.75]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

TAX = ROOT / "data/openalex_derived/taxonomy"
TOPIC_VEC = TAX / "topic_vectors_e5m.npy"
TOPIC_IDS = TAX / "topic_ids.txt"


def log(m: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def wait_mem(min_mb: int, why: str) -> None:
    import time as _t
    while True:
        avail = int(open("/proc/meminfo").readline().split()[1]) if False else \
            int([l for l in open("/proc/meminfo") if l.startswith("MemAvailable")][0].split()[1]) // 1024
        if avail >= min_mb:
            return
        log(f"  ждём память: avail={avail}MB < {min_mb}MB ({why})")
        _t.sleep(60)


def embed_terms(texts: list[str], batch: int = 4096) -> np.ndarray:
    import vps_embed
    m = vps_embed.get_model()
    parts = []
    for i in range(0, len(texts), batch):
        wait_mem(1500, f"embed batch {i}")
        parts.append(np.asarray(vps_embed.embed(m, texts[i:i + batch]), dtype=np.float32))
        log(f"  embed {min(i + batch, len(texts))}/{len(texts)}")
    return np.vstack(parts)


def cluster(X: np.ndarray, cos_thr: float, topk: int = 50,
            df_ord: np.ndarray | None = None) -> np.ndarray:
    """Greedy leader-кластеризация (фикс 27.09 01:17: connected components
    дал 1 гигантский кластер — перколяция по мостам между кластерами).

    Лидер = термин с максимальным df среди свободных; члены = ТОЛЬКО прямые
    соседи лидера с косинусом >= thr (среди свободных) — транзитивного слипания
    нет, диаметр кластера ограничен 2×thr.
    """
    from scipy import sparse

    X = X / np.linalg.norm(X, axis=1, keepdims=True).clip(min=1e-9)
    n = X.shape[0]
    block = 2048
    rows, cols = [], []
    wait_mem(1500, "similarity matmul")
    for s in range(0, n, block):
        e = min(s + block, n)
        S = X[s:e] @ X.T
        for r in range(e - s):
            idx = np.argpartition(-S[r], topk)[:topk]
            idx = idx[S[r][idx] >= cos_thr]
            rows.append(np.full(len(idx), s + r))
            cols.append(idx)
        del S
    if not rows:
        return np.arange(n)
    G = sparse.coo_matrix(
        (np.ones(sum(len(r) for r in rows)), (np.concatenate(rows), np.concatenate(cols))),
        shape=(n, n)).tocsr()

    order = df_ord if df_ord is not None else np.arange(n)
    labels = np.full(n, -1, dtype=np.int32)
    ncid = 0
    for i in order:
        if labels[i] >= 0:
            continue
        labels[i] = ncid
        for j in G[i].indices:
            if labels[j] < 0:
                labels[j] = ncid
        ncid += 1
    return labels


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand", required=True, help="candidates_clean.parquet (или candidates.parquet)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", required=True, help="имя домена для отчёта")
    ap.add_argument("--top", type=int, default=40000, help="сколько терминов по df берём")
    ap.add_argument("--cos", type=float, default=0.75)
    ap.add_argument("--min-cluster", type=int, default=2)
    ap.add_argument("--min-avail-mb", type=int, default=1500)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # 1) кандидаты
    df = pd.read_parquet(args.cand, columns=["term", "n_tok", "df", "growth", "first_year"])
    n0 = len(df)
    df = df[(df["n_tok"] >= 2)].sort_values("df", ascending=False).head(args.top).reset_index(drop=True)
    log(f"кандидатов: всего {n0} → multi(df desc, top) {len(df)} (cos>={args.cos})")
    if len(df) < 50:
        log("слишком мало кандидатов — выходим")
        return 1

    # 2) эмбеддинг (кэш: повторные запуски без пересчёта)
    cache = out / "embed_cache.npy"
    if cache.exists() and cache.stat().st_size > 1000:
        X = np.load(cache)
        log(f"embed: кэш {X.shape}")
    else:
        t0 = time.time()
        X = embed_terms(df["term"].tolist())
        np.save(cache, X)
        log(f"embed: {X.shape} за {time.time() - t0:.0f}s")

    # 3) кластеризация (greedy leader, df-приоритет)
    t0 = time.time()
    labels = cluster(X, args.cos, df_ord=np.argsort(-df["df"].to_numpy()))
    df["cluster"] = labels
    n_multi = int((df.groupby("cluster")["term"].size() >= args.min_cluster).sum())
    log(f"кластеров: {len(np.unique(labels))} (из них ≥{args.min_cluster} термов: {n_multi}) "
        f"за {time.time() - t0:.0f}s")

    # 4) rep + parent
    vecs = np.load(TOPIC_VEC)                       # (4516, 384) — l2 не нормирован
    ids = [l.strip() for l in open(TOPIC_IDS)]
    vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True).clip(min=1e-9)
    rows = []
    for cid, grp in df.groupby("cluster"):
        grp = grp.sort_values("df", ascending=False)
        rep = grp.iloc[0]
        rx = X[rep.name] / max(np.linalg.norm(X[rep.name]), 1e-9)
        p = int(np.argmax(vecs @ rx))
        pc = float((vecs @ rx)[p])
        rows.append({
            "child_id": f"{args.name}_c{int(cid):05d}",
            "parent_id": ids[p],
            "rep_term": rep["term"],
            "n_terms": int(len(grp)),
            "df_sum": int(grp["df"].sum()),
            "parent_cos": round(pc, 3),
            "growth_rep": float(rep["growth"]),
            "terms": json.dumps(grp["term"].head(12).tolist(), ensure_ascii=False),
        })
    seg = pd.DataFrame(rows).sort_values("df_sum", ascending=False).reset_index(drop=True)
    seg.to_parquet(out / "child_topics.parquet", index=False)

    # 5) отчёт
    multi = seg[seg["n_terms"] >= args.min_cluster]
    lines = [f"# Сегментация {args.name}: child-темы", "",
             f"кандидатов {len(df)}, кластеров {len(seg)} (мульти {len(multi)}), "
             f"косинус≥{args.cos}, parent → 4516 (e5)", "",
             "| # | child | parent | rep | термов | dfΣ | parent_cos |", "|---|---|---|---|---|---|---|"]
    for i, r in multi.head(40).iterrows():
        lines.append(f"| {i+1} | {r.child_id} | {r.parent_id} | {r.rep_term[:44]} | "
                     f"{r.n_terms} | {r.df_sum} | {r.parent_cos} |")
    (out / "segment_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"→ {out}/child_topics.parquet ({len(seg)} child) + segment_report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
