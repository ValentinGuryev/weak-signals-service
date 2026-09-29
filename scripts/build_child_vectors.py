#!/usr/bin/env python3
"""Precompute e5-векторов child-профилей (Addendum №15, ступень 15-1).

children.parquet (20 453) → текст = rep_term + " " + profile → e5 (passage:)
→ webapp/data/children/child_vectors_e5m.npy (N,768) + child_ids.json (порядок строк).

Запуск: .venv/bin/python scripts/build_child_vectors.py
Идемпотентно: при наличии npy и совпадающем N — не пересчитывает.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "webapp" / "data" / "children"
OUT_NPY = DEST / "child_vectors_e5m.npy"
OUT_IDS = DEST / "child_ids.json"


def main() -> int:
    t0 = time.time()
    df = pd.read_parquet(DEST / "children.parquet")
    texts = (df["rep_term"].astype(str) + " " + df["profile"].astype(str)).tolist()
    ids = df["child_id"].astype(str).tolist()
    if OUT_NPY.exists() and OUT_IDS.exists():
        old = json.loads(OUT_IDS.read_text())
        if len(old) == len(ids) and old == ids:
            print(f"[skip] уже есть: {OUT_NPY.name} ({len(ids)} строк)")
            return 0

    # токенизатор+модель e5 — тот же стек, что в webapp/app.py (семантика space)
    from tokenizers import Tokenizer
    import onnxruntime as ort
    ONNX_DIR = Path("/mnt/e/openalex_derived/e5m_onnx")
    tok = Tokenizer.from_file(str(ONNX_DIR / "tokenizer.json"))
    tok.enable_truncation(max_length=512)
    tok.enable_padding()
    so = ort.SessionOptions()
    so.intra_op_num_threads = 4
    sess = ort.InferenceSession(str(ONNX_DIR / "model.onnx"), so,
                                providers=["CPUExecutionProvider"])

    vecs = None
    B = 256
    for i in range(0, len(texts), B):
        batch = ["passage: " + t for t in texts[i:i + B]]
        enc = tok.encode_batch(batch)
        ids_a = np.array([e.ids for e in enc], dtype=np.int64)
        mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
        tti = np.array([e.type_ids for e in enc], dtype=np.int64)
        hs = sess.run(None, {"input_ids": ids_a, "attention_mask": mask,
                             "token_type_ids": tti})[0]
        m = mask.astype(np.float32)[:, :, None]
        pooled = (hs * m).sum(axis=1) / np.clip(m.sum(axis=1), 1, None)
        pooled /= np.clip(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9, None)
        if vecs is None:
            vecs = np.zeros((len(texts), pooled.shape[1]), dtype=np.float32)
        vecs[i:i + B] = pooled
        if i % (B * 20) == 0:
            print(f"  {i}/{len(texts)} ({time.time() - t0:.0f}s)", flush=True)
    np.save(OUT_NPY, vecs)
    OUT_IDS.write_text(json.dumps(ids, ensure_ascii=False))
    print(f"[ok] {OUT_NPY} {vecs.shape} + {OUT_IDS.name} ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
