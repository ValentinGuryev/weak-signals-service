#!/usr/bin/env python3
"""Wordshift-тренды кейса 010 (EcoSwing / СП-генераторы для ветроэнергетики).

S2-сигнал: семантический сдвиг «фундаментальное → инженерное» через монотонные тренды
частоты слов по периодам (метод 006 Amedvedev, аналог wordshift_fluxpump.py).

Источник: data/raw/openalex/ecoswing_corpus.json (1857 сырых; фильтр релевантности как в
паспорте: (wind|turbine|generator|machine) AND (superconduct|HTS|REBCO|YBCO) → 1579 рел.).
Выход: results/case_signals/wordshift_trends_ecoswing.json + печать фокус-групп.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from semantic_shift_v2 import clean_text, tokens  # noqa: E402
from wordshift_fluxpump import analyze_corpus  # noqa: E402  (переиспользуем анализ)

CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "ecoswing_corpus.json"
OUT_DIR = PROJECT_ROOT / "results" / "case_signals"

# Периоды: активность корпуса стартует ~2005 (паспорт: 1990-92:10 → 2023-25:232)
OA_PERIODS = {"-2005": (0, 2005), "2006-09": (2006, 2009), "2010-14": (2010, 2014),
              "2015-19": (2015, 2019), "2020-23": (2020, 2023), "2024-26": (2024, 2026)}

# STOP-слова: базовые (из fluxpump) + тематические стопы + стилистический мусор (LLM-фильтр:
# слова, растущие статистически, но НЕ означающие технологию — improve/demonstrate/achieve/offer…)
STOP_EXTRA = set("""abstract keywords index terms introduction conclusion results discussion
references figure fig table tables shown show shows using used use based due well however
also can may will one two new first last part paper study work year years present presents
performed measured obtained found shows demonstrates case cases different various high low
large small number several many much more most less least between within without with
after before during through under over about into from this these those that which where
when what how why who whose their there here then than both each other another such same
only very just also but and or not no nor for with by to of in on at from the a an is are
was were be been being it its as etc ie eg including include includes included via
respectively corresponding associated related between among non ieee forum news global
edition issue presented at laboratory national institute university center centre group
department division program project report annual final progress wind windturbine windfarm
turbine generator superconducting superconductor superconductivity hts rebco ybco sc machine
electrical electric energy power system systems using based develop developed development
show shows shown result results range ranges design designed can potential possible
increase increased decreases decrease improve improved demonstrate demonstrated achieve
achieved offer offers perform performed available require required operation operating
operate consider considered discuss discussed propose proposed allow allows enable enables
provide provides aim aims""".split())

# Фокус-группы для интерпретации (не стопы, а категории для отчёта)
FOCUS = {
    "приложение-драйвер": ["offshore", "onshore", "nacelle", "tower", "drivetrain", "gearbox",
                            "directdrive", "aircraft", "ship", "vessel", "smes", "hydrogen",
                            "marine", "aviation", "aero", "flying", "electricity", "grid"],
    "инженерия/зрелость (S2)": ["cooling", "cryogenic", "cryostat", "efficiency", "torque",
                                  "density", "weight", "mass", "compact", "reliability", "maintenance",
                                  "cost", "industrial", "commercial", "prototype", "fabrication",
                                  "manufactur", "scaleup", "testing", "fieldtest", "commission",
                                  "infield", "verified", "validation", "kilowatt", "megawatt",
                                  "optimiz", "integration", "rotor", "stator", "armature"],
    "фундамент/эффект": ["discovery", "mechanism", "theoret", "fundament", "phenomen",
                          "novel", "breakthrough", "record", "insight", "understand", "physics"],
    "материал/архитектура": ["coatedconductor", "bstco", "bscCO", "mgb2", "nb3sn", "nbti",
                              "lowtemperature", "magnet", "fieldcoil", "winding", "coil",
                              "permanentmagnet", "ferrite", "ndfeb", "rareearth", "pm",
                              "induction", "synchronous", "dd", "pmsg", "dfig", "pmsm"],
}

# LLM-фильтр: слова-обороты речи, НЕ означающие технологию (исключить из «находок»)
SPEECH_WORDS = set("""improve improve improve demonstrated demonstrate achieve achieved offer
offers perform performed provide provides aim aims enable enables enhance enhanced increase
increases increased decrease decreases reduced reduce reduction potential promising promising
novel new first show shows shown result results discuss discussed propose proposed""".split())


def relevance(w: dict) -> bool:
    t = ((w.get("title") or "") + " " + (w.get("abstract") or "")).lower()
    has_win = any(k in t for k in ["wind ", "turbine", "generator", "machine"])
    has_sc = any(k in t for k in ["superconduct", "hts", "rebco", "ybco", "bsc"])
    return has_win and has_sc


def main() -> None:
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    ws = data if isinstance(data, list) else data.get("works", [])

    texts_by_period: dict[str, list[str]] = {p: [] for p in OA_PERIODS}
    for w in ws:
        ab = w.get("abstract") or ""
        if len(ab) < 40 or not w.get("year"):
            continue
        if not relevance(w):
            continue
        p = next((pp for pp, (a, b) in OA_PERIODS.items() if a <= w["year"] <= b), None)
        if p:
            texts_by_period[p].append(ab)

    res = analyze_corpus(texts_by_period, min_count=3)

    out = OUT_DIR / "wordshift_trends_ecoswing.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    # LLM-фильтр: убрать обороты речи из «находок»
    ranked = [m for m in res["ranked"] if m["word"] not in SPEECH_WORDS and len(m["word"]) > 3]

    print("===== EcoSwing wordshift (%d работ релев., %d слов с трендом) =====" % (
        sum(len(v) for v in texts_by_period.values()), len(ranked)))
    print("Периоды (слов абстрактов):",
          ", ".join(f"{p}:{v}" for p, v in res["period_totals"].items()))

    # Топ-250 генеральных трендов
    print("\n--- ТОП-30 растущих (кроме оборотов речи) ---")
    up = [m for m in ranked if m["trend"] == "up"]
    up.sort(key=lambda m: -(m["freqs"][-1] if m["freqs"][-1] > 0 else m["monotonic"]))
    for m in up[:30]:
        f = ", ".join(f"{x:.1f}" for x in m["freqs"])
        print(f"  {m['word']:<20} ↑ [{f}]")

    print("\n--- ТОП-30 падающих ---")
    dn = [m for m in ranked if m["trend"] == "down"]
    dn.sort(key=lambda m: m["freqs"][0] if m["freqs"][0] > 0 else 1000)
    for m in dn[:30]:
        f = ", ".join(f"{x:.1f}" for x in m["freqs"])
        print(f"  {m['word']:<20} ↓ [{f}]")

    print("\n--- ТОП-10 с экстремумом (пик/впадина) ---")
    ex = [m for m in ranked if m["extremum"]]
    ex.sort(key=lambda m: -max(m["freqs"]))
    for m in ex[:10]:
        f = ", ".join(f"{x:.1f}" for x in m["freqs"])
        print(f"  {m['word']:<20} {m['extremum']} [{f}]")

    # Фокус-группы: суммарная частота по периодам (per 1000 слов)
    print("\n--- ФОКУС-ГРУППЫ (суммарная частота ‰ по периодам) ---")
    for group, words in FOCUS.items():
        sums = [0.0] * len(OA_PERIODS)
        periods = list(OA_PERIODS.keys())
        wf = {w: res["trends"].get(w, {}).get("freqs") for w in words}
        # частоты по словам берём из полного среза: пересчитаем из res
        for w in words:
            fr = res["trends"].get(w, {}).get("freqs")
            if fr:
                for i, x in enumerate(fr):
                    sums[i] += x
        line = ", ".join(f"{s:.1f}" for s in sums)
        print(f"  {group:<32} [{line}]  ({', '.join(periods)})")

    print("\n(JSON:", out, ")")


if __name__ == "__main__":
    main()