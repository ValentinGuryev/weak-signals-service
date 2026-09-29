#!/usr/bin/env python3
"""Этап А ночи 28→29.09: сборка единого пуля технологий (~105k) — NJ-14 v2.

Вход:  results/termtech_*/candidates_clean.parquet (9 доменов) + webapp/data/tech_ngi.parquet (sp).
Выход: data/openalex_derived/tech_pool_v1.parquet + results/runtime/tech_pool_v1_report.md

Правила (объявлены ДО прогона):
  нормализация: lower, дефис→пробел, схлопывание пробелов;
  ворота: 2 <= n_tok <= 6; НЕ snippet (is_snippet); НЕ GENERIC-фраза/модификатор
  (Medvedev: GENERIC_MODS_EXACT/-SUFFIX/GENERIC_PHRASES); НЕ GARBAGE_RE;
  df_sum >= 2. Всё счётчиком в отчёт — ворота можно пересмотреть утром (не скрыто).
  Дедуп: по term_norm; df/n_recent — сумма по доменам, first_year — минимум,
  growth/kpmi — максимум. sp-термы вносятся с birth/score/series/linked.
"""
import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_tech_ngi import (GENERIC_MODS_EXACT, GENERIC_MODS_SUFFIX,  # noqa: E402
                            GENERIC_PHRASES, is_snippet)
from rank_directions_ngi import GARBAGE_RE  # noqa: E402

OUT = ROOT / "data/openalex_derived/tech_pool_v1.parquet"
REPORT = ROOT / "results/runtime/tech_pool_v1_report.md"


def norm(s: str) -> str:
    return " ".join(s.lower().replace("-", " ").split())


def main() -> None:
    t0 = time.time()
    stats: dict[str, int] = {}
    frames = []
    for f in sorted(ROOT.glob("results/termtech_*/candidates_clean.parquet")):
        d = pd.read_parquet(f, columns=["term", "n_tok", "df", "first_year",
                                        "growth", "n_recent", "n_base", "kpmi"])
        d["domain"] = f.parent.name.replace("termtech_", "")
        frames.append(d)
    raw = pd.concat(frames, ignore_index=True)
    stats["строк во входных сторах"] = len(raw)

    raw["_n"] = raw["term"].map(norm)
    stats["уникальных после нормализации"] = raw["_n"].nunique()

    # ворота (по терм-группе — решение принимается по любому представителю)
    grp = raw.groupby("_n", sort=False)
    base = pd.DataFrame({
        "term": grp["term"].first(),
        "n_tok": grp["n_tok"].max(),
        "df_sum": grp["df"].sum(),
        "n_recent_sum": grp["n_recent"].sum(),
        "first_year": grp["first_year"].min(),
        "growth": grp["growth"].max(),
        "kpmi": grp["kpmi"].max(),
        "n_domains": grp["domain"].nunique(),
    }).reset_index()
    stats["уникальных в агрегате"] = len(base)

    def keep(row) -> tuple[bool, str]:
        t = row["term"]
        tl = t.lower()
        if not (2 <= row["n_tok"] <= 6):
            return False, "n_tok"
        if is_snippet(t):
            return False, "snippet"
        toks = set(tl.replace("-", " ").split())
        if tl in GENERIC_PHRASES:
            return False, "generic_phrase"
        if any(t in GENERIC_MODS_EXACT or t.endswith(GENERIC_MODS_SUFFIX)
               for t in toks):
            return False, "generic_mod"
        if GARBAGE_RE.search(t):
            return False, "garbage_re"
        if row["df_sum"] < 2:
            return False, "df<2"
        return True, ""

    verdicts = base.apply(keep, axis=1, result_type="expand")
    base["ok"], base["drop"] = verdicts[0], verdicts[1]
    for r, n in base[~base["ok"]]["drop"].value_counts().items():
        stats[f"отсев {r}"] = int(n)
    pool = base[base["ok"]].drop(columns=["ok", "drop"]).reset_index(drop=True)
    stats["ПУЛ после ворот"] = len(pool)

    # sp-слой (6238 термов tech_ngi: birth/score/series/linked)
    sp = pd.read_parquet(ROOT / "webapp/data/tech_ngi.parquet")
    sp["_n"] = sp["term"].map(norm)
    stats["sp термов"] = len(sp)
    have = set(pool["_n"])
    add = sp[~sp["_n"].isin(have)].copy()
    stats["sp только (новые)"] = len(add)
    new = pd.DataFrame({
        "_n": add["_n"], "term": add["term"], "n_tok": add["term"].map(
            lambda t: len(t.split())),
        "df_sum": add["df"], "n_recent_sum": add["n_recent"],
        "first_year": add["birth"], "growth": add["growth"], "kpmi": 0.0,
        "n_domains": 0,
    })
    pool = pd.concat([pool, new], ignore_index=True)
    # sp-статы для всех sp-термов (в т.ч. уже известных)
    sp_cols = sp.set_index("_n")[["birth", "score", "novelty", "growth",
                                  "impact", "series_json", "linked_json"]]
    pool = pool.merge(sp_cols, left_on="_n", right_index=True, how="left")
    pool["source"] = ["sp" if pd.notna(s) else "domain"
                      for s in pool["score"]]
    stats["ИТОГО пул"] = len(pool)
    stats["в т.ч. sp"] = int((pool["source"] == "sp").sum())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pool.to_parquet(OUT, index=False)

    lines = [f"# tech_pool_v1 — {time.strftime('%Y-%m-%d %H:%M:%S')}",
             f"\nВыход: `{OUT}` ({OUT.stat().st_size // 1024 // 1024} МБ)\n",
             "| этап | count |", "|---|---|"]
    lines += [f"| {k} | {v:,} |".replace(",", " ") for k, v in stats.items()]
    lines.append(f"\nВремя: {time.time()-t0:.0f} с. Ворота — в докстринге скрипта (объявлены ДО).")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
