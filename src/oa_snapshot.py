#!/usr/bin/env python3
"""OA Snapshot — движок работы со снапшотом OpenAlex (2026-06-26).

Роли: (1) план прогона по манифесту; (2) батч-ингест works → производные Parquet
(локально: taxonomy, T_stats, T_digest; на E:: T_text, topic_index);
(3) пост-пассы (topic_index, итоговый T_digest); (4) запросы: направление → ~50 тем.

Схема размещения (решение автора 2026-09-21):
  ЛОКАЛЬНО (WSL, бюджет ~20 ГБ): taxonomy(0.1) + T_stats(3-5) + T_digest(0.5-1)
  НА E: (освобождено ~120 ГБ):     T_text(66-99) + topic_index(5-10)
  ВРЕМЕННО (C:\\oa_tmp):           staging пачки снапшота, удаляются после обработки.

Ключевые решения:
- works партиционированы по updated_date ⇒ полный проход обязателен (одна ночь, ~190 батчей,
  ресумабельный чекпоинт по батчам).
- Тема/институты извлекаются регэкспом по стабильной JSON-структуре (без from_json-кастов).
- Абстракт хранится как есть (inverted index, JSON), реконструкция — только для кандидатов.
"""
from __future__ import annotations
import glob, json, logging, os, re, subprocess, sys, time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import duckdb

# ---------------------------------------------------------------- конфиг

WORK_COLS = """{'id':'VARCHAR','title':'VARCHAR','abstract_inverted_index':'JSON',
'publication_year':'INTEGER','language':'VARCHAR','type':'VARCHAR','cited_by_count':'INTEGER',
'counts_by_year':'JSON','topics':'VARCHAR','primary_topic':'JSON','institutions':'VARCHAR',
'is_retracted':'BOOLEAN','is_paratext':'BOOLEAN'}"""
# 'T(\d+)' — один backslash в значении (в Python-исходнике \\d)
RE_TOPIC  = '"id":"https://openalex.org/T([0-9]+)"'
RE_INST   = '"id":"https://openalex.org/I([0-9]+)"'
RE_PRIMARY = "T([0-9]+)$"

SCHEMA_TOPICS="STRUCT(id VARCHAR)[]"  # резерв, не используется

@dataclass
class Paths:
    local: Path          # локальный корень производной базы (data/openalex_derived/)
    e: Path              # корень на E: (/mnt/e/openalex_derived)
    staging: Path        # C:\oa_tmp (WSL-путь /mnt/c/oa_tmp)
    def taxonomy(self) -> Path: return self.local / "taxonomy"
    def stats(self) -> Path: return self.local / "T_stats"
    def digest(self) -> Path: return self.local / "T_digest"
    def digest_raw(self) -> Path: return self.local / "T_digest_raw"
    def text(self) -> Path: return self.e / "T_text"
    def topic_index(self) -> Path: return self.e / "topic_index"
    def plan(self) -> Path: return self.local / "ingest_plan.json"
    def log(self) -> Path: return self.local / "ingest.log"

# ---------------------------------------------------------------- план

@dataclass
class Batch:
    idx: int
    files: list  # относительные пути в works/ (updated_date=.../part_NNNN.gz)
    n_records: int = 0
    n_bytes: int = 0
    status: str = "pending"  # pending|done
    def rel_paths(self, works_root: Path) -> list[Path]:
        return [works_root / f for f in self.files]

def load_manifest(manifest_path: Path) -> dict:
    with open(manifest_path) as fh:
        m = json.load(fh)
    ws = next(e for e in m["entities"] if e["entity"] == "works")
    files = []
    for f in ws["files"]:
        url: str = f["url"]                       # s3://openalex/data/jsonl/works/updated_date=.../part_0000.gz
        rel = url.split("data/jsonl/works/")[1]   # updated_date=.../part_0000.gz
        files.append({"path": rel, "records": f["meta"]["record_count"], "bytes": f["meta"]["content_length"]})
    return {"date": m["date"], "total_records": ws["record_count"], "files": files}

def make_plan(manifest_path: Path, target_gb: float = 3.0, max_files: int = 64,
              works_root: Path = None, quiet: bool = False) -> list[Batch]:
    """Строит батчи по манифесту. Отсутствующие на диске файлы ПРОПУСКАЮТСЯ с пометкой
    (после инцидента 2026-09-21: источники никогда не трогаем, а их отсутствие не роняет план)."""
    m = load_manifest(manifest_path)
    batches, cur, cur_bytes = [], [], 0
    skipped = []
    for f in m["files"]:
        if works_root is not None and not (works_root / f["path"]).exists():
            skipped.append(f["path"])
            continue
        if (cur_bytes > 0 and cur_bytes + f["bytes"] / 1e9 > target_gb) or len(cur) >= max_files:
            batches.append(cur); cur, cur_bytes = [], 0
        cur.append(f); cur_bytes += f["bytes"] / 1e9
    if cur: batches.append(cur)
    if skipped and not quiet:
        print(f"[plan] пропущено отсутствующих файлов: {len(skipped)} "
              f"({sum(fc['records'] for fc in m['files'] if fc['path'] in skipped):,} записей)")
    out = []
    for i, files in enumerate(batches):
        out.append(Batch(idx=i, files=[f["path"] for f in files],
                         n_records=sum(f["records"] for f in files),
                         n_bytes=sum(f["bytes"] for f in files)))
    return out

# ---------------------------------------------------------------- Windows-нативы

def _ps(script: str) -> None:
    r = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-Command", script], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=3600)
    if r.returncode != 0:
        raise RuntimeError(f"powershell failed: {r.stderr[-400:]} ({r.stdout[-200:]})")

_WIN_MOUNTS = [("/mnt/ee/", "E:\\"), ("/mnt/e/", "E:\\"), ("/mnt/c/", "C:\\"), ("/mnt/d/", "D:\\")]

def _to_win(p: Path) -> str:
    s = str(p)
    for mnt, drv in _WIN_MOUNTS:
        if s.startswith(mnt):
            return drv + s[len(mnt):].replace("/", "\\")
    return s.replace("/", "\\")

