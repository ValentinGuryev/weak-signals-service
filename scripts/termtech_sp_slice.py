#!/usr/bin/env python3
"""TermTech v0: извлечение СП-среза OpenAlex с абстрактами → sp_slice/sp_works.parquet.

Дизайн: methodology/TERMTECH_DESIGN.md §2 (заморожен 2026-09-25).
Источник текста: E:/openalex_derived/T_text/year=*/publication_year=*/data_0.parquet
  (id, publication_year, title, abstract_inverted_index, ...) — 79 ГБ.
Фильтры (frozen): 6 СП-тем по regex display_name `superconduct|cryogen`,
  type IN белый список NJ-1, language='en', годы 2016–2026.

Resume: готовые годы (part size>0) пропускаются. Один процесс, mem<=3GB,
spill ТОЛЬКО E:/tmp_duck (правило план ночных работ 3). Лог в stdout (flush=True).

Запуск:
  HF_HUB_OFFLINE=1 .venv/bin/python scripts/termtech_sp_slice.py [--years 2026] [--smoke]
"""
import argparse
import math
import sys
import time
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
T_STATS = "data/openalex_derived/T_stats/year=*/*/*.parquet"
T_TEXT_E = "/mnt/e/openalex_derived/T_text"
OUT = ROOT / "data/openalex_derived/sp_slice"

# frozen (TERMTECH_DESIGN §2): regex superconduct|cryogen по display_name тем
SP_TIDS = [10037, 11766, 11803, 11808, 12491, 13200]
TYPE_OK = ("article", "review", "preprint", "book-chapter", "dissertation", "book",
           "letter", "editorial", "erratum", "standard", "report")
