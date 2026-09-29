#!/usr/bin/env python3
"""Тренировочный сет S2 v2: фундаментальные (OpenAlex ≤2005) vs прикладные (SNF-производство).

Проблема прокси-метки: OpenAlex post-2020 статьи по IBAD — это «улучшение свойств»
(granularity, buffer layers, enhancement of Jc), а НЕ производство. Производственные
доклады публикуются на конференциях (SNF), не в журналах. Поэтому:
  - фундаментальный пул = OpenAlex IBAD-статьи ≤2005 (якоря: Wang 1997, Arendt 2004,
    Foltyn 1999, Iijima, Kreiskott...) — реальные «открытие/эффект/механизм»;
  - прикладной пул = SNF-доклады тега ibad_tapes с производственной лексикой
    (production, reel-to-reel, mass, commercial, industrialization...) — реальные
    «производство/масштабирование» (Fujikura, SuperPower, Shanghai Superconductor...).

Выход: data/raw/openalex/ibad_semantic_train.json (обновлённый формат)
  {fund_works: [...], appl_snf: [...], meta}
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from semantic_shift_v2 import clean_text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_OLD = PROJECT_ROOT / "data" / "raw" / "openalex" / "ibad_semantic_train.json"
TOPICS = PROJECT_ROOT / "results" / "snf_index" / "topics_map.json"
SNF_DIRS = [
    PROJECT_ROOT / "data" / "raw" / "conferences" / "snf_ieeecsc" / "downloads_renamed",
    PROJECT_ROOT / "data" / "raw" / "conferences" / "snf_ieeecsc" / "downloads_renamed_v2",
]
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "ibad_semantic_train.json"

# Производственная лексика для отбора SNF-докладов в прикладной пул
PROD_RE = re.compile(
    r"production|manufactur|reel[\s-]?to[\s-]?reel|mass[\s-]?produc|commercial|industrial|"
    r"long[\s-]?length|scale[\s-]?up|throughput|pilot|prototype|\bR2R\b|yield|"
    r"quality[\s-]?control|cost[\s-]?reduc|process[\s-]?optim|automated|inline|production line",
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


def year_from_name(name: str) -> int | None:
    m = re.match(r"\((\d{4})\)", name)
    return int(m.group(1)) if m else None


def main() -> None:
    # --- Фундаментальный пул: OpenAlex ≤2005 (уже скачано с фильтром релевантности) ---
    old = json.loads(TRAIN_OLD.read_text(encoding="utf-8"))
    # поддержка обоих форматов: v1 ('train' с bucket) и уже-перезаписанный
    if "train" in old:
        fund = [w for w in old["train"] if w["bucket"] == "fund" and w.get("abstract")]
    else:
        fund = [w for w in old.get("fund_works", []) if w.get("abstract")]
    print(f"Фундаментальный пул (OpenAlex ≤2005): {len(fund)} работ с абстрактами")

    # --- Прикладной пул: SNF-доклады ibad_tapes с производственной лексикой ---
    tm = json.loads(TOPICS.read_text(encoding="utf-8"))
    ibad_files = tm.get("ibad_tapes", [])
    appl_snf = []
    for name in ibad_files:
        year = year_from_name(name)
        if not year or year < 2008:
            continue
        pdf = find_snf(name)
        if not pdf:
            continue
        txt = extract_text(pdf)
        clean = clean_text(txt)
        # жёсткий фильтр мусора: недостаточно алфавитного текста после чистки
        letters = len(re.findall(r"[A-Za-z]", clean))
        if letters < 300:
            continue
        # производственная лексика в тексте (абзацы)
        prod_paras = [p for p in clean.split(". ") if PROD_RE.search(p)]
        if len(prod_paras) >= 2:  # минимум 2 производственных абзаца
            appl_snf.append({
                "name": name, "year": year, "text": clean,
                "n_prod_paras": len(prod_paras),
                "label": "applied", "bucket": "appl_snf",
            })
    print(f"Прикладной пул (SNF с производственной лексикой): {len(appl_snf)} докладов")

    payload = {
        "method": "ibad_semantic_train_v2",
        "note": "fund=OpenAlex≤2005 (открытие/механизм), appl_snf=SNF-производство (масштаб/коммерциализация).",
        "fund_works": fund,
        "appl_snf": appl_snf,
        "meta": {"n_fund": len(fund), "n_appl_snf": len(appl_snf)},
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT}")
    print(f"meta: {payload['meta']}")


if __name__ == "__main__":
    main()
