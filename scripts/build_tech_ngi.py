#!/usr/bin/env python3
"""build_tech_ngi.py — Оценка ТЕХНОЛОГИЙ (мелких тем) по канону NGI.

Идея 1+2 (согласовано автором 28.09): технологии = emerging-термы sp-стора,
Оценка = новизна × рост × воздействие — те же формулы, что у крупных тем:

  * series/birth — из results/termtech/_yeardf (word×year×df, 2016..; cap=2025);
    birth = правило «затишье сбрасывает» (mirror rank_directions_ngi.birth_from_histogram);
  * novelty = 1 − sigmoid((age−15)/5), age = 2025 − birth;
  * growth  = g/(g+1), g = N(2023..2025)/N(2021..2022); N_раннее=0, N_позднее>0 → 1.0;
  * impact  = 1 − exp(−impact/40); impact = max накопленных входящих цитат связанных
    КРУПНЫХ тем (наследие: технология ⊂ тема) — связка терм↔тема:
      (а) терм ∈ n-граммах профилей children → parent_tid;
      (б) терм ∈ заголовках топ-работ digest → tid.
    Связка ≥1 тема = технология считается «частью» таксономии (иначе — не в пул).

Пул: first_year ≥ 2018 (порог автора) AND n_recent ≥ 5 (фильтр пайплайна).

Выход: webapp/data/tech_ngi.parquet
  term, first_year, n_recent, df, birth, novelty, growth, impact, score,
  series_json, linked_json (tid'ы, по убыванию impact)

Запуск: .venv/bin/python scripts/build_tech_ngi.py
"""
import glob
import json
import math
import os
import zlib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
Y_WINDOW = 2025
OUT = ROOT / "webapp" / "data" / "tech_ngi.parquet"


def log(m: str) -> None:
    print(m, flush=True)


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


# Фильтр обрывков абстрактов (фикс 28.09: «within a finite», «strategy to mitigate»
# проходили R-фильтры и попадали в топ по косинусу). Обрывок = служебные слова
# внутри фразы ИЛИ >5 слов.
SNIPPET_STOP = {
    "the", "of", "to", "within", "we", "our", "us", "is", "are", "be", "by",
    "on", "in", "at", "for", "with", "from", "that", "this", "it", "its",
    "which", "who", "show", "shows", "demonstrate", "contains", "using",
    "based", "using", "via", "into", "than", "such", "also", "however",
    "provide", "provided", "focused", "aimed", "recently", "increasingly",
}

# Мусор «на базе / на основе X» ( Medvedev, 28.09): модификаторные коллокации —
# НЕ технологии. Ловим по суффиксам/participial-модификаторам и явным словам.
GENERIC_MODS_EXACT = {
    "cutting-edge", "state-of-the-art", "advanced", "modern", "latest", "novel",
    "emerging", "new", "key", "based", "powered", "driven", "enabled",
    "assisted", "augmented", "enhanced", "oriented", "related", "specific",
    "dependent", "intensive", "grade", "level", "scale", "generative-ai",
}
GENERIC_MODS_SUFFIX = (
    "-based", "-powered", "-driven", "-enabled", "-assisted", "-augmented",
    "-oriented", "-related", "-enhanced", "-dependent", "-intensive",
    "-specific", "-aware", "-agnostic", "-ready", "-generated",
)
# Точные фразы-посуда (решение команды: «ai tools», «ai technologies» —
# не технологии, а общие слова)
GENERIC_PHRASES = {"ai tools", "ai technologies"}


def is_snippet(term: str) -> bool:
    w = term.lower().split()
    return len(w) > 5 or bool(set(w) & SNIPPET_STOP)


def is_generic_mod(term: str) -> bool:
    """True для «ai-powered», «machine learning-based», «ai tools»…"""
    tl = term.lower().replace("_", " ").strip()
    if tl in GENERIC_PHRASES:
        return True
    for tok in tl.split():
        if tok in GENERIC_MODS_EXACT or tok.endswith(GENERIC_MODS_SUFFIX):
            return True
    return False


def birth_rule(years_desc_present: list[int]) -> int | None:
    """Mirror rank_directions_ngi.birth_from_histogram (cap=2025)."""
    if not years_desc_present:
        return None
    ys = sorted(years_desc_present)
    seg = ys[-1]
    for y in reversed(ys[:-1]):
        if seg - y >= 3:
            break
        seg = y
    return seg


