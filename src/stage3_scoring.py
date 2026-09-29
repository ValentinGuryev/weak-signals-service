"""Этап 3: Score — метрика «зарождаемости» трендов + исторический бэктест.

Формула v1 (внутренний контракт §7), БЕЗ изменений:
    EmergenceScore(topic, t) = α·GrowthRate(t) + β·NoveltyScore(t) + γ·Acceleration(t)

- GrowthRate    = (публикации за Δt) / (все публикации темы)
- NoveltyScore  = 1 если тема впервые появилась < 12 мес назад, иначе затухает
- Acceleration  = вторая производная числа публикаций (растёт ли скорость роста)

Параметры (по умолчанию): α=0.4, β=0.35, γ=0.25, Δt=3 мес (1 квартал), порог Score>0.7.

Фильтры искажений (§7.1), НЕ меняющие формулу:
  - размерный порог (отсечь мелкие/шумовые темы и тему-«клей»);
  - устойчивость роста (минимум N кварталов подряд);
  - сглаживание временного ряда (эхо датировки arXiv).

Валидация (§4.5): исторический бэктест — Score на данных до cutoff,
топ-N трендов «тогда», проверка по реальности (рост после cutoff).
Метрики: precision@k, recall@k, средний лаг обнаружения.

Keyword-модуль (добавлен 2026-08-16): узкие под-темы, которые BERTopic не выделяет
(диодный эффект в сверхпроводниках и др.), ищутся по ключевым словам прямо в корпусе
и получают тот же Score. Вход: data/processed/papers.parquet.

Вход: data/processed/topics.json (темы + quarterly_counts).
Выход: results/top_trends.json, experiment/runs/backtest_*.json.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from utils import PROJECT_ROOT, load_config, setup_logging

logger = setup_logging()

# Квартал -> порядковый номер (для численных расчётов). 2006-Q1 = 0.
QUARTERS_PER_YEAR = 4


def quarter_to_int(q: str) -> int:
    """'2006-Q1' -> 0; '2026-Q3' -> 82. Устойчив к '2006Q1' и '2006-Q1'."""
    q = q.strip()
    if "-Q" in q:
        year, qn = q.split("-Q")
    elif "Q" in q:
        # '2006Q1'
        idx = q.index("Q")
        year, qn = q[:idx], q[idx + 1:]
    else:
        raise ValueError(f"Некорректный квартал: {q!r}")
    return (int(year) - 2006) * QUARTERS_PER_YEAR + int(qn) - 1


def int_to_quarter(idx: int) -> str:
    """0 -> '2006-Q1'."""
    year = 2006 + idx // QUARTERS_PER_YEAR
    qn = idx % QUARTERS_PER_YEAR + 1
    return f"{year}-Q{qn}"


def smooth(series: np.ndarray, window: int = 3) -> np.ndarray:
    """Простое сглаживание скользящим средним (эхо датировки arXiv, §7.1 п.4)."""
    if len(series) < window:
        return series.astype(float)
    kernel = np.ones(window) / window
    return np.convolve(series, kernel, mode="same")


def load_quarterly_series(topics: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Развернуть quarterly_counts (dict квартал->int) в плотный ряд по всем кварталам.

    Возвращает {topic_id: {'series': np.ndarray (83), 'start': int, 'end': int, ...}}.
    """
    all_q = set()
    for t in topics:
        all_q.update(t["quarterly_counts"].keys())
    qmin = min(quarter_to_int(q) for q in all_q)
    qmax = max(quarter_to_int(q) for q in all_q)
    n_q = qmax - qmin + 1
    logger.info("Квартальный диапазон: %s .. %s (%d кварталов)",
                int_to_quarter(qmin), int_to_quarter(qmax), n_q)

    out: dict[int, dict[str, Any]] = {}
    for t in topics:
        tid = t["topic_id"]
        counts = t.get("quarterly_counts", {})
        series = np.zeros(n_q, dtype=float)
        for q, c in counts.items():
            idx = quarter_to_int(q) - qmin
            if 0 <= idx < n_q:
                series[idx] = c
        # начало активности = первый квартал с ненулевым числом
        nonzero = np.nonzero(series)[0]
        start = int(nonzero[0]) if len(nonzero) else qmin
        end = int(nonzero[-1]) if len(nonzero) else qmin
        out[tid] = {
            "series": series,
            "start": start,
            "end": end,
            "size": t.get("size", 0),
            "label": t.get("label", ""),
            "top_words": t.get("top_words", []),
        }
    return out, qmin


