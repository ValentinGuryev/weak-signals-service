#!/usr/bin/env python3
"""build_tech_vectors.py — e5-вектора пуля технологий (tech_ngi) для семантического
ретривала в webapp/app.py (фиксирует токенный мусор 28.09: «air showers» и т.п.).

Выход: webapp/data/tech_ngi_vectors.npy (N×384 float32), порядок строк = tech_ngi.parquet.
Эмбеддинг — ТОТ ЖЕ код/e5-модель, что в app (passage-префикс).

Запуск: .venv/bin/python scripts/build_tech_vectors.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "webapp"))
import app as webapp  # noqa: E402  (загружает данные webapp + e5 ONNX)

OUT = ROOT / "webapp" / "data" / "tech_ngi_vectors.npy"


def main() -> None:
    terms = pd.read_parquet(ROOT / "webapp/data/tech_ngi.parquet")["term"].astype(str).tolist()
    if webapp.E5 is None:
        raise SystemExit("E5 недоступна — вектора не собрать")
    vecs = []
    B = 256
    for i in range(0, len(terms), B):
        vecs.append(webapp.e5_embed(terms[i:i + B], is_query=False))
    V = np.vstack(vecs).astype(np.float32)
    assert V.shape == (len(terms), 384), V.shape
    np.save(OUT, V)
    print(f"OK: {V.shape} -> {OUT} ({OUT.stat().st_size / 1e6:.1f} МБ)")

    # калибровка порога: топ-30 по косинусу на демо-запросах
    for q in ["Защита искусственного интеллекта", "Роботы", "Финтех"]:
        qv = webapp.e5_embed([q])[0]
        cos = V @ qv
        top = np.argsort(-cos)[:30]
        print(f"\n=== {q}")
        for j in top:
            print(f"  {cos[j]:.3f} | {terms[j]}")


if __name__ == "__main__":
    main()
