#!/usr/bin/env python3
"""C3 (NIGHT_PLAN): лёгкий multilingual-эмбеддер для ретривала на VPS.

Модель: `intfloat/multilingual-e5-small` (ONNX, ~118 МБ, ~200-300 МБ RAM) —
семантика + RU↔EN; вместо LaBSE (2 ГБ), которая на VPS (1.8 ГБ) не влезает.
Библиотека: fastembed (onnxruntime), качает модель при первом вызове (сеть!).

Режимы:
  --build-vectors   : закодировать все 4516 тем (name+description+keywords)
                      → taxonomy/topic_vectors_e5m.npy (один раз, локально)
  --query "текст"   : эмбеддинг запроса + косинус с векторами → топ-K тем
                      (смоук: проверить, что «защита ИИ» находит англ. темы)
  --smoke           : быстрый самотест (3 запроса, ожидаемые домены)

Примечание: вектора e5 НЕ смешиваются с LaBSE (другое пространство) —
на VPS и вектора, и запрос должны быть от ОДНОЙ модели.
Запуск: .venv/bin/python scripts/vps_embed.py --smoke
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TAX = ROOT / "data/openalex_derived/taxonomy"
MODEL = "intfloat/multilingual-e5-small"
# C3 (25.09): fastembed НЕ поддерживает e5-small (проверено: 0.2.1–0.8.1) →
# прямой onnxruntime (onnx/model.onnx 448МБ скачан на E:, не в WSL)
ONNX_DIR = Path("/mnt/e/openalex_derived/e5m_onnx")
VEC_OUT = TAX / "topic_vectors_e5m.npy"


def log(m: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


class E5Onnx:
    """Обёртка совместимая с fastembed.TextEmbedding: .embed(texts) → вектора.
    e5-протокол: префикс query:/passage: → mean-pooling (1_Pooling) → L2.
    """

    def __init__(self, onnx_dir: Path = ONNX_DIR):
        import onnxruntime as ort
        from tokenizers import Tokenizer
        if not (onnx_dir / "model.onnx").exists():
            raise FileNotFoundError(f"нет {onnx_dir}/model.onnx — скачать с HF {MODEL}")
        self.tok = Tokenizer.from_file(str(onnx_dir / "tokenizer.json"))
        self.tok.enable_truncation(max_length=512)
        self.tok.enable_padding()
        so = ort.SessionOptions()
        so.intra_op_num_threads = 2
        self.sess = ort.InferenceSession(
            str(onnx_dir / "model.onnx"), so,
            providers=["CPUExecutionProvider"])

    def embed(self, texts: list[str], batch: int = 32):
        for i in range(0, len(texts), batch):
            enc = self.tok.encode_batch(texts[i:i + batch])
            ids = np.array([e.ids for e in enc], dtype=np.int64)
            mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
            tti = np.array([e.type_ids for e in enc], dtype=np.int64)
            hs = self.sess.run(None, {"input_ids": ids, "attention_mask": mask,
                                      "token_type_ids": tti})[0]  # (B, L, 384)
            m = mask.astype(np.float32)[:, :, None]
            pooled = (hs * m).sum(axis=1) / np.clip(m.sum(axis=1), 1, None)
            pooled /= np.clip(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9, None)
            for row in pooled:
                yield row.astype(np.float32)


def get_model():
    log(f"модель {MODEL} (onnxruntime, файлы {ONNX_DIR})")
    return E5Onnx()


def embed(model, texts: list[str]) -> np.ndarray:
    # e5-префикс: «query: » / «passage: » (рекомендация модели)
    vecs = np.stack([np.asarray(v) for v in model.embed(texts)])
    return vecs


def encode_topics(model) -> int:
    import pyarrow.parquet as pq
    rows = pq.read_table(TAX / "topics.parquet").to_pylist()
    texts = []
    for r in rows:
        kw = r.get("keywords") or ""
        if not isinstance(kw, str):
            kw = " ".join(map(str, kw))
        texts.append(f"passage: {r.get('display_name','')}. "
                     f"{str(r.get('description',''))[:400]} {kw[:300]}")
    log(f"кодирую {len(texts)} тем ...")
    t0 = time.time()
    vecs = embed(model, texts)
    np.save(VEC_OUT, vecs.astype("float32"))
    log(f"→ {VEC_OUT} shape={vecs.shape} за {time.time()-t0:.0f} с")
    return 0


def topk(query: str, k: int = 10) -> list:
    import pyarrow.parquet as pq
    if not VEC_OUT.exists():
        log(f"нет {VEC_OUT} — сначала --build-vectors")
        return []
    model = get_model()
    rows = pq.read_table(TAX / "topics.parquet",
                         columns=["id", "display_name"]).to_pylist()
    V = np.load(VEC_OUT)
    q = embed(model, [f"query: {query}"])[0]
    q = q / (np.linalg.norm(q) + 1e-9)
    Vn = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)
    sim = Vn @ q
    idx = np.argsort(-sim)[:k]
    out = []
    for i in idx:
        tid = str(rows[int(i)]["id"]).rstrip("/").split("T")[-1]
        out.append((float(sim[int(i)]), f"T{tid}", rows[int(i)]["display_name"]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-vectors", action="store_true")
    ap.add_argument("--query", default=None)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model = get_model()
    if args.build_vectors:
        return encode_topics(model)
    if args.query:
        for s, tid, name in topk(args.query, args.top):
            print(f"{s:.3f} {tid} {name}")
        return 0
    if args.smoke:
        # антиподгонка: просто проверка доменов (не QA-16)
        for q in ["защита искусственного интеллекта",
                  "superconducting magnets",
                  "quantum computing"]:
            print(f"\n# {q}")
            for s, tid, name in topk(q, 5):
                print(f"  {s:.3f} {tid} {name}")
        return 0
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
