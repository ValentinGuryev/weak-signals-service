#!/usr/bin/env python3
"""Быстрый прототип: мотивы (триплеты) в графе flux pump vs joint.

Проверяем ГИПОТЕЗУ из docs/S3_TRIPLETS_PLAN.md:
- «состоялся» (flux pump) ⇔ при рождении появился bridge-мотив (связь между темами)
- «застрял» (joint) ⇔ рост внутри своего кластера, bridge редки

Метод (упрощённый прототип, не полный Wang):
1. Граф: id -> [cited], только внутренние рёбра (обе стороны в корпусе).
2. Узлы размечены по topic (flux pump CC / joint) и году.
3. Для каждого «нового» узла (год >= 2010) считаем:
   - cross_ratio: доля ссылок НА ДРУГУЮ тему (мост) среди внутренних ссылок узла;
   - in_cross: доля входящих ссылок из другой темы.
4. Сравниваем flux pump-узлы vs joint-узлы: у кого выше cross_ratio?
5. Динамика cross_ratio по годам рождения.

Выход: печать + results/case_signals/s3_motifs_proto.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REFS = PROJECT_ROOT / "data/raw/openalex/fluxpump_references.json"
CORPUS = PROJECT_ROOT / "data/raw/openalex/fluxpump_vs_joint_corpus.json"
OUT = PROJECT_ROOT / "results" / "case_signals" / "s3_motifs_proto.json"


def main() -> None:
    refs = json.loads(REFS.read_text())
    corpus = {x["id"]: x for x in json.loads(CORPUS.read_text())}

    # --- 1. Узлы: id -> {year, topic} ---
    node_info = {}
    for wid, meta in corpus.items():
        topic = meta.get("topic") or "?"
        year = meta.get("year")
        node_info[wid] = {"year": year, "topic": topic}

    # --- 2. Внутренние рёбра: u -> v (u цитирует v), обе в корпусе ---
    edges = []  # (u, v)
    for u, cited_list in refs.items():
        if u not in node_info:
            continue
        for v in cited_list:
            if v in node_info:
                edges.append((u, v))
    print(f"узлов: {len(node_info)}, внутр. рёбер: {len(edges)}")

    # темы
    topics = sorted({v["topic"] for v in node_info.values()})
    print(f"темы: {topics}")

    # --- 3. Для каждого узла: outgoing cross-ratio (доля ссылок на ДРУГУЮ тему) ---
    out_edges = defaultdict(list)  # u -> [v]
    in_edges = defaultdict(list)   # v <- [u]
    for u, v in edges:
        out_edges[u].append(v)
        in_edges[v].append(u)

    def cross_out(wid: str) -> float:
        vs = out_edges.get(wid, [])
        if not vs:
            return 0.0
        own = node_info[wid]["topic"]
        cross = sum(1 for v in vs if node_info[v]["topic"] != own)
        return cross / len(vs)

    def cross_in(wid: str) -> float:
        us = in_edges.get(wid, [])
        if not us:
            return 0.0
        own = node_info[wid]["topic"]
        cross = sum(1 for u in us if node_info[u]["topic"] != own)
        return cross / len(us)

    # --- 4. Сравнение по темам (узлы 2010+, с достаточным числом ссылок) ---
    stats = defaultdict(lambda: {"n": 0, "cross_out_sum": 0.0, "cross_in_sum": 0.0})
    per_year = defaultdict(lambda: defaultdict(lambda: {"n": 0, "co": 0.0, "ci": 0.0}))
    for wid, info in node_info.items():
        y = info["year"]
        if y is None or y < 2010:
            continue
        t = info["topic"]
        co = cross_out(wid)
        ci = cross_in(wid)
        # только узлы с >=3 ссылками (шум)
        if len(out_edges.get(wid, [])) >= 3 or len(in_edges.get(wid, [])) >= 3:
            stats[t]["n"] += 1
            stats[t]["cross_out_sum"] += co
            stats[t]["cross_in_sum"] += ci
            per_year[t][y]["n"] += 1
            per_year[t][y]["co"] += co
            per_year[t][y]["ci"] += ci

    print("\n=== Cross-topic ratio (мост между темами), узлы 2010+ ===")
    for t in topics:
        s = stats[t]
        if s["n"]:
            print(f"{t}: n={s['n']}, средний outgoing-cross={s['cross_out_sum']/s['n']:.2f}, "
                  f"средний incoming-cross={s['cross_in_sum']/s['n']:.2f}")

    # --- 5. Динамика по годам (скользящее среднее по 3 годам) ---
    print("\n=== Динамика outgoing-cross по году рождения (flux pump vs joint) ===")
    all_years = sorted({y for t in per_year for y in per_year[t]})
    for t in topics:
        series = []
        for y in all_years:
            d = per_year[t].get(y)
            if d and d["n"]:
                series.append((y, d["co"] / d["n"], d["n"]))
            else:
                series.append((y, None, 0))
        # сгладим по 3 годам
        print(f"\n{t}:")
        for i, (y, v, n) in enumerate(series):
            if v is None:
                continue
            lo = max(0, i - 1)
            hi = min(len(series), i + 2)
            vals = [series[j][1] for j in range(lo, hi) if series[j][1] is not None]
            avg = sum(vals) / len(vals) if vals else 0
            print(f"  {y}: cross={avg:.2f} (n={n})")

    # сохраняем
    out_data = {
        "method": "s3_motifs_proto: cross-topic ratio (bridge) в графе flux pump vs joint",
        "n_nodes": len(node_info), "n_edges": len(edges),
        "topics": topics,
        "stats": {t: {"n": s["n"], "cross_out_mean": s["cross_out_sum"]/s["n"] if s["n"] else 0,
                      "cross_in_mean": s["cross_in_sum"]/s["n"] if s["n"] else 0} for t, s in stats.items()},
        "per_year": {t: {str(y): {"n": d["n"], "co_mean": d["co"]/d["n"] if d["n"] else 0,
                                  "ci_mean": d["ci"]/d["n"] if d["n"] else 0}
                          for y, d in per_year[t].items()} for t in topics},
    }
    OUT.write_text(json.dumps(out_data, ensure_ascii=False, indent=1))
    print(f"\nсохранено: {OUT}")


if __name__ == "__main__":
    main()
