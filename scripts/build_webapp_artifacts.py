#!/usr/bin/env python3
"""C1 (NIGHT_PLAN): сборка артефактов лёгкого веб-сервиса → webapp/data/.

Что копируется/собирается (всё ЛОКАЛЬНОЕ, big files не тянем):
  taxonomy/  topic_vectors*.npy, topics.parquet, topic_ids.txt   (~30 МБ)
  digest/    T_digest/digest.parquet (топ-100 работ × 4516 тем)   (~16 МБ)
  ngi/       topic_ngi_cache*.parquet — нужен `--prefill` NJ-2 (нет → предупреждение)
  birth/     ngi_birth_cache.json                                (~1.4 МБ)
  lexicon/   results/qa_facet_lexicon_v1.json (если есть)
  termtech_<name>/ для КАЖДОГО готового стора (sp, q1ai, ...): candidates_clean +
             filter_report + series_<name>.parquet (серии топ-N по growth из _yeardf,
             mem 1GB; если стора ещё нет — missing в manifest, доберётся после E0)
  embed/     topic_vectors_e5m.npy — если прогнан scripts/vps_embed.py --build-vectors
             (нет → предупреждение: ретривал на VPS уйдёт в TF-IDF fallback)

Выход: webapp/data/... + webapp/manifest.json (что есть/чего нет).

Запуск: .venv/bin/python scripts/build_webapp_artifacts.py [--top-terms 500]
"""
import argparse
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "webapp/data"
TAX = ROOT / "data/openalex_derived/taxonomy"
DIG = ROOT / "data/openalex_derived/T_digest/digest.parquet"
SP_STORE = ROOT / "results/termtech"


def log(m: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def cp(src: Path, dst: Path) -> bool:
    if not src.exists():
        log(f"НЕТ: {src}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    log(f"cp {src.name} → {dst.relative_to(ROOT)} ({src.stat().st_size/1e6:.1f} МБ)")
    return True


def store_series(store: Path, name: str, top_n: int) -> bool:
    """Серии df по годам для top-N терминов TermTech-стора (по growth)."""
    cand = store / "candidates_clean.parquet"
    yeardir = store / "_yeardf"
    if not cand.exists() or not yeardir.exists():
        log(f"нет {store}: candidates/_yeardf — series_{name} пропущен")
        return False
    import duckdb
    import pandas as pd
    df = pd.read_parquet(cand, columns=["term", "growth"])
    terms = list(df.sort_values("growth", ascending=False)
                 .head(top_n)["term"])
    parts = sorted(yeardir.glob("year=*.parquet"))
    glob_sql = ", ".join(f"'{p}'" for p in parts)
    vals = ", ".join("'" + t.replace("'", "''") + "'" for t in terms)
    con = duckdb.connect(config={"memory_limit": "1GB",
                                 "temp_directory": "/mnt/e/openalex_derived/tmp_duck"})
    try:
        out = con.execute(f"""
            SELECT term, year, sum(df) AS df FROM read_parquet([{glob_sql}])
            WHERE term IN ({vals}) GROUP BY 1, 2
        """).fetchdf()
    finally:
        con.close()
    dst = DEST / f"termtech_{name}/series_{name}.parquet"
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(dst, index=False, compression="zstd")
    log(f"series_{name}: {len(terms)} терминов, {len(out)} строк → {dst}")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top-terms", type=int, default=500)
    args = ap.parse_args()

    DEST.mkdir(parents=True, exist_ok=True)
    manifest: dict = {"built": time.strftime("%Y-%m-%d %H:%M"), "ok": [], "missing": []}

    def step(name: str, fn, *a, **kw):
        try:
            ok = fn(*a, **kw)
        except Exception as e:  # noqa: BLE001
            log(f"ОШИБКА {name}: {e}")
            ok = False
        manifest["ok" if ok else "missing"].append(name)

    # 1) таксономия
    for f in ["topic_vectors.npy", "topic_vectors_i2.npy", "topics.parquet",
              "topics_i2.parquet", "topic_ids.txt"]:
        step(f"taxonomy/{f}", cp, TAX / f, DEST / "taxonomy" / f)
    # 2) дайджест работ (источники/кейсы)
    step("digest", cp, DIG, DEST / "digest/digest.parquet")
    # 3) NGI-кэш (NJ-2 --prefill)
    step("ngi_series", cp, TAX / "topic_ngi_cache.parquet",
         DEST / "ngi/topic_ngi_cache.parquet")
    step("ngi_impact", cp, TAX / "topic_ngi_cache_impact.parquet",
         DEST / "ngi/topic_ngi_cache_impact.parquet")
    # 4) birth-кэш
    step("birth_cache", cp, ROOT / "results/ngi_birth_cache.json",
         DEST / "birth/ngi_birth_cache.json")
    # 5) лексикон фасетов (fanout)
    step("lexicon", cp, ROOT / "results/qa_facet_lexicon_v1.json",
         DEST / "lexicon/qa_facet_lexicon_v1.json")
    # 6) TermTech-сторы (СП + демо-домен q1ai + ...): кандидаты + фильтр + серии
    for name, store in {"sp": SP_STORE,
                        "q1ai": ROOT / "results/termtech_q1ai"}.items():
        step(f"{name}_candidates", cp, store / "candidates_clean.parquet",
             DEST / f"termtech_{name}/candidates_clean.parquet")
        step(f"{name}_report", cp, store / "filter_report.json",
             DEST / f"termtech_{name}/filter_report.json")
        step(f"{name}_series", store_series, store, name, args.top_terms)
    # 7) Вектора тем e5 (C3: scripts/vps_embed.py --build-vectors) — если есть
    step("embed_vectors", cp, TAX / "topic_vectors_e5m.npy",
         DEST / "embed/topic_vectors_e5m.npy")

    (ROOT / "webapp/manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1))
    log(f"manifest: ok={len(manifest['ok'])} missing={manifest['missing']}")
    log("→ webapp/manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
