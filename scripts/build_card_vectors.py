#!/usr/bin/env python3
"""Ступень Д (Addendum №17): сборка карточного стора выдачи формы 1.

Вход : data/openalex_derived/tech_cards_v1_dedup.parquet (после Г-merge и Д2)
Выход: webapp/data/cards/tech_cards.parquet + tech_cards_vectors.npy

Правила (addendum №17, объявлен ДО):
  * в пул идут status=="ok" И llm != "invalid";
  * llm=="valid" → llm_valid=1 (первый слой гибрида), остальные → 0;
  * вектор = e5(passage) по тексту «name_en. problem_ru/…» — текст = name_en + ' ' +
    problem_en (fallback: term); батчи 256, embedding через app-энкодер (тот же ONNX);
  * в parquet: term=name_en, term_ru=name_ru, score_ngi/novelty/growth_n/impact,
    birth, n_recent, linked_json (темы), anchors_json, problem_ru/en, llm_valid.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "webapp/data/cards"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp",
                    default=str(ROOT / "data/openalex_derived/tech_cards_v1_dedup.parquet"))
    ap.add_argument("--limit", type=int, default=0, help="смоук: только N")
    args = ap.parse_args()
    t0 = time.time()

    df = pd.read_parquet(args.inp)
    n0 = len(df)
    if "llm" not in df.columns:        # смоук до Г-этапа: колонки нет
        df["llm"] = ""
    for _c, _d in {"name_ru": "", "problem_ru": "", "problem_en": "",
                   "anchors_json": "[]", "linked_json": "[]"}.items():
        if _c not in df.columns:       # смоук до Г/merge: колонки добавлены позже
            df[_c] = _d
    df = df[(df["status"] == "ok") & (df["llm"].fillna("") != "invalid")].copy()
    df["llm_valid"] = (df["llm"] == "valid").astype("int8")
    # при --limit берём ТОП по priority (сп-термы, свежие), а не случайную
    # голову файла — иначе выдача/наличие золота зависят от порядка строк
    if "priority" in df.columns:
        df = df.sort_values("priority", ascending=False)
    if args.limit:
        df = df.head(args.limit)

    # текст для эмбеддинга: название + обрезанная проблема (узкое место ночи:
    # [:150] даёт ~30-34 txt/s вместо 17 при [:300]; p50 problem_en = 175 симв.)
    texts = (df["name_en"].fillna("") + ". " +
             df["problem_en"].fillna("").str.slice(0, 150)).tolist()

    # импорт app даёт тот же e5-энкодер, что и сервис (консистентность косинусов)
    import sys
    sys.path.insert(0, str(ROOT / "webapp"))
    import app as webapp  # noqa: E402
    if webapp.E5 is None:
        raise SystemExit("e5 недоступен — вектора не собрать (явная ошибка, §9)")

    vecs = []
    t_emb = time.time()
    for i in range(0, len(texts), 256):
        vecs.append(webapp.e5_embed(texts[i:i + 256], is_query=False))
        if (i // 256) % 50 == 0:
            el = time.time() - t_emb
            rate = (i + 256) / max(el, 1e-9)
            print(f"  embed {i}/{len(texts)} ({rate:.1f} txt/s, "
                  f"ETA {(len(texts)-i)/max(rate,1e-9)/60:.0f} мин)", flush=True)
    vec = np.vstack(vecs).astype(np.float32)

    out = df[["term", "name_en", "name_ru", "problem_ru", "problem_en",
              "novelty", "growth_n", "impact", "score_ngi", "birth" if "birth" in df
              else "first_year", "n_recent_sum", "linked_json", "anchors_json",
              "llm_valid"]].rename(columns={"first_year": "birth",
                                            "n_recent_sum": "n_recent"})
    if "birth" not in out.columns:
        out["birth"] = df["first_year"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_DIR / "tech_cards.parquet", index=False)
    np.save(OUT_DIR / "tech_cards_vectors.npy", vec)
    print(f"пул карточек: {n0:,} → {len(out):,} (valid={int(df.llm_valid.sum()):,}); "
          f"вектора {vec.shape}; {time.time()-t0:.0f} с → {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