def compute_score(
    series: np.ndarray,
    start: int,
    alpha: float,
    beta: float,
    gamma: float,
    delta_t: int,
    novelty_window: int,
    now_idx: int,
    qmin: int,
    min_emergence: int = 0,
) -> dict[str, float]:
    """Score темы в момент now_idx (индекс от начала ряда).

    Возвращает {score, growth_rate, novelty, acceleration}.

    min_emergence — первый допустимый квартал зарождения тренда (относительный индекс,
    по умолчанию 0 = начало ряда). Решение команды: тренд не может зародиться
    раньше min_emergence (краевой артефакт начала датасета: в 2006 все темы выглядели «новыми»).
    """
    # сглаживание
    s = smooth(series, window=3)
    # активная часть (после старта), но не дальше now_idx
    lo = max(0, start - qmin)
    hi = min(now_idx - qmin, len(s) - 1)
    # до окна зарождаемости Score не считается (тренд не может зародиться раньше min_emergence)
    if hi < min_emergence:
        return {"score": 0.0, "growth_rate": 0.0, "novelty": 0.0, "acceleration": 0.0}
    if hi <= lo:
        return {"score": 0.0, "growth_rate": 0.0, "novelty": 0.0, "acceleration": 0.0}

    # --- GrowthRate: публикации за последние Δt кварталов / всего за активный период ---
    window = max(1, delta_t)
    recent = float(s[max(lo, hi - window + 1): hi + 1].sum())
    total = float(s[lo: hi + 1].sum())
    growth = recent / total if total > 0 else 0.0

    # --- NoveltyScore: тема появилась < novelty_window кварталов назад? ---
    # Тема, существовавшая ДО окна зарождаемости, не может быть «новой» —
    # иначе в начале датасета ВСЕ темы получили бы novelty=1 (краевой артефакт 2006).
    if start - qmin < min_emergence:
        novelty = 0.0
    else:
        age_quarters = hi - lo + 1  # сколько кварталов тема активна
        novelty = 1.0 if age_quarters < novelty_window else max(0.0, 1.0 - (age_quarters - novelty_window) / 20.0)

    # --- Acceleration: вторая производная (рост скорости роста) ---
    # берём последние ~5 кварталов, численно
    seg = s[max(lo, hi - 4): hi + 1]
    if len(seg) >= 3:
        d1 = np.diff(seg)
        acc = float(np.diff(d1).mean()) if len(d1) >= 2 else 0.0
    else:
        acc = 0.0
    # нормализация ускорения: масштаб ~ средний темп
    scale = float(np.mean(s[lo: hi + 1])) + 1e-9
    acc_norm = float(np.tanh(acc / scale))  # в [-1, 1]

    score = alpha * growth + beta * novelty + gamma * max(0.0, acc_norm)
    return {
        "score": float(score),
        "growth_rate": float(growth),
        "novelty": float(novelty),
        "acceleration": float(acc_norm),
    }


def apply_filters(topics: dict[int, dict[str, Any]], cfg: dict[str, Any], qmin: int) -> list[int]:
    """Фильтры искажений (§7.1): размер, активность, тема-«клей». Возвращает id тем для Score."""
    f = cfg["filters"]
    min_size = f.get("min_size", 50)
    min_quarters = f.get("min_quarters", 4)
    exclude_glue = f.get("exclude_glue", True)

    kept: list[int] = []
    for tid, info in topics.items():
        if info["size"] < min_size:
            continue
        active = info["end"] - info["start"] + 1
        if active < min_quarters:
            continue
        # тема-«клей»: очень большая, общие слова — исключаем (по конфигу)
        if exclude_glue and tid == 0:
            logger.info("Исключена тема-«клей»: id=0 (%s, size=%d)", info["label"], info["size"])
            continue
        kept.append(tid)
    logger.info("После фильтров (min_size=%d, min_quarters=%d): %d тем из %d",
                min_size, min_quarters, len(kept), len(topics))
    return kept


