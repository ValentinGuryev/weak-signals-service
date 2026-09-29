#!/usr/bin/env python3
"""Запуск батч-ингеста снапшота OpenAlex (конвейер: копирование E:→C: параллельно редукции).

Примеры:
  # тест (один файл, всё локально):
  oa_run_ingest.py --files /tmp/oa_loc/part_0060.gz --local /tmp/oa_loc/derived \
      --staging /tmp/oa_loc/staging --e /tmp/oa_loc/derived_e \
      --small /mnt/c/oa_tmp/small --post
  # реальный прогон (план из манифеста на E:, батчи ~3 ГБ):
  oa_run_ingest.py --manifest /mnt/ee/openalex-snapshot/data/jsonl/manifest.json \
      --works /mnt/ee/openalex-snapshot/data/jsonl/works \
      --local /home/user/projects/Hackathon/data/openalex_derived \
      --staging /mnt/c/oa_tmp --e /mnt/ee/openalex_derived \
      --small /mnt/c/oa_tmp/small   [--limit 5] [--post]
"""
import argparse, glob, json, logging, shutil, sys, threading, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import oa_snapshot as oa

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")


def _stale_mount(path: Path) -> bool:
    """E:/C: в таблице маунтов есть, но доступ не работает (WSL после переподключения USB).
    Возвращает True, если путь выглядит как Windows-drive и не существует."""
    s = str(path)
    return (s.startswith(("/mnt/e", "/mnt/c", "/mnt/d", "/mnt/ee"))
            and not path.exists())


