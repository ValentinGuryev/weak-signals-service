#!/usr/bin/env python3
"""Эквивалентность STOP + чанкованного шага 1 — БЕЗОПАСНЫЙ перезапуск проверки.

История: проверочный скрипт 26.09 20:53:31 делал to_pylist()+set() по 7 файлам
× 25–44 млн строк → своп-трайш → падение WSL (журнал 21:40). Здесь ЗАПРЕЩЕНО
to_pylist на больших колонках: только pyarrow.compute батчами (BATCH строк) и
DuckDB c memory_limit.

Контекст (восстановлено из транскриптов 25–26.09):
  * Оригинал termtech_mine.py (25.09 12:46 MSK): STOP = 178 слов, есть 'ourselves'.
    Им построены: quantum-эталон NJ-5 (26.09 02:12–02:39) и biomed 2016–2024
    (попытка 1: 03:23–03:38, попытка 2: 19:25–19:42).
  * Рефакторинг 26.09 20:31 (чанковка) потерял 'ourselves' в STOP; в 20:32
    вернули 'in'/'yourselves'-соседей, но 'ourselves' — пропущен → 177 слов.
  * Фикс этой сессией: 'ourselves' возвращён (STOP=178 == оригинал, проверено set-равенством).

Фазы:
  F1  STOP-фингерпринт ВСЕХ эталонных _yeardf (quantum 2016–2026, biomed 2016–2024):
      edge-граммы probe-слов (year=*.parquet) + униграммы (wyear=*.parquet).
      Ожидание: 'ourselves' отфильтрован (orig-STOP) во всех эталонах.
  F2  Пересборка шага 1 НОВЫМ кодом в eqcheck/:
        a) quantum 2026, CHUNK=50000 (один чанк);
        b) quantum 2026, CHUNK=7000 (5 чанков, многочанковый merge);
        c) biomed 2016, CHUNK=50000 (~7 чанков, реальный объём NJ-6).
  F3  Полный дифф each-new vs эталон (DuckDB, SUM(df) GROUP BY, FULL OUTER):
      допускается ТОЛЬКО 0/0/0 (extra_new/extra_old/val_diff).
  F4  Фингерпринт пересобранного: 'ourselves' снова отфильтрован.
Итог: PASS/FAIL → results/runtime/stop_equivalence_report.md (+ stdout).

Запуск:  source scripts/lib_cap.sh && cap_run stop-eq 6G \
            .venv/bin/python -u scripts/stop_equivalence_check.py
"""
from __future__ import annotations

import re
import sys
import time
import traceback
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import duckdb

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import importlib.util
_spec = importlib.util.spec_from_file_location("tm", ROOT / "scripts" / "termtech_mine.py")
tm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tm)

E = Path("/mnt/e/openalex_derived")
QREF = E / "termtech_quantum" / "_yeardf"      # эталон NJ-5 (оригинал, STOP=178)
BREF = E / "termtech_biomed" / "_yeardf"        # данные NJ-6 п.1+п.2 (оригинал, STOP=178)
EQ = E / "eqcheck"                              # пересборки этой проверки
REPORT = ROOT / "results" / "runtime" / "stop_equivalence_report.md"

BATCH = 1_000_000                               # жёсткий потолок чанка чтения
PROBES = ["ourselves", "in", "your", "the", "we"]
TS = time.strftime("%Y-%m-%d %H:%M:%S")

lines: list[str] = []


def out(msg: str = "") -> None:
    print(msg, flush=True)
    lines.append(msg)


# ---------- F1/F4: фингерпринт STOP (pyarrow, батчи, БЕЗ to_pylist) ----------

def fingerprint(path: Path, key: str) -> dict[str, tuple[int, int]]:
    """{probe: (n_gram_edge, unigram)} по колонке key ('term'|'word'), батчами."""
    pf = pq.ParquetFile(str(path))
    res = {w: [0, 0] for w in PROBES}
    for batch in pf.iter_batches(batch_size=BATCH, columns=[key]):
        col = batch.column(key)
        assert len(col) <= BATCH, "BATCH превышен — to_pylist-класс операций запрещён"
        for w in PROBES:
            m_edge = pc.or_(pc.match_substring_regex(col, rf"^{re.escape(w)} "),
                            pc.match_substring_regex(col, rf" {re.escape(w)}$"))
            m_uni = pc.equal(col, w)
            res[w][0] += pc.sum(pc.cast(m_edge, pa.int32())).as_py() or 0
            res[w][1] += pc.sum(pc.cast(m_uni, pa.int32())).as_py() or 0
    return {w: tuple(v) for w, v in res.items()}


