#!/usr/bin/env python3
"""build_children_store.py — конкатенация child-тем всех доменов →
webapp/data/children/children.parquet (V1-показ, штурм 27.09).

Вход:  /mnt/e/openalex_derived/termtech_*/segments/child_topics.parquet
Выход: webapp/data/children/children.parquet
       {parent_tid:int, child_id:str, rep_term:str, n_terms:int, df_sum:int,
        parent_cos:float, profile:str  (rep_term + terms, lowercase — для rel)}
Запуск: .venv/bin/python scripts/build_children_store.py  (повторяемый, идемпотентный)
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = sorted(Path("/mnt/e/openalex_derived").glob("termtech_*/segments/child_topics.parquet"))
OUT = ROOT / "webapp/data/children/children.parquet"


def main() -> int:
    if not SRC:
        print("нет segments/child_topics.parquet")
        return 1
    frames = []
    for p in SRC:
        df = pd.read_parquet(p)
        df["domain"] = p.parent.parent.name.replace("termtech_", "")
        frames.append(df)
        print(f"{p.parent.parent.name}: {len(df)} child")
    all_ch = pd.concat(frames, ignore_index=True)
    all_ch["parent_tid"] = (
        all_ch["parent_id"].astype(str).str.rstrip("/").str.split("T").str[-1].astype(int))
    # дедуп (27.09): одинаковый rep_term у одного parent из разных доменов —
    # оставить наиболее df_sum-тяжёлого (снимает видимые дубли «iot ×3» в выдаче)
    _before = len(all_ch)
    all_ch = (all_ch.sort_values("df_sum", ascending=False)
              .drop_duplicates(subset=["parent_tid", "rep_term"], keep="first"))
    if len(all_ch) < _before:
        print(f"дедуп: {_before} → {len(all_ch)} (снято {_before - len(all_ch)} дублей)")
    # профиль ребёнка для rel = rep_term + terms
    terms_lists = all_ch["terms"].apply(
        lambda s: json.loads(s) if isinstance(s, str) else list(s))
    all_ch["profile"] = (
        all_ch["rep_term"].astype(str).str.lower() + " " +
        terms_lists.apply(lambda L: " ".join(str(t).lower() for t in L)))
    out = all_ch[["parent_tid", "child_id", "rep_term", "n_terms", "df_sum",
                  "parent_cos", "domain", "profile"]]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT, index=False)
    print(f"→ {OUT}: {len(out)} child, {out.parent_tid.nunique()} parent'ов")
    return 0


if __name__ == "__main__":
    sys.exit(main())