def main() -> None:
    # ---- пул emerging-термов --------------------------------------------
    sp = pd.read_parquet(ROOT / "webapp/data/termtech_sp/candidates_clean.parquet")
    em = sp[(sp.first_year.fillna(9999) >= 2018) & (sp.n_recent >= 5)].copy()
    log(f"пул emerging (fy>=2018, n_recent>=5): {len(em)}")
    em = em[~em.term.astype(str).map(is_snippet)]
    log(f"после фильтра обрывков: {len(em)}")
    em = em[~em.term.astype(str).map(is_generic_mod)]
    log(f"после фильтра коллокаций «на базе/на основе»: {len(em)}")

    # ---- годовые ряды ТЕРМОВ (cap 2025) ---------------------------------
    # в _yeardf два набора: wyear=* (unigram, НЕ берём) и year=* (term, фразы — берём)
    files = sorted(glob.glob(str(ROOT / "results/termtech/_yeardf/year=*.parquet")))
    pool_set = set(em.term.str.lower())
    parts = []
    for f in files:
        p = pd.read_parquet(f, columns=["term", "year", "df"])
        p = p[p.term.str.lower().isin(pool_set)]
        parts.append(p)
    ydf = pd.concat(parts, ignore_index=True)
    del parts
    ydf = ydf[ydf.year <= Y_WINDOW]
    ydf = ydf.groupby(["term", "year"], as_index=False)["df"].sum()
    log(f"yeardf(term): {len(ydf)} терм-год, термов {ydf.term.nunique()}, "
        f"лет {int(ydf.year.min())}..{int(ydf.year.max())}")

    ser = {w.lower(): g.set_index("year")["df"].to_dict()
           for w, g in ydf.groupby("term")}
    del ydf

    # ---- связка терм ↔ крупная тема --------------------------------------
    # (а) children: n-граммы профилей → parent_tid
    ch = pd.read_parquet(ROOT / "webapp/data/children/children.parquet")
    prof_map: dict[str, set[int]] = {}
    for p, parent in zip(ch.profile.fillna("").str.lower(), ch.parent_tid):
        w = p.split()
        for k in range(1, 7):
            for i in range(len(w) - k + 1):
                prof_map.setdefault(" ".join(w[i:i + k]), set()).add(int(parent))
    del ch
    log(f"дети: n-грамм {len(prof_map)}")

    # (б) digest: crc32 n-грамм заголовков → tid
    dg = pd.read_parquet(ROOT / "webapp/data/digest/digest.parquet",
                         columns=["tid", "title"])
    dig_map: dict[int, set[int]] = {}
    for t, tid in zip(dg.title.fillna("").str.lower(), dg.tid):
        w = t.split()
        for k in range(1, 7):
            for i in range(len(w) - k + 1):
                dig_map.setdefault(zlib.crc32(" ".join(w[i:i + k]).encode()),
                                   set()).add(int(tid))
    del dg
    log(f"digest: n-грамм {len(dig_map)}")

    # ---- impact крупных тем ----------------------------------------------
    imp_df = pd.read_parquet(ROOT / "webapp/data/ngi/topic_ngi_cache_impact.parquet")
    IMPACT = dict(zip(imp_df.tid.astype(int), imp_df.impact.astype(int)))
    del imp_df

    # ---- сборка строк ------------------------------------------------------
    rows, drop_noseries, drop_nolink = [], 0, 0
    for r in em.itertuples():
        term = str(r.term)
        s = ser.get(term.lower())
        if not s:
            drop_noseries += 1
            continue
        linked = set(prof_map.get(term.lower(), ()))
        linked |= dig_map.get(zlib.crc32(term.lower().encode()), set())
        linked = {t for t in linked if t in IMPACT}
        if not linked:
            drop_nolink += 1
            continue
        years = [y for y in s if s[y] > 0]
        b = birth_rule(years)
        if b is None:
            drop_noseries += 1
            continue
        age = max(Y_WINDOW - b, 0)
        novelty = 1.0 - sigmoid((age - 15) / 5.0)
        n_late = sum(s.get(y, 0) for y in (2023, 2024, 2025))
        n_early = sum(s.get(y, 0) for y in (2021, 2022))
        if n_late == 0 and n_early == 0:
            drop_noseries += 1
            continue
        g = float("inf") if n_early == 0 else n_late / max(n_early, 1e-9)
        growth = 1.0 if (n_early == 0 and n_late > 0) else g / (g + 1.0)
        impact = max(IMPACT[t] for t in linked)
        impact_n = 1.0 - math.exp(-impact / 40.0)
        score = novelty * growth * impact_n
        linked_sorted = sorted(linked, key=lambda t: -IMPACT[t])
        series = {str(y): int(s[y]) for y in sorted(s) if s[y] > 0}
        rows.append({
            "term": term, "first_year": int(r.first_year), "n_recent": int(r.n_recent),
            "df": int(r.df), "birth": int(b),
            "novelty": round(novelty, 4), "growth": round(growth, 4),
            "impact": round(impact_n, 4), "score": round(score, 4),
            "series_json": json.dumps(series, ensure_ascii=False),
            "linked_json": json.dumps(linked_sorted[:10], ensure_ascii=False),
        })

    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT, index=False)
    log(f"ИТОГО технологий в пуле: {len(out)} "
        f"(выброшено: нет ряда/активности {drop_noseries}, нет связи с темой {drop_nolink})")
    log(f"score: min={out.score.min():.3f} med={out.score.median():.3f} max={out.score.max():.3f}")
    log(f"birth: min={out.birth.min()} max={out.birth.max()} (медиана {int(out.birth.median())})")
    log(f"-> {OUT} ({OUT.stat().st_size/1e6:.1f} МБ)")


if __name__ == "__main__":
    main()
