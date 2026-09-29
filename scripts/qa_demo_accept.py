#!/usr/bin/env python3
"""qa_demo_accept.py — приёмка ДЕМО (блокер аудита 27.09): 6 запросов областей →
webapp/app.py → ТОП-15 вывода сервиса → покрытие ≥11/16-17 + мусор ≤3 в топ-15.

Меряет ИМЕННО вывод демо (api_query), а не batch-файлы протокола (eval_stage9.py).
Плюс 2 контрольных запроса вне областей (информационно, без критерия) и печать
полных топ-15 для ручного осмотра «мусора вне GARBAGE_RE» (regex заморожен — НЕ правим).

Запуск (ДО старта ночи — смоук; и ночью — приёмка):
  .venv/bin/python scripts/qa_demo_accept.py [--cov 11] [--garb 3]
Выход: таблица + results/qa_demo_accept_report.json (exit 0 приёмка / 1 провал).
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "webapp"))

from eval_stage9 import load_oracles            # тот же загрузчик оракулов, что и batch
from rank_directions_ngi import GARBAGE_RE      # канон-regex мусора, один источник

QUERIES_DIR = ROOT / "results" / "qa_areas9"    # запросы = те же, что в batch-прогоне №9
REPORT = ROOT / "results" / "qa_demo_accept_report.json"
# контроль вне областей: q4-похожий (должен быть пуст/точен) + золотой СП-смоук
CONTROL = [
    ("control_offtopic", "Квантовые сенсоры и квантовая метрология"),
    ("control_golden_sp", "сверхпроводимость магнитные системы"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cov", type=int, default=11, help="мин. покрытие топ-15 (автор 27.09: 11)")
    ap.add_argument("--garb", type=int, default=3, help="макс. мусора в топ-15 (этап B)")
    a = ap.parse_args()

    print("Загрузка демо (webapp/app.py)…", flush=True)
    t0 = time.time()
    import app as webapp                        # noqa: E402  (data/ читаются при импорте)
    print(f"  демо загружено за {time.time()-t0:.1f}с, режим ретривала ниже", flush=True)

    oracles = load_oracles()
    # запросы областей — из run-файлов №9 (батч и демо меряются на ОДНОМ тексте)
    area_query = {}
    for p in sorted(QUERIES_DIR.glob("*.json")):
        area_query[p.stem] = json.loads(p.read_text())["query"]

    results, allpass = {}, True
    print(f"\n| область | запрос | топ-15 покрытие (need {a.cov}) | мусор (≤{a.garb}) | вердикт |")
    print("|---|---|---|---|---|")
    for slug, orc in oracles.items():
        q = area_query.get(slug)
        if not q:
            print(f"| {slug} | ⏳ нет запроса в qa_areas9/ | | | |")
            allpass = False
            continue
        r = webapp.api_query(q)
        rows = r["topics"][:15]
        good = set()
        for t in orc["targets"]:
            good |= {int(x) for x in t["allowed"]}
        ids15 = [int(x["tid"]) for x in rows]
        # M13 (фикс 28.09 01:0x, канон = eval_stage9): поцелево — цель покрыта,
        # если ЛЮБАЯ её allowed-тема в ids15 (раньше было good&ids15 — баг P0)
        cov = sum(1 for t in orc["targets"]
                  if set(ids15) & {int(x) for x in t["allowed"]})
        garb = sum(1 for x in rows if int(x["tid"]) not in good
                   and GARBAGE_RE.search(str(x["name"])))
        ok = cov >= a.cov and garb <= a.garb
        allpass &= ok
        results[slug] = {
            "query": q, "coverage": cov, "need": a.cov, "garbage": garb,
            "mode": r["retrieval"].get("model"), "ms": r["retrieval"].get("ms"),
            "top15": [{"tid": int(x["tid"]), "name": str(x["name"]),
                       "screen": round(float(x.get("screen", 0)), 4)} for x in rows],
            "missing": [t.get("n") for t in orc["targets"]
                        if not (set(ids15) & {int(x) for x in t["allowed"]})],
            "pass": ok,
        }
        print(f"| {slug} | {q[:34]} | {cov}/{a.cov} | {garb} | {'✅' if ok else '❌'} |")
        print(f"  топ-15: " + " | ".join(str(x["name"])[:38] for x in rows))

    # контроль вне областей — информационно (осмотр мусора вне regex + поведение сервиса)
    ctrl = {}
    for cid, q in CONTROL:
        r = webapp.api_query(q)
        ctrl[cid] = {"query": q,
                     "top15": [str(x["name"]) for x in r["topics"][:15]]}
        print(f"\n[control] {q}:")
        print("  " + " | ".join(ctrl[cid]["top15"]))

    verdict = "ПРИНЯТО ✅" if allpass else "НЕ ПРИНЯТО ❌"
    print(f"\nДЕМО-ПРИЁМКА: {verdict} "
          f"(критерий: каждая из 6 ≥{a.cov}/16-17 в топ-15, мусор ≤{a.garb})")
    REPORT.write_text(json.dumps({
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "cov": a.cov, "garb": a.garb,
        "areas": results, "control": ctrl, "accept": allpass,
    }, ensure_ascii=False, indent=1))
    print(f"Отчёт: {REPORT}")
    return 0 if allpass else 1


if __name__ == "__main__":
    sys.exit(main())