def compute_all_scores(
    topics: dict[int, dict[str, Any]],
    kept: list[int],
    cfg: dict[str, Any],
    now_idx: int,
    qmin: int,
    min_emergence: int = 0,
) -> dict[int, dict[str, Any]]:
    """Считает Score для всех kept тем в момент now_idx."""
    sc = cfg["score"]
    result: dict[int, dict[str, Any]] = {}
    for tid in kept:
        info = topics[tid]
        comps = compute_score(
            info["series"], info["start"],
            sc["alpha"], sc["beta"], sc["gamma"],
            sc["delta_t"], sc["novelty_window"], now_idx, qmin, min_emergence,
        )
        result[tid] = {
            "topic_id": tid,
            "label": info["label"],
            "top_words": info["top_words"],
            "size": info["size"],
            "evidence": info.get("evidence", []),
            "score": comps["score"],
            "components": {
                "growth_rate": comps["growth_rate"],
                "novelty": comps["novelty"],
                "acceleration": comps["acceleration"],
            },
            "start": info["start"],
            "end": info["end"],
        }
    return result


def build_evidence(df: pd.DataFrame, tid: int) -> list[str]:
    """Список arxiv_id документов темы (для evidence в top_trends.json)."""
    if df is None or df.empty or "topic" not in df.columns:
        return []
    sub = df[df["topic"] == tid]
    return sub["arxiv_id"].astype(str).head(10).tolist()


