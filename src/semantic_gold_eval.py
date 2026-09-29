#!/usr/bin/env python3
"""Классификатор S2 v2.1: логистическая регрессия на золотом стандарте (IBAD).

Золотой стандарт (data/raw/openalex/ibad_gold_standard.json): 100 абзацев,
размеченных по СМЫСЛУ (не по году): открытие/механизм = fundamental,
производство/масштаб = applied. Метки поставлены по маркерам + ручная проверка.

Метод: TF-IDF на стеммированных токенах → LogisticRegression (sklearn),
CV 5-fold, метрики. Сравнение с rule-based (semantic_shift_v2.classify_paragraph).

Выход: results/case_signals/semantic_v2_gold_eval.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from semantic_shift_v2 import clean_text, split_paragraphs, classify_paragraph

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GOLD = PROJECT_ROOT / "data" / "raw" / "openalex" / "ibad_gold_standard.json"
OUT = PROJECT_ROOT / "results" / "case_signals" / "semantic_v2_gold_eval.json"


def main() -> None:
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    print(f"Золотой стандарт: {len(gold)} абзацев")
    print("  fundamental:", sum(1 for x in gold if x["label"] == "fundamental"))
    print("  applied:", sum(1 for x in gold if x["label"] == "applied"))

    # ---- Rule-based (текущий классификатор) на золотом стандарте ----
    print("\n=== Rule-based (semantic_shift_v2) ===")
    conf = Counter()
    for x in gold:
        pred = "applied" if classify_paragraph(x["text"]) == "eng" else "fundamental"
        conf[(x["label"], pred)] += 1
    tp = conf[("applied", "applied")]
    fp = conf[("fundamental", "applied")]
    fn = conf[("applied", "fundamental")]
    tn = conf[("fundamental", "fundamental")]
    acc = (tp + tn) / len(gold)
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
    print(f"  accuracy={acc:.2f} precision={prec:.2f} recall={rec:.2f} F1={f1:.2f}")
    print(f"  confusion: {dict(conf)}")

    # ---- ML: TF-IDF + LogisticRegression ----
    print("\n=== ML: TF-IDF + LogisticRegression (5-fold CV) ===")
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import cross_val_predict, StratifiedKFold
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

        texts = [x["text"] for x in gold]
        labels = [1 if x["label"] == "applied" else 0 for x in gold]

        vec = TfidfVectorizer(
            token_pattern=r"[A-Za-z][A-Za-z\-']{2,}",
            stop_words="english", ngram_range=(1, 2), max_features=2000)
        X = vec.fit_transform(texts)
        print(f"  фич: {X.shape[1]}")

        clf = LogisticRegression(max_iter=1000, class_weight="balanced")
        cv = StratifiedKFold(5, shuffle=True, random_state=42)
        y_pred = cross_val_predict(clf, X, labels, cv=cv)
        acc = accuracy_score(labels, y_pred)
        prec = precision_score(labels, y_pred)
        rec = recall_score(labels, y_pred)
        f1 = f1_score(labels, y_pred)
        print(f"  accuracy={acc:.2f} precision={prec:.2f} recall={rec:.2f} F1={f1:.2f}")

        # Коэффициенты (топ фич для applied)
        clf.fit(X, labels)
        coefs = sorted(zip(vec.get_feature_names_out(), clf.coef_[0]), key=lambda x: -x[1])
        print("\n  ТОП-15 фич для APPLIED:")
        for w, c in coefs[:15]:
            print(f"    {w:<25} {c:+.3f}")
        print("\n  ТОП-15 фич для FUNDAMENTAL:")
        for w, c in coefs[-15:][::-1]:
            print(f"    {w:<25} {c:+.3f}")

        OUT.write_text(json.dumps({
            "n": len(gold),
            "rule": {"acc": acc, "prec": prec, "rec": rec, "f1": f1, "confusion": dict(conf)},
            "ml": {"acc": acc, "prec": prec, "rec": rec, "f1": f1, "cv": 5,
                   "top_applied": [(w, float(c)) for w, c in coefs[:15]],
                   "top_fund": [(w, float(c)) for w, c in coefs[-15:][::-1]]},
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nСохранено: {OUT}")
    except ImportError as e:
        print(f"  sklearn недоступен: {e}")


if __name__ == "__main__":
    main()
