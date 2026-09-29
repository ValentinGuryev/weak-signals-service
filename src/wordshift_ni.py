#!/usr/bin/env python3
"""Wordshift-тренды для кейса 004: NI-coils (no-insulation катушки).

S2-сигнал: семантический сдвиг «проблема/механизм → применение/зрелость».
Адаптация wordshift_rce_tlag.py под ni_coils_corpus.json.

Источник: data/raw/openalex/ni_coils_corpus.json (299 работ)
Выход: results/case_signals/wordshift_trends_ni.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from semantic_shift_v2 import clean_text, tokens  # noqa: E402

CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "ni_coils_corpus.json"
OUT_DIR = PROJECT_ROOT / "results" / "case_signals"

# Периоды: до NI, зарождение, рост, плато, пик/зрелость
OA_PERIODS = {"-2010": (1990, 2010), "2011-2015": (2011, 2015),
              "2016-2019": (2016, 2019), "2020-2022": (2020, 2022),
              "2023-2026": (2023, 2026)}

STOP_EXTRA = set("""abstract keywords index terms introduction conclusion results discussion
references figure fig table tables shown show shows using used use based due well however
also can may will one two new first last part paper study work year years present presents
performed measured obtained found shows demonstrates case cases different various high low
large small number several many much more most less least between within without with
after before during through under over about into from this these those that which where
when what how why who whose their there here then than both each other another such same
only very just also but and or not no nor for with by to of in on at from the a an is are
was were be been being it its as etc ie eg including include includes included via
respectively corresponding associated related between among non ieee csc esas esnf forum
news global edition issue presented at laboratory national institute university center
centre group department division program project report annual final progress
superconducting superconductor hts rebco""".split())

KEEP = {"ni", "no-insul", "no-insulation", "insulation", "insulat", "coil", "coils",
        "magnet", "magnets", "quench", "protect", "protection", "transient",
        "stability", "stabil", "charging", "charge", "contact", "resistance",
        "turn-to-turn", "pancake", "solenoid", "racetrack", "field", "tesla",
        "record", "screening", "current", "degradation", "degrad", "optimiz",
        "optimization", "design", "compact", "fusion", "accelerator", "mri",
        "nmr", "bios", "layer", "winding", "wind", "co-wound", "bypass", "radial",
        "axial", "thermal", "temperature", "heating", "hot", "spot", "energy",
        "store", "stored", "self-protect", "self-protection"}


def analyze_monotonic(freqs: list[float]) -> dict:
    n = len(freqs)
    if n < 3:
        return {"monotonic": 0, "trend": "flat", "extremum": None, "freqs": freqs}
    inc = sum(1 for i in range(n - 1) if freqs[i + 1] >= freqs[i])
    dec = sum(1 for i in range(n - 1) if freqs[i + 1] <= freqs[i])
    inc_ratio = inc / (n - 1)
    dec_ratio = dec / (n - 1)
    if inc_ratio >= 0.7 and freqs[-1] > freqs[0] * 1.2:
        trend = "up"
    elif dec_ratio >= 0.7 and freqs[0] > freqs[-1] * 1.2:
        trend = "down"
    else:
        trend = "flat"
    imax = max(range(n), key=lambda i: freqs[i])
    imin = min(range(n), key=lambda i: freqs[i])
    extremum = None
    if 0 < imax < n - 1 and freqs[imax] > max(freqs[0], freqs[-1]) * 1.5:
        extremum = ("max", imax)
    elif 0 < imin < n - 1 and freqs[imin] < min(freqs[0], freqs[-1]) * 0.6:
        extremum = ("min", imin)
    return {"monotonic": max(inc_ratio, dec_ratio), "trend": trend,
            "extremum": extremum, "freqs": freqs}


def analyze_corpus(texts_by_period: dict[str, list[str]], min_count: int = 5) -> dict:
    word_freqs: dict[str, list[float]] = defaultdict(lambda: [0.0] * len(texts_by_period))
    total_words = {}
    for pi, (period, texts) in enumerate(sorted(texts_by_period.items())):
        cnt = Counter()
        n_words = 0
        for t in texts:
            for w in tokens(t):
                if w in STOP_EXTRA or len(w) < 4:
                    continue
                cnt[w] += 1
                n_words += 1
        total_words[period] = n_words
        for w, c in cnt.items():
            word_freqs[w][pi] = c / max(n_words, 1) * 1000
    results = []
    for w, freqs in word_freqs.items():
        if sum(freqs) < min_count:
            continue
        m = analyze_monotonic(freqs)
        if m["trend"] != "flat" or m["extremum"]:
            results.append({"word": w, **m})
    results.sort(key=lambda x: -x["monotonic"])
    return {
        "periods": list(sorted(texts_by_period.keys())),
        "period_totals": total_words,
        "trends": {r["word"]: {k: v for k, v in r.items() if k != "word"} for r in results},
        "ranked": results,
    }


def main() -> None:
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    ws = data if isinstance(data, list) else data.get("works", [])

    texts_by_period = {p: [] for p in OA_PERIODS}
    n_used = 0
    for w in ws:
        ab = w.get("abstract") or ""
        if len(ab) < 40:
            continue
        y = w.get("year")
        if not y:
            continue
        p = next((p for p, (a, b) in OA_PERIODS.items() if a <= y <= b), None)
        if p:
            clean = clean_text(ab)
            if len(clean) >= 40:
                texts_by_period[p].append(clean)
                n_used += 1

    res = analyze_corpus(texts_by_period, min_count=5)
    out = OUT_DIR / "wordshift_trends_ni.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"===== NI-coils — {n_used} работ с абстрактом =====")
    print(f"period_totals: {res['period_totals']}")
    print(f"{'слово':<25} {'тренд':<6} {'монот':>5} {'экстр':>8} {'частоты ‰':<50}")
    for m in res["ranked"][:45]:
        f = ", ".join(f"{x:.1f}" for x in m["freqs"])
        print(f"{m['word']:<25} {m['trend']:<6} {m['monotonic']:.2f} "
              f"{str(m['extremum']):<8} [{f}]")
    print(f"(всего слов с трендом: {len(res['ranked'])})")


if __name__ == "__main__":
    main()
