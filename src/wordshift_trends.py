#!/usr/bin/env python3
"""Поиск семантических маркеров с монотонным трендом / экстремумом по времени.

Кейс 001_ibad_mgo, S2. Дискриминация «фундаментальное vs прикладное» по лексике НЕ
работает (см. semantic_shift_v2.md §7-8). Ищем ДРУГИЕ маркеры: слова/понятия,
частота которых МОНОТОННО растёт или падает, или имеет экстремум (пик/впадину).

Источники:
1) SNF-корпус (полные тексты, тег ibad_tapes + контрольные теги)
2) OpenAlex-корпус (абстракты, 426 работ 1997-2026)

Метод: для каждого слова — частота на 1000 слов по периодам; оценка монотонности
(доля инверсий в последовательности частот) и экстремума (позиция максимума/минимума).
Выход: results/case_signals/wordshift_trends_<src>.json + печать ТОП.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from semantic_shift_v2 import clean_text, split_paragraphs, tokens

SNF_DIRS = [
    PROJECT_ROOT / "data" / "raw" / "conferences" / "snf_ieeecsc" / "downloads_renamed",
    PROJECT_ROOT / "data" / "raw" / "conferences" / "snf_ieeecsc" / "downloads_renamed_v2",
]
TOPICS = PROJECT_ROOT / "results" / "snf_index" / "topics_map.json"
CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "ibad_abstracts_corpus.json"
OUT_DIR = PROJECT_ROOT / "results" / "case_signals"

# Периоды для SNF (по 3-4 года) и для OpenAlex (по 4-5 лет)
SNF_PERIODS = {"2008-2011": (2008, 2011), "2012-2015": (2012, 2015),
               "2016-2019": (2016, 2019), "2020-2023": (2020, 2023), "2024-2025": (2024, 2025)}
OA_PERIODS = {"1997-2001": (1997, 2001), "2002-2006": (2002, 2006),
              "2007-2011": (2007, 2011), "2012-2016": (2012, 2016),
              "2017-2021": (2017, 2021), "2022-2026": (2022, 2026)}

# Стоп-слова (дополнительно к tokens())
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
centre group department division program project report annual final progress""".split())

PERIOD_WORDS = re.compile(r"^(20\d\d|19\d\d)$")


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


def year_from_name(name: str) -> int | None:
    m = re.match(r"\((\d{4})\)", name)
    return int(m.group(1)) if m else None


def analyze_monotonic(freqs: list[float]) -> dict:
    """Оценить монотонность и экстремум последовательности частот."""
    n = len(freqs)
    if n < 3:
        return {"monotonic": 0, "trend": "flat", "extremum": None, "freqs": freqs}
    # монотонность: доля пар без инверсии (0..1), отдельно рост и падение
    inc = sum(1 for i in range(n - 1) if freqs[i + 1] >= freqs[i])
    dec = sum(1 for i in range(n - 1) if freqs[i + 1] <= freqs[i])
    inc_ratio = inc / (n - 1)
    dec_ratio = dec / (n - 1)
    # тренд
    if inc_ratio >= 0.8 and freqs[-1] > freqs[0] * 1.3:
        trend = "up"
    elif dec_ratio >= 0.8 and freqs[0] > freqs[-1] * 1.3:
        trend = "down"
    else:
        trend = "flat"
    # экстремум: позиция макс/мин (не на краях)
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
    """Словарь период → список текстов → тренды слов."""
    # частота слов по периодам (на 1000 слов)
    word_freq = {}  # word -> {period: per1000}
    word_count = Counter()
    period_totals = {}
    for p, texts in texts_by_period.items():
        toks = []
        for t in texts:
            toks.extend(tokens(t))
        toks = [w for w in toks if w not in STOP_EXTRA and not PERIOD_WORDS.match(w)]
        total = len(toks)
        period_totals[p] = total
        cnt = Counter(toks)
        for w, c in cnt.items():
            word_count[w] += c
            word_freq.setdefault(w, {})[p] = 1000 * c / total if total else 0

    # тренды
    periods = list(texts_by_period.keys())
    trends = {}
    for w, cf in word_freq.items():
        if word_count[w] < min_count:
            continue
        freqs = [cf.get(p, 0) for p in periods]
        # минимальная частота в период (для шума)
        if max(freqs) < 0.3:
            continue
        m = analyze_monotonic(freqs)
        m["word"] = w
        m["count"] = word_count[w]
        trends[w] = m

    # сортировка: сначала сильные тренды (up/down), потом экстремумы
    def score(m):
        s = 0
        if m["trend"] == "up": s += 100
        elif m["trend"] == "down": s += 90
        if m["extremum"]: s += 50
        s += min(m["monotonic"] * 50, 50)
        return s
    ranked = sorted(trends.values(), key=score, reverse=True)
    return {
        "periods": periods,
        "period_totals": period_totals,
        "trends": {w: {k: v for k, v in m.items() if k != "word"}
                   for w, m in trends.items()},
        "ranked": [m for m in ranked if m["trend"] != "flat" or m["extremum"]],
    }


