#!/usr/bin/env python3
"""Этап Б ночи 28→29.09: индекс «терм → документы-источники» (Aho-Corasick).

Вход : data/openalex_derived/tech_pool_v1.parquet (широкий пул)
Выход: data/openalex_derived/tech_docs_v1.parquet (по 1 строке на терм:
       hits_n + топ-3 документа по году, abstract 1200 симв. — только у лучшего
       = якорь для карточки) + results/runtime/tech_docs_v1_report.md
Промежуточные части: /mnt/e/openalex_derived/tmp_techdocs/ (E:, удаляются после merge).

Правила (объявлены ДО прогона):
  * пул для индекса (pool_v2): first_year>=2018 И n_recent>=5 (канон emerging
    из termtech_filter) — из 1.36M широкого пула;
  * нормализация обеих сторон: lower, НЕ-буквы/цифры → пробел, схлопывания;
    совпадение только по границам слова;
  * источники: 9 доменных слайсов (E:) + sp_slice + slice_q1ai (где рождён sp-пул);
  * дедуп доков по (term, work_id); топ-3 по (year desc); hits_n — все попадания;
  * resume: готовые части не перечитываются (идемпотентно по имени файла).

Запуск:
  смоук: .venv/bin/python scripts/build_tech_docindex.py --domain quantum --procs 1
  ночь : .venv/bin/python scripts/build_tech_docindex.py --procs 2
"""
import argparse
import glob
import json
import multiprocessing as mp
import os
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
POOL = ROOT / "data/openalex_derived/tech_pool_v1.parquet"
OUT = ROOT / "data/openalex_derived/tech_docs_v1.parquet"
TMP = Path("/mnt/e/openalex_derived/tmp_techdocs")
REPORT = ROOT / "results/runtime/tech_docs_v1_report.md"
TOPK = 3
ABSTRACT_N = 1200
TITLE_N = 300

_NONWORD = re.compile(r"[^0-9a-zа-яё]+")

_A = None      # automaton (fork-shared)
_IDX = None    # term_norm -> idx
_PATLEN = None # длина паттерна в символах (границы слова)


def ntext(s: str) -> str:
    return _NONWORD.sub(" ", s.lower()).strip()


def _init(patterns: list[str], idx: dict[str, int]):
    global _A, _IDX, _PATLEN
    import ahocorasick
    a = ahocorasick.Automaton()
    for pat, i in patterns:
        a.add_word(pat, i)
    a.make_automaton()
    _A, _IDX = a, idx
    _PATLEN = np.zeros(len(idx), dtype=np.int32)
    for pat, i in patterns:
        _PATLEN[i] = len(pat)


