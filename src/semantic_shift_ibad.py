#!/usr/bin/env python3
"""Семантический сдвиг S2 по IBAD: «показали эффект» → «оптимизировали условия».

Источник 1: SNF-доклады (полные тексты, 474 PDF, 2008-2025).
Источник 2: заголовки OpenAlex (81 строгая IBAD-статья).

Метрика: доля «инжиниринговой» лексики (производство, оптимизация, R2R,
скорость, масштаб) vs «эффектной» (свойства, рекорд, возможность, перспектива).
Считаем по абзацам: абзац инжиниринговый, если в нём ≥1 маркер инжиниринга
И нет маркера «эффекта» (или маркеров инжиниринга больше).

Идея (из METHODOLOGY §4a): зреющая технология смещается от «мы показали,
что работает» к «мы оптимизировали условия производства». Это сигнал S2 —
стадия зрелости (гейт).

Выход: results/case_signals/... → печать в консоль (данные для графика).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNF_DIRS = [
    PROJECT_ROOT / "data" / "raw" / "conferences" / "snf_ieeecsc" / "downloads_renamed",
    PROJECT_ROOT / "data" / "raw" / "conferences" / "snf_ieeecsc" / "downloads_renamed_v2",
]
TOPICS = PROJECT_ROOT / "results" / "snf_index" / "topics_map.json"
OPENALEX = PROJECT_ROOT / "data" / "raw" / "openalex" / "ibad_mgo_competitors.json"

# ---- Лексика ----
# Инжиниринг / производство (S2 «открытие → оптимизация»)
ENG_WORDS = re.compile(
    r"production|manufactur|fabricat|industrial|commercial|reel[\s-]?to[\s-]?reel|R2R|"
    r"high[\s-]?rate|throughput|scale[\s-]?up|scalab|mass[\s-]?produc|"
    r"optimiz|improve|process|cost[\s-]?reduc|yield|long[\s-]?length|"
    r"continuous|automated|in[\s-]?line|on[\s-]?line|prototype|pilot",
    re.I)
# Эффект / открытие / рекорд
EFF_WORDS = re.compile(
    r"demonstrat|discover|first[\s-]?time|record|breakthrough|"
    r"achieve|possib|potential|promis|novel|new[\s-]?concept|"
    r"remarkable|superior|enhanc|improv|increase",
    re.I)

# ---- Агрегированная лексика для SNF (из wordshift-анализа) ----
# Прикладная/системная лексика (растёт): устройства, применение, интеграция
APPL_WORDS = re.compile(
    r"applications?|fusion|energy|power|magnets?|quantum|cables?|cooling|technology|devices?|"
    r"systems?|integration|wind|aviation|medical|accelerator|tokamak|grid|motor|generator",
    re.I)
# Научно-конкретная лексика (падает): лента, свойства, эффект
LAB_WORDS = re.compile(
    r"ybco|critical|loss|vortex|coil|voltage|tape|wire|films?|fault|sample|measured|"
    r"current density|flux|substrate|layer|resistance|temperature dependence",
    re.I)


def find_snf(name: str) -> Path | None:
    for d in SNF_DIRS:
        p = d / name
        if p.exists():
            return p
    return None


def extract_text(pdf: Path) -> str:
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
        out = tf.name
    try:
        subprocess.run(["pdftotext", str(pdf), out], check=True, timeout=60,
                       capture_output=True)
        return open(out, encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""
    finally:
        Path(out).unlink(missing_ok=True)


def split_paragraphs(text: str) -> list[str]:
    """Разбить на абзацы (по пустым строкам / большим разрывам)."""
    text = re.sub(r"\s+", " ", text)          # схлопнуть пробелы
    # абзацы по границам предложений, длина > 40 символов
    paras = [p.strip() for p in re.split(r"(?<=[.!?])\s+(?=[A-ZА-Я])", text) if len(p.strip()) > 40]
    return paras


def classify(paras: list[str]) -> tuple[int, int, int]:
    """Вернуть (инжиниринг, эффект, нейтрально)."""
    eng = eff = neu = 0
    for p in paras:
        e = bool(ENG_WORDS.search(p))
        f = bool(EFF_WORDS.search(p))
        if e and not f:
            eng += 1
        elif f and not e:
            eff += 1
        else:
            neu += 1
    return eng, eff, neu


def analyze_text(text: str) -> dict:
    paras = split_paragraphs(text)
    eng, eff, neu = classify(paras)
    total = eng + eff + neu
    return {
        "paragraphs": total,
        "eng": eng, "eff": eff, "neu": neu,
        "eng_share": eng / total if total else 0,
        "eff_share": eff / total if total else 0,
    }


def main() -> None:
    # ---- SNF ----
    with open(TOPICS) as f:
        tm = json.load(f)
    ibad = tm.get("ibad_tapes", [])

    periods = {"2008-2010": (2008, 2010), "2011-2013": (2011, 2013),
               "2014-2016": (2014, 2016), "2017-2019": (2017, 2019),
               "2020-2022": (2020, 2022), "2023-2025": (2023, 2025)}
    agg = {p: {"n": 0, "eng": 0, "eff": 0, "neu": 0, "paras": 0,
               "appl": 0, "lab": 0, "words": 0} for p in periods}
    failed = 0

    for name in ibad:
        m = re.match(r"\((\d{4})\)", name)
        if not m:
            continue
        year = int(m.group(1))
        period = next((p for p, (a, b) in periods.items() if a <= year <= b), None)
        if not period:
            continue
        pdf = find_snf(name)
        if not pdf:
            failed += 1
            continue
        txt = extract_text(pdf)
        if len(txt) < 300:
            failed += 1
            continue
        r = analyze_text(txt)
        agg[period]["n"] += 1
        agg[period]["eng"] += r["eng"]
        agg[period]["eff"] += r["eff"]
        agg[period]["neu"] += r["neu"]
        agg[period]["paras"] += r["paragraphs"]
        # агрегированная лексика (по словам)
        words = re.findall(r"[a-zA-Z][a-zA-Z\-]{3,}", txt.lower())
        agg[period]["words"] += len(words)
        agg[period]["appl"] += sum(1 for w in words if APPL_WORDS.search(w))
        agg[period]["lab"] += sum(1 for w in words if LAB_WORDS.search(w))

    print("=== SNF: семантический сдвиг по периодам ===")
    print(f"{'период':<10} {'докл':>4} {'абзацы':>7} {'инж%':>6} {'эфф%':>6} {'нейтр%':>7}")
    for p, (a, b) in periods.items():
        d = agg[p]
        tot = d["eng"] + d["eff"] + d["neu"]
        eng_p = 100 * d["eng"] / tot if tot else 0
        eff_p = 100 * d["eff"] / tot if tot else 0
        neu_p = 100 * d["neu"] / tot if tot else 0
        print(f"{p:<10} {d['n']:>4} {d['paras']:>7} {eng_p:>5.1f}% {eff_p:>5.1f}% {neu_p:>6.1f}%")
    print(f"(не извлечено: {failed})")

    print("\n=== SNF: прикладная vs лабораторная лексика (на 1000 слов) ===")
    print(f"{'период':<10} {'докл':>4} {'слов':>8} {'прикладн%':>9} {'лаборат%':>9} {'Δ':>7}")
    for p, (a, b) in periods.items():
        d = agg[p]
        if not d["words"]:
            continue
        appl_p = 1000 * d["appl"] / d["words"]
        lab_p = 1000 * d["lab"] / d["words"]
        print(f"{p:<10} {d['n']:>4} {d['words']:>8} {appl_p:>8.2f} {lab_p:>8.2f} {appl_p-lab_p:>+6.2f}")

    # ---- OpenAlex заголовки ----
    print("\n=== OpenAlex: заголовки строгих IBAD-статей ===")
    with open(OPENALEX) as f:
        comps = json.load(f)
    pat = re.compile(r"\bIBAD\b|ion[\s-]?beam[\s-]?assisted", re.I)
    works = [w for w in comps["ibad_mgo"]["works"] if pat.search(w.get("title", ""))]
    oa_periods = {"<2008": lambda y: y < 2008, "2008-2015": lambda y: 2008 <= y <= 2015,
                  ">2015": lambda y: y > 2015}
    oa_agg = {p: {"n": 0, "eng": 0, "eff": 0, "neu": 0} for p in oa_periods}
    for w in works:
        y = w.get("year")
        if not y:
            continue
        period = next((p for p, fn in oa_periods.items() if fn(y)), None)
        if not period:
            continue
        t = w.get("title", "")
        e = bool(ENG_WORDS.search(t))
        f = bool(EFF_WORDS.search(t))
        oa_agg[period]["n"] += 1
        if e and not f:
            oa_agg[period]["eng"] += 1
        elif f and not e:
            oa_agg[period]["eff"] += 1
        else:
            oa_agg[period]["neu"] += 1
    print(f"{'период':<10} {'статей':>5} {'инж%':>6} {'эфф%':>6} {'нейтр%':>7}")
    for p in oa_periods:
        d = oa_agg[p]
        tot = d["eng"] + d["eff"] + d["neu"]
        if not tot:
            continue
        print(f"{p:<10} {d['n']:>5} {100*d['eng']/tot:>5.1f}% {100*d['eff']/tot:>5.1f}% {100*d['neu']/tot:>6.1f}%")

    # примеры заголовков
    print("\nПримеры заголовков по периодам (OpenAlex):")
    for p, fn in oa_periods.items():
        ws = [w for w in works if w.get("year") and fn(w["year"])]
        ws.sort(key=lambda w: w.get("cited_by_count", 0), reverse=True)
        if ws:
            print(f"  {p}: " + " | ".join(w["title"][:55] for w in ws[:3]))


if __name__ == "__main__":
    main()