def fingerprint_dir(d: Path, years: list[int]) -> dict[int, dict[str, tuple[int, int]]]:
    """Фингерпринт по year=*.parquet (edge-граммы); униграммы — из wyear=*.parquet."""
    out_cfg: dict[int, dict[str, tuple[int, int]]] = {}
    for y in years:
        yp = d / f"year={y}.parquet"
        wp = d / f"wyear={y}.parquet"
        if not yp.exists():
            continue
        f_y = fingerprint(yp, "term")
        f_w = fingerprint(wp, "word") if wp.exists() else {w: (0, 0) for w in PROBES}
        # verdict-сигнал: edge из year= (n>1 фильтр) + униграмма из wyear=
        # (word-фильтр). Униграмма в year= НЕ фильтруется и в оригинале тоже
        # (n==1 пропускает STOP-проверку) — поэтому НЕ берём её в verdict.
        merged = {w: (f_y[w][0], f_w[w][1]) for w in PROBES}
        out_cfg[y] = merged
    return out_cfg


def verdict(fp: dict[str, tuple[int, int]]) -> str:
    e, u = fp.get("ourselves", (0, 0))
    return "orig-STOP(178, ourselves фильтр ✓)" if (e == 0 and u == 0) \
        else f"⚠ НЕ orig-STOP: edge={e} uni={u}"


# ---------- F2: пересборка новым кодом ----------

def rebuild(slice_path: Path, year: int, out_dir: Path, chunk: int) -> int:
    out(f"  пересборка {slice_path.parent.name}/{year} CHUNK={chunk} …")
    tm.CHUNK_DOCS = chunk
    ypart = out_dir / "_yeardf" / f"year={year}.parquet"
    wpart = out_dir / "_yeardf" / f"wyear={year}.parquet"
    ypart.parent.mkdir(parents=True, exist_ok=True)
    tbl = pq.read_table(str(slice_path), columns=["title", "abstract"])
    t0 = time.time()
    n = tm.build_year_parts(tbl, year, ypart, wpart)
    del tbl
    out(f"    docs={n}, {time.time()-t0:.1f}s, rows year={pq.read_metadata(str(ypart)).num_rows}")
    return n


# ---------- F3: полный дифф (DuckDB, memory-limited) ----------

def full_diff(old: Path, new: Path, key: str) -> tuple[int, int, int, list[str]]:
    con = duckdb.connect()
    con.execute("SET memory_limit='2GB'; SET threads=2; "
                "SET temp_directory='/mnt/e/eqcheck/_ducktmp';")
    sql = f"""
    WITH o AS (SELECT {key} AS k, SUM(df)::BIGINT AS d FROM read_parquet('{old}') GROUP BY k),
         n AS (SELECT {key} AS k, SUM(df)::BIGINT AS d FROM read_parquet('{new}') GROUP BY k),
         m AS (SELECT COALESCE(o.k, n.k) AS k, o.d AS od, n.d AS nd
               FROM o FULL OUTER JOIN n ON o.k = n.k)
    SELECT COUNT(*) FILTER (WHERE od IS NULL),
           COUNT(*) FILTER (WHERE nd IS NULL),
           COUNT(*) FILTER (WHERE od IS NOT NULL AND nd IS NOT NULL AND od <> nd)
    FROM m
    """
    extra_new, extra_old, val_diff = con.execute(sql).fetchone()
    sample = [r[0] for r in con.execute(f"""
        WITH o AS (SELECT {key} AS k, SUM(df)::BIGINT AS d FROM read_parquet('{old}') GROUP BY k),
             n AS (SELECT {key} AS k, SUM(df)::BIGINT AS d FROM read_parquet('{new}') GROUP BY k),
             m AS (SELECT COALESCE(o.k, n.k) AS k, o.d AS od, n.d AS nd
                   FROM o FULL OUTER JOIN n ON o.k = n.k)
        SELECT k FROM m WHERE od IS NULL OR nd IS NULL OR od <> nd LIMIT 5
    """).fetchall()]
    con.close()
    return int(extra_new), int(extra_old), int(val_diff), sample


