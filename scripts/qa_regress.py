#!/usr/bin/env python3
"""QA-регресс-сет (шаг 2 плана): стабильность выдачи на НЕСКОЛЬКИХ формулировках.

Один запуск = 5 прогонов одним процессом (LaBSE грузится один раз).
Spill DuckDB — на E: (tmp_duck), НЕ в ./.tmp: урок OOM-падения 24.09 12:40.
  q1  «Защита ИИ» канонический (RU)     — QA-покрытие по оракулу, нужно ≥12/16
  q2  «Защита ИИ» длинный (RU)          — то же
  q3  «Защита ИИ» EN                    — то же
  q4  «Квантовые сенсоры» (посторонний) — PRECISION: покрытие «Защиты ИИ» ≤2/16 (§7.10)
  q5  «сверхпроводимость магнитные системы» — ЗОЛОТОЙ СМОУК (years 2016-2026):
      fusion #1, SC-materials #2, Magnetic Field Sensors #8 (эталон 23.09)

QA-случаи (q1-q4) скорятся scripts/qa_protect_score.py (v2, topic_id-оракул).
Регресс считается ЗЕЛЁНЫМ, если: золотой смоук 3/3 + precision q4 пройден.
Покрытие q1-q3 на baseline МОЖЕТ быть FAIL (до шагов 3-7) — это норма:
сегодняшний прогон фиксирует baseline, а не ворота.

Использование:
  .venv/bin/python scripts/qa_regress.py [--only q1_ru_canonical,q5_golden_smoke]
Выход: results/qa_regress/<id>.json{,.score.json} + results/qa_regress_summary.json
Код возврата: 0 — золотой смоук и precision в норме; 1 — нарушение.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import oa_snapshot as oa  # noqa: E402

LOCAL = ROOT / "data/openalex_derived"
E = Path("/mnt/e/openalex_derived")
OUTDIR = ROOT / "results/qa_regress"
SCORE = ROOT / "scripts/qa_protect_score.py"
NEED_QA = 12          # критерий 12/16 (заморожен в оракуле)
PRECISION_MAX = 2     # §7.10: посторонний запрос — не больше 2/16 «Защиты ИИ»

# --- формулировки (правятся автором; QA-окно 2026 — как прогон 1) ---
CASES = [
    {"id": "q1_ru_canonical", "qa": True,
     "query": "Выдай темы по защите ИИ в 2026 году", "years": (2026, 2026)},
    {"id": "q2_ru_long", "qa": True,
     "query": "Безопасность искусственного интеллекта: защита языковых моделей от атак "
              "и инъекций промптов, приватность данных, регулирование и надёжность ИИ-систем",
     "years": (2026, 2026)},
    {"id": "q3_en", "qa": True,
     "query": "AI security and safety: protecting language models from attacks, prompt "
              "injection defense, privacy-preserving AI, AI governance and regulation, "
              "reliable trustworthy AI",
     "years": (2026, 2026)},
    {"id": "q4_offtopic_quant_sensors", "qa": True, "precision": True,
     "query": "Квантовые сенсоры и квантовая метрология", "years": (2026, 2026)},
    {"id": "q5_golden_smoke", "qa": False,
     "query": "сверхпроводимость магнитные системы", "years": (2016, 2026)},
]

# золотой эталон смоука 23.09 (results/smoke_post_final.json): позиция → подстрока имени
GOLDEN = [(1, "Magnetic confinement fusion"), (2, "Superconducting Materials"),
          (8, "Magnetic Field Sensors")]


def score_qa(run_path: Path) -> dict:
    """Запустить скорер v2 subprocess'ом, вернуть его .score.json."""
    r = subprocess.run([sys.executable, str(SCORE), "--run", str(run_path)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"скорер упал: {r.stderr[-500:]}")
    return json.loads(run_path.with_suffix(".score.json").read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="список id через запятую, напр. q1_ru_canonical,q5_golden_smoke")
    ap.add_argument("--topics", type=int, default=60)
    ap.add_argument("--topk", type=int, default=50)
    ap.add_argument("--mem", default="2GB",
                    help="DuckDB memory_limit (деф 2GB: 4GB ОOMился на q5 в 7.4ГБ-машине)")
    ap.add_argument("--threads", type=int, default=4,
                    help="DuckDB threads (деф 4: меньше пик при spill на E:)")
    ap.add_argument("--gate", default=None,
                    help="И5: доменный гейт (напр. 3,2) вместо regex-маски; без флага — legacy")
    ap.add_argument("--fanout", action="store_true",
                    help="И1 стратегия A: кластеризация top-M + RRF (замороженный конфиг)")
    ap.add_argument("--route", action="store_true",
                    help="§4а: лексический routing → matched(gate+C+t500)/fallback(legacy t60k50)")
    ap.add_argument("--embed-variant", choices=["base", "i2"], default="base",
                    help="вектора matched-профиля: base | i2 (И2 data-driven aliases, шаг 5)")
    args = ap.parse_args()
    gate = [int(x) for x in args.gate.split(",")] if args.gate else None
    fanout_cfg = {"m": 240, "k": 12, "ktop": 25, "rrf_c": 60, "seed": 42} if args.fanout else None
    routing_cfg = {"profiles": {
        "matched": {"gate": [3, 2], "topics": 500, "topk": 500,
                    "vectors": ("topic_vectors_i2.npy" if args.embed_variant == "i2" else None),
                    "fanout": {"m": 240, "k": 12, "ktop": 25, "rrf_c": 60, "seed": 42,
                               "source": "lexicon",
                               "lexicon_path": str(ROOT / "results/qa_facet_lexicon_v1.json")}},
        "fallback": {"gate": None, "topics": 60, "topk": 50, "fanout": None}}} if args.route else None

    only = set(args.only.split(",")) if args.only else None
    OUTDIR.mkdir(parents=True, exist_ok=True)

    P = oa.Paths(local=LOCAL, e=E, staging=Path("/mnt/c/oa_tmp"))
    import duckdb
    # spill ТОЛЬКО на E: (урок 24.09: duckdb_temp_storage в ./.tmp = 20 ГБ + OOM)
    (E / "tmp_duck").mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET threads={args.threads}; SET memory_limit='{args.mem}'")
    con.execute(f"SET temp_directory='{E}/tmp_duck'")

    # summary: дозагружаем существующий и дописываем после КАЖДОГО кейса
    # (падение процесса не должно терять результаты — урок OOM 24.09)
    out = ROOT / "results/qa_regress_summary.json"
    if out.exists():
        try:
            summary = json.loads(out.read_text())
            summary.setdefault("cases", [])
        except Exception:
            summary = None
    else:
        summary = None
    if summary is None:
        summary = {"cases": [], "started": time.strftime("%Y-%m-%d %H:%M:%S")}
    by_id = {r["id"]: r for r in summary["cases"]}

    def flush():
        order = {c["id"]: i for i, c in enumerate(CASES)}
        rows = sorted(by_id.values(), key=lambda r: order.get(r["id"], 99))
        gold = [r for r in rows if "golden" in r]
        prec = [r for r in rows if "precision_ok" in r]
        summary["cases"] = rows
        summary["golden_pass"] = all(r["golden_pass"] for r in gold) if gold else None
        summary["precision_pass"] = all(r["precision_ok"] for r in prec) if prec else None
        summary["duck"] = {"threads": args.threads, "mem": args.mem,
                           "temp_directory": f"{E}/tmp_duck"}
        summary["gate"] = gate
        summary["fanout"] = fanout_cfg
        summary["routing"] = bool(routing_cfg)
        summary["topics"] = args.topics
        summary["topk"] = args.topk
        summary["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        summary["total_sec"] = round(time.time() - t0, 1)
        out.write_text(json.dumps(summary, ensure_ascii=False, indent=1))

    t0 = time.time()

    for c in CASES:
        if only and c["id"] not in only:
            continue
        t1 = time.time()
        print(f"\n=== {c['id']}: «{c['query'][:70]}» years={c['years'][0]}-{c['years'][1]} ===")
        res = oa.query_directions(con, P, c["query"], topk=args.topk,
                                  n_topics=args.topics, match="embed",
                                  years=c["years"], gate_domains=gate,
                                  fanout=fanout_cfg, routing=routing_cfg)
        run_path = OUTDIR / f"{c['id']}.json"
        run_path.write_text(json.dumps(res, ensure_ascii=False, indent=1))
        row = {"id": c["id"], "query": c["query"], "years": list(c["years"]),
               "run": str(run_path.relative_to(ROOT)),
               "n_directions": len(res["directions"]),
               "sec": round(time.time() - t1, 1)}

        if c.get("qa"):
            sc = score_qa(run_path)
            row.update({"covered": sc["covered"], "need": sc["need"],
                        "tier_A": sc["tier_A"], "tier_B": sc["tier_B"],
                        "pass": sc["pass"],
                        "missing_allowed": sc["missing_allowed"]})
            tag = "PASS✅" if sc["pass"] else "FAIL❌"
            print(f"  QA покрытие: {sc['covered']}/{sc['total']} (нужно {sc['need']}) {tag} "
                  f"| A {sc['tier_A']} B {sc['tier_B']} | {row['sec']}с")
            if c.get("precision"):
                ok = sc["covered"] <= PRECISION_MAX
                summary["precision_pass"] = ok
                row["precision_ok"] = ok
                print(f"  PRECISION (посторонний, нужно ≤{PRECISION_MAX}): "
                      f"{sc['covered']}/16 {'OK✅' if ok else 'ПРОВАЛ❌ — мимо кассы'}")
        else:
            names = [d.get("display_name", "") for d in res["directions"]]
            checks = []
            for rank, sub in GOLDEN:
                got = sub.lower() in names[rank - 1].lower() if len(names) >= rank else False
                checks.append({"rank": rank, "expect": sub, "got": names[rank - 1] if len(names) >= rank else None,
                               "ok": bool(got)})
                print(f"  золото #{rank}: {'OK✅' if got else 'СБОЙ❌'} "
                      f"(ожидали «{sub}», got «{names[rank - 1] if len(names) >= rank else '-'}»)")
            row["golden"] = checks
            row["golden_pass"] = all(x["ok"] for x in checks)
            row["top10"] = names[:10]

        summary["cases"].append(row)
        by_id[row["id"]] = row
        flush()  # инкрементально — падение не сотрёт накопленное

    con.close()
    flush()

    # итоговая таблица
    print("\n" + "=" * 78)
    print(f"{'case':<28} {'покрытие':>9} {'нужно':>6} {'A/B':>9} {'статус':>8}")
    for r in summary["cases"]:
        if "covered" in r:
            print(f"{r['id']:<28} {r['covered']:>9} {r['need']:>6} "
                  f"{r['tier_A']}/{r['tier_B']:>3} {'PASS✅' if r['pass'] else 'FAIL❌':>8}")
        else:
            print(f"{r['id']:<28} {'—':>9} {'—':>6} {'—':>9} "
                  f"{('3/3 OK✅' if r.get('golden_pass') else 'СБОЙ❌'):>8}")
    ok = bool(summary.get("golden_pass")) and bool(summary.get("precision_pass"))
    print(f"\nЗолотой смоук: {('OK✅' if summary.get('golden_pass') else 'СБОЙ❌' if summary.get('golden_pass') is False else 'не прогнан')} | "
          f"Precision q4: {('OK✅' if summary.get('precision_pass') else 'ПРОВАЛ❌' if summary.get('precision_pass') is False else 'не прогнан')} | "
          f"итог: {'ЗЕЛЁНЫЙ🟢' if ok else 'КРАСНЫЙ🔴'} | {summary.get('total_sec', '?')}с")
    print(f"Отчёт: {out.relative_to(ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
