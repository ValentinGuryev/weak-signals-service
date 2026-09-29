#!/usr/bin/env python3
"""Cross-citation конкурентов: SNSPD vs TES vs InGaAs-SPAD (кейс 006).

Пары: SNSPD↔TES, SNSPD↔SPAD, TES↔SPAD.
Для каждой: A→B (доля ссылок работ A на корпус B), B→A, мосты (работы в обоих корпусах).
Калибровка по METHODOLOGY S3-таблице (изоляция/связанные/доминанта/новичок).
Выход: results/case_signals/s3_cross_competitor_snspd.json
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OA = PROJECT_ROOT / "data" / "raw" / "openalex"
OUT = PROJECT_ROOT / "results" / "case_signals" / "s3_cross_competitor_snspd.json"

# корпуса + refs
CORPORA = {
    "SNSPD": (json.loads((OA / "snspd_corpus.json").read_text(encoding="utf-8")),
              json.loads((OA / "snspd_full.json").read_text(encoding="utf-8"))),
    "TES": (json.loads((OA / "tes_corpus.json").read_text(encoding="utf-8")),
            json.loads((OA / "tes_refs.json").read_text(encoding="utf-8"))),
    "SPAD": (json.loads((OA / "spad_corpus.json").read_text(encoding="utf-8")),
             json.loads((OA / "spad_refs.json").read_text(encoding="utf-8"))),
}

# id-множества корпусов
IDS = {k: {w["id"] for w in corp} for k, (corp, _) in CORPORA.items()}


def cross(a: str, b: str) -> dict:
    """A→B: сколько ссылок работ A указывают на корпус B."""
    _, refs_a = CORPORA[a]
    _, refs_b = CORPORA[b]
    ids_b = IDS[b]
    # у refs_a ключи = id работы A
    a_total = 0
    a_to_b = 0
    for wid, rlist in refs_a.items():
        if not rlist:
            continue
        a_total += len(rlist)
        for r in rlist:
            if r in ids_b:
                a_to_b += 1
    return a_total, a_to_b


def main() -> None:
    pairs = [("SNSPD", "TES"), ("SNSPD", "SPAD"), ("TES", "SPAD")]
    results = []
    for a, b in pairs:
        a_total, a_to_b = cross(a, b)
        b_total, b_to_a = cross(b, a)
        # мосты: работы в обоих корпусах
        bridges = IDS[a] & IDS[b]
        pct_ab = 100.0 * a_to_b / a_total if a_total else 0
        pct_ba = 100.0 * b_to_a / b_total if b_total else 0
        # вердикт по калибровке
        if pct_ab < 1 and pct_ba < 1 and len(bridges) == 0:
            verdict = "ИЗОЛЯЦИЯ (равные конкуренты, разные сообщества)"
        elif pct_ab < 1 and pct_ba < 1:
            verdict = "слабая изоляция (но есть мосты)"
        elif 1 <= max(pct_ab, pct_ba) <= 7 and min(pct_ab, pct_ba) < 1:
            verdict = "НОВИЧОК vs СТАНДАРТ (асимметрия)"
        elif max(pct_ab, pct_ba) > 8 and min(pct_ab, pct_ba) < 2:
            verdict = "ДОМИНАНТА vs ВАРИАЦИЯ (асимметрия)"
        else:
            verdict = "СВЯЗАННЫЕ (одно сообщество)"
        r = {
            "pair": f"{a} vs {b}",
            f"{a}_to_{b}": f"{a_to_b}/{a_total} ({pct_ab:.2f}%)",
            f"{b}_to_{a}": f"{b_to_a}/{b_total} ({pct_ba:.2f}%)",
            "bridges": len(bridges),
            "bridges_examples": list(bridges)[:3],
            "verdict": verdict,
        }
        results.append(r)
        print(f"\n=== {a} vs {b} ===")
        print(f"  {a}→{b}: {a_to_b}/{a_total} ({pct_ab:.2f}%)")
        print(f"  {b}→{a}: {b_to_a}/{b_total} ({pct_ba:.2f}%)")
        print(f"  мосты: {len(bridges)}")
        print(f"  ВЕРДИКТ: {verdict}")

    # размеры корпусов
    sizes = {k: len(v) for k, (v, _) in CORPORA.items()}
    out = {"question": "Как конкуренты SNSPD (TES, InGaAs-SPAD) цитируют друг друга?",
           "corpus_sizes": sizes, "pairs": results,
           "date": "2026-09-03"}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT}")


if __name__ == "__main__":
    main()
