#!/usr/bin/env python3
"""Точечный патч webapp-паркета из батч-jsonl (план fix_two_problems_plan_20260929, шаг 5).

Зачем НЕ полная пересборка (build_card_vectors, 93 мин):
  * impact B применён in-place к webapp-паркету (recalibrate_impact_v2) — полная
    пересборка из tech_cards_v1_dedup.parquet молча откатила бы его к ночному k;
  * пересборка переэмбедит 160k строк (~93 мин) вместо ~2-3k изменённых.

Что делает (по строке на терм из jsonl, последняя запись выигрывает):
  * v=1 (valid)  → name_en/name_ru/problem_ru + llm_valid=1;
                    переэмбед строки, если name_en изменился (текст как в
                    build_card_vectors: name_en + '. ' + problem_en[:150]);
  * v=0 (invalid) → строка СОХРАНЯЕТСЯ как llm_valid=0 (ОТКЛОНЕНИЕ от пункта
                    «удаление строки» плана — защита gold/покрытия: отбракованный
                    gold-терм иначе навсегда уходит из пула и рушит frozen-gate
                    presence; показ невалида и так исключает LLM_GATE, см. K2).
                    Фиксируется в отчёте: сколько invalid оставлено.
  * терм из jsonl не найден в паркете → пропуск + счётчик.

Выход: тот же паркет + npy (in-place, с бэкапом .bak), + JSON-отчёт рядом.
Запуск: .venv/bin/python scripts/patch_cards_from_batch.py
"""
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "webapp/data/cards/tech_cards.parquet"
VECS = ROOT / "webapp/data/cards/tech_cards_vectors.npy"
JSONL = ROOT / "results/tech_cards_llm_batch_v1.jsonl"
REPORT = ROOT / "results/runtime/cards_batch_patch_report.json"


def main() -> None:
    t0 = time.time()
    df = pd.read_parquet(CARDS)
    vec = np.load(VECS)
    if len(df) != len(vec):
        raise SystemExit(f"parquet ({len(df)}) и npy ({len(vec)}) не совпадают — стоп")

    recs: dict[str, dict] = {}
    for line in JSONL.read_text().splitlines():
        try:
            r = json.loads(line)
            recs[r["term"]] = r
        except json.JSONDecodeError:
            continue

    pos = {t: i for i, t in enumerate(df["term"])}
    upd = emb_terms = invalid_kept = missing = 0
    changes = []                          # (row_idx,) для переэмбеда
    for term, r in recs.items():
        i = pos.get(term)
        if i is None:
            missing += 1
            continue
        if r.get("valid"):
            old_name = df.at[i, "name_en"] or ""
            new_name = (r.get("name_en") or "").strip() or old_name
            df.at[i, "name_en"] = new_name
            df.at[i, "name_ru"] = (r.get("name_ru") or "").strip()
            df.at[i, "problem_ru"] = (r.get("problem_ru") or "").strip()
            if int(df.at[i, "llm_valid"]) != 1:
                df.at[i, "llm_valid"] = 1
            upd += 1
            if new_name != old_name:
                changes.append(i)
        else:
            invalid_kept += 1             # остаётся llm_valid=0 (см. докстринг)

    emb_terms = len(changes)
    if changes:
        # тот же e5-энкодер, что и в сервисе (консистентность косинусов, как в Д)
        sys.path.insert(0, str(ROOT / "webapp"))
        import app as webapp  # noqa: E402
        if webapp.E5 is None:
            raise SystemExit("e5 недоступен — переэмбед невозможен (явная ошибка, §9)")
        prob = df["problem_en"].fillna("").astype(str).str.slice(0, 150).to_numpy()
        names = df["name_en"].fillna("").astype(str).to_numpy()
        texts = [f"{names[i]}. {prob[i]}" for i in changes]
        for s in range(0, len(texts), 256):
            v = webapp.e5_embed(texts[s:s + 256], is_query=False)
            for j, row in enumerate(changes[s:s + 256]):
                vec[row] = v[j].astype(np.float32)
        # норма у e5 сохраняется (модель отдаёт нормализованные), перепроверка:
        norms = np.linalg.norm(vec[changes], axis=1)
        print(f"переэмбед {emb_terms} строк: norm min/mean/max = "
              f"{norms.min():.3f}/{norms.mean():.3f}/{norms.max():.3f}", flush=True)

    bak = CARDS.with_suffix(".parquet.bak_patch")
    if not bak.exists():
        shutil.copy2(CARDS, bak)
        shutil.copy2(VECS, VECS.with_suffix(".npy.bak_patch"))
    df.to_parquet(CARDS, index=False)
    np.save(VECS, vec)
    out = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "jsonl_terms": len(recs),
           "valid_upd": upd, "reembedded": emb_terms,
           "invalid_kept": invalid_kept, "missing_in_parquet": missing,
           "llm_valid_total": int(df["llm_valid"].sum()), "pool": len(df)}
    REPORT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(out, ensure_ascii=False), f"{time.time()-t0:.0f} с → {REPORT}")


if __name__ == "__main__":
    main()
