#!/usr/bin/env python3
"""QA-скорер v2: покрытие целей ТОЛЬКО по topic_id из ЗАМОРОЖЕННОГО оракула.

Критерий (решение автора 2026-09-24): 12 из 16 = 75% (Tier A+B, results/qa_ceiling_audit.md).
Оракул: results/qa_allowed_sets.json — заморожен ДО правок ретривала;
sha256 зафиксирован в methodology/QA_RETRIEVAL_PLAN_2026-09-24.md §6, шаг 1.

Почему v2 (аудит 24.09, фиксы A.2/A.3):
  - v1 матчил regex по BLOB темы → ложные «да» («privacy» в Big Data and Digital
    Economy, «interpret» в Medical Research) и невзятые эквиваленты (T10400,
    T13851 были в топ-50 выдачи, но не засчитывались);
  - v1: need = int(16*0.8+0.999) = 13 при критерии автора 12/16 → тихий FAIL
    на честных 12/16;
  - blob читать ЗАПРЕЩЕНО ещё и потому, что И2 (alias-словарь) дописывает слова
    в blob — скорер «починил» бы оракул самоисполняющимся 12/16 (аудит A.2).

Правило покрытия: цель №N покрыта, ЕСЛИ ЛЮБАЯ тема из allowed[N] присутствует
среди topic_id выдачи (run.json → directions[].topic_id).
"""
import argparse
import hashlib
import json
from pathlib import Path

ORACLE = Path("results/qa_allowed_sets.json")
NEED = 12      # фиксировано решением автора (НЕ 80%/13!)
TOTAL = 16


def main():
    ap = argparse.ArgumentParser(description="QA scorer v2 (topic_id only, 12/16)")
    ap.add_argument("--run", required=True, help="JSON выдачи oa_run_query (--json)")
    ap.add_argument("--oracle", default=str(ORACLE), help="путь к allowed-sets")
    ap.add_argument("--verbose", action="store_true", help="показать все выданные темы")
    args = ap.parse_args()

    # --- оракул (проверки целостности) ---
    raw = Path(args.oracle).read_bytes()
    oracle = json.loads(raw)
    sha = hashlib.sha256(raw).hexdigest()
    targets = {int(t["n"]): t for t in oracle["targets"]}
    assert len(targets) == 12, f"в оракуле {len(targets)} in-scope целей, ожидалось 12"
    assert oracle["criterion"]["covered_needed"] == NEED
    oos = {int(t["n"]) for t in oracle.get("out_of_scope", [])}
    bonus = {int(t["n"]) for t in oracle.get("bonus", [])}
    assert len(targets) + len(oos) + len(bonus) == TOTAL, "12 in-scope + oos + bonus != 16"

    # --- выдача ---
    run = json.load(open(args.run))
    returned = {}
    for d in run["directions"]:
        returned[int(d["topic_id"])] = d.get("display_name", "")
    ret_ids = set(returned)

    all_allowed = sorted({t for v in targets.values() for t in v["allowed"]})

    print(f"Запрос: «{run['query']}» (match={run['match']}), выдано тем: {len(returned)}")
    print(f"Оракул: {args.oracle} sha256={sha[:16]}… | критерий: {NEED}/{TOTAL} (75%, Tier A+B)")

    covered = 0
    hits = {}
    miss_allowed = set()
    rows = []
    for n in sorted(targets):
        t = targets[n]
        found = next((tid for tid in t["allowed"] if tid in ret_ids), None)
        if found is not None:
            covered += 1
            mark = "✅"
            hit = [found, returned[found], "allowed"]
        else:
            mark = "❌"
            hit = ["-", "-", "-"]
            miss_allowed.update(t["allowed"])
        hits[str(n)] = [mark, hit]
        rows.append((n, mark, t["tier"], t["tech"], hit))
        tier = t["tier"]
        print(f"{mark} #{n:<3} [Tier {tier}] {t['tech'][:58]:<60} <- "
              + (f"T{hit[0]} «{str(hit[1])[:44]}»" if found else
                 "нет allowed-тем в выдаче: " + ",".join(f"T{x}" for x in t["allowed"])))

    # --- итог ---
    pct = 100.0 * covered / TOTAL
    verdict = "PASS ✅" if covered >= NEED else "FAIL ❌"
    nA = sum(1 for t in targets.values() if t["tier"] == "A")
    nB = len(targets) - nA
    covA = sum(1 for n, m, tier, *_ in rows if tier == "A" and m == "✅")
    covB = covered - covA
    print(f"\nПОКРЫТИЕ: {covered}/{TOTAL} = {pct:.0f}% (нужно ≥{NEED} = 75%) -> {verdict}")
    print(f"  Tier A: {covA}/{nA}   Tier B: {covB}/{nB}")
    print(f"  out-of-scope (не считаются): {sorted(oos)} | bonus: {sorted(bonus)} (не в 12)")
    print(f"  уникальных allowed-тем в валидном множестве: {len(all_allowed)} (R-NEW-5); "
          f"не найдено {len(miss_allowed & set(all_allowed))}: "
          + ",".join(f"T{x}" for x in sorted(miss_allowed & set(all_allowed))))

    if args.verbose:
        print("\n--- все выданные темы ---")
        for tid, name in sorted(returned.items()):
            tag = "★allowed" if tid in set(all_allowed) else ""
            print(f"  T{tid:<6} {name} {tag}")

    out = Path(args.run).with_suffix(".score.json")
    prev = None
    if out.exists():
        try:
            prev = json.loads(out.read_text()).get("covered")
        except Exception:
            prev = None
    out.write_text(json.dumps({
        "scorer": "v2-topic_id-oracle",
        "oracle": args.oracle,
        "oracle_sha256": sha,
        "criterion": f"{NEED}/{TOTAL} (75%, Tier A+B)",
        "run": args.run, "query": run["query"], "match": run["match"],
        "returned": len(returned), "covered": covered, "total": TOTAL,
        "pct": pct, "need": NEED, "pass": covered >= NEED,
        "tier_A": f"{covA}/{nA}", "tier_B": f"{covB}/{nB}",
        "out_of_scope": sorted(oos), "bonus": sorted(bonus),
        "unique_allowed": len(all_allowed),
        "missing_allowed": sorted(miss_allowed & set(all_allowed)),
        "prev_score_v1": prev,
        "hits": hits,
    }, ensure_ascii=False, indent=1))
    print(f"Отчёт: {out}" + (f" (v1 был: {prev}/16)" if prev is not None else ""))


if __name__ == "__main__":
    main()
