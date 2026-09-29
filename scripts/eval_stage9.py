#!/usr/bin/env python3
"""eval_stage9.py — оценка этапа 1 (addendum №9): покрытие топ-50, need=ceil(0.7N),
мусор GARBAGE_RE. Защита — qa_allowed_sets.json, остальные — qa_oracles_6areas_v1.json.
Дополнительно: топ-15 (база этапа 2)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rank_directions_ngi import GARBAGE_RE

ROOT = Path(__file__).resolve().parent.parent

def load_oracles():
    oracles = {}
    pa = json.loads((ROOT / "results/qa_allowed_sets.json").read_text())
    oracles["protect"] = {
        "need": 12, "n": 16,
        "targets": [{"n": t["n"], "allowed": [int(x) for x in t["allowed"]]}
                    for t in pa["targets"]],
    }
    six = json.loads((ROOT / "results/qa_oracles_6areas_v1.json").read_text())
    slug = {"Индустриальный ИИ": "industrial", "Инфраструктура ИИ": "infra",
            "Роботы": "robots", "Финтех": "fintech", "Edge": "edge"}
    for area, d in six["areas"].items():
        oracles[slug[area]] = {
            "need": d["need"], "n": d["n_tech"],
            "targets": [{"n": t["n"], "allowed": [int(x) for x in t["allowed"]]}
                        for t in d["targets"]]}
    return oracles

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="stage9", help="каталог с *_fin_ngi_full.json (stage9/stage10/...)")
    a = ap.parse_args()
    oracles = load_oracles()
    print("| область | топ-50 (need) | мусор50 | топ-15 (need) | мусор15 | не покрыто | вердикт |")
    print("|---|---|---|---|---|---|---|")
    allpass = True
    for slug, orc in oracles.items():
        p = ROOT / f"results/{a.dir}/{slug}_fin_ngi_full.json"
        if not p.exists():
            print(f"| {slug} | ⏳ цепочка не доехала | | | | |")
            allpass = False
            continue
        d = json.loads(p.read_text())
        rows = d.get("rows") or d.get("top")
        good = set()
        for t in orc["targets"]:
            good |= set(t["allowed"])
        ids50 = {int(r["topic_id"]) for r in rows[:50]}
        ids15 = {int(r["topic_id"]) for r in rows[:15]}
        cov = sum(1 for t in orc["targets"] if ids50 & set(t["allowed"]))
        c15 = sum(1 for t in orc["targets"] if ids15 & set(t["allowed"]))
        miss = [t["n"] for t in orc["targets"] if not (ids50 & set(t["allowed"]))]
        garb = sum(1 for r in rows[:50]
                   if int(r["topic_id"]) not in good and GARBAGE_RE.search(r["name"]))
        # критерий этапа B (автор 27.09): мусор ≤3 в ТОП-15 (слоты 15−12)
        garb15 = sum(1 for r in rows[:15]
                     if int(r["topic_id"]) not in good and GARBAGE_RE.search(r["name"]))
        ok = cov >= orc["need"] and garb <= 1
        allpass &= ok
        print(f"| {slug} | {cov}/{orc['need']} | {garb} | {c15}/{orc['need']} | "
              f"{garb15} | {miss or '—'} | {'✅' if ok else '❌'} |")
    print(f"\nЭТАП 1: {'ПРОЙДЕН ✅' if allpass else 'НЕ ПРОЙДЕН ❌'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
