#!/usr/bin/env python3
"""S3-cross для кейса 007: взаимные цитирования JTWPA ↔ KITWPA ↔ JPA.

Пары:
  1. JTWPA (A, 265) ↔ KITWPA (B, 66)  — refs из jtwpa_full.json
  2. JTWPA (A, 265) ↔ JPA резонаторный (386) — refs из jtwpa_full.json + jpa_resonator_full.json
Плюс мосты (пересечение корпусов).
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
corpus = json.loads((ROOT / "data/raw/openalex/jtwpa_corpus.json").read_text(encoding="utf-8"))
jpa = json.loads((ROOT / "data/raw/openalex/jpa_resonator_corpus.json").read_text(encoding="utf-8"))
full_jt = json.loads((ROOT / "data/raw/openalex/jtwpa_full.json").read_text(encoding="utf-8"))
full_jpa = json.loads((ROOT / "data/raw/openalex/jpa_resonator_full.json").read_text(encoding="utf-8"))

A = {w["id"]: w for w in corpus if w["class"] == "A"}
B = {w["id"]: w for w in corpus if w["class"] == "B"}
J = {w["id"]: w for w in jpa}

def refs_of(fullmap, ids):
    """id -> set(referenced ids)."""
    out = {}
    for wid in ids:
        v = fullmap.get(wid, {})
        out[wid] = set(v.get("referenced_works", []))
    return out

refsA = refs_of(full_jt, A)
refsB = refs_of(full_jt, B)
refsJ = refs_of(full_jpa, J)

def cross(refs_X, target_ids):
    """Сколько работ X ссылаются хотя бы на одну работу target; всего ссылок X→target."""
    tgt = set(target_ids)
    n_works = 0
    n_links = 0
    for wid, rset in refs_X.items():
        hit = rset & tgt
        if hit:
            n_works += 1
            n_links += len(hit)
    return n_works, len(refs_X), n_links


print("=== S3-cross: JTWPA ↔ KITWPA ↔ JPA (кейс 007) ===\n")
print(f"Размеры: JTWPA(A)={len(A)}, KITWPA(B)={len(B)}, JPA={len(J)}")

# Пары
pairs = [
    ("JTWPA(A) → KITWPA(B)", refsA, set(B)),
    ("KITWPA(B) → JTWPA(A)", refsB, set(A)),
    ("JTWPA(A) → JPA", refsA, set(J)),
    ("JPA → JTWPA(A)", refsJ, set(A)),
    ("KITWPA(B) → JPA", refsB, set(J)),
    ("JPA → KITWPA(B)", refsJ, set(B)),
]
for label, refs, tgt in pairs:
    n_works, total, n_links = cross(refs, tgt)
    pct = 100 * n_works / max(total, 1)
    print(f"{label:24s}: {n_works}/{total} работ ({pct:.2f}%), ссылок {n_links}")

# Мосты (пересечение корпусов)
idsA, idsB, idsJ = set(A), set(B), set(J)
print(f"\nМосты A∩B (работы в обоих JTWPA и KITWPA корпусах): {len(idsA & idsB)}")
print(f"Мосты A∩J (работы в обоих JTWPA и JPA): {len(idsA & idsJ)}")
for wid in list(idsA & idsJ)[:8]:
    print(f"  - {A.get(wid, J.get(wid, {})).get('title', '?')[:80]}")

# Сводка в JSON
result = {
    "A_size": len(A), "B_size": len(B), "J_size": len(J),
    "A_to_B": cross(refsA, set(B))[:2],
    "B_to_A": cross(refsB, set(A))[:2],
    "A_to_J": cross(refsA, set(J))[:2],
    "J_to_A": cross(refsJ, set(A))[:2],
    "B_to_J": cross(refsB, set(J))[:2],
    "J_to_B": cross(refsJ, set(B))[:2],
    "bridges_AB": len(idsA & idsB), "bridges_AJ": len(idsA & idsJ),
}
out = ROOT / "results/case_signals/s3_cross_jtwpa.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\nСохранено: {out}")