def main() -> None:
    # ===== SNF: ibad_tapes + контроль =====
    with open(TOPICS) as f:
        tm = json.load(f)

    for tag in ["ibad_tapes", "cables", "fusion"]:
        files = tm.get(tag, [])
        texts_by_period: dict[str, list[str]] = {p: [] for p in SNF_PERIODS}
        for name in files:
            year = year_from_name(name)
            if not year:
                continue
            p = next((p for p, (a, b) in SNF_PERIODS.items() if a <= year <= b), None)
            if not p:
                continue
            pdf = find_snf(name)
            if not pdf:
                continue
            txt = extract_text(pdf)
            clean = clean_text(txt)
            if len(clean) < 500:
                continue
            texts_by_period[p].append(clean)
        res = analyze_corpus(texts_by_period)
        out = OUT_DIR / f"wordshift_trends_snf_{tag}.json"
        out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n===== SNF тег '{tag}' (wordshift тренды) =====")
        print(f"{'слово':<22} {'тренд':<6} {'монот':>5} {'экстр':>8} {'частоты ‰':<45}")
        for m in res["ranked"][:20]:
            f = ", ".join(f"{x:.1f}" for x in m["freqs"])
            print(f"{m['word']:<22} {m['trend']:<6} {m['monotonic']:.2f} "
                  f"{str(m['extremum']):<8} [{f}]")
        print(f"(всего слов с трендом: {len(res['ranked'])})")

    # ===== OpenAlex-корпус (абстракты) =====
    if CORPUS.exists():
        data = json.loads(CORPUS.read_text(encoding="utf-8"))
        texts_by_period: dict[str, list[str]] = {p: [] for p in OA_PERIODS}
        for w in data["works"]:
            ab = w.get("abstract") or ""
            if len(ab) < 40:
                continue
            y = w.get("year")
            p = next((p for p, (a, b) in OA_PERIODS.items() if a <= y <= b), None)
            if p:
                texts_by_period[p].append(ab)
        res = analyze_corpus(texts_by_period, min_count=3)
        out = OUT_DIR / "wordshift_trends_openalex.json"
        out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n===== OpenAlex-корпус (абстракты IBAD) =====")
        print(f"{'слово':<22} {'тренд':<6} {'монот':>5} {'экстр':>8} {'частоты ‰':<55}")
        for m in res["ranked"][:25]:
            f = ", ".join(f"{x:.1f}" for x in m["freqs"])
            print(f"{m['word']:<22} {m['trend']:<6} {m['monotonic']:.2f} "
                  f"{str(m['extremum']):<8} [{f}]")
        print(f"(всего слов с трендом: {len(res['ranked'])})")


if __name__ == "__main__":
    main()
