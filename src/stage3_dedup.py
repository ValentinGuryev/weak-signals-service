"""Этап 3.5: Дедупликация трендов — объединение «семейств» под-тем в один тренд.

Проблема (обнаружена 2026-08-17 при экспертной валидации):
BERTopic (nr_topics=N) фрагментирует одну большую область на несколько кластеров,
каждый получает отдельный Score → в списке «трендов» появляются содержательные
дубликаты (семейства): например, термоэлектрики разбиты на #10/#16/#13.

Что делает модуль:
1. Исключает мусор: тему-«outlier» (tid=-1), пустые label'ы.
2. Строит «семейства»: связные компоненты по сильной близости (Jaccard top-слов > порог
   ИЛИ пересечение документов > порог).
3. Внутри семейства выбирает «родителя» (максимальный Score) и помечает остальных
   как «дубликаты».
4. Агрегирует: суммарный Score (взвешенный по размеру), объединённые top-слова/статьи.

Вход: results/top_trends.json (тренды + Score).
Выход: results/top_trends_deduped.json + отчёт results/dedup_report.json.

Принцип (внутренний контракт): НЕ удаляем данные, не меняем формулу — только агрегируем
и помечаем дубликаты для прозрачности.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()


# --- семантическая близость ---

def words_of(trend: dict[str, Any]) -> set[str]:
    """Множество слов тренда (top_words, без стемминг-артефактов _N и служебных)."""
    tid = trend.get("topic_id", 0)
    if tid < 0:
        # keyword-тема: слова из label (KW: name)
        return set(trend.get("label", "").replace("KW: ", "").split())
    out = set()
    for w in trend.get("top_words", []):
        w = w.strip("_").lower()
        if w and not w.isdigit() and len(w) > 1:
            out.add(w)
    return out


def jaccard(a: set[str], b: set[str]) -> float:
    u = a | b
    if not u:
        return 0.0
    return len(a & b) / len(u)


def doc_overlap(evidence_a: list[str], evidence_b: list[str]) -> float:
    """Доля общих статей от меньшего списка."""
    if not evidence_a or not evidence_b:
        return 0.0
    a, b = set(evidence_a), set(evidence_b)
    inter = a & b
    return len(inter) / min(len(a), len(b))


# --- семейства ---

def build_families(
    trends: list[dict[str, Any]],
    word_threshold: float = 0.30,
    doc_threshold: float = 0.30,
) -> list[list[int]]:
    """Связные компоненты по сильной близости. Возвращает списки индексов трендов."""
    n = len(trends)
    words = [words_of(t) for t in trends]
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(n):
        for j in range(i + 1, n):
            # сила связи: Jaccard top-слов ИЛИ пересечение документов
            jac = jaccard(words[i], words[j])
            doc = doc_overlap(trends[i].get("evidence", []), trends[j].get("evidence", []))
            if jac >= word_threshold or doc >= doc_threshold:
                union(i, j)

    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return [g for g in groups.values() if len(g) > 1]


def aggregate(trends: list[dict[str, Any]], members: list[int]) -> dict[str, Any]:
    """Агрегировать семейство в один тренд (родитель = max Score, остальные — дубликаты)."""
    parent_idx = max(members, key=lambda i: trends[i].get("score", 0.0))
    parent = trends[parent_idx]
    others = [i for i in members if i != parent_idx]

    # суммарный Score (взвешенный по размеру)
    sizes = [trends[i].get("size", 0) for i in members]
    total_size = sum(sizes)
    weights = [s / total_size for s in sizes] if total_size else [1 / len(members)] * len(members)
    agg_score = sum(trends[i].get("score", 0.0) * w for i, w in zip(members, weights))

    # объединённые top-слова (уникальные, сохраняя порядок родителя)
    merged_words: list[str] = []
    for i in [parent_idx] + others:
        for w in trends[i].get("top_words", []):
            if w not in merged_words:
                merged_words.append(w)

    # объединённые статьи (уникальные)
    merged_ev: list[str] = []
    for i in [parent_idx] + others:
        for e in trends[i].get("evidence", []):
            if e not in merged_ev:
                merged_ev.append(e)

    return {
        "topic_id": parent["topic_id"],
        "label": parent["label"],
        "top_words": merged_words,
        "score": float(agg_score),
        "components": parent.get("components", {}),
        "size": total_size,
        "evidence": merged_ev,
        "family": {
            "member_topic_ids": [trends[i]["topic_id"] for i in members],
            "member_labels": [trends[i]["label"] for i in members],
            "n_members": len(members),
            "parent_topic_id": parent["topic_id"],
            "duplicates": [trends[i]["topic_id"] for i in others],
        },
    }


def dedup(
    trends: list[dict[str, Any]],
    word_threshold: float = 0.30,
    doc_threshold: float = 0.30,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Дедупликация. Возвращает (чистые тренды, отчёт)."""
    # 1. исключить мусор: outlier, пустые
    clean, removed = [], []
    for t in trends:
        tid = t.get("topic_id", 0)
        label = t.get("label", "")
        if tid == -1 or label.lower() == "outlier" or not label:
            removed.append({"topic_id": tid, "label": label, "reason": "outlier/пустой"})
        else:
            clean.append(t)
    logger.info("Исключено мусора: %d (outlier/пустые)", len(removed))

    # 2. семейства
    families = build_families(clean, word_threshold, doc_threshold)
    logger.info("Семейств (связных компонент >1): %d", len(families))

    # 3. агрегация
    member_flags = set()
    out: list[dict[str, Any]] = []
    for fam in families:
        agg = aggregate(clean, fam)
        out.append(agg)
        for m in fam:
            member_flags.add(id(clean[m]))
    for i, t in enumerate(clean):
        if id(t) not in member_flags:
            out.append(t)

    # 4. сортировка по Score
    out.sort(key=lambda x: -x.get("score", 0.0))

    report = {
        "n_input": len(trends),
        "n_removed_misc": len(removed),
        "n_families": len(families),
        "n_family_members": sum(len(f) for f in families),
        "n_output": len(out),
        "removed_misc": removed,
        "families": [
            {
                "parent": clean[f[0]]["label"],
                "members": [clean[i]["label"] for i in f],
            }
            for f in families
        ],
    }
    return out, report


def main() -> None:
    ap = argparse.ArgumentParser(description="Дедупликация трендов")
    ap.add_argument("--input", default="results/top_trends/top_trends_full.json")
    ap.add_argument("--output", default="results/top_trends/top_trends_deduped.json")
    ap.add_argument("--word-threshold", type=float, default=0.30)
    ap.add_argument("--doc-threshold", type=float, default=0.30)
    args = ap.parse_args()

    in_path = PROJECT_ROOT / args.input
    if not in_path.exists():
        raise FileNotFoundError(f"Тренды не найдены: {in_path}")
    data = json.loads(in_path.read_text(encoding="utf-8"))
    trends = data["trends"]

    out, report = dedup(trends, args.word_threshold, args.doc_threshold)

    result = {
        "generated_at": data.get("generated_at"),
        "params": data.get("params", {}),
        "dedup_params": {
            "word_threshold": args.word_threshold,
            "doc_threshold": args.doc_threshold,
        },
        "n_input": len(trends),
        "n_output": len(out),
        "trends": out,
    }
    out_path = PROJECT_ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Записано: %s (%d трендов)", out_path, len(out))

    rep_path = out_path.with_name("dedup_report.json")
    rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Отчёт: %s", rep_path)


if __name__ == "__main__":
    main()
