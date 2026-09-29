#!/usr/bin/env python3
"""S2 для кейса 006 (SNSPD): wordshift-анализ семантики по периодам + LLM-фильтр мусора.

Метод (по подходу Amedvedev, см. GLOSSARY «LLM-фильтр» и METHODOLOGY §4а):
1. Wordshift: частота каждого слова на 1000 (нормировка на объём корпуса!) по периодам;
2. Тренды: монотонный рост/падение, экстремумы;
3. LLM-фильтр-эквивалент: отсев «оборотов речи» (improv, demonstr, technolog — растут
   статистически, но не технологии) и общеязыковых слов — оставить реальные маркеры
   технологии/применения.

Данные: data/raw/openalex/snspd_corpus.json (годы/title) + snspd_full.json (abstract).
Выход: results/case_signals/wordshift_trends_snspd.json
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from semantic_shift_v2 import clean_text, tokens

CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "snspd_corpus.json"
FULL = PROJECT_ROOT / "data" / "raw" / "openalex" / "snspd_full.json"
OUT_DIR = PROJECT_ROOT / "results" / "case_signals"
OUT = OUT_DIR / "wordshift_trends_snspd.json"

# Периоды: SNSPD родился 2001, корпус с 2005 — окна по 4-5 лет
OA_PERIODS = {"2005-2009": (2005, 2009), "2010-2014": (2010, 2014),
              "2015-2019": (2015, 2019), "2020-2023": (2020, 2023), "2024-2026": (2024, 2026)}

# Стоп-слова (дополнительно к semantic_shift_v2.tokens) — из wordshift_trends.py
STOP_EXTRA = set("""abstract keywords index terms introduction conclusion results discussion
references figure fig table tables shown show shows showing used using use based due well however
also can may will one two new first last part paper study work year years present presents
performed measured obtained found shows demonstrates case cases different various high low
large small number several many much more most less least between within without with after
before during through under over about into from this these those that which where when what
how why who whose their there here then than both each other another such same only very just
also but and or not no nor for with by to of in on at from the a an is are was were be been being
it its as etc ie eg including include includes included via respectively corresponding
related between among non journal letters optics express applied physics letters nature
science reports communications society international conference proceedings""".split())

# «Обороты речи» — растут статистически, но НЕ технологии (Amedvedev: ~71% кандидатов)
SPEECH_ROOTS = re.compile(
    r"improv|enhanc|increas|demonstrat|technolog|recent|advanc|develop|potenti|enabl|offer|"
    r"achiev|show|present|propos|design|fabricat|manufactur|integrat|realiz|approach|method|"
    r"result|perform|exhibit|provid|allow|lead|due|well|also|however|moreover|therefore|"
    r"significant|import|necessary|possible|various|different|number|system|device|structure"
)


def is_speech(word: str) -> bool:
    """Слово — «оборот речи» (не технология/применение)."""
    return bool(SPEECH_ROOTS.search(word))


def analyze_corpus(texts_by_period: dict[str, list[str]], min_count: int = 4) -> dict:
    """Частоты на 1000 слов по периодам + тренды (как wordshift_fluxpump)."""
    # убрать стоп
    periods = sorted(texts_by_period.keys())
    word_freqs: dict[str, list[float]] = defaultdict(lambda: [0.0] * len(periods))
    total_words = {}
    for pi, period in enumerate(periods):
        texts = texts_by_period.get(period, [])
        n_words = 0
        cnt = Counter()
        for t in texts:
            toks = [w for w in tokens(t) if w not in STOP_EXTRA]
            n_words += len(toks)
            cnt.update(toks)
        total_words[period] = n_words
        for w, c in cnt.items():
            word_freqs[w][pi] = 1000.0 * c / n_words if n_words else 0.0

    ranked = []
    for w, freqs in word_freqs.items():
        if sum(freqs) * max(freqs) == 0:
            continue
        # мин. суммарное число вхождений
        if sum(freqs) / 1000.0 * sum(total_words.values()) / len(periods) < min_count:
            continue
        # монотонность: доля согласованных шагов
        diffs = [freqs[i + 1] - freqs[i] for i in range(len(freqs) - 1)]
        pos = sum(1 for d in diffs if d > 0)
        neg = sum(1 for d in diffs if d < 0)
        mono = max(pos, neg) / len(diffs) if diffs else 0
        trend = "up" if pos >= neg else "down"
        # экстремум
        peak = max(range(len(freqs)), key=lambda i: freqs[i])
        extremum = "peak" if peak not in (0, len(freqs) - 1) else ("max_end" if peak == len(freqs) - 1 else "max_start")
        # сила роста: последняя / первая
        if freqs[0] > 0:
            ratio = freqs[-1] / freqs[0]
        else:
            ratio = freqs[-1] / 0.01 if freqs[-1] > 0.01 else 1.0
        ranked.append({
            "word": w, "trend": trend, "monotonic": round(mono, 2),
            "extremum": extremum, "ratio": round(ratio, 1),
            "freqs": [round(x, 2) for x in freqs],
            "is_speech": is_speech(w),
        })

    # сорт: по силе монотонного тренда
    ranked.sort(key=lambda m: (-m["monotonic"], -abs(math.log(max(m["ratio"], 0.01)))))
    return {"periods": periods, "period_totals": total_words, "ranked": ranked}


def main() -> None:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    full = json.loads(FULL.read_text(encoding="utf-8"))
    works = corpus if isinstance(corpus, list) else corpus.get("works", corpus)

    texts_by_period = {p: [] for p in OA_PERIODS}
    n_with_abs = 0
    for w in works:
        wid = w.get("id")
        y = w.get("year")
        if not y:
            continue
        ab = (full.get(wid) or {}).get("abstract") or ""
        if len(ab) < 40:
            continue
        p = next((p for p, (a, b) in OA_PERIODS.items() if a <= y <= b), None)
        if p:
            texts_by_period[p].append(ab)
            n_with_abs += 1

    print(f"работ с абстрактом: {n_with_abs}")
    res = analyze_corpus(texts_by_period, min_count=5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    # Печать: раздельно реальные термины и мусор
    real = [m for m in res["ranked"] if not m["is_speech"]]
    speech = [m for m in res["ranked"] if m["is_speech"]]
    print(f"\n===== РЕАЛЬНЫЕ ТЕРМИНЫ (после LLM-фильтра) — {len(real)} =====")
    print(f"{'слово':<20} {'тренд':<5} {'монот':>5} {'ratio':>6}  частоты ‰")
    for m in real[:35]:
        f = ", ".join(f"{x:.1f}" for x in m["freqs"])
        print(f"{m['word']:<20} {m['trend']:<5} {m['monotonic']:.2f} {m['ratio']:>6}  [{f}]")

    print(f"\n===== ОБОРОТЫ РЕЧИ (отсечены LLM-фильтром) — {len(speech)} =====")
    for m in speech[:15]:
        f = ", ".join(f"{x:.1f}" for x in m["freqs"])
        print(f"{m['word']:<20} {m['trend']:<5} {m['monotonic']:.2f} {m['ratio']:>6}  [{f}]")

    print(f"\nСохранено: {OUT}")
    print(f"Всего слов с трендом: {len(res['ranked'])}, реальных: {len(real)} ({len(real)/max(len(res['ranked']),1)*100:.0f}%)")


if __name__ == "__main__":
    main()