def copy_worker(in_q, out_q, P, works_root):
    """Фон: стадирует батчи (нативные копии E:→C:) → out_q [(batch, staged_files)]. 1 вперёд."""
    while True:
        b = in_q.get()
        if b is None:
            out_q.put(None); return
        files = ([Path(f) if not f.startswith("updated_date") else works_root / f for f in b.files]
                 if works_root else [Path(f) for f in b.files])
        # стадирование нужно по ПРЕФИКСУ пути (E:), не по exists():
        # exists() на протухшем маунте == False, и батч уйдёт в "local" с битыми путями
        need_stage = bool(files) and str(files[0]).startswith(("/mnt/e/", "/mnt/ee/"))
        try:
            if need_stage:
                if _stale_mount(files[0]):
                    out_q.put((b, None, f"copy error: E: не смонтирован ({files[0]})"))
                    continue
                dst = P.staging / f"b{b.idx}"
                # свежий слот: осколки убитого прогона (kill/resume) НЕ переживают — win_copy_to_staging
                # пропускает существующие файлы (>1000 Б), и битый gz дошёл бы до reduce (драйв 2026-09-21)
                shutil.rmtree(dst, ignore_errors=True)
                dst.mkdir(parents=True, exist_ok=True)
                oa.win_copy_to_staging(files, dst)
                out_q.put((b, [dst / f.name for f in files], "staged"))
            else:
                out_q.put((b, files, "local"))
        except Exception as ex:  # noqa: BLE001
            out_q.put((b, None, f"copy error: {ex}"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--works")
    ap.add_argument("--manifest")
    ap.add_argument("--files", nargs="*")
    ap.add_argument("--local", required=True)
    ap.add_argument("--e", required=True)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--small")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--skip", type=int, default=0, help="пропустить первые N батчей плана (для целевого теста)")
    ap.add_argument("--batch-gb", type=float, default=3.0)
    ap.add_argument("--threads", type=int, default=6, help="dirty перезапрос: для пост-пассов можно поднимать (напр. 12)")
    ap.add_argument("--mem", type=str, default="4GB", help="лимит памяти DuckDB: для крупных батчей/пост-пассов поднимать (напр. 6GB)")
    ap.add_argument("--post", action="store_true")
    ap.add_argument("--post-only", action="store_true", help="только пост-пассы (без батчей)")
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    P = oa.Paths(local=Path(args.local), e=Path(args.e), staging=Path(args.staging))
    for d in (P.local, P.e):
        d.mkdir(parents=True, exist_ok=True)

    import duckdb
    con = duckdb.connect()
    con.execute(f"SET threads={args.threads}; SET memory_limit='{args.mem}'")
    # threads=6 (вместо 12): пик декомпрессии ниже — OOM на 3-файловых батчах (драйв 2026-09-21)
    # --mem: крупные файлы (gz ~1.1 ГБ → ~10 ГБ JSON) бьют лимит 4 ГБ → ночной OOM 2026-09-22,
    # поднято через --mem 6GB (машина свободна: ~5.9 ГБ available)
    try:
        if args.small:
            # NJ-0 фикс: taxonomy из union ВСЕХ дневных файлов снапшота (4516 тем),
            # а не из одного staging-файла (потерял 34 темы)
            oa.build_taxonomy(con, P, Path(args.small),
                              snapshot_jsonl=Path(args.manifest).parent
                              if getattr(args, "manifest", None) else None)
            logging.info("taxonomy OK")

        if args.files:
            batches, total = [oa.Batch(idx=0, files=list(args.files))], 1
        else:
            assert args.manifest and args.works
            batches = oa.make_plan(Path(args.manifest), target_gb=args.batch_gb, works_root=Path(args.works))
            if args.skip:
                batches = batches[args.skip:]
            total = len(batches)
            logging.info(f"План: {total} батчей, {sum(b.n_records/1e6 for b in batches):.0f}M записей, "
                         f"{sum(b.n_bytes/1e9 for b in batches):.0f} ГБ gz")

        state = oa.load_state(P)
        if args.resume and state.get("batches"):
            # ⚠️ resume сверяем по НАБОРАМ ФАЙЛОВ, а не по idx: план (make_plan) строится
            # заново и зависит от того, какие файлы сейчас лежат на E: (докачка из S3
            # добавляет 261 файлов → батчи сдвигаются → idx из старого state больше не
            # соответствует тем же файлам и молча пропустил бы НЕ обработанные батчи).
            done_files = {frozenset(b["files"]): b["idx"] for b in state["batches"] if b["status"] == "done"}
            kept, skipped = [], 0
            for b in batches:
                if frozenset(b.files) in done_files:
                    skipped += 1
                else:
                    kept.append(b)
            batches = kept
            logging.info(f"Resume: уже готово {skipped}/{total} батчей, осталось {len(batches)}")
        else:
            state["batches"] = []

        works_root = Path(args.works) if args.works else None
        in_q = __import__("queue").Queue()
        out_q = __import__("queue").Queue(maxsize=1)
        cw = threading.Thread(target=copy_worker, args=(in_q, out_q, P, works_root), daemon=True)
        cw.start()

        if args.post_only:
            import os as _os
            only_dedup = _os.environ.get("OA_DEDUP_ONLY") == "1"    # годовой режим: только dedup
            skip_dedup = _os.environ.get("OA_SKIP_DEDUP") == "1"    # финал: только topic_index+digest
            if only_dedup and skip_dedup:
                raise SystemExit("OA_DEDUP_ONLY и OA_SKIP_DEDUP одновременно нельзя")
            mode = "dedup" if only_dedup else ("topic_index+digest" if skip_dedup else "dedup + topic_index + digest")
            logging.info(f"Режим --post-only: пост-пассы ({mode})...")
            if not skip_dedup:
                oa.build_dedup(con, P)
            if not only_dedup:
                oa.build_topic_index(con, P)
                oa.build_digest_final(con, P)
            logging.info("Пост-пассы OK")
            return

        t0 = time.time(); times = []
        limit = len(batches) if args.limit is None else min(args.limit, len(batches))
        if limit:
            in_q.put(batches[0])  # seed: копия первого батча
        for i in range(limit):
            b2, src_files, how = out_q.get()
            if b2.idx != batches[i].idx or src_files is None:
                raise RuntimeError(f"батч {batches[i].idx}: {how}")
            if i + 1 < limit:
                in_q.put(batches[i + 1])  # копия следующего идёт ПАРАЛЛЕЛЬНО редукции текущего
            tb = time.time()
            oa.reduce_batch(con, src_files, P, b2.idx)
            times.append(time.time() - tb)
            eta = (limit - i - 1) * (sum(times) / len(times)) / 60
            # чекпоинт
            state["batches"] = [x for x in state["batches"] if x["idx"] != b2.idx] + \
                               [{"idx": b2.idx, "files": b2.files, "status": "done"}]
            oa.save_state(P, state)
            # стадинг слот
            slot = P.staging / f"b{b2.idx}"
            if slot.exists():
                shutil.rmtree(slot, ignore_errors=True)
            logging.info(f"[{i+1}/{limit}] батч {b2.idx} {how} {b2.n_records/1e6:.1f}M rec "
                         f"({sum(times)/len(times):.0f}s/батч, ETA ~{eta:.0f} мин) {oa.progress(P, total)}")
        in_q.put(None)

        logging.info(f"Батчи готовы: {len(times)} шт за {time.time()-t0:.0f} с "
                     f"({sum(times)/len(times):.0f} с/батч средн.)")

        if args.post:
            logging.info("Пост-пассы: dedup + topic_index + digest...")
            oa.build_dedup(con, P)
            oa.build_topic_index(con, P)
            oa.build_digest_final(con, P)
            logging.info("Пост-пассы OK")
    finally:
        con.close()


if __name__ == "__main__":
    main()