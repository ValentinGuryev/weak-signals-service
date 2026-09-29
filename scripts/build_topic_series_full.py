#!/usr/bin/env python3
"""NJ-1: полная история тем из сырого снапшота → taxonomy/topic_series_full.parquet.

Один проход по data/jsonl/works (634 ГБ gz, ВСЕ годы, включая дожнезаводские) даёт
гистограммы (tid × year): n_raw — все работы, n_ok — с фильтром type IN (белый список
журнал 24.09 09:30, без dataset/other). Это снимает API-зависимость birth для N×G×I
и левый цензинг базы 2016+ навсегда (см. план ночных работ NJ-1).

Дизайн (уроки прошлых ночей):
 * прогресс и RESUME — по одному дневному каталогу updated_date=* за проход:
   каждая готовая дата → series_full_parts/<date>.parquet; существующие пропускаются;
 * состояние агрегации крошечное (≈4516×Nyears строк на дату) — память не взрывается;
 * merged-финал: SUM по (tid, year) из всех частей → выходной parquet;
 * printed progress — flush=True (никаких буферизованных «тихих» часов).

Запуск (ночь, одиночно):
  HF_HUB_OFFLINE=1 .venv/bin/python scripts/build_topic_series_full.py \
      [--threads 2] [--mem 2GB]
--threads: агрегация stateless (малый state) — под утреннее окно можно 6 (НЕ для
  запросов по T_stats! это другой класс задач). Дефолт 2 — консервативно.
"""
import argparse
import sys
import time
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
WORKS = Path("/mnt/e/openalex-snapshot/data/jsonl/works")
OUT = ROOT / "data/openalex_derived/taxonomy/topic_series_full.parquet"
PARTS = ROOT / "data/openalex_derived/series_full_parts"

TYPE_OK = ("article", "review", "preprint", "book-chapter", "dissertation", "book",
           "letter", "editorial", "erratum", "standard", "report")
TYPES_SQL = ", ".join(f"'{t}'" for t in TYPE_OK)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--mem", default="2GB")
    ap.add_argument("--smoke", action="store_true",
                    help="смоук на тестовых данных: ОДИН самый мелкий дневной каталог, "
                         "без финального merge (чекпоинт части остаётся — resume его переиспользует)")
    args = ap.parse_args()

    dirs = sorted(d for d in WORKS.glob("updated_date=*") if d.is_dir())
    if args.smoke:
        with_gz = [d for d in dirs if any(d.glob("*.gz"))]
        if not with_gz:
            sys.exit("FAIL: нет ни одного каталога с .gz")
        dirs = [min(with_gz, key=lambda d: sum(f.stat().st_size for f in d.glob("*.gz")))]
        print(f"SMOKE: единственный непустой каталог {dirs[0].name}", flush=True)
    if not dirs:
        sys.exit(f"FAIL: нет updated_date-каталогов в {WORKS}")
    PARTS.mkdir(exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET threads={args.threads}; SET memory_limit='{args.mem}'")
    spill = Path("/mnt/e/openalex_derived/tmp_duck")
    spill.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{spill}'")

    t0 = time.time()
    done = skip = fail = 0
    for i, d in enumerate(dirs, 1):
        part = PARTS / f"{d.name}.parquet"
        if part.exists() and part.stat().st_size > 0:
            skip += 1
            continue
        gz = sorted(d.glob("*.gz"))
        if not gz:
            continue  # пустая дата — без чекпоинта (маркер 0 байт ломал resume-сверку)
            continue
        files = ", ".join(f"'{f}'" for f in gz)
        try:
            con.execute(f"""
              COPY (
                SELECT cast(regexp_extract(t.unnest, '(\\d+)$', 1) AS BIGINT) AS tid,
                       w.publication_year AS yr,
                       count(*) AS n_raw,
                       count(*) FILTER (WHERE w.type IN ({TYPES_SQL})) AS n_ok
                FROM read_json([{files}], format='newline_delimited',
                               ignore_errors=true) w,
                     UNNEST(list_transform(w.topics, x -> x.id)) AS t
                WHERE w.publication_year IS NOT NULL
                GROUP BY 1, 2
              ) TO '{part}' (FORMAT PARQUET, COMPRESSION ZSTD)""")
            done += 1
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"[fail] {d.name}: {e}", flush=True)
            if fail >= 5:
                sys.exit("FAIL: 5 ошибок подряд — стоп")
        if (done + skip) % 10 == 0 or i == len(dirs):
            el = time.time() - t0
            print(f"[{i}/{len(dirs)}] ok={done} skip={skip} fail={fail} {el:.0f}s",
                  flush=True)

    if args.smoke:
        print(f"SMOKE OK: обработано дат={done + skip} fail={fail} за {time.time()-t0:.0f}s; "
              f"merge пропущен (--smoke). Части: {PARTS}", flush=True)
        return 0 if fail == 0 else 1

    # финальный merge
    parts = sorted(str(p) for p in PARTS.glob("*.parquet") if p.stat().st_size > 0)
    print(f"merge {len(parts)} частей...", flush=True)
    files = ", ".join(f"'{p}'" for p in parts)
    con.execute(f"""
      COPY (
        SELECT tid, yr, sum(n_raw) AS n_raw, sum(n_ok) AS n_ok
        FROM read_parquet([{files}]) WHERE tid IS NOT NULL
        GROUP BY 1, 2
      ) TO '{OUT}' (FORMAT PARQUET, COMPRESSION ZSTD, OVERWRITE_OR_IGNORE)""")
    n_rows, n_tid, y0, y1 = con.execute(
        f"SELECT count(*), count(DISTINCT tid), min(yr), max(yr) FROM read_parquet('{OUT}')"
    ).fetchone()
    snap_t = len((ROOT / "data/openalex_derived/taxonomy/topic_ids.txt").read_text().splitlines())
    print(f"OK: {OUT} rows={n_rows} tids={n_tid} (taxonomy={snap_t}) years={y0}..{y1} "
          f"fail={fail} total={time.time()-t0:.0f}s", flush=True)
    if n_tid < snap_t:
        print("WARN: tids < taxonomy — сверить с union дампа тем (возможны темы без работ "
              "в works-дампе: проверить вручную)", flush=True)
    print("Критерий готовности NJ-1: строк >0, tids==union тем, выборка birth совпадает "
          "с ngi_birth_cache.json", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
