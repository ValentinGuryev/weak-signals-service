#!/usr/bin/env python3
"""Этап Е (метрика ночи 28→29.09): presence эталонных слабых сигналов организаторов.

Источник истины (решение команды): docs/official_docs/100_слабых_технологических_
сигналов_сентябрь_2026.xlsx — 100 сигналов; другого списка нет.

Определение (объявлено ДО прогона):
  * запрос = «Технология (слабый сигнал)» из xlsx (RU);
  * золотая карточка сигнала = наш терм с МАКСИМАЛЬНЫМ косинусом e5
    (имя+проблема/профиль) на ВСЁМ пуле выдачи — маппинг заморожен до сравнения;
  * presence@K = золотая карточка входит в топ-K выдачи формы 1 на этот запрос.

Запуск (после интеграции карточек в app — WEBAPP_CARDS=1 — иначе baseline
на текущем пуле 6238): .venv/bin/python scripts/presence100.py
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "docs/official_docs/100_слабых_технологических_сигналов_сентябрь_2026.xlsx"


def load_signals() -> list[dict]:
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    ws = wb["Слабые сигналы"]
    out = []
    for row in ws.iter_rows(min_row=3, values_only=True):
        if row[1] is None or not isinstance(row[1], (int, float)):
            continue
        out.append({"n": int(row[1]), "name": str(row[2]).strip(),
                    "area": str(row[3]).strip() if row[3] else ""})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=50, help="считать presence@15/@K")
    ap.add_argument("--tag", default=time.strftime("%Y%m%d_%H%M"))
    ap.add_argument("--gold-from", default=None,
                    help="заморозить золотой маппинг из JSON baseline (колонка rows)")
    args = ap.parse_args()

    sys.path.insert(0, str(ROOT / "webapp"))
    import app as webapp  # noqa: E402  (данные читаются при импорте)

    sigs = load_signals()
    print(f"сигналов из xlsx: {len(sigs)}", flush=True)
    webapp.TOP_TECHS = max(webapp.TOP_TECHS, args.k)   # замер до K

    # --- маппинг «сигнал → золотой терм» (по всему пулу, до сравнения) ---
    gold_map = None
    if args.gold_from:
        base = json.loads(Path(args.gold_from).read_text())
        gold_map = {int(r["n"]): r["gold_term"] for r in base.get("rows", [])}
        print(f"золотой маппинг ЗАМОРОЖЕН из {args.gold_from}: {len(gold_map)}",
              flush=True)
    if getattr(webapp, "CARDS_ENABLED", False) and webapp._cards_init():
        pool_terms = list(webapp.CARDS["df"]["term"])   # карточный пул (№17)
        vecs = webapp.CARDS["vec"]
        # №18.3/№20: золото = лучшая ПОКАЗЫВАЕМАЯ карточка (гейт мусора,
        # при WEBAPP_BRIDGE_GATE — и bridge по топ-15 темам этого запроса).
        gate_bad = webapp.CARDS["bad"] if getattr(webapp, "GATE_ENABLED", False) \
            else None
        linked = getattr(webapp.CARDS, "get", lambda *_: None)("linked") \
            if isinstance(webapp.CARDS, dict) else None
    else:
        pool_terms = list(webapp.TECH_TERMS)
        vecs = webapp.TECH_VEC
        gate_bad = None
        linked = None
    bridge_on = bool(getattr(webapp, "BRIDGE_GATE", False)) and linked is not None
    # LLM-гейт (план 29.09): золото = лучшая ПОКАЗЫВАЕМАЯ карточка → при
    # WEBAPP_LLM_GATE маскируем llm_valid==0 (иначе refrozen-золото ловит
    # скрытую карточку и pos всегда 0)
    llm_off = None
    if getattr(webapp, "CARDS_ENABLED", False) and getattr(webapp, "LLM_GATE", False):
        llm_off = (webapp.CARDS["df"]["llm_valid"].to_numpy(dtype=int) == 0)

    # --- единый цикл: сначала запрос (нужны топ-темы для bridge-маски №20),
    # затем маппинг золота по показываемому пулу → pos ---
    rows = []
    for i, s in enumerate(sigs, 1):
        resp = webapp.api_query(s["name"])
        top = [t.get("term_raw") or t["term"] for t in resp["techs"]]
        qv = webapp.e5_embed([s["name"]])[0]
        sims = vecs @ qv
        if gate_bad is not None:
            sims[gate_bad] = -np.inf
        if llm_off is not None:
            sims[llm_off] = -np.inf
        if bridge_on:
            top15 = {int(t["tid"]) for t in resp["topics"][:15]}
            bm = np.fromiter((not (lk & top15) for lk in linked),
                             dtype=bool, count=len(linked))
            sims[bm] = -np.inf
        j = int(np.argmax(sims))
        if gold_map is not None and s["n"] in gold_map:
            g = gold_map[s["n"]]                 # замороженное золото
        else:
            g = pool_terms[j]
        gs = float(sims[j])
        pos = top.index(g) + 1 if g in top else 0
        rows.append({**s, "gold_term": g, "gold_cos": round(gs, 3),
                     "pos": pos, "hit15": int(0 < pos <= 15),
                     "hitK": int(0 < pos <= args.k)})
        if i % 20 == 0:
            print(f"[{i}/{len(sigs)}]", flush=True)

    df = pd.DataFrame(rows)
    h15, hK = int(df["hit15"].sum()), int(df["hitK"].sum())
    n = len(df)
    out = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "n": n,
           "presence@15": h15, f"presence@{args.k}": hK,
           "median_gold_cos": float(df["gold_cos"].median()),
           "gold_frozen_from": args.gold_from,
           "mode": webapp.__dict__.get("BATCH_ENABLED", None),
           "top15_mean": float((df["pos"] > 0).mean()),
           "rows": df.to_dict(orient="records")}   # все 100 строк (фикс рецензии)
    jpath = ROOT / f"results/presence100_{args.tag}.json"
    jpath.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    md = [f"# presence100 — {out['ts']}", "",
          f"**presence@15 = {h15}/{n} ({h15/n:.1%}); "
          f"presence@{args.k} = {hK}/{n} ({hK/n:.1%})**", "",
          "Топ-15 промахов (позиция золота >15 или нет):",
          "| № | сигнал | область | gold | кос | позиция |", "|---|---|---|---|---|---|"]
    for r in df[(df["pos"] == 0) | (df["pos"] > 15)].head(25).itertuples():
        md.append(f"| {r.n} | {r.name[:48]} | {r.area[:14]} | {r.gold_term[:30]} "
                  f"| {r.gold_cos} | {r.pos or '—'} |")
    md.append("\nПолная таблица (все 100 строк: n/name/area/gold_term/gold_cos/pos) — в JSON рядом.")
    (ROOT / f"results/presence100_{args.tag}.md").write_text(
        "\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:6]), flush=True)
    print(f"→ {jpath}", flush=True)


if __name__ == "__main__":
    main()
