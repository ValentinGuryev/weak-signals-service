#!/usr/bin/env python3
"""qa_two_problems.py — приёмка ДВУХ проблем сессии (план fix_two_problems_plan_20260929):
  K1: фрагмент-имена в топ-15 формы 1 = 0 (по фикс-набору 6 запросов областей №9);
  K2: при WEBAPP_LLM_GATE=1 — 100% показанных карточек llm_valid==1;
  K3: ≥90% показанных карточек имеют problem_ru ≥10 слов.

Флаги окружения выставляются ДО импорта app: карточный режим в конфиге VPS
(CARDS=1, GATE=1, BRIDGE_GATE=1, TAU=0.84) + LLM_GATE=1 (или --no-llm-gate для
сравнения «что было»). Запросы — те же, что в batch/демо-приёмке (qa_areas9).

Запуск: .venv/bin/python scripts/qa_two_problems.py [--no-llm-gate]
Выход: таблица + results/qa_two_problems_report.json (exit 0 = K1..K3 выполнены).
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUERIES_DIR = ROOT / "results" / "qa_areas9"
REPORT = ROOT / "results" / "qa_two_problems_report.json"
# фикс-набор: 6 областей (запросы берутся из qa_areas9, тот же текст, что в №9/приёмке)
SLUGS = ["robots", "fintech", "protect", "edge", "industrial", "infra"]


def looks_like_fragment(name: str) -> bool:
    """K1-эвристика (одна на все запросы): 2-6 слов, первая буква — заглавная/цифра.
    Проверка — автоматика + печать имён для ручного контроля в отчёте."""
    w = name.split()
    if not (2 <= len(w) <= 6):
        return True
    if not re.match(r"^[A-Z0-9«\"'(\[]", name):
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-llm-gate", action="store_true",
                    help="замер без WEBAPP_LLM_GATE (сравнение с baseline)")
    a = ap.parse_args()

    os.environ["WEBAPP_CARDS"] = "1"
    os.environ["WEBAPP_GATE"] = "1"
    os.environ["WEBAPP_BRIDGE_GATE"] = "1"
    os.environ.setdefault("WEBAPP_TAU", "0.84")
    os.environ["WEBAPP_LLM_GATE"] = "0" if a.no_llm_gate else "1"

    sys.path.insert(0, str(ROOT / "webapp"))
    print("Загрузка демо (webapp/app.py)…", flush=True)
    t0 = time.time()
    import app as webapp  # noqa: E402
    print(f"  за {time.time()-t0:.1f}с; LLM_GATE={int(webapp.LLM_GATE)}, "
          f"TAU={webapp.TAU}, BRIDGE={int(webapp.BRIDGE_GATE)}", flush=True)

    area_query = {}
    for p in sorted(QUERIES_DIR.glob("*.json")):
        area_query[p.stem] = json.loads(p.read_text())["query"]

    rows_out, k1_frag = {}, 0
    k2_tot = k2_valid = k3_tot = k3_ok = shown_tot = 0
    print(f"\n| запрос | показано | llm_valid% (K2) | фрагменты (K1) | problem≥10 (K3) |")
    print("|---|---|---|---|---|")
    for slug in SLUGS:
        q = area_query.get(slug)
        if not q:
            print(f"| {slug} | ⏳ нет запроса | | | |")
            continue
        r = webapp.api_query(q)
        techs = r.get("techs", [])[:15]
        names = [str(t.get("term") or "") for t in techs]
        frags = [n for n in names if looks_like_fragment(n)]
        valid = sum(1 for t in techs if int(t.get("llm_valid", 0)) == 1)
        probs = sum(1 for t in techs
                    if len(str(t.get("problem_ru") or "").split()) >= 10)
        n = len(techs)
        shown_tot += n; k2_tot += n; k2_valid += valid
        k3_tot += n; k3_ok += probs; k1_frag += len(frags)
        rows_out[slug] = {"query": q, "shown": n, "llm_valid": valid,
                          "fragments": frags, "names": names,
                          "problem10": probs,
                          "problems": [str(t.get("problem_ru") or "")[:120]
                                       for t in techs]}
        print(f"| {slug} | {n} | {valid}/{n} | {len(frags)} | {probs}/{n} |")
        for nm in names:
            print(f"    {'❌' if looks_like_fragment(nm) else '·'} {nm}")

    k2_pct = 100 * k2_valid / max(k2_tot, 1)
    k3_pct = 100 * k3_ok / max(k3_tot, 1)
    res = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"),
           "llm_gate": os.environ["WEBAPP_LLM_GATE"],
           "K1_fragments_total": k1_frag, "K1_pass": k1_frag == 0,
           "K2_valid_pct": round(k2_pct, 1), "K2_pass": k2_pct >= 99.9,
           "K3_problem10_pct": round(k3_pct, 1), "K3_pass": k3_pct >= 90.0,
           "shown_total": shown_tot, "areas": rows_out}
    Path(REPORT).parent.mkdir(parents=True, exist_ok=True)
    Path(REPORT).write_text(json.dumps(res, ensure_ascii=False, indent=1))
    verdict = res["K1_pass"] and res["K2_pass"] and res["K3_pass"]
    print(f"\nK1 фрагменты={k1_frag} ({'✅' if res['K1_pass'] else '❌'}) | "
          f"K2 llm_valid={k2_pct:.1f}% ({'✅' if res['K2_pass'] else '❌'}) | "
          f"K3 problem≥10={k3_pct:.1f}% ({'✅' if res['K3_pass'] else '❌'}) → "
          f"{'ПРИНЯТО' if verdict else 'НЕ ПРИНЯТО'}")
    print(f"Отчёт: {REPORT}")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
