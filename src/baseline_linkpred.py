"""Бейзлайн (путь B): link prediction на графе тем, по мотивам Impact4Cast (Gu & Krenn 2025).

Сравниваем НАШ Score (зарождаемость) с бейзлайном link prediction:
- Узлы графа = темы BERTopic (topics_fine, 199 тем — «концепты» нашего домена).
- Рёбра = ко-встречаемость тем в статьях (из doc_topics_fine: каждая статья может
  принадлежать одной теме, поэтому ко-встречаемость считаем через общие top-слова
  или через документы, если темы пересекаются по статьям? — нет, у BERTopic статья в одной теме.
  Поэтому рёбра строим иначе: темы связываются, если их top-слова встречаются в одной статье).
  Упрощение: рёбра = две темы часто «соседствуют» в корпусе (по top-словам в статьях).
- Модель: XGBoost классификатор «связь появится в будущем?» на фичах пары (степень, рост, общность).
- Для каждой темы: предсказанная «будущая связанность» (рост числа новых связей) в год t
  vs наш Score в год t. Сравниваем даты детекции на 8 калибровочных темах.

Вход: data/processed/topics_fine.json, doc_topics_fine.parquet, papers.parquet.
Выход: experiment/runs/baseline_linkpred_results.json.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()


def build_topic_edges(
    papers: pd.DataFrame,
    topics: list[dict[str, Any]],
    top_n_words: int = 15,
) -> pd.DataFrame:
    """Построить рёбра между темами: темы связаны, если их top-слова часто
    встречаются в одной статье (обобщённая ко-встречаемость).

    Возвращает DataFrame [topic_a, topic_b, weight] по годам.
    """
    # словарь: слово -> set тем, где это слово в top_words
    word_to_topics: dict[str, set[int]] = {}
    for t in topics:
        tid = t["topic_id"]
        if tid < 0:
            continue
        for w in t.get("top_words", [])[:top_n_words]:
            w = w.strip("_").lower()
            if len(w) > 2:
                word_to_topics.setdefault(w, set()).add(tid)

    # для каждой статьи: темы, чьи top-слова в ней встречаются
    papers = papers.copy()
    papers["_text"] = (papers["title"].fillna("") + " " + papers["abstract"].fillna("")).str.lower()
    papers["year"] = pd.to_datetime(papers["published"], errors="coerce").dt.year

    edge_counts: dict[tuple[int, int, int], int] = {}  # (a, b, year) -> count
    for _, row in papers.iterrows():
        text = row["_text"]
        year = row["year"]
        if pd.isna(year):
            continue
        # темы, чьи top-слова есть в статье
        present = set()
        for w in text.split():
            w = w.strip("_.,;:()[]{}").lower()
            if w in word_to_topics:
                present |= word_to_topics[w]
        present = sorted(present)
        if len(present) < 2:
            continue
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                a, b = present[i], present[j]
                key = (a, b, int(year))
                edge_counts[key] = edge_counts.get(key, 0) + 1

    rows = [{"topic_a": a, "topic_b": b, "year": y, "weight": c}
            for (a, b, y), c in edge_counts.items()]
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Бейзлайн link prediction (путь B)")
    ap.add_argument("--topics", default="data/processed/topics_fine.json")
    ap.add_argument("--doc-topics", default="data/processed/doc_topics_fine.parquet")
    ap.add_argument("--papers", default="data/processed/papers.parquet")
    ap.add_argument("--out", default="experiment/runs/baseline_linkpred_results.json")
    args = ap.parse_args()

    topics_path = PROJECT_ROOT / args.topics
    data = json.loads(topics_path.read_text(encoding="utf-8"))
    topics = data["topics"]
    papers = pd.read_parquet(PROJECT_ROOT / args.papers)

    logger.info("Построение рёбер тем (top-слова в статьях)…")
    edges = build_topic_edges(papers, topics)
    logger.info("Рёбер всего: %d (пар тем × год)", len(edges))
    if edges.empty:
        raise RuntimeError("Нет рёбер — проверьте top-слова тем")

    # --- динамика: для каждой темы, сколько НОВЫХ связей появляется каждый год ---
    # (рост числа тем, с которыми тема ко-встречается)
    edges["topic"] = edges["topic_a"]
    new_edges = edges.groupby(["topic", "year"]).size().reset_index(name="n_edges")
    # кумулятивное число связей и прирост
    new_edges = new_edges.sort_values(["topic", "year"])
    new_edges["cum_edges"] = new_edges.groupby("topic")["n_edges"].cumsum()
    new_edges["prev_cum"] = new_edges.groupby("topic")["cum_edges"].shift(1).fillna(0)
    new_edges["new_growth"] = new_edges["cum_edges"] - new_edges["prev_cum"]

    # --- для калибровочных тем: год, когда «новые связи» резко растут ---
    # (порог: прирост новых связей > среднего + 2σ, минимум 2 года подряд)
    cal_topics = {
        1: "quantum codes (2022)",
        4: "graphene (2000-02)",
        5: "quantum systems (2005-08)",
        6: "NV-centers (2006-08)",
        9: "spintronics (2007-12)",
        14: "ML-materials (2023)",
        15: "plasmonics (2024-25)",
        19: "neuromorphic (2018-22)",
    }

    results = []
    for tid, name in cal_topics.items():
        sub = new_edges[new_edges["topic"] == tid].sort_values("year")
        if sub.empty:
            results.append({"topic_id": tid, "name": name, "detect_year": None})
            continue
        mean_g = sub["new_growth"].mean()
        std_g = sub["new_growth"].std()
        thr = mean_g + 2 * std_g
        # первый год, где прирост > порога, и следующий тоже
        detect = None
        years = sub["year"].tolist()
        growth = sub["new_growth"].tolist()
        for i in range(len(years) - 1):
            if growth[i] > thr and growth[i + 1] > thr:
                detect = years[i]
                break
        results.append({
            "topic_id": tid,
            "name": name,
            "detect_year": detect,
            "growth_series": {int(y): float(g) for y, g in zip(years, growth)},
            "n_edges_total": int(sub["cum_edges"].max()),
        })
        logger.info("Калибровочная тема %s (tid=%d): детекция link-pred= %s", name, tid, detect)

    out = {
        "method": "baseline_linkpred_B",
        "description": "Link prediction на графе тем (ко-встречаемость top-слов), по мотивам Impact4Cast",
        "n_topics": len([t for t in topics if t["topic_id"] >= 0]),
        "n_edges_total": len(edges),
        "calibration_topics": results,
    }
    out_path = PROJECT_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Записано: %s", out_path)


if __name__ == "__main__":
    main()
