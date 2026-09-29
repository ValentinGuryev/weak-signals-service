#!/usr/bin/env python3
"""Быстрый локальный скан мусора по 3 базам Этапа 1 (0 запросов Lens)."""
import json, re
from pathlib import Path

RULES = {
 "sc_dc_cables": {
    "must": r"superconduct|hts\b|mgb2",
    "junk": r"semiconductor|\bcmos\b|integrated circuit|solar cell|\bled\b|optical fiber|fibre|fiber optic",
    "suspect": r"google|rey|jingzhiyi|sichuan|varian|samsung|intel",
 },
 "iron_based": {
    "must": r"iron.based|pnictide|feas|fese|fete|bafe|smfeaso|lifeas|superconduct",
    "junk": r"drug|pharma|vaccine|battery\b|solar cell|\bled\b|fuel cell|tumor|antibod",
    "suspect": "",
 },
 "sc_induction_heaters": {
    "must": r"induction heat",
    "junk": r"high.?throughput screening|semiconductor|\bcmos\b|microwave|food cooking|\bplasma\b",
    "suspect": "",
 },
}

def asg(r):
    a = r.get("assignee") or "—"
    if isinstance(a, str): return a.split(";")[0].strip()
    return "—"

for case, rules in RULES.items():
    d = json.loads(Path(f"data/raw/patents/cases/{case}.json").read_text())
    pats = [p for p in d["patents"] if p.get("relevant")]
    text = lambda r: f"{r.get('title','')} {r.get('abstract','')}".lower()
    junk_hits = [r for r in pats if re.search(rules["junk"], text(r))]
    must_fail = [r for r in pats if not re.search(rules["must"], text(r))]
    suspect = [r for r in pats if rules["suspect"] and re.search(rules["suspect"], text(r))]
    print(f"===== {case}: релев {len(pats)} =====")
    print(f"  JUNK (стоп-слова): {len(junk_hits)}")
    for r in junk_hits[:12]:
        print(f"    {r.get('year')} | {asg(r)} | {(r.get('title') or '')[:95]}")
    print(f"  БЕЗ обязательного контекста: {len(must_fail)}")
    for r in must_fail[:10]:
        print(f"    {r.get('year')} | {asg(r)} | {(r.get('title') or '')[:95]}")
    if rules["suspect"]:
        print(f"  ПОДОЗРЕНИЯ (игроки): {len(suspect)}")
        for r in suspect[:12]:
            print(f"    {r.get('year')} | {asg(r)} | {(r.get('title') or '')[:95]}")
    print()