def win_copy_to_staging(files: Iterable[Path], staging: Path, chunk: int = 60):
    """Нативный Copy-Item E:→C:\\oa_tmp (обходит медленный 9p-write; чтение тоже нативное)."""
    fl = [str(p) for p in files if not (staging / p.name).exists() or (staging / p.name).stat().st_size < 1000]
    for i in range(0, len(fl), chunk):
        names = "', '".join(_to_win(Path(p)) for p in fl[i:i+chunk])
        wd = _to_win(staging)
        for attempt in range(3):
            _ps(f"$ErrorActionPreference='Continue'; New-Item -ItemType Directory -Force -Path '{wd}' | Out-Null; "
                f"$ok=0; $fail=0; foreach ($p in @('{names}')) {{ try {{ Copy-Item $p '{wd}\\' -Force; $ok++ }} catch {{ $fail++ }} }}; "
                f"'{chr(10)}win_copy ok=$ok fail=$fail'")
            missing = [p for p in fl[i:i+chunk] if not (staging / Path(p).name).exists() or (staging / Path(p).name).stat().st_size < 1000]
            if not missing:
                break
            time.sleep(5)  # ретрай после паузы (транзитные сбои копирования)
    for p in files:
        if not (staging / p.name).exists():
            raise RuntimeError(f"staging copy failed: {p}")

# ---------------------------------------------------------------- таксономия

def build_taxonomy(con: duckdb.DuckDBPyConnection, P: Paths, small_dir: Path,
                   snapshot_jsonl: Path | None = None):
    """Малые сущности (topics/subfields/fields/domains/keywords) → taxonomy/*.parquet (локально).
    FIX NJ-0 (24.09): snapshot_jsonl — каталог data/jsonl снапшота; если задан, читаются
    ВСЕ дневные файлы `updated_date=*/**.gz` сущности (union), а НЕ один staging-файл.
    Старое поведение (small_dir/<ent>.gz) потеряло 34 темы: в стейджинг попал только
    2026-06-26, а 34 темы жили в дневных файлах 06-18..06-25 (4482 вместо 4516)."""
    d = P.taxonomy(); d.mkdir(parents=True, exist_ok=True)
    spec = {
        "topics":    "SELECT id, display_name, description, keywords, subfield.id AS subfield_id, field.id AS field_id, domain.id AS domain_id, works_count, cited_by_count",
        "subfields": "SELECT id, display_name, field.id AS field_id",
        "fields":    "SELECT id, display_name, domain.id AS domain_id",
        "domains":   "SELECT id, display_name",
    }
    for ent, sel in spec.items():
        if snapshot_jsonl is not None:
            fs = sorted(snapshot_jsonl.glob(f"{ent}/**/*.gz"))
            if not fs:
                continue
            fl = ", ".join(f"'{f}'" for f in fs)
            srcq = (f"read_json([{fl}], format='newline_delimited', "
                    f"union_by_name=true, ignore_errors=true)")
        else:
            src = small_dir / f"{ent}.gz"
            if not src.exists():
                continue
            srcq = f"read_json_auto('{src}', format='newline_delimited')"
        con.execute(f"COPY ({sel} FROM {srcq}) "
                    f"TO '{d}/{ent}.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)")

# ---------------------------------------------------------------- редукция батча

def _read_q(con: duckdb.DuckDBPyConnection, files: list[Path]):
    pat = ", ".join(f"'{f}'" for f in files)
    return f"read_json_auto([{pat}], format='newline_delimited', columns={WORK_COLS}, ignore_errors=true)"

def reduce_batch(con: duckdb.DuckDBPyConnection, files: list[Path], P: Paths, batch_idx: int, chunk_size: int = 8):
    """Один батч: gz читается ОДИН раз ПОРЦИЯМИ (chunked) → локальный parquet → из него три вывода.
    Порции ограничивают пик памяти (~1-2 ГБ на порцию) — устойчиво к состоянию машины (OOM ушёл).
    Дедуп по id выполняет глобальный build_dedup (пост-пасс по годам)."""
    import shutil
    for d in (P.stats(), P.text(), P.digest_raw()):
        d.mkdir(parents=True, exist_ok=True)
    tb = P.local / "tmp_batches"
    tb.mkdir(parents=True, exist_ok=True)
    tdir = tb / f"b{batch_idx:04d}"
    shutil.rmtree(tdir, ignore_errors=True)
    tdir.mkdir(parents=True, exist_ok=True)
    cols = ("id, publication_year, language, type, cited_by_count, counts_by_year, "
            "topics, primary_topic, institutions, title, abstract_inverted_index, "
            "is_retracted, is_paratext")
    for ci in range(0, len(files), chunk_size):
        ch = files[ci:ci + chunk_size]
        src = _read_q(con, ch)
        con.execute(f"COPY (SELECT {cols} FROM {src} WHERE publication_year >= 2016) "
                    f"TO '{tdir}/chunk={ci // chunk_size:02d}.parquet' "
                    f"(FORMAT PARQUET, COMPRESSION ZSTD, OVERWRITE_OR_IGNORE)")
    base = f"read_parquet('{tdir}/**/*.parquet')"
    # T_stats
    sel_stats = f"""
      SELECT id, publication_year, language, type, cited_by_count, counts_by_year,
             list_transform(regexp_extract_all(coalesce(topics,'[]'), '{RE_TOPIC}', 1), x->CAST(x AS INT)) AS topic_ids,
             try_cast(regexp_extract(coalesce(json_extract_string(primary_topic,'$.id'),''), '{RE_PRIMARY}', 1) AS INT) AS primary_topic_id,
             list_transform(regexp_extract_all(coalesce(institutions,'[]'), '{RE_INST}', 1), x->CAST(x AS INT)) AS institution_ids,
             is_retracted, is_paratext
      FROM {base}"""
    con.execute(f"COPY ({sel_stats}) TO '{P.stats()}/batch={batch_idx:04d}' (FORMAT PARQUET, COMPRESSION ZSTD, OVERWRITE_OR_IGNORE, PARTITION_BY (publication_year))")
    # T_text
    sel_text = f"""
      SELECT id, publication_year, title, abstract_inverted_index,
             is_retracted, is_paratext FROM {base}"""
    con.execute(f"COPY ({sel_text}) TO '{P.text()}/batch={batch_idx:04d}' (FORMAT PARQUET, COMPRESSION ZSTD, OVERWRITE_OR_IGNORE, PARTITION_BY (publication_year))")
    # digest_raw: топ-200 по цитированиям в пределах батча для каждой темы
    sel_digest = f"""
      WITH w AS (SELECT * FROM {base} WHERE topics IS NOT NULL),
           p AS (SELECT w.id, t.unnest AS tid, w.publication_year, w.cited_by_count, w.title
                 FROM w, unnest(list_transform(regexp_extract_all(coalesce(w.topics,'[]'), '{RE_TOPIC}', 1), x->CAST(x AS INT))) AS t)
      SELECT * EXCLUDE (rn) FROM (
        SELECT p.*, row_number() OVER (PARTITION BY tid ORDER BY cited_by_count DESC) AS rn FROM p
      ) WHERE rn <= 200"""
    con.execute(f"COPY ({sel_digest}) TO '{P.digest_raw()}/batch={batch_idx:04d}.parquet' (FORMAT PARQUET, COMPRESSION ZSTD, OVERWRITE_OR_IGNORE)")
    shutil.rmtree(tdir, ignore_errors=True)