def _process_file(path: str) -> tuple[str, int, int, int]:
    """→ (part_path, docs_scanned, matched_events, rows)."""
    domain = path.split("/slices/")[-1].split("/")[0] if "/slices/" in path \
        else Path(path).parent.name
    stem = re.sub(r"[^A-Za-z0-9_.=]+", "_", f"{domain}__{Path(path).stem}")
    part = TMP / f"{stem}.parquet"
    if part.exists() and part.stat().st_size > 0:
        try:
            pq.read_schema(part)      # валидация: усечённая part → пересоздаём
            return (str(part), 0, 0, -1)  # resume
        except Exception:
            part.unlink(missing_ok=True)  # битая часть отброшена, файл переигран
    best: dict[int, list] = {}   # idx -> [(year, wid, title, abstract|None)]
    seen: dict[int, set] = {}
    n_docs = n_hit_docs = 0
    pf = pq.ParquetFile(path)
    cols = [c for c in ("id", "publication_year", "sp_tids", "title", "abstract")
            if c in pf.schema_arrow.names]
    for batch in pf.iter_batches(batch_size=2000, columns=cols):
        recs = batch.to_pylist()
        for r in recs:
            n_docs += 1
            title = r.get("title") or ""
            ab = r.get("abstract") or ""
            if not title and not ab:
                continue
            text = ntext(title) + " " + ntext(ab)
            hits = set()
            for end, i in _A.iter(text):
                st = end + 1 - int(_PATLEN[i])
                if (st == 0 or text[st - 1] == " ") and (
                        end + 1 == len(text) or text[end + 1] == " "):
                    hits.add(i)
            if not hits:
                continue
            n_hit_docs += 1
            y = int(r.get("publication_year") or 0)
            wid = str(r.get("id") or "")
            t3 = title[:TITLE_N]
            a12 = ab[:ABSTRACT_N] if ab else None
            st = [int(x) for x in (r.get("sp_tids") or [])][:12]
            for i in hits:
                lst = best.setdefault(i, [])
                sids = seen.setdefault(i, set())
                if wid in sids:
                    continue
                sids.add(wid)
                if len(lst) < TOPK:
                    lst.append((y, wid, t3, a12, st))
                else:
                    mn = min(range(len(lst)), key=lambda k: lst[k][0])
                    if y > lst[mn][0]:
                        lst[mn] = (y, wid, t3, a12, st)
    # сериализация части
    rows = []
    for i, docs in best.items():
        docs = sorted(docs, key=lambda d: -d[0])
        # abstract храним у САМОГО СВЕЖЕГО дока, у которого он есть
        # (фикс смоука 23:30: rank0 без abstract → у терма не оставалось текста)
        a_idx = next((k for k, d in enumerate(docs) if d[3]), None)
        dd = [{"y": y, "id": wid, "t": t,
               "a": (a if k == a_idx else None), "s": st}
              for k, (y, wid, t, a, st) in enumerate(docs)]
        rows.append({"idx": i, "docs": json.dumps(dd, ensure_ascii=False)})
    # атомарная запись (рецензия P2-6): битая part.tmp после kill не пройдёт
    # проверку resume и не уронит финальный merge
    tmp = part.with_suffix(".parquet.tmp")
    pd.DataFrame(rows or [{"idx": -1, "docs": "[]"}]).to_parquet(tmp, index=False)
    os.replace(tmp, part)
    return (str(part), n_docs, n_hit_docs, len(rows))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default=None, help="смоук: один домен слайсов")
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--skip-sp", action="store_true",
                    help="не читать sp_slice/slice_q1ai (смоук)")
    args = ap.parse_args()

    t0 = time.time()
    TMP.mkdir(parents=True, exist_ok=True)
    # Чистка осиротевших .tmp — ОДИН раз ДО старта пула. В воркерах нельзя:
    # параллельный воркер удалял чужой рабочий tmp → FileNotFoundError на
    # os.replace (инцидент ночи 29.09 01:52, обвал Б на файле 21/121).
    for stale in TMP.glob("*.parquet.tmp"):
        stale.unlink(missing_ok=True)

    pool = pd.read_parquet(POOL)
    v2 = pool[(pool["first_year"] >= 2018) & (pool["n_recent_sum"] >= 5)].copy()
    v2["_p"] = v2["_n"].map(ntext)
    v2 = v2[v2["_p"].str.split().str.len().between(2, 6)]
    v2 = v2.drop_duplicates("_p")
    print(f"pool_v1={len(pool)} → pool_v2={len(v2)} (fy≥2018 & n_recent≥5)", flush=True)
    idx = {p: i for i, p in enumerate(v2["_p"])}
    term_of = dict(enumerate(v2["term"]))
    patterns = [(p, i) for p, i in idx.items()]

    # входы
    files = []
    if args.domain:
        files = sorted(glob.glob(
            f"/mnt/e/openalex_derived/slices/{args.domain}/year=*.parquet"))
    else:
        files = sorted(glob.glob("/mnt/e/openalex_derived/slices/*/year=*.parquet"))
        if not args.skip_sp:
            for base in (ROOT / "data/openalex_derived/sp_slice",
                         ROOT / "data/openalex_derived/slice_q1ai"):
                files += sorted(glob.glob(str(base / "**" / "year=*.parquet"),
                                          recursive=True)) or \
                    sorted(glob.glob(str(base / "*.parquet")))
    print(f"файлов входа: {len(files)}", flush=True)

    print("сборка AC-автомата…", flush=True)
    t_ac = time.time()
    with mp.Pool(args.procs, initializer=_init, initargs=(patterns, idx)) as pool_:
        # ОСВОБОЖДЕНИЕ ПАМЯТИ (рецензия S1: merge-пик 5.62 ГБ → цель ≤4 ГБ):
        # pool/v2/patterns/idx родителю больше не нужны (воркеры получили копии
        # при fork) — держать их через scan+merge нельзя.
        n_pool1, n_pool2 = len(pool), len(v2)
        del pool, v2, patterns, idx
        import gc
        gc.collect()
        parts, total_docs, total_rows = [], 0, 0
        for k, res in enumerate(pool_.imap(_process_file, files, chunksize=1), 1):
            part, nd, _nh, rows = res
            parts.append(part)
            total_docs += nd
            if rows >= 0:
                total_rows += rows
            print(f"[{k}/{len(files)}] {Path(part).name} docs={nd} rows={rows} "
                  f"({time.time()-t_ac:.0f}s)", flush=True)

    # финальный merge частей: топ-3 по году на терм, abstract — только лучший.
    # Память (S1-фикс): dict → кортежи (y,id,t,a,s), явный del+gc на каждой части,
    # выход пишется потоково ParquetWriter'ом (без накопления out_rows/out_df).
    print("merge частей…", flush=True)
    import gc
    import pyarrow as pa
    import pyarrow.parquet as pq2
    best: dict[int, list] = {}
    for pi, p in enumerate(parts, 1):
        d = pd.read_parquet(p, columns=["idx", "docs"])
        for r in d.itertuples(index=False):
            if r.idx < 0:
                continue
            for doc in json.loads(r.docs):
                t = (doc["y"], doc["id"], doc.get("t", ""),
                     doc.get("a"), doc.get("s") or [])  # кортеж вместо dict
                lst = best.setdefault(r.idx, [])
                if len(lst) < TOPK:
                    lst.append(t)
                else:
                    mn = min(range(len(lst)), key=lambda k: lst[k][0])
                    if t[0] > lst[mn][0]:
                        lst[mn] = t
        del d
        if pi % 5 == 0:
            gc.collect()
            print(f"  merge: {pi}/{len(parts)} частей, термов={len(best):,}",
                  flush=True)
    gc.collect()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    sch = pa.schema([("term", pa.string()), ("docs_n", pa.int32()),
                     ("docs_json", pa.string())])
    writer = pq2.ParquetWriter(str(args.out), sch)
    batch: list[dict] = []
    for i, docs in best.items():
        docs = sorted(docs, key=lambda d: -d[0])
        dd = [{"y": y, "id": wid, "t": t, "a": a, "s": s}
              for (y, wid, t, a, s) in docs]
        batch.append({"term": term_of[i], "docs_n": len(dd),
                      "docs_json": json.dumps(dd, ensure_ascii=False)})
        if len(batch) >= 50000:
            writer.write_table(pa.Table.from_pylist(batch, schema=sch))
            batch = []
    if batch:
        writer.write_table(pa.Table.from_pylist(batch, schema=sch))
    writer.close()
    matched = len(best)
    del best
    gc.collect()

    cov = matched / max(n_pool2, 1)
    # чистка промежуточных частей
    for p in parts:
        try:
            os.remove(p)
        except OSError:
            pass
    try:
        TMP.rmdir()
    except OSError:
        pass

    lines = [
        f"# tech_docs_v1 — {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"- пул_v1 (термов в индексе): {n_pool1:,}; пул_v2 = {n_pool2:,}",
        f"- файлов просканировано: {len(files)}; документов: {total_docs:,}",
        f"- термов с ≥1 документом: {matched:,} ({cov:.1%})",
        f"- выход: `{args.out}` ({Path(args.out).stat().st_size // 1024 // 1024} МБ)",
        f"- время: {time.time()-t0:.0f} с; procs={args.procs}; domain={args.domain}",
    ]
    Path(REPORT).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
