#!/usr/bin/env python3
"""l0_diagnose.py — диагноз L0 после вердикта addendum №9 (27→28.09, ночь).

Для КАЖДОЙ непокрытой цели каждой области находит место отсечения:
  RETRIEVAL — темы нет в directions (ретривал не выдал);
  WINDOW    — в directions/probe, но НЕ в hybrid-окне (top-100 по probe-score ∪ top-K child_rel);
  WIN130    — в окне, но retr_rank > 130 → отсечён финальным win-фильтром;
  SCORE50   — дошёл до финального скоринга, но место 51..130;
  SCORE15   — в топ-50, но место 16..50 (этап B).
Плюс: где цель была в addendum №8 (qa_areas, topk500) — что изменил №9.

Выход: таблица в stdout + results/runtime/l0_diagnosis_20260928.md
Запуск: .venv/bin/python scripts/l0_diagnose.py
Диагностика — разбор данных; параметры №10 выбираются СЛЕДУЮЩИМ addendum ДО прогона.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from eval_stage9 import load_oracles  # noqa: E402

OUT = ROOT / "results" / "runtime" / "l0_diagnosis_20260928.md"


def load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def main() -> int:
    oracles = load_oracles()
    lines = ["# L0-диагноз (после вердикта addendum №9), ночь 27→28.09\n"]
    print(f"{'область':11s} {'цель':5s} {'№8 поз':7s} {'retr9':6s} {'окно':4s} "
          f"{'fin':5s} {'итог':10s}")
    for slug, orc in oracles.items():
        run9 = load(ROOT / "results" / "qa_areas9" / f"{slug}.json")
        run8 = load(ROOT / "results" / "qa_areas" / f"{slug}.json")
        probe = load(Path(f"/tmp/S9_{slug}_probe_ngi_full.json"))
        hyb = load(Path(f"/tmp/S9_{slug}_hyb.json"))
        fin = load(Path(f"/tmp/S9_{slug}_fin_ngi_full.json"))
        if not (run9 and probe and hyb and fin):
            print(f"{slug:11s} ⏳ нет файлов (probe/hyb/fin) — пропуск")
            continue
        dirs9 = {int(d["topic_id"]): i + 1 for i, d in enumerate(run9["directions"])}
        dirs8 = ({int(d["topic_id"]): i + 1 for i, d in enumerate(run8["directions"])}
                 if run8 else {})
        pr = {int(r["topic_id"]): r for r in probe["all"]}
        pr_rank = {int(r["topic_id"]): i + 1
                   for i, r in enumerate(sorted(probe["all"],
                                                key=lambda x: -float(x["screen"])))}
        # окно №9 = retr_rank ≤100 (win100) ∪ extras top-K по child_rel
        hw = hyb.get("hybrid_window", {})
        win = ({aid for aid, pos in dirs9.items() if pos <= int(hw.get("win100", 100))}
               | {int(x) for x in hw.get("extra_tids", [])})
        fin_rows = fin.get("all") or []
        fin_pos = {int(r["topic_id"]): i + 1 for i, r in enumerate(fin_rows)}
        top50 = {int(r["topic_id"]) for r in (fin.get("top") or fin_rows)[:50]}
        top15 = {int(r["topic_id"]) for r in (fin.get("top") or fin_rows)[:15]}

        lines.append(f"\n## {slug}")
        tally = {"RETRIEVAL": 0, "WINDOW": 0, "WIN130": 0, "SCORE50": 0,
                 "SCORE15": 0, "COVERED15": 0}
        for t in orc["targets"]:
            allowed = [int(x) for x in t["allowed"]]
            if set(allowed) & top15:
                tally["COVERED15"] += 1
                continue
            # лучший allowed = тот, что продвинулся дальше по конвейеру
            def stage(aid: int) -> tuple:
                if aid in top50:
                    s = 4
                elif aid in fin_pos:
                    s = 3
                elif aid in win:
                    s = 2
                elif aid in dirs9:
                    s = 1
                else:
                    s = 0
                return (s, -fin_pos.get(aid, 10**6))
            best = max(allowed, key=stage)
            s = stage(best)[0]
            reason = {0: "RETRIEVAL", 1: "WINDOW", 2: "WIN130",
                      3: "SCORE50", 4: "SCORE15"}[s]
            tally[reason] += 1
            r9 = dirs9.get(best, "—")
            r8 = dirs8.get(best, "—")
            pp = pr_rank.get(best, "—")
            fp = fin_pos.get(best, "—")
            print(f"{slug:11s} {str(t.get('n'))[:44]:46s} №8={r8:<5} retr9={r9:<5} "
                  f"probe={pp:<4} окно={'✔' if best in win else '✘'} "
                  f"fin={fp:<4} → {reason}")
            lines.append(f"- `{str(t.get('n'))[:60]}` best-T{best}: №8-ранг={r8}, "
                         f"№9-retr_rank={r9}, probe-ранг={pp}, "
                         f"в_окне={'да' if best in win else 'нет'}, "
                         f"fin-позиция={fp} → **{reason}**")
        ok50 = sum(1 for t in orc["targets"]
                   if {int(x) for x in t["allowed"]} & top50)
        lines.append(f"\nПокрытие топ-50: {ok50}/{orc['need']}. "
                     f"Счётчик таргетов: {tally}")
        print(f"  => {slug}: {ok50}/{orc['need']}, таргеты: {tally}")

    OUT.write_text("\n".join(lines))
    print(f"\nОтчёт: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
