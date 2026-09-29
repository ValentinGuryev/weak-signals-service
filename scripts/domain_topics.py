#!/usr/bin/env python3
"""Подготовка списков тем доменов для ночных срезов TermTech (план ночных работ NJ-5..9).

Берёт topics.parquet (4516 тем), применяет доменный regex (frozen-список ниже),
отсекает очевидные ложные срабатывания (исключения), оставляет топ-N по works_count
(ограничение времени среза: ~60 тем ≈ 2-4 ч на E:; см. урок AI-среза 25.09).

Выход:
  results/runtime/domain_<name>_topics.txt   — id через запятую (для --topics)
  results/runtime/domain_<name>_topics.md    — аудит-список (имена тем)
  results/runtime/domain_topics_report.json  — сводка

Запуск: .venv/bin/python scripts/domain_topics.py [--max 60]
"""
import argparse
import json
import re
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
TOPICS = ROOT / "data/openalex_derived/taxonomy/topics.parquet"
OUT = ROOT / "results/runtime"

# frozen-список доменов (правка только с обоснованием;NJ-5..9 в план ночных работ)
DOMAINS = {
    "quantum": {
        "rx": r"quantum",
        "except": r"",
        "note": "квантовые технологии (вычисления, сенсоры, материалы)",
    },
    "biomed": {
        "rx": r"genom|gene edit|crispr|immunotherap|drug discovery|drug delivery|"
              r"clinical|bioinformat|single-cell|microbiome|cell therap|antibody|"
              r"vaccine|mrna|organoid|liquid biops|medical image|neurodegener|"
              r"theranost|nanomedicine|proteomic",
        "except": r"",
        "note": "био/медицинские технологии (узкий эмерджинг-контур, НЕ все 201 темы)",
    },
    "energy": {
        "rx": r"fusion|fission|nuclear|batter|energy stor|photovolta|solar cell|"
              r"hydrogen|electroly|microgrid|grid control|supercapacitor",
        "except": r"",
        "note": "энергетика/климат (накопители, водород, fusion)",
    },
    "materials": {
        "rx": r"metallurg|alloy|ceramic|polymer|additive manufact|3-d print|"
              r"thin film|coating|metamaterial|high-entropy|superconduct.*material",
        "except": r"",
        "note": "материалы/производство",
    },
    "robotics": {
        "rx": r"robot|autonomous vehicle|drone|unmanned aerial|soft robot|actuator",
        "except": r"",
        "note": "робототехника/дроны/АТС",
    },
    "space": {
        "rx": r"spacecraft|satellite|aerospace|spaceflight|rocket|orbital|avionic",
        "except": r"",   # голый 'space' НЕ берём: Banach Space, Green Space, Sequence Spaces
        "note": "космос/авиация (без ложных срабатываний на мат. «space»)",
    },
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=60,
                    help="максимум тем на домен (по works_count)")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    rows = pq.read_table(TOPICS).to_pylist()
    report = {}
    for name, cfg in DOMAINS.items():
        rx = re.compile(cfg["rx"], re.I)
        ex = re.compile(cfg["except"], re.I) if cfg["except"] else None
        hits = [r for r in rows
                if rx.search(str(r.get("display_name", "")))
                and not (ex and ex.search(str(r.get("display_name", ""))))]
        hits.sort(key=lambda r: -(r.get("works_count") or 0))
        hits = hits[: args.max]
        ids = [int(str(r["id"]).rstrip("/").split("T")[-1]) for r in hits]
        (OUT / f"domain_{name}_topics.txt").write_text(",".join(map(str, ids)))
        lines = [f"# Домен «{name}» — {cfg['note']}", "",
                 f"Тем: {len(ids)} (из {len([r for r in rows if rx.search(str(r.get('display_name','')))])} по regex, "
                 f"топ-{args.max} по works_count)", "",
                 "| tid | тема | works |", "|---|---|---|"]
        for r in hits:
            tid = str(r["id"]).rstrip("/").split("T")[-1]
            lines.append(f"| T{tid} | {r['display_name']} | {r.get('works_count')} |")
        (OUT / f"domain_{name}_topics.md").write_text("\n".join(lines) + "\n")
        report[name] = {"n_topics": len(ids), "note": cfg["note"]}
        print(f"{name:10s} → {len(ids):3d} тем  (файлы domain_{name}_topics.*)")

    (OUT / "domain_topics_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1))
    print("report → results/runtime/domain_topics_report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
