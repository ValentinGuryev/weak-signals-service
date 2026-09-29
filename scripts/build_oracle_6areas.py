#!/usr/bin/env python3
"""build_oracle_6areas.py — кандидаты тем для оракулов областей 2..6
(методика: results/runtime/ORACLE_METHOD_20260927.md, заморожена ДО прогона).

Выход: results/oracle_candidates_6areas.md — таблица для ручного разбора
(топ-10 LaBSE + топ-5 лекс) и results/oracle_candidates_6areas.json.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

XLSX = ROOT / "data/100_слабых_технологических_сигналов_сентябрь_2026.xlsx"
AREAS = {"Индустриальный ИИ", "Инфраструктура ИИ", "Роботы", "Финтех", "Edge"}
VEC = ROOT / "data/openalex_derived/taxonomy/topic_vectors.npy"


def toks(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-zа-я0-9]{4,}", str(s).lower())
            if t not in {"the", "and", "for", "with", "from", "into", "that"}}


def main() -> int:
    import openpyxl
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["Слабые сигналы"]
    rows = list(ws.iter_rows(values_only=True))
    data = [(int(r[1]), str(r[2]).strip(), str(r[3]).strip())
            for r in rows[2:] if r[1] is not None and str(r[3]).strip() in AREAS]
    wb.close()
    print(f"технологий: {len(data)}")

    topics = pd.read_parquet(ROOT / "data/openalex_derived/taxonomy/topics.parquet")
    tid = [int(str(i).rstrip("/").split("T")[-1]) for i in topics["id"]]
    names = topics["display_name"].astype(str).tolist()
    V = np.load(VEC)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-9)

    import sentence_transformers  # noqa
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer("sentence-transformers/LaBSE", device="cpu")
    texts = [f"{t} [{a}]" for _, t, a in data]
    Q = m.encode(texts, batch_size=32, normalize_embeddings=True,
                 show_progress_bar=False)
    sims = Q @ V.T

    # лекс: токен-пересечение tech vs имя темы (топ-5 по джаккарду IDF-облегч.)
    lex_out = []
    tk = [toks(f"{t} {a}") for _, t, a in data]
    n_tok = len(tk)
    dfc = {}
    for s in tk:
        for w in s:
            dfc[w] = dfc.get(w, 0) + 1
    name_toks = [toks(n) for n in names]
    for i in range(n_tok):
        scores = []
        for j, nt in enumerate(name_toks):
            inter = tk[i] & nt
            if not inter:
                scores.append((-1.0, j))
                continue
            idf = sum(np.log((n_tok + 1) / (dfc[w] + 1)) + 1 for w in inter)
            scores.append((idf / len(tk[i]), j))
        scores.sort(reverse=True)
        lex_out.append([(tid[j], names[j], round(s, 3)) for s, j in scores[:5]])

    out_md = ["# Кандидаты оракулов областей 2..6 (LaBSE топ-10 + лекс топ-5)\n"]
    js = []
    for i, (num, tech, area) in enumerate(data):
        top10 = sorted(((float(sims[i, j]), j) for j in range(len(tid))),
                       reverse=True)[:10]
        js.append({"n": num, "area": area, "tech": tech,
                   "labse": [[tid[j], names[j], round(float(s), 3)] for s, j in top10],
                   "lex": lex_out[i]})
        out_md.append(f"\n## №{num} [{area}] {tech[:110]}")
        out_md.append("LaBSE: " + " | ".join(
            f"{k}:{names[j][:46]}({s:.2f})" for k, (s, j) in enumerate(top10)))
        out_md.append("LEX: " + " | ".join(
            f"{t}:{n[:40]}" for t, n, _ in lex_out[i]))
    (ROOT / "results/oracle_candidates_6areas.md").write_text(
        "\n".join(out_md), encoding="utf-8")
    (ROOT / "results/oracle_candidates_6areas.json").write_text(
        json.dumps(js, ensure_ascii=False, indent=1))
    print(f"→ results/oracle_candidates_6areas.md/.json ({len(js)} записей)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
