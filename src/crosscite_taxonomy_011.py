#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 011: матрица взаимных цитирований между таксономическими группами (S3-cross-taxonomy).

Строит ориентированную матрицу цитирований: из группы X в группу Y =
число работ группы X, ссылающихся на работы группы Y (внутри корпуса 19999 работ).
Разбивка: всего / до окна (≤2018) / после окна (2019+).

Вход: data/raw/openalex/srf_corpus.json + srf_problem_supplement.json
Выход: печать матриц; сигнальный файл пишется отдельным шагом.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- группы (приоритет: первый матч, как в таксономии) ---
GROUPS = [
    ("Nb3Sn (тренд)",        r"nb\s*3\s*sn|niobium[\s-]?tin|niob[\s-]?tin|\bb3sn\b", None),
    ("Nb bulk (зрелый)",     r"\bniobium\b|\bNb\b", None),
    ("Др.СП-материалы",      r"\bNbN\b|\bNbTiN\b|\bMgB2\b|SIS multilayer", None),
    ("SRF-системы",          r"cryomodule|cryoplant|XFEL|international linear collider|FCC|CEPC|energy recovery linac", None),
    ("NC/медь",              r"normal conducting|copper|CLIC|two-beam", None),
    ("Диэлектрич./THz",      r"dielectric laser|dielectric wakefield|THz|photonic", None),
    ("Плазма/лазер",         r"plasma wakefield|laser wakefield|laser plasma accelerator|plasma acceleration", None),
]
C = [(n, re.compile(p, re.I)) for n, p, _ in GROUPS]
NAMES = [n for n, _, _ in GROUPS]


def classify(txt: str) -> int | None:
    for i, (_, p) in enumerate(C):
        if p.search(txt):
            return i
    return None


def main():
    works = []
    for p in (ROOT / "data/raw/openalex/srf_corpus.json", ROOT / "data/raw/openalex/srf_problem_supplement.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        works.extend(w for w in d["works"] if w.get("year"))
    seen, uniq = set(), []
    for w in works:
        if w["id"] not in seen:
            seen.add(w["id"]); uniq.append(w)
    works = uniq
    print(f"корпус: {len(works)}")

    # id → группа + год
    gid = {}
    for w in works:
        g = classify((w.get("title") or "") + " " + (w.get("abstract") or ""))
        if g is not None:
            gid[w["id"]] = g
    print(f"классифицировано: {len(gid)} работ (без фона); фон = {len(works)-len(gid)}")

    # три независимых счётчика: all / pre(<=2018) / post(2019+) по ГОДУ ЦИТИРУЮЩЕЙ работы
    mat_all, mat_pre, mat_post = Counter(), Counter(), Counter()
    for w in works:
        cf = gid.get(w["id"])
        if cf is None:
            continue
        yr = w.get("year") or 0
        for r in (w.get("references") or []):
            rg = gid.get(r)
            if rg is None:
                continue
            mat_all[(cf, rg)] += 1
            if yr <= 2018:
                mat_pre[(cf, rg)] += 1
            else:
                mat_post[(cf, rg)] += 1

    def pr(m, title):
        n_edges = sum(m.values())
        n_self = sum(v for (i, j), v in m.items() if i == j)
        print(f"\n=== {title}  (рёбер внутри корпуса: {n_edges}, self-cites {n_self}) ===")
        hdr = "       " + "".join(f"{n[:10]:>11}" for n in NAMES)
        print(hdr)
        for i, n in enumerate(NAMES):
            row = "".join(f"{m.get((i, j), 0):>11}" for j in range(len(NAMES)))
            print(f"{n[:10]:>7} {row}")
        print("\nДоля ссылок группы i в группу j (% по строкам):")
        print("       " + "".join(f"{n[:10]:>11}" for n in NAMES))
        for i, n in enumerate(NAMES):
            tot = sum(m.get((i, j), 0) for j in range(len(NAMES)))
            row = "".join(f"{100*m.get((i,j),0)/tot:10.1f}%" if tot else f"{'—':>11}" for j in range(len(NAMES)))
            print(f"{n[:10]:>7} {row}")

    pr(mat_all, "ВСЕ ГОДЫ")
    pr(mat_pre, "ДО ОКНА: цитирующие ≤2018")
    pr(mat_post, "ПОСЛЕ ОКНА: цитирующие 2019+")


if __name__ == "__main__":
    main()