#!/usr/bin/env python3
"""TermTech v0: мининг tech-терминов из СП-среза → results/termtech/.

Дизайн: methodology/TERMTECH_DESIGN.md §3 (заморожен 2026-09-25):
  шаг 1: n-граммы 1–4 (только title+abstract, en), df + series по годам;
  шаг 2: ключность kPMI >= 0.05 (для n>1) + df <= 50% среза;
  шаг 3: df >= 20, growth = (n2023-25/3)/(n2016-22/7+1), first_year,
         emerging = first_year>=2018 И n2023-25>=5; ранжирование по growth.
  шаг 4 (синхронизация синонимов) — СТАДИЯ 2, в v0 не участвует.
Eval (§5, frozen): recall по 14 технологиям; маркеры-синонимы сравниваются
  по нормализованным строкам. Список НЕ является входом конвейера — только оценка.

Урок 25.09: глобальный dict на ~35M терминов умирал молчаливым OOM →
погодовая запись df на диск (_yeardf/*.parquet), агрегация — DuckDB.

УРОК 26.09 (падения WSL 03:43 и 19:47 — см. журнал 20:55): погодовой dict
на 36–44M терминов + его Arrow-копия при записи давали пик 6.5–7 ГБ на
ИТЕРАЦИЮ → OOM-killer ронял python в init.scope → systemd выключал VM WSL
целиком (teardown + crash-loop). Фиксы (методология НЕ тронута — те же
формули, пороги, порядок операций):
  1) шаг 1 — ЧАНКАМИ по CHUNK_DOCS строк: словарь чанка (~1–2 ГБ) пишется
     частичными row-группами в year=*.parquet.tmp и атомарно переименовывается
     (resume не видит недописанные файлы). Дубли (term, year) из разных чанков
     схлопываются SUM'ой в шаге 2 — семантика «df = число работ в году» та же;
  2) шаг 2 — целиком в DuckDB (COPY промежуточных результатов на диск,
     memory_limit 3GB + spill E:/tmp_duck): в Python попадают ТОЛЬКО термины
     df>=20 с пробелом (под kPMI, ровно исходное множество multi_idx) и
     готовые кандидаты. all_terms.parquet пишется COPY + JOIN kPMI (NaN для
     не-multi И для multi df 5–19 — ⚠ дивергенция от оригинала, где kPMI был
     у всех multi; аудит 27.09 P2: на выдачу не влияет — filter/recall/retro
     читают candidates, не all_terms).

Выход:
  results/termtech/candidates.parquet   — прошедшие фильтры термины
  results/termtech/all_terms.parquet    — все термины df>=5 (для sensitivity)
  results/termtech/eval_report.json     — recall + sensitivity
  results/termtech/top_terms.md         — топ-100 по growth + топ-40 emerging
  <OUT>/_agg/allt.parquet               — промежуточная агрегация (df>=5, без kPMI)

Запуск: .venv/bin/python scripts/termtech_mine.py [--smoke-year 2026]
"""
import argparse
import gc
import json
import math
import os
import re
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
SLICE = ROOT / "data/openalex_derived/sp_slice"
OUTDIR = ROOT / "results/termtech"

# --- frozen params (TERMTECH_DESIGN §3) ---
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-+#.][a-z0-9]+)*")
MAX_N = 4
CHUNK_DOCS = 50_000        # фикс 26.09: размер чанка шага 1 (ресурсный лимит, не методология)
STOP = set("""a about above after again against all am an and any are aren't as at be
because been before being below between both but by can cannot could couldn't did didn't
do does doesn't doing don't down during each few for from further had hadn't has hasn't
have haven't having he her here hers herself him himself his how i if in into is isn't
it its itself let's me more most mustn't my myself no nor not of off on once only or
other ought our ours ourselves out over own same shan't she should shouldn't so some such
than that the their theirs them themselves then there these they this those through to
too under until up very was wasn't we were weren't what when where which while who whom
why with won't would wouldn't you your yours yourself yourselves also may might one two
three first second new using used use results result shown show shows paper present
based method methods analysis study research work works data effect effects value values
type types number numbers""".split())
MIN_DF = 20                 # §3 шаг 3
KPMI_MIN = 0.05             # §3 шаг 2
DF_MAX_FRAC = 0.50          # §3 шаг 2
MIN_YEAR_CNT = 3            # first_year
EMERGING_FIRST_YEAR = 2018
EMERGING_RECENT_MIN = 5