# ---------------------------------------------------------------- пост-пассы

def build_dedup(con: duckdb.DuckDBPyConnection, P: Paths):
    """Глобальная дедупликация по id (партиции снапшота могут пересекаться!).
    Для каждого года читаем ВСЕ источники (batch-части + уже собранные year=),
    оставляем id с максимальным cited_by_count, пишем year-финалы и удаляем batch-структуру.
    temp_directory — на E: (spill безопасен).

    ⚠️ Объединение batch= + year= ОБЯЗАТЕЛЬНО: ночной прогон идёт с --resume, при котором
    тестовые батчи (0-6) уже схлопнуты в year=YYYY, а новые батчи пишут batch=NNNN.
    Если читать только batch= (как в старой версии), данные тестовых year=YYYY будут
    ЗАТЁРТЫ на каждом повторном --post-only → потеря работ. То же при докачке файлов
    из S3 (--files + --post-only): новые batch= не должны затирать готовые year=.

    ⚠️ Tech: publication_year живёт в ИМЕНИ КАТАЛОГА (партиция), а не в файле
    (PARTITION_BY убирает её из данных). Одиночный glob при чтении подставляет её из
    имени каталога, но read_parquet([glob1, glob2]) этого НЕ делает (binder error
    при PARTITION_BY). Поэтому разные источники объединяются UNION ALL BY NAME
    с ЯВНЫМ списком колонок (без HIVE-мусора batch/year).
    """
    import shutil, os as _os
    y_from = int(_os.environ.get("OA_YEAR_FROM", "2016"))
    y_to   = int(_os.environ.get("OA_YEAR_TO", "2026"))
    con.execute(f"SET temp_directory='{P.e}/tmp_duck'")
    con.execute("SET preserve_insertion_order=false")  # ⚠️ OOM до спилла на окне 25M строк 2016
    # ⚠️ OOM-фикс v6 (23.09, оба падения 2024 на строке чанк-COPY): буферный пул
    # коннекта ПОСЛЕ фазы-1 (keys+статы) тёплый — чанк текста упирался в лимит
    # даже с 20 файлами, тогда как тест на 40 тяжёлых файлах на СВЕЖЕМ коннекте
    # проходил без спилла. Лечение: свежее подключение на каждый чанк и на фазу-3.
    _th = con.execute("SELECT current_setting('threads')").fetchone()[0]
    _ml = con.execute("SELECT current_setting('memory_limit')").fetchone()[0]

    def _fresh() -> duckdb.DuckDBPyConnection:
        c = duckdb.connect()
        # ⚠️ temp_directory — ПЕРВЫМ (SET до первого использования temp, иначе NotImplementedError)
        c.execute(f"SET temp_directory='{P.e}/tmp_duck'")
        c.execute(f"SET threads={_th}; SET memory_limit='{_ml}'; SET preserve_insertion_order=false")
        return c
    dedup_cols = ("id, publication_year, language, type, cited_by_count, counts_by_year, "
                  "topic_ids, primary_topic_id, institution_ids, is_retracted, is_paratext")
    dedup_cols_text = ("id, publication_year, title, abstract_inverted_index, "
                       "is_retracted, is_paratext")
    for y in range(y_from, y_to + 1):
        import glob as _g
        def _sources(root_dir, year):
            """Все глобы данных года: batch-части и/или готовые year-финалы."""
            pats = []
            for pat in (f"{root_dir}/batch=*/publication_year={year}/data_*.parquet",
                        f"{root_dir}/year={year}/publication_year={year}/data_*.parquet"):
                if _g.glob(pat):
                    pats.append(pat)
            return pats
        st_pats = _sources(P.stats(), y)
        tx_pats = _sources(P.text(), y)
        if not st_pats:
            continue
        st_src = " UNION ALL BY NAME ".join(
            f"SELECT {dedup_cols} FROM read_parquet('{p}')" for p in st_pats)
        tx_src = " UNION ALL BY NAME ".join(
            f"SELECT {dedup_cols_text} FROM read_parquet('{p}')" for p in tx_pats) if tx_pats else None
        # ⚠️ OOM-фикс 2026-09-22 (v4, потоковый): НИКАКОГО окна и никаких тяжёлых полей
        # в хеше. (1) keys = лёгкие колонки выигравшей копии на id (max cited): спилл-дружелюбный
        # GROUP BY + arg_max, в памяти ~2ГБ на 25M id. (2) источник присоединяется к keys
        # ПОТОКОМ через внутренний JOIN по (id + все лёгкие ключи) — память не зависит от
        # размера результата, абстракты/JSON текут сквозь без материализации.
        keys_pq = f"{P.stats()}/keys={y}.parquet"
        shutil.rmtree(keys_pq, ignore_errors=True)
        _p1 = _fresh()  # ⚠️ v8: фаза-1 на СВОЕМ коннекте — закроем до чанков, иначе её
        try:            # пул (~2.6 ГБ) держит систему, и чанк-коннект падает (08-й случай)
            _p1.execute(f"""
          COPY (
            SELECT id,
                   max(cited_by_count) AS c,
                   arg_max(publication_year, cited_by_count) AS py,
                   arg_max(language, cited_by_count) AS language,
                   arg_max(type, cited_by_count) AS type
            FROM ({st_src})
            GROUP BY id
          ) TO '{keys_pq}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
            tmp_stats = f"{P.stats()}/year_tmp={y}"
            shutil.rmtree(tmp_stats, ignore_errors=True)  # ⚠️ FIX3: мусор прерванного запуска
            _p1.execute(f"""
          COPY (
            SELECT s.* FROM ({st_src}) s
            JOIN read_parquet('{keys_pq}') k
              ON s.id = k.id AND s.cited_by_count = k.c AND s.publication_year = k.py
             AND s.language IS NOT DISTINCT FROM k.language AND s.type IS NOT DISTINCT FROM k.type
          ) TO '{tmp_stats}' (FORMAT PARQUET, COMPRESSION ZSTD, PARTITION_BY (publication_year))
        """)
        finally:
            _p1.close()  # ← системная память освобождена ДО текстовых чанков
        if tx_src:
            tmp_text = f"{P.text()}/year_tmp={y}"
            manifest = Path(tmp_text) / "manifest.txt"
            # ⚠️ OOM-фикс 2026-09-23 v2 (провал года 2024): монолитный COPY текста
            # (10.9 ГБ/год) упирается в memory_limit 3GB ДО конца прогона (померено:
            # даже 40 файлов → MaxRSS 3.4 ГБ, запас нулевой; год в 2× крупнее — падает).
            # Лечение — ЧАНКИ по ~40 входных файлов: память сбрасывается между COPY.
            # Sid=substr(id,22) сохранён (хеш-JOIN 1.8 → 0.6 ГБ, фикс 09-23 утро).
            # Resume: manifest.txt (строка = входные файлы чанка через '|') — уже
            # посчитанные входы повторно НЕ считаются; выходы чанков — уникальные
            # файлы data_cNNNN.parquet (глобы data_* / ** их подхватывают везде).
            # MOVE отдельным именем обязателен: повторный COPY в тот же partition-
            # каталог перетирает data_0.parquet (проверено 23.09: 3 COPY → 1 файл).
            done_inputs: set = set()
            n_done = 0
            if manifest.exists() and _g.glob(f"{tmp_text}/**/*.parquet", recursive=True):
                for _ln in manifest.read_text().splitlines():
                    if _ln.strip():
                        done_inputs.update(_ln.split("|"))
                        n_done += 1
            else:
                shutil.rmtree(tmp_text, ignore_errors=True)  # ⚠️ FIX3: мусор прерванного запуска
            tx_files = []
            for _pat in tx_pats:
                tx_files.extend(sorted(_g.glob(_pat)))
            tx_files = [f for f in tx_files if f not in done_inputs]
            _CHUNK = int(_os.environ.get("OA_TEXT_CHUNK", "40"))
            _tdir = P.text() / f"chunk_tmp={y}"
            _outdir = Path(tmp_text) / f"publication_year={y}"
            _outdir.mkdir(parents=True, exist_ok=True)
            n_ch = (len(tx_files) + _CHUNK - 1) // _CHUNK
            for _ci in range(n_ch):
                _part = tx_files[_ci * _CHUNK:(_ci + 1) * _CHUNK]
                _src = " UNION ALL BY NAME ".join(
                    f"SELECT {dedup_cols_text} FROM read_parquet('{p}')" for p in _part)
                shutil.rmtree(_tdir, ignore_errors=True)  # свежий слот на каждый чанк
                _c = _fresh()  # ⚠️ v6: чистый буферный пул (тёплый коннект = падение 23.09)
                try:
                    # ⚠️ v7 (23.09, падения чанков 6/15 файлов): INNER JOIN на МЕЛКОМ
                    # чанке оптимизатор duckdb ПЕРЕВОРАЧИВАЛ (build на стороне текста →
                    # абстрактные индексы в хеш → 2.9 ГБ за 20 с → OOM). Semi-join через
                    # IN фиксирует build на keys (RIGHT_SEMI, план проверен): та же
                    # семантика (keys уникален по id, py=год партиции), пик как в тесте.
                    _c.execute(f"""
                  COPY (
                    SELECT t.* FROM ({_src}) t
                    WHERE (substr(t.id, 22), t.publication_year)
                          IN (SELECT substr(id, 22), py FROM read_parquet('{keys_pq}'))
                  ) TO '{_tdir}' (FORMAT PARQUET, COMPRESSION ZSTD, PARTITION_BY (publication_year))
                """)
                finally:
                    _c.close()
                _src_f = _tdir / f"publication_year={y}" / "data_0.parquet"
                _dst_f = _outdir / f"data_c{n_done + _ci:04d}.parquet"
                shutil.move(str(_src_f), str(_dst_f))  # move внутри E: — дёшево (rename)
                with open(manifest, "a") as _mf:  # манифест ПОСЛЕ move: крак = пересчёт
                    _mf.write("|".join(_part) + "\n")  # одного чанка, не потеря (фаза-3 дедупит)
                print(f"[dedup {y}] text-chunk {n_done + _ci + 1}/{n_done + n_ch} "
                      f"({len(_part)} файлов) готов", flush=True)
            shutil.rmtree(_tdir, ignore_errors=True)
        # ⚠️ Фаза 3 (OOM-фикс v5 + v6: СВЕЖИЙ коннект — окно/GroupBy идут после
        # фазы-1 и чанков, тёплый пул не оставляем): JOIN по (id,c,py,lang,type)
        # пропускает ИДЕНТИЧНЫЕ копии
        # id (равный cited из разных партиций снапшота). Добиваем их окном, но ТОЛЬКО по
        # выделенным дублям (1.5M строк вместо 25M — влезает в память).
        _c3 = _fresh()  # ⚠️ v6: фаза-3 на свежем коннекте (тёплый пул = падение 23.09)
        for _root, _glob, _ord in (
            (P.stats(), f"{tmp_stats}/**/*.parquet",
             "publication_year ASC, language ASC, type ASC"),
            (P.text(), f"{tmp_text}/**/*.parquet",
             "publication_year ASC, title ASC, abstract_inverted_index ASC"),
        ):
            import glob as _g
            if not _g.glob(_glob, recursive=True):
                continue
            dup_n = _c3.execute(f"""
              SELECT count(*) FROM (
                SELECT id FROM read_parquet('{_glob}') GROUP BY id HAVING count(*) > 1
              )""").fetchone()[0]
            if dup_n == 0:
                continue
            pid = f"{_root}/dup_ids=tmp.parquet"
            _c3.execute(f"""
              COPY (SELECT id FROM read_parquet('{_glob}') GROUP BY id HAVING count(*) > 1)
              TO '{pid}' (FORMAT PARQUET)
            """)
            _sh2 = _root / f"year_tmp2={y}"
            import shutil as _sh2m
            _sh2m.rmtree(_sh2, ignore_errors=True)
            (_sh2 / "win").mkdir(parents=True, exist_ok=True)
            (_sh2 / "cln").mkdir(parents=True, exist_ok=True)
            _c3.execute(f"""
              COPY (
                SELECT q.* EXCLUDE (rn) FROM (
                  SELECT w.*, row_number() OVER (PARTITION BY w.id ORDER BY {_ord}) AS rn
                  FROM read_parquet('{_glob}') w
                  JOIN read_parquet('{pid}') d ON w.id = d.id
                ) q WHERE q.rn = 1
              ) TO '{_sh2}/win' (FORMAT PARQUET, COMPRESSION ZSTD, PARTITION_BY (publication_year))
            """)
            _c3.execute(f"""
              COPY (
                SELECT c.* FROM read_parquet('{_glob}') c
                ANTI JOIN read_parquet('{pid}') d ON c.id = d.id
              ) TO '{_sh2}/cln' (FORMAT PARQUET, COMPRESSION ZSTD, PARTITION_BY (publication_year))
            """)
            # объединить win+cln в год-финал с дедупом по (id, ...) внутри UNION
            _c3.execute(f"""
              COPY (
                SELECT u.* FROM (
                  SELECT * FROM read_parquet('{_sh2}/win/**/*.parquet')
                  UNION ALL BY NAME
                  SELECT * FROM read_parquet('{_sh2}/cln/**/*.parquet')
                ) u
              ) TO '{_root}/year_final={y}' (FORMAT PARQUET, COMPRESSION ZSTD, PARTITION_BY (publication_year))
            """)
            _sh2m.rmtree(_sh2, ignore_errors=True)
            Path(pid).unlink(missing_ok=True)
            _sh2m.rmtree(_root / f"year_tmp={y}", ignore_errors=True)
            (_root / f"year_final={y}").rename(_root / f"year_tmp={y}")
        _c3.close()
        # swap: удалить старые year= и batch-структуру года, переименовать year_tmp
        import shutil as _sh
        _sh.rmtree(P.stats() / f"year={y}", ignore_errors=True)
        _sh.rmtree(P.text() / f"year={y}", ignore_errors=True)
        for root in (P.stats(), P.text()):
            for d in list(root.glob(f"batch=*/publication_year={y}")):
                _sh.rmtree(d, ignore_errors=True)
            for d in list(root.glob(f"batch=*")):  # ⚠️ FIX1: только ПУСТЫЕ оболочки
                if not any(d.iterdir()):
                    _sh.rmtree(d, ignore_errors=True)
        (P.stats() / f"keys={y}.parquet").unlink(missing_ok=True)
        (P.stats() / f"year_tmp={y}").rename(P.stats() / f"year={y}")
        if tx_src:  # ⚠️ FIX2: text-финал только при наличии text-источников
            (P.text() / f"year_tmp={y}").rename(P.text() / f"year={y}")

def build_topic_index(con: duckdb.DuckDBPyConnection, P: Paths):
    """topic_index: (topic_id, work_id, year, cited) локально из T_stats → сортировка → E:."""
    P.topic_index().mkdir(parents=True, exist_ok=True)
    con.execute(f"""
      COPY (
        SELECT t.unnest AS topic_id, w.id AS work_id, w.publication_year AS year, w.cited_by_count AS cited
        FROM read_parquet('{P.stats()}/year=*/*/*.parquet') w
        CROSS JOIN unnest(w.topic_ids) AS t
        ORDER BY t.unnest, w.cited_by_count DESC
      ) TO '{P.topic_index()}/topic_index.parquet' (FORMAT PARQUET, COMPRESSION ZSTD, OVERWRITE_OR_IGNORE)
    """)

def build_digest_final(con: duckdb.DuckDBPyConnection, P: Paths, top_k: int = 100):
    P.digest().mkdir(parents=True, exist_ok=True)
    raw = f"{P.digest_raw()}/**/*.parquet"
    if not glob.glob(raw, recursive=True):
        logging.warning("build_digest_final: T_digest_raw пуст — digest не пересобран")
        return
    con.execute(f"""
      COPY (
        SELECT * EXCLUDE (rn) FROM (
          SELECT *, row_number() OVER (PARTITION BY tid ORDER BY cited_by_count DESC) AS rn
          FROM read_parquet('{raw}')
        ) WHERE rn <= {top_k}
      ) TO '{P.digest()}/digest.parquet' (FORMAT PARQUET, COMPRESSION ZSTD, OVERWRITE_OR_IGNORE)
    """)

def load_state(P: Paths) -> dict:
    sp = P.plan()
    if sp.exists():
        with open(sp) as fh: return json.load(fh)
    return {"batches": [], "built_at": None}

def save_state(P: Paths, state: dict):
    tmp = P.plan().with_suffix(".tmp")
    with open(tmp, "w") as fh: json.dump(state, fh, ensure_ascii=False, indent=1)
    tmp.replace(P.plan())

def progress(P: Paths, total: int) -> str:
    st = load_state(P)
    done = sum(1 for b in st["batches"] if b["status"] == "done")
    return f"[ingest] {done}/{total} батчей ({100*done/max(total,1):.0f}%)"

# ---------------------------------------------------------------- эмбеддинги тем (LaBSE)

_EMB_MODEL = None

def _get_embedder(model_name: str = "sentence-transformers/LaBSE"):
    global _EMB_MODEL
    if _EMB_MODEL is None:
        from sentence_transformers import SentenceTransformer
        import torch
        torch.set_num_threads(12)
        _EMB_MODEL = SentenceTransformer(model_name, local_files_only=False)
    return _EMB_MODEL

def build_topic_embeddings(con: duckdb.DuckDBPyConnection, P: Paths, model_name: str = "sentence-transformers/LaBSE"):
    """4516 тем → векторы LaBSE → taxonomy/topic_vectors.npy + topic_ids.txt (локально, ~14 МБ)."""
    import numpy as np
    tax = P.taxonomy()
    df = con.execute(f"""
      SELECT id, display_name, coalesce(description,'') AS descr, coalesce(keywords,'[]') AS kw
      FROM read_parquet('{tax}/topics.parquet')""").df()
    import ast
    def _kw(v):
        if v is None:
            return ""
        if isinstance(v, str):
            return " ".join(ast.literal_eval(v))
        return " ".join(v)
    texts = [f"{r.display_name}. {r.descr} {_kw(r.kw)}" for r in df.itertuples()]
    model = _get_embedder(model_name)
    vec = model.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=True)
    np.save(tax / "topic_vectors.npy", vec.astype("float32"))
    (tax / "topic_ids.txt").write_text("\n".join(df["id"]))
    return vec.shape

def _topic_vectors(P: Paths):
    import numpy as np
    return np.load(P.taxonomy() / "topic_vectors.npy"), \
           (P.taxonomy() / "topic_ids.txt").read_text().split("\n")

# ---------------------------------------------------------------- запросы (слои 1-4)

# Лексический матчер направления (правило v1, ЗАМОРОЖЕНО журнал 24.09 18:15).
# Ключи = слова НАЗВАНИЯ направления («Защита ИИ»), НЕ темы-цели теста.
ROUTING_RULE_V1 = ("keys-v1: RU=(ии|искусственн|интеллект)AND(защит|безопасн); "
                    "EN=(ai|artificial intelligence|llm)AND(safety|security|secure)")

def route_query(query: str) -> dict:
    """§4а: лексический матчинг запроса к направлению «Защита ИИ».
    Косинус-вариант ОТВЕРГНЁТ замером (нет зазора: q1=0.284 < q4=0.425 — журнал 18:15).
    Возвращает {matched, matched_by, keys_hit, rule} — уходит в телеметрию результата."""
    q = (query or "").lower()
    hit = []
    if any(k in q for k in ("ии", "искусственн", "интеллект")) and \
       any(k in q for k in ("защит", "безопасн")):
        hit.append("ru")
    en_topic = ("ai " in q or q.startswith("ai") or " ai" in q or
                "artificial intelligence" in q or "llm" in q)
    if en_topic and any(k in q for k in ("safety", "security", "secure")):
        hit.append("en")
    return {"matched": bool(hit),
            "matched_by": ("lexical-" + "+".join(hit)) if hit else "none",
            "keys_hit": hit, "rule": ROUTING_RULE_V1}


def query_directions(con: duckdb.DuckDBPyConnection, P: Paths, query_ru: str,
                     topk: int = 50, years: tuple = (2016, 2026),
                     n_topics: int = 60, match: str = "embed",
                     skip_mega: bool = True,
                     gate_domains: Optional[list] = None,
                     fanout: Optional[dict] = None,
                     routing: Optional[dict] = None,
                     vectors_name: Optional[str] = None) -> dict:
    """Полный конвейер: запрос → темы → кандидаты → направления (агрегация) + топ-работы из digest.
    match='embed' — LaBSE (мультиязычный); match='tfidf' — TF-IDF fallback (без модели).
    gate_domains (И5, альтернатива А-2): список номеров доменов OpenAlex (напр. [3,2] =
    Physical + Social Sciences) — ЕДИНСТВЕННАЯ активная механика отсева на прогоне:
    темы вне доменов маскируются (sim=-1) ВМЕСТО regex-маски mega_mask. None = старое поведение.
    (Доменный гейт вместо имён: COVID/мед-темы структурно в Health(4)/Life(1) Sciences.)
    fanout (И1, стратегия A — решение 16:05): dict {"m","k","ktop","rrf_c",
    "seed","n_topics"} — кластеризация top-M кандидатов, подзапросы = темы-представители
    центроидов, RRF = подзапросы + оригинальный запрос. Словарь из теста НЕ используется
    (А-1 отменён автором). None = без fanout. Телеметрия: result["fanout"] (§4а/§7.11).
    fanout["source"]="lexicon" (стратегия C, лексикон заморожен до замера):
    source="lexicon" → подзапросы = фасеты из fanout["lexicon_path"] (results/qa_facet_lexicon_v1.json),
    семантика expansion: кандидаты = plain top-N ∪ top-ktop каждого фасета (без k-means);
    SQL-LIMIT при fanout поднимается до len(chosen) (фикс A.5/§7.8 для niche-целей).
    routing (§4а; словарь ключей и ПРОФИЛИ ЗАМОРОЖЕНЫ — журнал 24.09 18:15): dict
    {"profiles": {"matched": {...,"gate","fanout","topics","topk"}, "fallback": {...}}}.
    route_query(query) — лексический матчер v1 ( RU: (ии|искусственн|интеллект) AND
    (защит|безопасн); EN: (ai | ai|artificial intelligence|llm) AND (safety|security|secure) ).
    Профиль применяется ПЕРЕД конвейером; result["routing"] = telem {matched, keys_hit, profile}.
    Косинус-матчер отвергнут замером (зазора нет: q1=0.284 < q4=0.425)."""
    import numpy as np
    tax = P.taxonomy()
    topics = con.execute(f"""
      SELECT id, display_name, coalesce(description,'') AS descr, keywords,
             subfield_id, field_id, domain_id
      FROM read_parquet('{tax}/topics.parquet')""").df()
    # routing §4а: лексический матчинг → профиль matched/fallback (заморожены 24.09 18:15)
    routing_telem = None
    if routing is not None:
        r = route_query(query_ru)
        prof = routing["profiles"]["matched" if r["matched"] else "fallback"]
        gate_domains = prof.get("gate")
        fanout = prof.get("fanout")
        n_topics = int(prof.get("topics", n_topics))
        topk = int(prof.get("topk", topk))
        vectors_name = prof.get("vectors", vectors_name)
        routing_telem = {**r, "profile": "matched" if r["matched"] else "fallback"}
    # отсев кандидатов (одна механика на прогон): доменный гейт ИЛИ legacy regex-маска
    mega_mask = np.zeros(len(topics), dtype=bool)
    if gate_domains is not None:
        dom_num = topics["domain_id"].str.extract(r"domains/(\d+)")[0]
        mega_mask = (~dom_num.isin([str(d) for d in gate_domains]) | dom_num.isna()).to_numpy()
    elif skip_mega:
        mega_mask = topics["display_name"].str.contains(
            "Linguistic, Cultural|Legal and Regulatory|Military Technology|Electrical and Electromagnetic|Social Sciences and Policies|Diverse Approaches|Educational Systems|Healthcare and Education|Medicine and Dentistry|General "
            "|Interdisciplinary|Multidisciplinary", regex=True, na=False).to_numpy()
    fanout_telem = None
    if match == "embed":
        import ast
        vecs = np.load(tax / (vectors_name or "topic_vectors.npy"))
        vids = (tax / "topic_ids.txt").read_text().split("\n")
        pos = topics["id"].map({v: i for i, v in enumerate(vids)}).to_numpy()
        model = _get_embedder()
        qv = model.encode([query_ru], normalize_embeddings=True, show_progress_bar=False)[0]
        V = vecs[pos]
        sim = V @ qv
        sim = np.where(mega_mask, -1.0, sim)
        fanout_telem = None
        if fanout:
            chosen, fanout_telem = _fanout_choose(topics, V, sim, mega_mask, qv, model,
                                                  {**(fanout or {}), "n_topics": n_topics})
        else:
            top_idx = np.argsort(sim, kind="stable")[::-1][:n_topics]
            chosen = topics.iloc[top_idx][["id", "display_name"]].assign(score=sim[top_idx])
    else:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        topics["text"] = (topics["display_name"] + " " + topics["descr"] +
                          " " + topics["keywords"].fillna("").astype(str))
        vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=30000,
                              sublinear_tf=True)
        X = vec.fit_transform(topics["text"].tolist() + [query_ru.lower()])
        sim = cosine_similarity(X[-1:], X[:-1])[0]
        sim = np.where(mega_mask, -1.0, sim)
        top_idx = sim.argsort()[::-1][:n_topics]
        chosen = topics.iloc[top_idx][["id", "display_name"]].assign(score=sim[top_idx])
    tid_codes = [int(re.search(r"(\d+)$", i).group(1)) for i in chosen["id"]]
    # направления: агрегация по T_stats (локально, сек); при fanout LIMIT >= len(chosen)
    # (иначе A.5 вырезает niche-цели, попавшие через фасеты/кластеры — §7.8)
    eff_topk = max(topk, len(chosen)) if fanout else topk
    tid_sql = ", ".join(map(str, tid_codes))
    agg = con.execute(f"""
      WITH w AS (SELECT * FROM read_parquet('{P.stats()}/year=*/*/*.parquet')
                 WHERE publication_year BETWEEN {years[0]} AND {years[1]}
                   AND NOT is_paratext AND NOT is_retracted),
           p AS (SELECT w.id, t.unnest AS tid, w.publication_year, w.cited_by_count
                 FROM w, unnest(w.topic_ids) AS t WHERE t.unnest IN ({tid_sql}))
      SELECT p.tid AS topic_id,
             count(DISTINCT p.id) AS n_works,
             sum(p.cited_by_count) AS n_cites,
             min(p.publication_year) AS y0, max(p.publication_year) AS y1
      FROM p GROUP BY 1 ORDER BY n_works DESC, n_cites DESC, p.tid LIMIT {eff_topk}
    """).df()
    agg = agg.merge(chosen.rename(columns={"id": "oid"})[["oid", "display_name", "score"]].assign(
        topic_id=chosen["id"].str.extract(r"(\d+)$").astype(int)), on="topic_id", how="left")
    # топ-работы направлений из T_digest (локально)
    dig = con.execute(f"""
      SELECT tid, id, publication_year, cited_by_count, title
      FROM read_parquet('{P.digest()}/**/*.parquet')
      WHERE tid IN ({tid_sql}) AND title IS NOT NULL
    """).df()
    by_dir: dict = {}
    for _, r in agg.iterrows():
        sub = dig[dig["tid"] == r["topic_id"]].sort_values("cited_by_count", ascending=False).head(5)
        by_dir[int(r["topic_id"])] = sub["id"].tolist(), sub["title"].tolist()
    return {"query": query_ru, "match": match, "directions": agg.to_dict("records"),
            "top_works": by_dir, "fanout": fanout_telem, "routing": routing_telem}


def _fanout_choose(topics, V, sim0, mega_mask, qv, model, cfg: dict):
    """И1, стратегия A (замороженный конфиг — журнал 24.09 16:05):
    1) первый проход: top-M НЕзамаскированных кандидатов по cos(оригинал);
    2) k-means(k, seed) по их векторам; подзапрос кластера = blob ближайшей к центроиду темы;
    3) RRF: избиратели = подзапросы (вклад за top-ktop) + оригинальный запрос (вклад за top-M),
       score = Σ 1/(c + rank);
    4) top-N (N=cfg['n_topics']) кандидатов по RRF → дальше обычная агрегация.
    Вырождение (M_eff < 2k) → fallback: обычный top-N, telem.fallback=true (§7.11: провал).
    Тестовые словари/ответы НЕ используются (А-1 отменён автором)."""
    import numpy as np
    import hashlib
    from sklearn.cluster import KMeans
    M = int(cfg.get("m", 240)); k = int(cfg.get("k", 12))
    KTOP = int(cfg.get("ktop", 25)); C = float(cfg.get("rrf_c", 60))
    seed = int(cfg.get("seed", 42)); N = int(cfg.get("n_topics", 60))
    source = cfg.get("source", "cluster")

    def tid_of(i):
        return int(re.search(r"(\d+)$", str(topics.iloc[i]["id"])).group(1))

    def top_unmasked(order, n):
        return [int(i) for i in order if not mega_mask[i]][:n]

    order0 = np.argsort(-sim0, kind="stable")
    pool = top_unmasked(order0, M)
    telem = {"mode": f"fanout-{source}",
             "config": {"m": M, "k": k, "ktop": KTOP, "rrf_c": C,
                        "seed": seed, "n_topics": N, "source": source},
             "fallback": False, "clusters": [], "subqueries": []}

    # --- стратегия C: expansion по замороженному лексикону (без k-means) ---
    if source == "lexicon":
        lex = json.loads(Path(cfg["lexicon_path"]).read_text())
        texts = list(lex["facets"])
        telem["lexicon"] = {"path": cfg["lexicon_path"],
                            "sha256": hashlib.sha256(Path(cfg["lexicon_path"]).read_bytes()).hexdigest(),
                            "n_facets": len(texts)}
        rrf = np.zeros(len(topics))
        rank0 = {t: r for r, t in enumerate(order0)}
        plain = top_unmasked(order0, N)          # избиратель «оригинал» = plain top-N
        for t in plain:
            rrf[t] += 1.0 / (C + rank0[t])
        qvs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        for j, qv_j in enumerate(qvs):
            sim_j = np.where(mega_mask, -1.0, V @ qv_j)
            hits = top_unmasked(np.argsort(-sim_j, kind="stable"), KTOP)
            for r, t in enumerate(hits):
                rrf[t] += 1.0 / (C + r)
            telem["subqueries"].append({
                "text": texts[j][:200],
                "top": [[tid_of(t), str(topics.iloc[t]["display_name"])[:70]] for t in hits[:5]]})
        cand = np.where(rrf > 0)[0]
        cand = cand[~mega_mask[cand]]
        order_c = cand[np.argsort(-rrf[cand], kind="stable")]
        chosen = topics.iloc[order_c][["id", "display_name"]].assign(score=rrf[order_c])
        return chosen, telem

    if len(pool) < 2 * k:
        telem["fallback"] = True
        telem["reason"] = f"M_effective={len(pool)} < 2k={2 * k}"
        top_idx = np.argsort(sim0, kind="stable")[::-1][:N]
        chosen = topics.iloc[top_idx][["id", "display_name"]].assign(score=sim0[top_idx])
        return chosen, telem

    Vpool = V[pool]
    km = KMeans(n_clusters=k, random_state=seed, n_init=10).fit(Vpool)
    labels = km.labels_
    reps, texts = [], []
    for j in range(k):
        members = [pool[i] for i in range(len(pool)) if labels[i] == j]
        if not members:
            continue
        rep = members[int(np.argmax(V[members] @ km.cluster_centers_[j]))]
        reps.append(rep)
        texts.append(f"{topics.iloc[rep]['display_name']}. {topics.iloc[rep]['descr']}")
        telem["clusters"].append({"rep_tid": tid_of(rep),
                                  "rep_name": str(topics.iloc[rep]["display_name"]),
                                  "size": len(members)})
    qvs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    rrf = np.zeros(len(topics))
    rank0 = {t: r for r, t in enumerate(order0)}
    for t in pool:                      # избиратель «оригинал»: вклад только за top-M
        rrf[t] += 1.0 / (C + rank0[t])
    for j, qv_j in enumerate(qvs):      # избиратели-подзапросы: вклад только за top-ktop
        sim_j = np.where(mega_mask, -1.0, V @ qv_j)
        hits = top_unmasked(np.argsort(-sim_j, kind="stable"), KTOP)
        for r, t in enumerate(hits):
            rrf[t] += 1.0 / (C + r)
        telem["subqueries"].append({
            "text": texts[j][:200],
            "top": [[tid_of(t), str(topics.iloc[t]["display_name"])[:70]] for t in hits[:5]]})
    cand = np.where(rrf > 0)[0]
    cand = cand[~mega_mask[cand]]
    order_c = cand[np.argsort(-rrf[cand], kind="stable")][:N]
    chosen = topics.iloc[order_c][["id", "display_name"]].assign(score=rrf[order_c])
    return chosen, telem

# ---------------------------------------------------------------- BM25 (собственная реализация)

import collections, math

def _tok(s: str) -> list[str]:
    return [t for t in re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", (s or "").lower()) if len(t) > 1]

def bm25_rank(docs: list, query: str, k1: float = 1.5, b: float = 0.75) -> list:
    """Okapi-BM25 ранжирование списка (id, title) по запросу (без зависимостей)."""
    if not docs:
        return []
    q = _tok(query)
    if not q:
        return list(docs)
    toks = [[_tok(t) for t in [d[1]]][0] for d in docs]
    N = len(docs)
    df = collections.Counter(t for t in toks for t in t)
    lens = [len(t) or 1 for t in toks]
    avgl = sum(lens) / len(lens)
    idf = {t: math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5)) for t in q if df[t]}
    scored = []
    for d, tl, l in zip(docs, toks, lens):
        tf = collections.Counter(tl)
        s = 0.0
        for t in q:
            if t not in idf:
                continue
            f = tf.get(t, 0)
            s += idf[t] * f * (k1 + 1) / (f + k1 * (1 - b + b * l / avgl))
        scored.append((s, d))
    scored.sort(key=lambda x: -x[0])
    return [d for _, d in scored if _ > 0] + [d for s, d in scored if s <= 0]

# ---------------------------------------------------------------- CLI-обёртка

def run(query: Optional[str] = None, actions: Optional[list] = None):
    pass  # реализуется в scripts/oa_run_*.py

if __name__ == "__main__":
    pass