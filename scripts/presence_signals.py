#!/usr/bin/env python3
"""Presence-метрика заочного тура (объявлена в №15 ДО): доля 142 allowed-тем
сигналов организатора в топ-15/топ-50 по 6 area-запросам. На финальном конфиге
app (порядок = дефолт). Не является критерием приёмки — показатель «перемещения
сигналов в топ выдачи».

Запуск: .venv/bin/python scripts/presence_signals.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "webapp"))

from eval_stage9 import load_oracles  # noqa: E402
import app as webapp  # noqa: E402

webapp.TOP_TOPICS = 10 ** 6  # полный kept для топ-50


def main() -> int:
    oracles = load_oracles()
    allowed_all = set()
    for orc in oracles.values():
        for t in orc["targets"]:
            allowed_all |= {int(x) for x in t["allowed"]}
    hit15, hit50, rows = set(), set(), []
    for slug, orc in oracles.items():
        q = json.loads((ROOT / "results" / "qa_areas9" / f"{slug}.json").read_text())["query"]
        r = webapp.api_query(q)
        ids = [int(x["tid"]) for x in r["topics"]]
        a = set()
        for t in orc["targets"]:
            a |= {int(x) for x in t["allowed"]}
        h15 = a & set(ids[:15])
        h50 = a & set(ids[:50])
        hit15 |= h15
        hit50 |= h50
        rows.append((slug, q, len(h15), len(h50), len(a),
                     r["retrieval"].get("child_delivered", 0)))
    n = len(allowed_all)
    print(f"Порядок: {webapp.ORDER} | allowed всего: {n}")
    print("| область | запрос | presence@15 | presence@50 | allowed |")
    print("|---|---|---|---|---|")
    for slug, q, h15, h50, na, _ in rows:
        print(f"| {slug} | {q} | {h15} | {h50} | {na} |")
    print(f"\nSUMMARY presence@15 = {len(hit15)}/{n} = {len(hit15)/n:.3f} | "
          f"presence@50 = {len(hit50)}/{n} = {len(hit50)/n:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