TYPES_SQL = ", ".join(f"'{t}'" for t in TYPE_OK)
YEARS = list(range(2016, 2027))


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main() -> int:
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--mem", default="3GB")
    ap.add_argument("--years", help="через запятую, напр. 2026 (для смоука)")
    ap.add_argument("--smoke", action="store_true", help="год 2026, один поток")
    ap.add_argument("--topics", default=None,
                    help="P3: id тем через запятую (дефолт = 6 СП-тем frozen)")
    ap.add_argument("--out", default=None,
                    help="P3: каталог выхода (дефолт data/openalex_derived/sp_slice)")
    ap.add_argument("--chunk-rows", type=int, default=20000,
                    help="строк aj в чанке реконструкции (память ~ лимит/ch)")
    args = ap.parse_args()

    tids = ([int(x) for x in args.topics.split(",")]
            if args.topics else SP_TIDS)
    if args.out:
        OUT = Path(args.out)

    if args.smoke:
        years = [2026]
        args.threads = 1
    elif args.years:
        years = [int(y) for y in args.years.split(",")]
    else:
        years = YEARS

    OUT.mkdir(parents=True, exist_ok=True)
    TMPAJ = OUT / "_ajtmp"
    TMPAJ.mkdir(parents=True, exist_ok=True)
    spill = Path(T_TEXT_E).parent / "tmp_duck"
    con = duckdb.connect(config={
        "memory_limit": args.mem,
        "threads": args.threads,
        "temp_directory": str(spill) if spill.exists() else ":memory:",
    })

    tids_sql = ",".join(str(t) for t in tids)
    # урок 25.09 (инцидент 13:40, AI-срез 1.47M работ): материализация СЫРОГО
    # aj для matched-строк умирала OOM (134k строк × ~20KB JSON > лимита).
    # Решение: реконструкция abstract СРАЗУ в потоке COPY, build-сторона —
    # маленькая таблица y_ids (~134k строк/год); aj нигде не материализуется.
    con.execute("SET preserve_insertion_order=false")

    # 1) id среза из T_stats (локально): фильтры frozen
    log(f"building id set from T_stats (тем: {len(tids)}) ...")
    t0 = time.time()
    con.execute(f"""
        CREATE OR REPLACE TABLE sp_ids AS
        SELECT id, publication_year,
               list_filter(topic_ids, x -> x IN ({tids_sql})) AS sp_tids
        FROM read_parquet('{T_STATS}')
        WHERE list_has_any(topic_ids, [{tids_sql}])
          AND language = 'en'
          AND type IN ({TYPES_SQL})
          AND publication_year BETWEEN 2016 AND 2026
    """)
    n_ids = con.execute("SELECT count(*) FROM sp_ids").fetchone()[0]
    log(f"sp_ids = {n_ids} works ({time.time()-t0:.1f}s)")

    # 2) по годам: join с T_text на E:, реконструкция абстракта из inverted index
    t_all = time.time()
    for y in years:
        part = OUT / f"year={y}.parquet"
        if part.exists() and part.stat().st_size > 0:
            log(f"{y}: skip (exists, {part.stat().st_size} B)")
            continue
        txt = f"{T_TEXT_E}/year={y}/publication_year={y}/data_0.parquet"
        if not Path(txt).exists():
            log(f"{y}: NO SOURCE {txt} — skip")
            continue
        t0 = time.time()
        # id года — маленькая build-сторона; фильтрация ДО реконструкции JSON
        con.execute(f"""
            CREATE OR REPLACE TABLE y_ids AS
            SELECT id, publication_year, sp_tids FROM sp_ids
            WHERE publication_year = {y}
        """)
        # Фаза A: ОДИН проход по E: → сырой aj на диск (только join+COPY,
        # без json-реконструкции). Уроки 13:40 и 14:00: память умирала на
        # json-расширении для ~134k matched-строк AI-среза (1.8/1.8 GiB).
        aj = TMPAJ / f"year={y}.aj.parquet"
        if not (aj.exists() and aj.stat().st_size > 0):
            con.execute(f"""
                COPY (
                  SELECT y.id, y.publication_year, y.sp_tids, t.title,
                         t.abstract_inverted_index AS aj
                  FROM y_ids y
                  JOIN read_parquet('{txt}') t ON t.id = y.id
                ) TO '{aj}' (FORMAT PARQUET, COMPRESSION ZSTD)
            """)
        n_aj = con.execute(
            f"SELECT count(*) FROM read_parquet('{aj}')").fetchone()[0]
        # Фаза B: реконструкция чанками по hash(id) — json-расширение чанка
        # укладывается в лимит памяти; aj читается с ЛОКАЛЬНОГО диска
        n_ch = max(1, math.ceil(n_aj / max(args.chunk_rows, 1)))
        chunk_files = []
        for i in range(n_ch):
            cf = TMPAJ / f"year={y}.p{i}.parquet"
            chunk_files.append(cf)
            if cf.exists() and cf.stat().st_size > 0:
                continue
            con.execute(f"""
                COPY (
                  SELECT src.id, src.publication_year, src.sp_tids, src.title,
                         (SELECT string_agg(w, ' ' ORDER BY pos)
                          FROM (SELECT k.key AS w,
                                       unnest(CAST(k.value AS INT[])) AS pos
                                FROM json_each(src.aj) k)
                         ) AS abstract
                  FROM read_parquet('{aj}') src
                  WHERE hash(src.id) % {n_ch} = {i}
                ) TO '{cf}' (FORMAT PARQUET, COMPRESSION ZSTD)
            """)
        # склейка чанков → год, чистка временных файлов
        if Path(part).exists() and part.stat().st_size == 0:
            part.unlink()
        glob_sql = ", ".join(f"'{c}'" for c in chunk_files)
        con.execute(f"""
            COPY (SELECT * FROM read_parquet([{glob_sql}]))
            TO '{part}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
        con.execute("DROP TABLE y_ids")
        for c in chunk_files:
            c.unlink(missing_ok=True)
        aj.unlink(missing_ok=True)
        n = con.execute(f"SELECT count(*) FROM read_parquet('{part}')").fetchone()[0]
        n_abs = con.execute(
            f"SELECT count(*) FROM read_parquet('{part}') WHERE abstract IS NOT NULL"
        ).fetchone()[0]
        log(f"{y}: {n} works ({n_abs} with abstract), {time.time()-t0:.1f}s, "
            f"{part.stat().st_size/1e6:.0f} MB")

    # 3) итог
    parts = sorted(OUT.glob("year=*.parquet"))
    if parts:
        glob_sql = ", ".join(f"'{p}'" for p in parts)
        tot = con.execute(
            f"SELECT count(*), count(abstract) FROM read_parquet([{glob_sql}])"
        ).fetchone()
        log(f"DONE: {len(parts)} parts, {tot[0]} works, {tot[1]} abstracts, "
            f"{time.time()-t_all:.1f}s total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
