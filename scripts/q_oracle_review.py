#!/usr/bin/env python3
"""Визуальная сверка пары «запрос ↔ оракул ↔ выдача» (вариант 4, автор 28.09).

Выход: results/runtime/QUERY_ORACLE_REVIEW_20260928.md — по каждой области:
запрос, технологии xlsx (колонки организатора), allowed-темы оракула (имена),
топ-15 демо (✓ = покрытие цели). Плюс разворот сырых колонок xlsx.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "webapp"))

from eval_stage9 import load_oracles  # noqa: E402
import app as webapp  # noqa: E402

OUT = ROOT / "results" / "runtime" / "QUERY_ORACLE_REVIEW_20260928.md"
XLSX = ROOT / "docs" / "official_docs" / "100_слабых_технологических_сигналов_сентябрь_2026.xlsx"

TID_NAME = {int(str(v).rstrip("/").split("T")[-1]): str(n)
            for v, n in zip(webapp.TOPICS["id"], webapp.TOPICS["display_name"])}

_xl = pd.read_excel(XLSX, header=1)          # строка 1 = реальный заголовок
_xl = _xl.dropna(subset=["№"])
XLSX_BY_N = {int(r["№"]): r for _, r in _xl.iterrows()}


def xlsx_dump() -> list[str]:
    raw = pd.read_excel(XLSX, header=None)
    lines = ["## Сырые колонки xlsx организатора (первые 6 строк)", ""]
    lines.append("```")
    lines.append(raw.head(6).to_string(max_colwidth=60))
    lines.append("```")
    return lines


def main() -> int:
    oracles = load_oracles()
    # queries из run-файлов №9
    area_query = {p.stem: json.loads(p.read_text())["query"]
                  for p in (ROOT / "results" / "qa_areas9").glob("*.json")}
    # топ-15 из последнего отчёта приёмки
    rep = json.loads((ROOT / "results" / "qa_demo_accept_report.json").read_text())
    ids15_by: dict = {}
    out = ["# Сверка «запрос ↔ оракул ↔ выдача» — 28.09 (вариант 4, ручной просмотр)",
           "",
           "Оракул = технологии xlsx организатора (слабые сигналы), замапленные на темы",
           "таксономии (allowed). Запрос в приёмке = bare-имя области. Цель покрыта, если",
           "ХОТЯ БЫ ОДНА allowed-тема в топ-15.", ""]
    out += xlsx_dump()
    for slug, orc in oracles.items():
        q = area_query.get(slug, "?")
        r15 = rep["areas"].get(slug, {})
        top15 = r15.get("top15", [])
        ids15 = {int(t["tid"]) for t in top15}
        ids15_by[slug] = ids15
        out += [f"## {slug} — запрос: «{q}»",
                f"покрытие {r15.get('coverage')}/11, мусор {r15.get('garbage')}", "",
                "| № | Технология xlsx (слабый сигнал) | allowed-темы таксономии | в топ-15? |", "|---|---|---|---|"]
        for i, t in enumerate(orc["targets"], 1):
            allowed = [int(x) for x in t["allowed"]]
            names = "<br>".join(f"`{a}` {TID_NAME.get(a, '?')}" for a in allowed)
            hit = "✅" if ids15 & set(allowed) else "—"
            try:
                xr = XLSX_BY_N.get(int(t.get("n", -1)))
                tech = str(xr["Технология (слабый сигнал)"]).replace("|", "/") if xr is not None else f"№{t.get('n')}"
                stage = str(xr.get("Стадия развития", ""))[:30]
            except Exception:
                tech, stage = f"№{t.get('n')}", ""
            out.append(f"| {i} | {tech} <br>_(стадия: {stage})_ | {names} | {hit} |")
        out += ["", "### Топ-15 выдачи демо", ""]
        for j, t in enumerate(top15, 1):
            mark = "✓" if int(t["tid"]) in {int(x) for tgt in orc["targets"] for x in tgt["allowed"]} else " "
            out.append(f"{j:2}. [{mark}] {t['name']} (tid {t['tid']})")
        out.append("")
    OUT.write_text("\n".join(out))
    print(f"written: {OUT} ({len(out)} lines)")    # краткая выжимка для чата: industrial + infra (с текстом технологий)
    for slug in ("industrial", "infra"):
        orc = oracles[slug]
        print(f"\n=== {slug} «{area_query.get(slug)}» ===")
        for i, t in enumerate(orc["targets"], 1):
            allowed = [int(x) for x in t["allowed"]]
            xr = XLSX_BY_N.get(int(t.get("n", -1)))
            tech = str(xr["Технология (слабый сигнал)"])[:78] if xr is not None else f"№{t.get('n')}"
            names = "; ".join(TID_NAME.get(a, "?") for a in allowed)
            hit = "✅" if ids15_by.get(slug, set()) & set(allowed) else "—"
            print(f"{i:2}. {hit} {tech}\n     → {names[:100]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