def main() -> int:
    out(f"# STOP-эквивалентность — отчёт {TS}")
    out(f"Код: scripts/termtech_mine.py, STOP={len(tm.STOP)} слов, "
        f"ourselves={'есть' if 'ourselves' in tm.STOP else 'НЕТ'} (оригинал: 178, есть)")
    all_ok = True
    Path("/mnt/e/eqcheck/_ducktmp").mkdir(parents=True, exist_ok=True)

    # --- F1: эталоны ---
    out("\n## F1: фингерпринт STOP эталонных файлов")
    q_years = sorted(int(p.stem.split("=")[1]) for p in QREF.glob("year=*.parquet"))
    b_years = sorted(int(p.stem.split("=")[1]) for p in BREF.glob("year=*.parquet"))
    for name, d, years in (("quantum(NJ-5 эталон)", QREF, q_years),
                           ("biomed(NJ-6 п.1+п.2)", BREF, b_years)):
        fps = fingerprint_dir(d, years)
        for y, fp in fps.items():
            v = verdict(fp)
            out(f"  {name} {y}: ourselves edge(year)/uni(wyear) = {fp['ourselves']} → {v}")
            if "⚠" in v:
                all_ok = False

    # --- F2: пересборки ---
    out("\n## F2: пересборка новым кодом (восстановленный STOP)")
    EQ.mkdir(exist_ok=True)
    jobs = [
        ("smoke_q2026_single", E / "slices" / "quantum" / "year=2026.parquet", 2026, 50_000),
        ("smoke_q2026_multi", E / "slices" / "quantum" / "year=2026.parquet", 2026, 7_000),
        ("smoke_b2016", E / "slices" / "biomed" / "year=2016.parquet", 2016, 50_000),
    ]
    built: dict[str, tuple[Path, Path]] = {}
    for name, slice_p, year, chunk in jobs:
        out_dir = EQ / name
        yp = out_dir / "_yeardf" / f"year={year}.parquet"
        wp = out_dir / "_yeardf" / f"wyear={year}.parquet"
        rebuild(slice_p, year, out_dir, chunk)
        built[name] = (yp, wp)
    tm.CHUNK_DOCS = 50_000

    # --- F3: полные диффы ---
    out("\n## F3: полный дифф vs эталон (SUM(df) GROUP BY; ожидается 0/0/0)")
    diffs = [
        ("q2026 single", QREF / "year=2026.parquet", built["smoke_q2026_single"][0], "term"),
        ("q2026 single", QREF / "wyear=2026.parquet", built["smoke_q2026_single"][1], "word"),
        ("q2026 multi ", QREF / "year=2026.parquet", built["smoke_q2026_multi"][0], "term"),
        ("q2026 multi ", QREF / "wyear=2026.parquet", built["smoke_q2026_multi"][1], "word"),
        ("b2016       ", BREF / "year=2016.parquet", built["smoke_b2016"][0], "term"),
        ("b2016       ", BREF / "wyear=2016.parquet", built["smoke_b2016"][1], "word"),
    ]
    for name, old, new, key in diffs:
        en, eo, vd, sample = full_diff(old, new, key)
        ok = (en == 0 and eo == 0 and vd == 0)
        all_ok &= ok
        out(f"  {name} {key:5s}: extra_new={en} extra_old={eo} val_diff={vd} "
            f"→ {'PASS' if ok else 'FAIL'}")
        if not ok:
            out(f"    примеры: {sample}")

    # --- F4: фингерпринт пересобранного ---
    out("\n## F4: фингерпринт пересобранного (должен быть orig-STOP)")
    for name, (yp, wp) in built.items():
        year = int(yp.stem.split("=")[1])
        fps = fingerprint_dir(yp.parent, [year])
        fp = fps[year]
        v = verdict(fp)
        out(f"  {name}: ourselves edge(year)/uni(wyear) = {fp['ourselves']} → {v}")
        if "⚠" in v:
            all_ok = False

    out(f"\n## ИТОГ: {'PASS ✅' if all_ok else 'FAIL ❌'}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"отчёт: {REPORT}", flush=True)
    return 0 if all_ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        Path("/home/user/projects/Hackathon/results/runtime/"
             "stop_equivalence_report.md").write_text(
            "\n".join(lines) + "\n\nCRASH:\n" + traceback.format_exc(), encoding="utf-8")
        sys.exit(2)
