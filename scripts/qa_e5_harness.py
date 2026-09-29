#!/usr/bin/env python3
"""C3a (NIGHT_PLAN): харнесс QA-16 для ретривала e5-small (отдельный от qa_regress!).

Замороженный критерий (NIGHT_PLAN C3a): ≥12/16 на QA-16, иначе TF-IDF как
основной ретривал (фиксировать в STATUS; порог не подгоняется).

Механика (без порогов): запрос q1..q4 → e5-эмбеддинг (тот же ONNX, что C2) →
cosine с topic_vectors_e5m.npy → топ-K (K = 50, как профиль выдачи сервиса)
→ topic_id-выдача → qa_protect_score (замороженный оракул, 12/16).

Выход: results/qa_e5harness/{q*.json, summary.md}
Запуск: .venv/bin/python scripts/qa_e5_harness.py [--topk 50] [--backend e5|tfidf]

C3a-решение (25.09 01:0x): e5 прошёл смоук, НО критерий ≥12/16 НЕ прошёл
(q1 2/16, q2 7/16, q3 9/16) → по плану меряем TF-IDF (антиподгонка: оба
прогона при одном замороженном топ-K и одном оракуле).
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from vps_embed import E5Onnx, TAX, VEC_OUT  # noqa: E402

QA_DIR = ROOT / "results/qa_regress"
OUT = ROOT / "results/qa_e5harness"
SCORE = ROOT / "scripts/qa_protect_score.py"
CASES = ["q1_ru_canonical", "q2_ru_long", "q3_en", "q4_offtopic_quant_sensors"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topk", type=int, default=50)
    ap.add_argument("--backend", choices=["e5", "tfidf"], default="e5")
    ap.add_argument("--variant", choices=["base", "i2"], default="base",
                    help="i2: вектора topic_vectors_e5m_i2.npy (алиасы И2 — та же "
                         "frozen-методика, что дала LaBSE 12/12)")
    ap.add_argument("--onnx-dir", default=None,
                    help="каталог ONNX (для проверки int8 перед деплоем C4)")
    ap.add_argument("--vec-file", default=None,
                    help="путь к .npy векторов (дефолт по --variant)")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    import pyarrow.parquet as pq
    topics = pq.read_table(TAX / "topics.parquet",
                           columns=["id", "display_name"]).to_pylist()
    vec_path = (Path(args.vec_file) if args.vec_file else
                TAX / ("topic_vectors_e5m_i2.npy" if args.variant == "i2"
                       else "topic_vectors_e5m.npy"))
    V = np.load(vec_path)
    print(f"backend={args.backend} variant={args.variant} K={args.topk} "
          f"vectors={vec_path.name}", flush=True)
    tfidf_vec = None
    if args.backend == "tfidf":
        # TF-IDF-фолбэк C2: корпус name+description+keywords, один фитер на все кейсы
        from sklearn.feature_extraction.text import TfidfVectorizer
        import pyarrow.parquet as pq2
        full = pq2.read_table(TAX / "topics.parquet").to_pylist()
        docs = []
        for r in full:
            kw = r.get("keywords") or ""
            if not isinstance(kw, str):
                kw = " ".join(map(str, kw))
            docs.append(f"{r['display_name']} {str(r.get('description') or '')} {kw}")
        tfidf_vec = TfidfVectorizer(max_features=100000, ngram_range=(1, 2),
                                    token_pattern=r"(?u)\b[\w-]{3,}\b")
        M = tfidf_vec.fit_transform(docs)
        print(f"tfidf: {M.shape}", flush=True)
    else:
        model = E5Onnx(Path(args.onnx_dir) if args.onnx_dir else None)
    results = {}
    for cid in CASES:
        run = json.loads((QA_DIR / f"{cid}.json").read_text())
        q = run["query"]
        t0 = time.time()
        if args.backend == "tfidf":
            qv = tfidf_vec.transform([q])
            sim = (M @ qv.T).toarray().ravel()
        else:
            # e5-префикс "query: " добавляет сам E5Onnx.embed
            qv = next(iter(model.embed([q])))
            sim = V @ qv
        order = np.argsort(-sim)[:args.topk]
        dirs = [{"topic_id": str(topics[int(i)]["id"]).rstrip("/").split("T")[-1],
                 "display_name": topics[int(i)]["display_name"]}
                for i in order]
        out = {"query": q, "match": f"{args.backend}-harness", "fanout": None,
               "routing": {"profile": "e5-harness"}, "directions": dirs}
        jp = OUT / f"{cid}.json"
        jp.write_text(json.dumps(out, ensure_ascii=False, indent=1))
        ms = int((time.time() - t0) * 1000)
        # скоринг замороженным скорером
        pr = subprocess.run(
            [sys.executable, str(SCORE), "--run", str(jp)],
            capture_output=True, text=True, cwd=ROOT)
        tail = [l for l in pr.stdout.splitlines() if "Покрытие" in l
                or "covered" in l.lower() or "/16" in l]
        results[cid] = {"ms": ms, "score_out": tail,
                        "rc": pr.returncode,
                        "stdout": pr.stdout, "stderr": pr.stderr}
        print(f"{cid}: {ms} мс, скорер rc={pr.returncode}", flush=True)
        print("   " + "\n   ".join(tail[-3:]), flush=True)

    # summary
    lines = [f"# C3a: {args.backend}/{args.variant} retrieval на QA-16 (харнесс)", "",
             f"Критерий: ≥12/16. topk={args.topk}. Время: {time.strftime('%Y-%m-%d %H:%M')}", ""]
    n_pass = 0
    for cid, r in results.items():
        lines.append(f"## {cid} ({r['ms']} мс)")
        lines.append("```")
        lines.append(r["stdout"].strip()[-1500:])
        lines.append("```")
        # PASS только по строке ПОКРЫТИЕ (не по критерию в шапке скорера!)
        cov_lines = [l for l in r["stdout"].splitlines() if "ПОКРЫТИЕ" in l]
        if cov_lines and "FAIL" not in cov_lines[-1]:
            n_pass += 1
    sfx = f"_{args.backend}" + (f"_{args.variant}" if args.variant != "base" else "")
    (OUT / f"summary{sfx}.md").write_text("\n".join(lines) + "\n")
    print(f"итог: {n_pass} кейса с ≥12/16; summary → {OUT}/summary{sfx}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