def keyword_trends(
    papers_path: Path,
    keywords: list[str],
    cfg: dict[str, Any],
    qmin: int,
    n_q: int,
) -> dict[int, dict[str, Any]]:
    """Keyword-детекция: найти документы по ключевым словам, построить квартальную динамику,
    вернуть в том же формате, что темы BERTopic (для compute_all_scores).

    keywords — список фраз (нижний регистр), документ матчится если содержит любую.
    Возвращает {topic_id (отрицательные: -100, -101...): {...}} — не пересекаются с BERTopic (0..199).
    """
    if not keywords:
        return {}
    df = pd.read_parquet(papers_path)
    txt = (df["title"].fillna("").astype(str) + " " + df["abstract"].fillna("").astype(str)).str.lower()
    mask = txt.str.contains("|".join(keywords), regex=True, na=False)
    sub = df[mask].copy()
    if sub.empty:
        logger.warning("Keyword-детекция: ни одного документа по ключам %s", keywords)
        return {}

    # квартальная динамика в формате quarterly_counts ("YYYY-Qn")
    sub["_q"] = pd.to_datetime(sub["published"], errors="coerce").dt.to_period("Q").astype(str)
    # pd.to_period("Q") даёт "2020Q1" -> нормализуем в "2020-Q1" (аккуратно, без дублей)
    def _norm(q: str) -> str:
        if "-Q" in q or q == "":
            return q
        # "2020Q2" -> "2020-Q2" (вставить дефис перед Q, не дублировать)
        return q[:4] + "-" + q[4:]
    sub["_q"] = sub["_q"].map(_norm)
    counts = sub.groupby("_q").size().to_dict()
    # отфильтровать пустые
    counts = {k: v for k, v in counts.items() if k}

    # ряд (плотный, как у тем)
    series = np.zeros(n_q, dtype=float)
    for q, c in counts.items():
        idx = quarter_to_int(q) - qmin
        if 0 <= idx < n_q:
            series[idx] = c
    nonzero = np.nonzero(series)[0]
    start = int(nonzero[0]) if len(nonzero) else 0

    # topic_id: -100 - len(существующих) ... — уникальные, не пересекаются с BERTopic
    tid = -100 - len(keyword_trends._cache) if hasattr(keyword_trends, "_cache") else -100
    # проще: использовать индекс в списке — задаётся в main, тут возвращаем по одному ключу
    return {
        tid: {
            "series": series,
            "start": start,
            "end": int(nonzero[-1]) if len(nonzero) else 0,
            "size": len(sub),
            "label": f"KW: {keywords[0]}",
            "top_words": keywords,
            "evidence": sub["arxiv_id"].astype(str).head(10).tolist(),
        }
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Записано: %s", path)


def main() -> None:
    ap = argparse.ArgumentParser(description="Этап 3: Score трендов + бэктест")
    ap.add_argument("--config", default="experiment/configs/iter_002.yaml")
    args = ap.parse_args()

    cfg = load_config(args.config)
    topics_path = PROJECT_ROOT / cfg["data"]["input"]
    if not topics_path.exists():
        raise FileNotFoundError(f"Темы не найдены: {topics_path}")
    data = json.loads(topics_path.read_text(encoding="utf-8"))
    topics_in = data["topics"]

    topics, qmin = load_quarterly_series(topics_in)
    n_q = max(info["series"].shape[0] for info in topics.values()) if topics else 0

    # --- Keyword-детекция: узкие под-темы, которые BERTopic не выделяет ---
    # (диодный эффект и др.). Добавляются как отдельные «темы» с отрицательными id.
    kw_cfg = cfg.get("keywords", {})
    kw_items = kw_cfg.get("items", [])  # [{name, patterns:[...]}, ...]
    kw_start = 0
    for item in kw_items:
        name = item.get("name", "kw")
        patterns = item.get("patterns", [])
        papers_path = PROJECT_ROOT / kw_cfg.get("papers_input", "data/processed/papers.parquet")
        kt = keyword_trends(papers_path, patterns, cfg, qmin, n_q)
        for tid, info in kt.items():
            info["label"] = f"KW: {name}"
            # уникальный отрицательный id
            new_tid = -200 - kw_start
            kw_start += 1
            topics[new_tid] = info
        if kt:
            logger.info("Keyword-тема «%s»: %d док.", name, list(kt.values())[0]["size"])

    kept = apply_filters(topics, cfg, qmin)

    # --- min_emergence: тренд не может зародиться раньше этого квартала ---
    # (решение команды: игнорируем первые годы — краевой артефакт 2006)
    min_em_year = cfg["score"].get("min_emergence_year", 2006)
    min_emergence = max(0, (min_em_year - 2006) * QUARTERS_PER_YEAR - qmin)
    if min_emergence > 0:
        logger.info("Краевой артефакт: тренд не может зародиться раньше %s (min_emergence=%d)",
                    int_to_quarter(min_emergence + qmin), min_emergence)

    # --- Score на ВСЕХ данных (до 2026-Q3) — итоговый рейтинг ---
    now_idx = qmin + n_q - 1
    scores_all = compute_all_scores(topics, kept, cfg, now_idx, qmin, min_emergence)

    # --- Бэктест: Score на данных до cutoff (конец 2022) ---
    cutoff = pd.Timestamp(cfg["data"]["cutoff"])
    # индекс квартала, соответствующего последнему полному кварталу до cutoff
    cut_year, cut_q = cutoff.year, (cutoff.month - 1) // 3 + 1
    cut_idx = (cut_year - 2006) * QUARTERS_PER_YEAR + cut_q - 1 - 1  # последний ПОЛНЫЙ квартал до cutoff
    # но не раньше начала
    cut_idx = max(cut_idx, qmin)
    scores_back = compute_all_scores(topics, kept, cfg, cut_idx, qmin, min_emergence)
    logger.info("Бэктест: Score на данных до %s (квартал %s, idx=%d)",
                cutoff.date(), int_to_quarter(cut_idx), cut_idx)

    # --- Метрики бэктеста: precision@k / recall@k ---
    k = cfg["backtest"]["top_k"]
    ranked_back = sorted(scores_back.items(), key=lambda x: -x[1]["score"])[:k]
    # «подтвердился» = тема выросла после cutoff (среднее за 3 квартала после > среднего до)
    horizon = cfg["backtest"]["horizon_years"]
    horizon_q = horizon * QUARTERS_PER_YEAR
    confirmed, unconfirmed = [], []
    for tid, s in ranked_back:
        series = topics[tid]["series"]
        before = float(series[max(0, cut_idx - qmin - 8): cut_idx - qmin + 1].mean()) if cut_idx - qmin > 0 else 0.0
        after = float(series[cut_idx - qmin + 1: min(len(series), cut_idx - qmin + 1 + horizon_q)].mean())
        ok = after > before * 1.2  # рост ≥ 20% после cutoff
        (confirmed if ok else unconfirmed).append({"topic_id": tid, "label": s["label"], "score": s["score"], "before": before, "after": after})

    precision = len(confirmed) / k if k else 0.0
    # recall@k: доля всех «выросших» тем, попавших в топ-k (приближение)
    all_grown = [tid for tid, s in scores_back.items() if True]  # placeholder
    # правильнее: доля выросших тем, которые в топ-k, от всех выросших
    grown_all = 0
    for tid, s in scores_back.items():
        series = topics[tid]["series"]
        before = float(series[max(0, cut_idx - qmin - 8): cut_idx - qmin + 1].mean()) if cut_idx - qmin > 0 else 0.0
        after = float(series[cut_idx - qmin + 1: min(len(series), cut_idx - qmin + 1 + horizon_q)].mean())
        if after > before * 1.2:
            grown_all += 1
    recall = len(confirmed) / grown_all if grown_all else 0.0
    logger.info("Бэктест precision@%d=%.2f, recall@%d=%.2f (выросло всего: %d)",
                k, precision, k, recall, grown_all)

    # --- Калибровка порога по бэктесту (§7): порог, максимизирующий F1 на подтверждённых ---
    calibrated_threshold = None
    if cfg["backtest"].get("calibrate", False):
        # все темы с score на конец 2022 + метка подтверждения
        labels = {}
        for tid, s in scores_back.items():
            series = topics[tid]["series"]
            before = float(series[max(0, cut_idx - qmin - 8): cut_idx - qmin + 1].mean()) if cut_idx - qmin > 0 else 0.0
            after = float(series[cut_idx - qmin + 1: min(len(series), cut_idx - qmin + 1 + horizon_q)].mean())
            labels[tid] = 1 if after > before * 1.2 else 0
        # сетка порогов по фактическим score
        scores_vals = sorted({round(s["score"], 4) for s in scores_back.values()})
        best_f1, best_thr = -1, None
        for thr in scores_vals:
            tp = sum(1 for tid, s in scores_back.items() if s["score"] >= thr and labels[tid] == 1)
            fp = sum(1 for tid, s in scores_back.items() if s["score"] >= thr and labels[tid] == 0)
            fn = sum(1 for tid, s in scores_back.items() if s["score"] < thr and labels[tid] == 1)
            f1 = (2 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
            if f1 > best_f1:
                best_f1, best_thr = f1, thr
        calibrated_threshold = best_thr
        logger.info("Калибровка порога по бэктесту: лучший порог=%.4f (F1=%.3f)",
                    best_thr if best_thr is not None else -1, best_f1)

    # --- Итоговый top_trends.json ---
    ranked_all = sorted(scores_all.items(), key=lambda x: -x[1]["score"])
    threshold = cfg["score"]["threshold"]
    if cfg["backtest"].get("calibrate", False) and calibrated_threshold is not None:
        threshold = calibrated_threshold
        logger.info("Порог заменён калиброванным: %.4f (вместо %.4f)", calibrated_threshold, cfg["score"]["threshold"])

    doc_df = None
    doc_path = PROJECT_ROOT / cfg["data"].get("doc_topics", "")
    if doc_path.exists():
        doc_df = pd.read_parquet(doc_path)

    trends_out = []
    for tid, s in ranked_all:
        if s["score"] >= threshold:
            # evidence: у keyword-тем (отрицательный id) — из keyword-детекции, иначе из doc_topics
            ev = s.get("evidence", []) or build_evidence(doc_df, tid)
            trends_out.append({
                "topic_id": tid,
                "label": s["label"],
                "top_words": s.get("top_words", []),
                "score": s["score"],
                "components": s["components"],
                "size": s["size"],
                "evidence": ev,
            })

    out = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "params": {
            "alpha": cfg["score"]["alpha"], "beta": cfg["score"]["beta"],
            "gamma": cfg["score"]["gamma"], "delta_t": cfg["score"]["delta_t"],
            "novelty_window": cfg["score"]["novelty_window"],
            "min_emergence_year": min_em_year,
            "threshold": threshold,
            "filters": cfg["filters"],
        },
        "n_topics_scored": len(kept),
        "n_trends_above_threshold": len(trends_out),
        "trends": trends_out,
    }
    write_json(PROJECT_ROOT / cfg["output"]["trends"], out)

    # --- Отчёт бэктеста ---
    backtest_out = {
        "cutoff": str(cutoff.date()),
        "top_k": k,
        "precision_at_k": precision,
        "recall_at_k": recall,
        "n_grown_total": grown_all,
        "confirmed": confirmed,
        "unconfirmed": unconfirmed,
    }
    write_json(PROJECT_ROOT / cfg["output"]["backtest"], backtest_out)

    # --- Сводный отчёт ---
    report = {
        "n_topics_input": len(topics_in),
        "n_topics_scored": len(kept),
        "n_trends_above_threshold": len(trends_out),
        "top5_by_score": [{"topic_id": t[0], "label": t[1]["label"], "score": round(t[1]["score"], 3)} for t in ranked_all[:5]],
        "backtest": {k_: v_ for k_, v_ in backtest_out.items() if k_ in ("precision_at_k", "recall_at_k", "n_grown_total")},
    }
    write_json(PROJECT_ROOT / cfg["output"]["report"], report)


if __name__ == "__main__":
    main()
