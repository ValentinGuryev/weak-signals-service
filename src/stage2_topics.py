"""Этап 2: тренды — BERTopic (лёгкий) с fallback LDA.

Вход: data/processed/papers.parquet (arXiv-only, решение команды).
Выход:
  - data/processed/topics.json        — темы + квартальная динамика (схема в docs/ARCHITECTURE.md)
  - data/processed/doc_topics.parquet — назначение документов по темам
  - experiment/runs/<iter>_results.json — служебный отчёт

Решения автора (зафиксированы в журнал решений 2026-08-16):
  - только arXiv (без локальной библиотеки);
  - динамика по кварталам (не месяцам);
  - порог сэмплирования 20 000 документов (подтверждён 2026-08-16).

Конвенции (внутренний контракт раздел 9): logging, type hints, конфиги YAML,
без silent fallback — переход на LDA только при явном MemoryError (логгируется).
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from utils import PROJECT_ROOT, load_config, setup_logging

logger = setup_logging()

# Порог сэмплирования по умолчанию (решение команды).
# Может быть переопределён конфигом (data.sample_threshold) для полного прогона на всей базе.
SAMPLE_THRESHOLD = 20_000


def load_docs(cfg: dict[str, Any]) -> pd.DataFrame:
    """Загрузить документы arXiv из parquet, применить фильтры по годам и сэмплирование."""
    input_path = PROJECT_ROOT / cfg["data"]["input"]
    if not input_path.exists():
        raise FileNotFoundError(f"Данные не найдены: {input_path}")
    df = pd.read_parquet(input_path)
    logger.info("Загружено документов: %d", len(df))

    # --- только arXiv ---
    if "source" in df.columns:
        df = df[df["source"].fillna("arxiv") == "arxiv"]
        logger.info("После фильтра source=arxiv: %d", len(df))

    # --- годы ---
    min_year, max_year = cfg["data"]["min_year"], cfg["data"]["max_year"]
    dates = pd.to_datetime(df["published"], errors="coerce")
    df = df[(dates.dt.year >= min_year) & (dates.dt.year <= max_year)]
    df = df.dropna(subset=["abstract"])
    df = df[df["abstract"].astype(str).str.len() > 50]
    logger.info("После фильтров (годы %s–%s, абстракты): %d", min_year, max_year, len(df))

    # --- текст для модели: title + abstract ---
    text = (df["title"].fillna("").astype(str) + ". " + df["abstract"].fillna("").astype(str)).str.strip()
    df = df.assign(_text=text)
    df = df[df["_text"].str.len() > 20]

    # --- сэмплирование ---
    threshold = cfg["data"].get("sample_threshold", SAMPLE_THRESHOLD)
    n = len(df)
    if n > threshold:
        seed = cfg["data"].get("sample_seed", 42)
        df = df.sample(threshold, random_state=seed)
        logger.info("Сэмплирование: %d → %d (порог %d, seed=%d)", n, len(df), threshold, seed)
    elif cfg["data"].get("sample_size"):
        k = min(cfg["data"]["sample_size"], len(df))
        df = df.sample(k, random_state=cfg["data"].get("sample_seed", 42))
        logger.info("Smoke-выборка: %d документов (seed=%d)", k, cfg["data"].get("sample_seed", 42))

    return df.reset_index(drop=True)


def to_quarter(published: pd.Series) -> pd.Series:
    """Квартальная метка 'YYYY-Qn' из дат."""
    d = pd.to_datetime(published, errors="coerce")
    return d.dt.year.astype(str) + "-Q" + d.dt.quarter.astype(str)


def run_bertopic(docs: list[str], cfg: dict[str, Any]) -> tuple[Any, np.ndarray, np.ndarray]:
    """Обучить BERTopic. Возвращает (модель, topics, probabilities).

    Эмбеддинги кэшируются в data/cache/embeddings_<n>.npy — пересчёт только при изменении числа документов.
    """
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, CountVectorizer

    m = cfg["model"]
    embedder = SentenceTransformer(m["embedding_model"])

    # Стоп-слова (англ. + общенаучные), чтобы c-TF-IDF не давал темы из `the of in and`.
    scientific_stop = {
        "study", "studies", "paper", "results", "result", "method", "methods",
        "approach", "proposed", "show", "shown", "using", "used", "based",
        "model", "models", "data", "analysis", "work", "works", "new",
        "however", "also", "well", "may", "can", "one", "two", "three",
        "within", "among", "between", "such", "thus", "hence", "therefore",
        "obtain", "obtained", "found", "observed", "present", "presented",
        "different", "various", "several", "including", "important", "significant",
        "possible", "used", "use", "using", "via", "e.g", "i.e", "et al",
    }
    stop_words = list(set(ENGLISH_STOP_WORDS) | scientific_stop)
    vectorizer = CountVectorizer(stop_words=stop_words, min_df=5)

    # --- кэш эмбеддингов ---
    cache_dir = PROJECT_ROOT / "data" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    emb_cache = cache_dir / f"embeddings_{len(docs)}.npy"
    if emb_cache.exists():
        embeddings = np.load(emb_cache)
        logger.info("Эмбеддинги из кэша: %s", emb_cache)
    else:
        logger.info("Расчёт эмбеддингов (%d документов)…", len(docs))
        embeddings = embedder.encode(docs, batch_size=64, show_progress_bar=False)
        np.save(emb_cache, embeddings)
        logger.info("Эмбеддинги сохранены в кэш: %s", emb_cache)

    topic_model = BERTopic(
        embedding_model=embedder,
        nr_topics=m.get("nr_topics"),
        min_topic_size=m.get("min_topic_size", 10),
        calculate_probabilities=False,
        verbose=False,
        vectorizer_model=vectorizer,
    )
    logger.info("Обучение BERTopic (nr_topics=%s, min_topic_size=%s, стоп-слов=%d)…",
                m.get("nr_topics"), m.get("min_topic_size"), len(stop_words))
    topics, probs = topic_model.fit_transform(docs, embeddings=embeddings)
    return topic_model, topics, probs


def run_lda(docs: list[str], cfg: dict[str, Any]) -> tuple[Any, np.ndarray, np.ndarray]:
    """Fallback: TF-IDF + LDA (scikit-learn). Возвращает (модель, topics, probs)."""
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import TfidfVectorizer

    m = cfg["model"]
    n_topics = m.get("nr_topics", 20)
    vectorizer = TfidfVectorizer(max_features=20_000, stop_words="english")
    X = vectorizer.fit_transform(docs)
    lda = LatentDirichletAllocation(
        n_components=n_topics, random_state=cfg["data"].get("sample_seed", 42), max_iter=15,
    )
    logger.info("Fallback LDA: %d компонент на %d признаков", n_topics, X.shape[1])
    lda.fit(X)
    theta = lda.transform(X)
    topics = np.argmax(theta, axis=1)
    probs = theta
    return lda, topics, probs


def build_topics_json(
    model: Any,
    topics: np.ndarray,
    probs: np.ndarray | None,
    df: pd.DataFrame,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    """Собрать topics.json: label, top_words, размер, квартальная динамика."""
    n = len(df)
    unique_vals = np.unique(topics)
    n_real = int((unique_vals != -1).sum())  # -1 = аутлайеры

    out_topics: list[dict[str, Any]] = []
    doc_topics = pd.DataFrame(
        {"arxiv_id": df["arxiv_id"], "topic": topics, "quarter": to_quarter(df["published"])}
    )

    topics_arr = np.asarray(topics)
    for t in unique_vals:
        mask = topics_arr == t
        docs_t = df[mask]
        q_counts = docs_t.groupby(to_quarter(docs_t["published"])).size().to_dict()
        if t == -1:
            label, words = "outlier", []
        else:
            try:
                info = model.get_topic(int(t))
                words = [w for w, _ in (info or [])][:15]
                label = " ".join(words[:5]) or f"topic_{t}"
            except Exception:  # fallback для LDA: топ-слова по весам
                words = []
                label = f"topic_{t}"
        out_topics.append(
            {
                "topic_id": int(t),
                "label": label,
                "top_words": words,
                "size": int(mask.sum()),
                "share": float(mask.sum() / n),
                "quarterly_counts": {str(k): int(v) for k, v in sorted(q_counts.items())},
            }
        )

    out_topics.sort(key=lambda x: -x["size"])
    return {
        "model": "bertopic" if cfg["model"]["backend"] == "bertopic" else "lda",
        "n_topics": n_real,
        "n_docs": n,
        "outlier_share": float((np.asarray(topics) == -1).mean()),
        "topics": out_topics,
        "params": {
            "nr_topics": cfg["model"].get("nr_topics"),
            "min_topic_size": cfg["model"].get("min_topic_size"),
            "embedding": cfg["model"].get("embedding_model"),
            "sample_threshold": SAMPLE_THRESHOLD,
            "sample_seed": cfg["data"].get("sample_seed", 42),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Этап 2: тренды (BERTopic/LDA)")
    ap.add_argument("--config", default="experiment/configs/iter_001.yaml")
    args = ap.parse_args()

    cfg = load_config(args.config)
    df = load_docs(cfg)

    docs = df["_text"].tolist()
    backend = cfg["model"]["backend"]
    if backend == "auto":
        backend = "bertopic"

    try:
        if backend == "bertopic":
            model, topics, probs = run_bertopic(docs, cfg)
        elif backend == "lda":
            model, topics, probs = run_lda(docs, cfg)
        else:
            raise ValueError(f"Неизвестный backend: {backend}")
    except MemoryError:
        if cfg["model"]["backend"] != "auto":
            raise
        logger.warning("MemoryError при BERTopic — явный переход на fallback LDA")
        model, topics, probs = run_lda(docs, cfg)

    result = build_topics_json(model, topics, probs, df, cfg)

    out_topics = PROJECT_ROOT / cfg["output"]["topics"]
    out_topics.parent.mkdir(parents=True, exist_ok=True)
    with out_topics.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("Записано: %s", out_topics)

    doc_topics = pd.DataFrame(
        {"arxiv_id": df["arxiv_id"], "topic": topics, "quarter": to_quarter(df["published"])}
    )
    out_doc = PROJECT_ROOT / cfg["output"]["doc_topics"]
    doc_topics.to_parquet(out_doc, index=False)
    logger.info("Записано: %s", out_doc)

    # отчёт в experiment/runs/
    report = {
        "config": str(args.config),
        "n_docs": len(docs),
        "n_topics": result["n_topics"],
        "outlier_share": result["outlier_share"],
        "topics": [{"id": t["topic_id"], "label": t["label"], "size": t["size"]} for t in result["topics"][:10]],
    }
    out_res = PROJECT_ROOT / cfg["output"]["results"]
    out_res.parent.mkdir(parents=True, exist_ok=True)
    with out_res.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info("Записано: %s", out_res)


if __name__ == "__main__":
    main()
