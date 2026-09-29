#!/usr/bin/env python3
"""S2 v2 для кейса 003: flux pump — плотность инженерной vs фундаментальной лексики.

Тот же продвинутый пайплайн, что для NI-coils (semantic_v2_ni.py):
сбалансированные словари + плотность маркеров (‰) по периодам.

Словари под flux pump:
- ENG (инженерия): efficiency, contactless, charging, current lead, coil, magnet,
  power, output, voltage, stack, dynamo, transformer, rectifier, compact, cooling,
  closed-loop, control, protection, thermal...
- EFF (фундамент): mechanism, theory, fundamental, physics, phenomenon, dynamic
  resistance, decay, trigger, superconducting joint, flux motion, vortex...

Источник: data/raw/openalex/fluxpump_vs_joint_corpus.json (290 flux pump)
Выход: results/case_signals/semantic_v2_fluxpump.json
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from semantic_shift_v2 import clean_text, tokens  # noqa: E402

CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "fluxpump_vs_joint_corpus.json"
OUT = PROJECT_ROOT / "results" / "case_signals" / "semantic_v2_fluxpump.json"

# Периоды (как в wordshift_fluxpump.py)
PERIODS = {"1997-2005": (1997, 2005), "2006-2010": (2006, 2010),
           "2011-2015": (2011, 2015), "2016-2019": (2016, 2019),
           "2020-2022": (2020, 2022), "2023-2026": (2023, 2026)}

# === Сбалансированные словари под flux pump ===
# Инженерия: применение, системы, эффективность, безгелиевый
ENG_STEMS = set("""effici contactless charg current lead coil magnet power output
voltag stack dynamo transform rectifi compact cool closed-loop control protect
thermal heat load energ transfer cryogen inject circuit supply pump wound
rotor stator armature""".split())
# Фундаментальное: механизм, физика, эффект
EFF_STEMS = set("""mechan theoret fundament basic physics phenomen discover reveal
elucid uncover novel surpris unexpect demonstr record breakthr possibl potenti
promis first new unique decay trigger dynamic resist joint flux motion vortex
principle origin explain""".split())

MULTI_ENG = re.compile(
    r"current lead|contactless|cooling (system|power)|heat load|closed[- ]?loop|"
    r"transformer[- ]?rectifier|power supply|energy (efficiency|transfer)|"
    r"charging (time|rate)|flux pump (system|circuit)|cryogen[- ]?free|"
    r"no[- ]?current[- ]?lead|current injection|magnet (charging|energization)|"
    r"space (application|mission)|satellite|cryocooler", re.I)
MULTI_EFF = re.compile(
    r"dynamic resist|flux (motion|creep|jump)|decay (rate|time)|trigger|"
    r"mechanism of|underlying (mechanism|physics)|fundamental (physics|mechanism)|"
    r"theoretical (model|analysis)|first (time|demonstration|observation)|"
    r"new (phenomenon|mechanism|physics)", re.I)


def eng_density(text: str) -> dict:
    clean = clean_text(text)
    toks = tokens(clean)
    n = len(toks)
    if n < 20:
        return None
    eng = sum(1 for t in toks if t in ENG_STEMS)
    eff = sum(1 for t in toks if t in EFF_STEMS)
    eng_multi = len(MULTI_ENG.findall(clean))
    eff_multi = len(MULTI_EFF.findall(clean))
    return {
        "eng_per_1000": 1000 * (eng + 2 * eng_multi) / n,
        "eff_per_1000": 1000 * (eff + 2 * eff_multi) / n,
        "n": n,
    }


def period_of(year: int) -> str | None:
    for p, (a, b) in PERIODS.items():
        if a <= year <= b:
            return p
    return None


def main() -> None:
    random.seed(42)
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    ws = data if isinstance(data, list) else data.get("works", [])

    docs_by_period: dict[str, list[dict]] = {p: [] for p in PERIODS}
    n_fp = 0
    for w in ws:
        if "Flux" not in (w.get("topic") or ""):
            continue
        n_fp += 1
        ab = w.get("abstract") or ""
        if len(ab) < 200:
            continue
        y = w.get("year")
        p = period_of(y) if y else None
        if not p:
            continue
        d = eng_density(ab)
        if d:
            docs_by_period[p].append(d)

    def boot(xs):
        vals = []
        for _ in range(1000):
            sample = [random.choice(xs) for _ in xs]
            vals.append(sum(sample) / len(sample))
        vals.sort()
        return vals[25], vals[975]

    out = {}
    print("=== S2 v2: flux pump (003) — плотность инженерной/фундаментальной лексики ===")
    print(f"{'период':<10} {'раб':>4} {'инж‰':>6} {'фунд‰':>6} {'Δ(инж-фунд)‰':>12}")
    for p in PERIODS:
        docs = docs_by_period[p]
        if not docs:
            out[p] = {"n": 0}
            print(f"{p:<10} {'—':>4}")
            continue
        engs = [d["eng_per_1000"] for d in docs]
        effs = [d["eff_per_1000"] for d in docs]
        deltas = [e - f for e, f in zip(engs, effs)]
        em, fm, dm = sum(engs)/len(engs), sum(effs)/len(effs), sum(deltas)/len(deltas)
        out[p] = {
            "n": len(docs),
            "eng_per_1000": em, "eng_ci": boot(engs),
            "eff_per_1000": fm, "eff_ci": boot(effs),
            "delta_mean": dm, "delta_ci": boot(deltas),
        }
        print(f"{p:<10} {len(docs):>4} {em:>6.1f} {fm:>6.1f} {dm:>+12.1f}")
    out["_meta"] = {"tag": "fluxpump_v2", "total_fp": n_fp, "periods": PERIODS}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT}")


if __name__ == "__main__":
    main()
