#!/usr/bin/env python3
"""S2 v2 (финальный): NI-coils — плотность инженерной лексики по периодам.

Честный подход: не бинарный ярлык (вся тема инженерная), а ПЛОТНОСТЬ
инженерных маркеров (eng‰) и фундаментальных (eff‰) по периодам.
Показывает, РАСТЁТ ли инженерная составляющая (S2-гейт зрелости).

Источник: data/raw/openalex/ni_coils_corpus.json
Выход: results/case_signals/semantic_v2_ni.json
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

CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "ni_coils_corpus.json"
OUT = PROJECT_ROOT / "results" / "case_signals" / "semantic_v2_ni.json"

PERIODS = {"-2010": (1990, 2010), "2011-2015": (2011, 2015),
           "2016-2019": (2016, 2019), "2020-2022": (2020, 2022),
           "2023-2026": (2023, 2026)}

# === Сбалансированные словари ===
# Инженерия КОНСТРУКЦИИ (не производства): проектирование, защита, тесты, оптимизация
ENG_STEMS = set("""design construct build test simul model numer optim quench protect
stabil reliab wind coil magnet solenoid pancak racetrack insert charg contact
resist radial axial turn layer-wound degrad damage safeti""".split())
# Фундаментальное: механизм, открытие, новизна
EFF_STEMS = set("""mechan theoret fundament basic insight understand phenomen discover
reveal elucid uncover novel surpris unexpect demonstr record breakthr possibl
potenti promis first new unique""".split())

# Многословные маркеры
MULTI_ENG = re.compile(
    r"no[- ]?insulation|metal[- ]?insulation|partial[- ]?insulation|self[- ]?protect|"
    r"contact resist|quench protect|charging time|turn[- ]?to[- ]?turn|"
    r"screening current|hot spot|normal zone|thermal runaway", re.I)
MULTI_EFF = re.compile(
    r"first time|underlying mechanism|fundamental (mechanism|physics)|"
    r"new (phenomenon|mechanism|physics)|theoretical (model|analysis)", re.I)


def eng_density(text: str) -> dict:
    """Плотность инженерных и фундаментальных маркеров (на 1000 слов)."""
    clean = clean_text(text)
    toks = tokens(clean)
    n = len(toks)
    if n < 20:
        return None
    eng = sum(1 for t in toks if t in ENG_STEMS)
    eff = sum(1 for t in toks if t in EFF_STEMS)
    # многословные (на исходном, не токены) — считаем по вхождениям
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
    works = json.loads(CORPUS.read_text(encoding="utf-8"))
    docs_by_period: dict[str, list[dict]] = {p: [] for p in PERIODS}
    for w in works:
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
    print("=== S2 v2: NI-coils — плотность инженерной/фундаментальной лексики ===")
    print(f"{'период':<10} {'раб':>4} {'инж‰':>6} {'фунд‰':>6} {'Δ(инж-фунд)‰':>12}")
    for p in PERIODS:
        docs = docs_by_period[p]
        if not docs:
            out[p] = {"n": 0}
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
    out["_meta"] = {"tag": "ni_coils_v3", "total": len(works), "periods": PERIODS}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT}")


if __name__ == "__main__":
    main()