# --- eval (§5, frozen ДО прогона) ---
EVAL = [
    ("superconducting_diode", ["superconducting diode", "josephson diode",
                               "superconducting diode effect"]),
    ("snspd", ["superconducting nanowire single-photon detector",
               "nanowire single-photon", "snspd"]),
    ("jtwpa", ["josephson traveling-wave parametric amplifier",
               "traveling-wave parametric", "jtwpa"]),
    ("flux_pump", ["flux pump"]),
    ("ibad", ["ion-beam assisted deposition", "ibad"]),
    ("rce_dr", ["reactive co-evaporation", "rce dr"]),
    ("coated_conductor", ["coated conductor", "rebco tape", "2g hts"]),
    ("mgb2", ["mgb2", "magnesium diboride"]),
    ("smes", ["superconducting magnetic energy storage"]),
    ("ni_coils", ["no-insulation", "ni coil", "no insulating"]),
    ("corc", ["corc cable", "conductor on round core"]),
    ("sfcl", ["superconducting fault current limiter", "sfcl"]),
    ("hydrides", ["superconducting hydride", "hydrogen-rich superconduct"]),
    ("nb3sn", ["nb3sn", "niobium-tin"]),
]


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def tokenize(text: str):
    return TOKEN_RE.findall(text.lower())


def norm_term(t: str) -> str:
    return re.sub(r"\s+", " ", t.strip().lower())


def part_readable(path: Path) -> bool:
    """Читается ли parquet-часть (ловим недописанные файлы прошлых падений)."""
    if not (path.exists() and path.stat().st_size > 0):
        return False
    try:
        return pq.read_metadata(path).num_rows >= 0
    except Exception:
        return False


def build_year_parts(tbl: pa.Table, year: int, ypart: Path, wpart: Path) -> int:
    """Шаг 1, чанкованный фикс 26.09: df/word_df чанками → частичные row-группы.

    Пер-документальная логика (стоп-слова, n-граммы 1..4, числовые фильтры) —
    ДОСЛОВНО из оригинала (frozen). Семантика df unchanged: чанковые дубли
    (term, year) схлопываются SUM'ой в агрегации шага 2.
    """
    schema_y = pa.schema([("term", pa.string()), ("year", pa.int32()),
                          ("df", pa.int32())])
    schema_w = pa.schema([("word", pa.string()), ("year", pa.int32()),
                          ("df", pa.int32())])
    tmp_y = Path(str(ypart) + ".tmp")
    tmp_w = Path(str(wpart) + ".tmp")
    n_local = 0
    wrote = False
    with pq.ParquetWriter(str(tmp_y), schema_y, compression="zstd") as wy, \
         pq.ParquetWriter(str(tmp_w), schema_w, compression="zstd") as ww:
        for off in range(0, tbl.num_rows, CHUNK_DOCS):
            sub = tbl.slice(off, CHUNK_DOCS)
            df_chunk = defaultdict(int)       # term -> число работ в чанке
            word_chunk = defaultdict(int)     # униграмма -> число работ в чанке
            for title, abstract in zip(sub.column("title").to_pylist(),
                                       sub.column("abstract").to_pylist()):
                text = (title or "") + " " + (abstract or "")
                if not text.strip():
                    continue
                n_local += 1
                toks = tokenize(text)
                if not toks:
                    continue
                terms = set()
                for n in range(1, MAX_N + 1):
                    for i in range(len(toks) - n + 1):
                        gram = toks[i:i + n]
                        if n > 1 and (gram[0] in STOP or gram[-1] in STOP):
                            continue
                        if all(re.fullmatch(r"[0-9.]+", g) for g in gram):
                            continue
                        terms.add(" ".join(gram))
                for t in terms:
                    df_chunk[t] += 1
                for w in set(toks):
                    if w not in STOP:
                        word_chunk[w] += 1
            if df_chunk:
                wy.write_table(pa.table({
                    "term": pa.array(list(df_chunk.keys()), pa.string()),
                    "year": pa.array([year] * len(df_chunk), pa.int32()),
                    "df": pa.array(list(df_chunk.values()), pa.int32()),
                }))
                wrote = True
            if word_chunk:
                ww.write_table(pa.table({
                    "word": pa.array(list(word_chunk.keys()), pa.string()),
                    "year": pa.array([year] * len(word_chunk), pa.int32()),
                    "df": pa.array(list(word_chunk.values()), pa.int32()),
                }))
                wrote = True
            del df_chunk, word_chunk
    if not wrote:  # год без текста: пишем пустые файлы, чтобы resume работал
        pq.write_table(pa.table({"term": pa.array([], pa.string()),
                                 "year": pa.array([], pa.int32()),
                                 "df": pa.array([], pa.int32())}),
                       tmp_y, compression="zstd")
        pq.write_table(pa.table({"word": pa.array([], pa.string()),
                                 "year": pa.array([], pa.int32()),
                                 "df": pa.array([], pa.int32())}),
                       tmp_w, compression="zstd")
    os.replace(tmp_y, ypart)   # атомарно: недописанное не проходит resume-проверку
    os.replace(tmp_w, wpart)
    return n_local


