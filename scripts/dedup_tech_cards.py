#!/usr/bin/env python3
"""Этап Д2 (ночь 28→29.09): дедупликация карточек — одна технология = одна карточка.

решение команды: «убедиться что нет дубликатов (одна и та же по сути
технология под разными, синонимичными именами)».

Правила (объявлены ДО прогона):
  1. точный дедуп: нормализованное name_en (lower, пунктуация→пробел, схлопывание)
     ИЛИ тот же набор токенов (перестановка) → один кластер;
  2. нечёткий дедуп ВНУТРИ блоков (блок = пара (первый токен, последний токен)
     отсортированного имени + один из топ-linked-тем):
     rapidfuzz token_sort_ratio ≥ 90 → кластер;
  3. хранитель кластера = карточка с максимальным score_ngi (tie → n_recent_sum);
     остальные идут в aliases (термы), из выдачи исключаются;
  4. метка: сколько кластеров/термов схлопнуто — в отчёт, никаких скрытых слияний.

Выход: <in>_dedup.parquet + results/runtime/tech_dedup_report.md
"""
import argparse
import json
import re
import time
from pathlib import Path

import pandas as pd
import rapidfuzz
from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parent.parent


def norm_name(s: str) -> str:
    return " ".join(re.sub(r"[^0-9a-zа-яё]+", " ", str(s).lower()).split())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp",
                    default=str(ROOT / "data/openalex_derived/tech_cards_final.parquet"))
    ap.add_argument("--ratio", type=int, default=90)
    args = ap.parse_args()
    t0 = time.time()
    df = pd.read_parquet(args.inp)
    ok = df[df["status"] == "ok"].copy()
    n0 = len(ok)
    ok["_n"] = ok["name_en"].map(norm_name)
    ok["_key"] = ok["_n"].map(lambda s: " ".join(sorted(s.split())))

    parent = {i: i for i in ok.index}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    # 1) точный дедуп (нормализация + перестановка токенов)
    for key, grp in ok.groupby("_key"):
        if len(grp) > 1:
            idx = list(grp.index)
            for j in idx[1:]:
                union(idx[0], j)

    # 2) нечёткий дедуп внутри блоков (первый+последний токены имени)
    def block_of(s: str) -> tuple[str, str]:
        t = sorted(s.split())
        return (t[0] if t else "", t[-1] if t else "")

    ok["_blk"] = ok["_n"].map(block_of)
    pairs, skipped, skipped_terms = 0, 0, 0
    for blk, grp in ok.groupby("_blk"):
        if len(grp) < 2:
            continue
        if len(grp) > 20000:      # защита от гигантских хаб-блоков
            skipped += 1
            skipped_terms += len(grp)
            continue
        idx = list(grp.index)
        names = grp["_n"].tolist()
        m = rapidfuzz.process.cdist(
            names, names, scorer=fuzz.token_sort_ratio,
            score_cutoff=args.ratio, workers=-1)
        for a in range(len(idx)):
            row = m[a]
            for b in range(a + 1, len(idx)):
                if row[b] >= args.ratio:
                    union(idx[a], idx[b])
                    pairs += 1
        del m

    # 3) сборка кластеров
    ok["_cl"] = [find(i) for i in ok.index]
    keep_rows = []
    for cl, grp in ok.groupby("_cl"):
        grp = grp.sort_values(["score_ngi", "n_recent_sum"],
                              ascending=False, kind="mergesort")
        k = grp.iloc[0]
        aliases = [t for t in grp["term"].tolist() if t != k["term"]]
        keep_rows.append((k.name, aliases))

    alias_map = {}
    for i, al in keep_rows:
        kept_term = ok.loc[i, "term"]
        for a in al:
            alias_map[a] = kept_term
    out = df.copy()
    out["alias_of"] = out["term"].map(alias_map)
    out.loc[(out["status"] == "ok") & (out["term"].isin(alias_map)),
            "status"] = "duplicate"
    out.loc[out["term"].isin(alias_map), "reason"] = "dedup_alias"

    dst = Path(args.inp).with_name(
        Path(args.inp).stem.replace("_final", "") + "_dedup.parquet")
    out.to_parquet(dst, index=False)

    n_alias = len(alias_map)
    lines = [f"# tech_dedup — {time.strftime('%Y-%m-%d %H:%M:%S')}",
             f"\n- вход: {args.inp}; OK до дедупа: {n0:,}",
             f"- схлопнуто термов-алиасов: {n_alias:,} "
             f"({n_alias / max(n0, 1):.1%}); осталось уникальных: {n0 - n_alias:,}",
             f"- пар слито (ratio≥{args.ratio}): {pairs:,}; время {time.time()-t0:.0f} с"]
    if skipped:
        lines.append(f"- ⚠️ ПРОПУЩЕНО БЛОКОВ >20000: {skipped} ({skipped_terms} термов "
                     f"НЕ сравнены попарно — дедуп для них не гарантирован; §9: явная фиксация)")
    lines += [f"- выход: {dst}",
              "\n## Примеры кластеров", ""]
    shown = 0
    for i, al in keep_rows:
        if al and shown < 15:
            lines.append(f"- **{ok.loc[i, 'name_en']}** ← {', '.join(al[:5])}")
            shown += 1
    rp = ROOT / "results/runtime/tech_dedup_report.md"
    rp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:8]))


if __name__ == "__main__":
    main()
