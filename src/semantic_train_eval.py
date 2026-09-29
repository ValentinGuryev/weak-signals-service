#!/usr/bin/env python3
"""Отладка классификатора S2 v2 на контрастных пулах (fund=OpenAlex≤2005, appl=SNF-производство).

Различие от v1: классифицируем АБЗАЦЫ (не абстракты целиком).
Для фундаментального пула — абзацы абстрактов OpenAlex.
Для прикладного пула — абзацы полных текстов SNF (с производственной лексикой).

Метрика: на уровне абзацев — сколько «eng» vs «eff» в каждом пуле.
Ожидание: appl-пул → много eng, fund-пул → много eff/neu.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from semantic_shift_v2 import classify_paragraph, clean_text, split_paragraphs

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN = PROJECT_ROOT / "data" / "raw" / "openalex" / "ibad_semantic_train.json"
OUT = PROJECT_ROOT / "results" / "case_signals" / "semantic_v2_train_eval.json"


def main() -> None:
    data = json.loads(TRAIN.read_text(encoding="utf-8"))
    fund = data["fund_works"]
    appl = data["appl_snf"]
    print(f"Пул fundamental (OpenAlex≤2005): {len(fund)} | Пул applied (SNF-prod): {len(appl)}")

    # Абзацы
    def collect(text: str) -> list[str]:
        return split_paragraphs(clean_text(text))

    fund_paras = [p for w in fund for p in collect(w.get("abstract") or "")]
    appl_paras = [p for w in appl for p in collect(w.get("text") or "")]

    print(f"\nАбзацев: fund={len(fund_paras)}, appl={len(appl_paras)}")

    def dist(paras):
        c = Counter(classify_paragraph(p) for p in paras)
        n = len(paras)
        return {k: (v, 100 * v / n if n else 0) for k, v in c.items()}, n

    fd, fn = dist(fund_paras)
    ad, an = dist(appl_paras)
    print(f"\n{'пул':<8} {'n':>5} {'eng%':>7} {'eff%':>7} {'neu%':>7}")
    print(f"{'fund':<8} {fn:>5} {fd['eng'][1]:>6.1f}% {fd['eff'][1]:>6.1f}% {fd['neu'][1]:>6.1f}%")
    print(f"{'appl':<8} {an:>5} {ad['eng'][1]:>6.1f}% {ad['eff'][1]:>6.1f}% {ad['neu'][1]:>6.1f}%")

    # Классификация ДОКУМЕНТА по перевесу абзацев (eng > eff → applied, иначе fundamental)
    def doc_pred(text: str) -> str:
        paras = collect(text)
        if not paras:
            return "no_text"
        c = Counter(classify_paragraph(p) for p in paras)
        return "applied" if c["eng"] > c["eff"] else ("fundamental" if c["eff"] > c["eng"] else "mixed")

    conf = Counter()
    for w in fund:
        conf[("fundamental", doc_pred(w.get("abstract") or ""))] += 1
    for w in appl:
        conf[("applied", doc_pred(w.get("text") or ""))] += 1

    print("\nConfusion (документный уровень):")
    for true in ["fundamental", "applied"]:
        row = {p: conf[(true, p)] for p in ["applied", "fundamental", "mixed", "no_text"]}
        print(f"  {true:<12} → {row}")

    tp = conf[("applied", "applied")]
    fp = conf[("fundamental", "applied")]
    fn_ = conf[("applied", "fundamental")]
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn_) if tp + fn_ else 0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
    print(f"\nApplied: precision={prec:.2f} recall={rec:.2f} F1={f1:.2f}")

    # Примеры: фундаментальные, которые классифицированы как applied (ошибки)
    print("\nОшибки: фундаментальные → applied (примеры):")
    errs = [(w, doc_pred(w.get("abstract") or "")) for w in fund]
    errs = [(w, p) for w, p in errs if p == "applied"]
    errs.sort(key=lambda x: x[0]["cited_by_count"], reverse=True)
    for w, p in errs[:6]:
        print(f"  [{w['year']}] {w['title'][:75]} | цит {w['cited_by_count']}")

    print("\nОшибки: applied(SNF) → fundamental (примеры):")
    errs2 = [(w, doc_pred(w.get("text") or "")) for w in appl]
    errs2 = [(w, p) for w, p in errs2 if p == "fundamental"]
    for w, p in errs2[:6]:
        print(f"  [{w['year']}] {w['name'][:75]}")

    OUT.write_text(json.dumps({
        "paragraph_dist": {"fund": {k: v[0] for k, v in fd.items()},
                           "appl": {k: v[0] for k, v in ad.items()}},
        "confusion": dict(conf),
        "precision_applied": prec, "recall_applied": rec, "f1_applied": f1,
        "n_fund": len(fund), "n_appl": len(appl),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT}")


if __name__ == "__main__":
    main()