def main() -> int:
    global SLICE, OUTDIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke-year", type=int, help="мини-прогон по одному году")
    ap.add_argument("--slice", default=None,
                    help="каталог среза (P3: произвольный набор тем)")
    ap.add_argument("--out", default=None,
                    help="каталог выхода (P3: results/termtech_<slug>)")
    args = ap.parse_args()
    if args.slice:
        SLICE = Path(args.slice)
    if args.out:
        OUTDIR = Path(args.out)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    parts = sorted(SLICE.glob("year=*.parquet"))
    if not parts:
        log("Нет sp_slice — сначала termtech_sp_slice.py")
        return 1
    if args.smoke_year:
        parts = [p for p in parts if f"year={args.smoke_year}." in str(p)]

    t_all = time.time()
    yeardir = OUTDIR / "_yeardf"
    yeardir.mkdir(parents=True, exist_ok=True)
    n_docs = 0
    n_docs_by_year = {}

    for p in parts:
        t0 = time.time()
        year = int(re.search(r"year=(\d{4})", str(p)).group(1))
        ypart = yeardir / f"year={year}.parquet"
        wpart = yeardir / f"wyear={year}.parquet"
        if part_readable(ypart) and part_readable(wpart):
            n_docs_by_year[year] = -1  # объём работ года уже известен из sp_slice
            meta = pq.read_metadata(ypart)
            log(f"{p.name}: skip (exists, {meta.num_rows} terms)")
            continue
        # недописанный мусор прошлых падений — убрать и пересчитать
        for bad in (ypart, wpart, Path(str(ypart) + ".tmp"), Path(str(wpart) + ".tmp")):
            if bad.exists():
                log(f"удаление недописанного {bad.name}")
                bad.unlink()
        tbl = pq.read_table(p, columns=["title", "abstract"])
        n_local = build_year_parts(tbl, year, ypart, wpart)
        del tbl
        n_docs_by_year[year] = n_local
        n_docs += n_local
        log(f"{p.name}: {n_local} docs, chunked parts written, {time.time()-t0:.1f}s")

    # число работ года: из sp_slice напрямую (не зависит от skip)
    if any(v == -1 for v in n_docs_by_year.values()):
        n_docs_by_year = {}
        for p in parts:
            y = int(re.search(r"year=(\d{4})", str(p)).group(1))
            n_docs_by_year[y] = pq.read_metadata(p).num_rows
        n_docs = sum(n_docs_by_year.values())
    log(f"corpus: {n_docs} docs, {time.time()-t_all:.1f}s")

    # --- агрегация: целиком в DuckDB (фикс 26.09 — в Python не материализуем) ---
    yglob = str(yeardir / "year=*.parquet")
    wglob = str(yeardir / "wyear=*.parquet")
    aggdir = OUTDIR / "_agg"
    aggdir.mkdir(parents=True, exist_ok=True)
    allt_p = aggdir / "allt.parquet"        # df>=5, без kPMI (промежуточник)
    py_p = aggdir / "py.parquet"            # (term, year, ydf) — после чанк-merge
    wdf_p = aggdir / "word_df.parquet"
    spill = "/mnt/e/openalex_derived/tmp_duck"
    # memory_limit 4GB + preserve_insertion_order=false (фикс 26.09 23:5x: фаза 1
    # глобальным GROUP BY на 450M строк biomed упиралась в лимит 3GB даже со
    # спиллом → OOM rc=1; теперь фаза 1 ПОГОДОВО, ≤44M групп на запрос).
    # Spill на E: (20GB практика A0). Фильтры MIN_DF/kPMI frozen.
    con = duckdb.connect(config={"memory_limit": "4GB", "threads": 2,
                                 "temp_directory": spill,
                                 "preserve_insertion_order": False})
    # фаза 1: схлоп чанковых дублей (term, year) — погодово (эквивалентность:
    # SUM ассоциативен, группировка (term,year) та же, порядок строк не значим)
    log("фаза 1: чанк-merge (term, year) по годам …")
    stale = aggdir / "py.parquet"          # недописанный остаток попытки 23:53
    if stale.exists():
        stale.unlink()
    for yp in sorted(yeardir.glob("year=*.parquet")):
        y = int(re.search(r"year=(\d{4})", yp.name).group(1))
        con.execute(f"""
            COPY (SELECT term, year, SUM(df)::INT AS ydf
                  FROM read_parquet('{yp}') GROUP BY term, year)
                  TO '{aggdir}/py_{y}.parquet' (FORMAT parquet, COMPRESSION zstd)
        """)
        log(f"  py_{y}.parquet done")
    # фаза 2: агрегация по терминам → allt. ⚠ ФОЛЛБЭК АУДИТА 27.09: глобальный
    # GROUP BY на ~390M строк падал OOM (3.7/3.7 GiB) ДАЖЕ при memory_limit 4GB +
    # spill (попытки 26.09 23:53 и 27.09 00:26) → двухуровневая агрегация:
    # (1.5) один потоковый проход редистрибуции по 16 hash-бакетам,
    # (2) GROUP BY внутри каждого бакета (~1/16 данных, пик ~1-2 ГБ).
    # Эквивалентность: бакет по hash(term) детерминирован — один термин всегда
    # в одном бакете → склейка бакетов ≡ глобальному GROUP BY (SUM/CASE ассоциативны,
    # HAVING df>=5 применяется к тем же суммам).
    log("фаза 1.5: редистрибуция py_* → bkt/ (16 бакетов) …")
    bdir = aggdir / "bkt"
    if bdir.exists():
        shutil.rmtree(bdir)
    con.execute(f"""
        COPY (SELECT term, year, ydf,
                     CAST(hash(term) & 15 AS TINYINT) AS bck
              FROM read_parquet('{aggdir}/py_*.parquet'))
              TO '{bdir}' (FORMAT parquet, COMPRESSION zstd, PARTITION_BY bck)
    """)
    log("фаза 2: агрегация по бакетам → allt …")
    bparts = []
    for k in range(16):
        bp = aggdir / f"allt_b{k:02d}.parquet"
        con.execute(f"""
            COPY (
              SELECT term,
                     CAST(LENGTH(string_split(term, ' ')) AS BIGINT) AS n_tok,
                     df, first_year, growth, n_recent, n_base
              FROM (
                SELECT term,
                       SUM(ydf)::INT AS df,
                       MIN(CASE WHEN ydf >= {MIN_YEAR_CNT} THEN year END)::INT AS first_year,
                       SUM(CASE WHEN year BETWEEN 2023 AND 2025 THEN ydf ELSE 0 END)::INT AS n_recent,
                       SUM(CASE WHEN year BETWEEN 2016 AND 2022 THEN ydf ELSE 0 END)::INT AS n_base,
                       (SUM(CASE WHEN year BETWEEN 2023 AND 2025 THEN ydf ELSE 0 END) / 3.0)
                       / (SUM(CASE WHEN year BETWEEN 2016 AND 2022 THEN ydf ELSE 0 END) / 7.0 + 1.0)
                           AS growth
                FROM read_parquet('{bdir}/bck={k}/*.parquet')
                GROUP BY term
                HAVING SUM(ydf) >= 5
              )
            ) TO '{bp}' (FORMAT parquet, COMPRESSION zstd)
        """)
        bparts.append(str(bp))
        log(f"  бакет {k+1}/16 done")
    files_sql = ", ".join(f"'{p}'" for p in bparts)
    con.execute(f"""
        COPY (SELECT * FROM read_parquet([{files_sql}]))
              TO '{allt_p}' (FORMAT parquet, COMPRESSION zstd)
    """)
    for bp in bparts:
        Path(bp).unlink(missing_ok=True)
    shutil.rmtree(bdir, ignore_errors=True)
    n_terms_total = pq.read_metadata(allt_p).num_rows
    log(f"aggregated terms: {n_terms_total}")
    log(f"df>=5: {n_terms_total} terms")
    # word_df (униграммы, без порога — как в оригинале)
    con.execute(f"""
        COPY (SELECT word, SUM(df)::INT AS df FROM read_parquet('{wglob}')
              GROUP BY word) TO '{wdf_p}' (FORMAT parquet, COMPRESSION zstd)
    """)

    # kPMI: в Python — ТОЛЬКО multi-термины df>=20 (ровно исходное множество
    # multi_idx = n_tok>1 & df>=MIN_DF; формула и math.log — дословно оригинал)
    c20 = con.execute(f"""
        SELECT term, df FROM read_parquet('{allt_p}')
        WHERE df >= {MIN_DF} AND strpos(term, ' ') > 0
    """).fetchdf()
    wdf = con.execute(f"SELECT word, df FROM read_parquet('{wdf_p}')").fetchdf()
    word_df = dict(zip(wdf["word"], wdf["df"]))
    del wdf
    log(f"kPMI: multi-token df>={MIN_DF}: {len(c20)}")
    N = float(max(n_docs, 1))
    terms20 = c20["term"].tolist()
    dfs20 = c20["df"].tolist()
    del c20
    vals = np.empty(len(terms20))
    for j in range(len(terms20)):
        t = terms20[j]
        d = float(dfs20[j])
        words = t.split(" ")
        prod = 1.0
        for w in words:
            prod *= max(float(word_df.get(w, d)), 1.0)
        vals[j] = math.log(max(d, 1.0) * (N ** (len(words) - 1)) / prod)
    kdf = pd.DataFrame({"term": terms20, "kpmi": vals})
    del terms20, dfs20, vals
    # kPMI → parquet, затем кадры освобождаются ДО тяжёлых COPY (фикс капа 26.09):
    # в Python остаётся только word_df (~0.5 ГБ), join читает parquet со стороны DuckDB
    kpmi_p = aggdir / "kpmi.parquet"
    kdf.to_parquet(kpmi_p, compression="zstd")
    del kdf
    gc.collect()

    # all_terms.parquet: все df>=5, kpmi = NaN в НЕ multi и в multi df 5-19
    # (ДИВЕРГЕНЦИЯ от оригинала, аудит 27.09 P2: оригинал считал kPMI для всех multi;
    #  на выдачу не влияет — filter/recall/retro читают candidates, не all_terms)
    con.execute(f"""
        COPY (
          SELECT a.term, a.n_tok, a.df, a.first_year, a.growth,
                 a.n_recent, a.n_base,
                 COALESCE(k.kpmi, CAST('NaN' AS DOUBLE)) AS kpmi
          FROM read_parquet('{allt_p}') a
          LEFT JOIN read_parquet('{kpmi_p}') k ON a.term = k.term
        ) TO '{OUTDIR / "all_terms.parquet"}' (FORMAT parquet, COMPRESSION zstd)
    """)
    log(f"all_terms: {n_terms_total} rows")

    # --- фильтры §2/§3 (frozen) ---
    cand = con.execute(f"""
        SELECT a.term, a.n_tok, a.df, a.first_year, a.growth,
               a.n_recent, a.n_base, k.kpmi
        FROM read_parquet('{allt_p}') a
        LEFT JOIN read_parquet('{kpmi_p}') k ON a.term = k.term
        WHERE a.df >= {MIN_DF}
          AND a.df <= {DF_MAX_FRAC} * {n_docs}
          AND (a.n_tok = 1 OR k.kpmi >= {KPMI_MIN})
        ORDER BY a.growth DESC
    """).fetchdf()
    cand.to_parquet(OUTDIR / "candidates.parquet", compression="zstd")
    log(f"candidates: {len(cand)} (df>={MIN_DF}, df<=50%, kPMI>={KPMI_MIN})")

    # --- eval §5 + sensitivity (±×2 по df_min и kpmi_min) ---
    def recall(df_min: int, kpmi_min: float) -> dict:
        sub = cand[(cand["df"] >= df_min)
                   & ((cand["n_tok"] == 1) | (cand["kpmi"] >= kpmi_min))]
        terms_norm = [norm_term(t) for t in sub["term"]]
        res = {}
        for name, markers in EVAL:
            found = None
            for m in markers:
                for t in terms_norm:
                    if m == t or f" {m} " in f" {t} " or t.startswith(m + " ") \
                       or t.endswith(" " + m):
                        found = m
                        break
                if found:
                    break
            res[name] = found
        return res

    base = recall(MIN_DF, KPMI_MIN)
    n_found = sum(1 for v in base.values() if v)
    sens = {
        "df40_kpmi0.1": sum(1 for v in recall(40, 0.10).values() if v),
        "df10_kpmi0.025": sum(1 for v in recall(10, 0.025).values() if v),
    }
    report = {
        "n_docs": n_docs,
        "n_terms_total": int(n_terms_total),
        "n_candidates": int(len(cand)),
        "eval_frozen": "methodology/TERMTECH_DESIGN.md §5 (2026-09-25)",
        "recall": {k: v for k, v in base.items()},
        "recall_n": f"{n_found}/{len(EVAL)}",
        "superconducting_diode_found": base["superconducting_diode"] is not None,
        "sensitivity_recall_n": sens,
        "params": {"min_df": MIN_DF, "kpmi_min": KPMI_MIN,
                   "df_max_frac": DF_MAX_FRAC},
    }
    (OUTDIR / "eval_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    log(f"recall {report['recall_n']}; diode found = "
        f"{report['superconducting_diode_found']}; sensitivity {sens}")

    # --- top_terms.md ---
    lines = ["# TermTech v0 — топ терминов (СП-срез, frozen params)",
             "", f"Доков: {n_docs}; кандидатов: {len(cand)}", "",
             "## Топ-100 по growth (df>=20)", "",
             "| # | term | df | first_year | growth | kPMI |",
             "|---|---|---|---|---|---|"]
    for i, r in enumerate(cand.head(100).itertuples(), 1):
        kval = r.kpmi
        k = "" if kval is None or (isinstance(kval, float) and math.isnan(kval)) else f"{kval:.2f}"
        fy = r.first_year if r.first_year is not None and not (
            isinstance(r.first_year, float) and math.isnan(r.first_year)) else "-"
        lines.append(f"| {i} | {r.term} | {r.df} | {fy} | {r.growth:.2f} | {k} |")
    lines += ["", "## Топ-40 emerging (first_year>=2018, n_recent>=5)", "",
              "| # | term | df | first_year | growth |", "|---|---|---|---|---|"]
    em = cand[(pd.to_numeric(cand["first_year"], errors="coerce").fillna(9999)
               >= EMERGING_FIRST_YEAR)
              & (cand["n_recent"] >= EMERGING_RECENT_MIN)].head(40)
    for i, r in enumerate(em.itertuples(), 1):
        lines.append(f"| {i} | {r.term} | {r.df} | {int(r.first_year)} | {r.growth:.2f} |")
    (OUTDIR / "top_terms.md").write_text("\n".join(lines) + "\n")
    log(f"top_terms.md written; total {time.time()-t_all:.1f}s")

    # промежуточные (term,year)-merge'ы больше не нужны; allt оставляем для аудита
    for pyp in aggdir.glob("py_*.parquet"):
        try:
            pyp.unlink()
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
