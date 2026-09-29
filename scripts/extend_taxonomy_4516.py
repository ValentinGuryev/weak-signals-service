#!/usr/bin/env python3
"""NJ-0: фикс дырки таксономии 4482 → 4516 + перенормировка весов (одобрение автора 2026-09-24).

Инцидент (журнал 24.09): build_taxonomy брал ОДИН staging-файл small/topics.gz
(= updated_date 2026-06-26 → 4482 темы), а union снапшота = 4516 (6 дневных файлов;
works 2016-2026 ссылаются ровно на эти 4516 — замкнутость доказана). Потерянные 34 темы
(в т.ч. T14174 «AI and Decision Support Systems») имеют работы в базе, но невидимы ретривалу.

Что делает (всё атомарно, со старта — бэкап старых файлов):
 1) union дампа тем снапшота → SQL: старые 4482 строки ∪ 34 недостающих → topics_new.parquet;
 2) topic_ids.txt перегенерируется ИЗ нового parquet (формат: URL через \\n, БЕЗ trailing
    newline, порядок = порядок строк parquet — сверяется при верификации);
 3) base-вектора: blob ТОЧНО по шаблону build_topic_embeddings
    (f"{display_name}. {descr} {_kw(kw)}", _kw как в оригинале) для ВСЕХ 4516 → LaBSE →
    topic_vectors.npy (полная перезапись, не append — гарантирует согласованность);
 4) i2-вектора: метод И2-data ЗАМОРОЖЕН (журнал 19:25): топ-6 термов tf×ln(N/df) из названий
    СОБСТВЕННЫХ работ темы (T_digest, N=4516, df≤200, EN-stopwords, uni len≥4/bi len≥6,
    tie-break по алфавиту) → blob + " | " + термы → LaBSE → topic_vectors_i2.npy +
    topics_i2.parquet (id, blob, n_alias, aliases);
 5) верификация: 4516 строк; txt==parquet ids (порядок); формы (4516,768); NaN нет;
    косинус новых base-векторов С бэкапом старых по 20 случайным старым темам > 0.999
    (ловит расхождение шаблона blob — единственная тихая опасность пересборки).

Запуск (ночь, одиночно, ничего параллельного — урок ENOMEM):
  HF_HUB_OFFLINE=1 OMP_NUM_THREADS=2 .venv/bin/python scripts/extend_taxonomy_4516.py
Далее — ОДИНОЧНЫЙ регресс: HF_HUB_OFFLINE=1 .venv/bin/python scripts/qa_regress.py \
  --route --embed-variant i2   (ожидание: 12/12/12 + q4 prec 0/16 + q5 3/3)

--dry: только диагностика (union, 34 недостающих, dtype, наличие digest-алиасов), без записи.
"""
import argparse
import ast
import collections
import math
import os
import re
import shutil
import sys
import time
from pathlib import Path

import duckdb
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TAX = ROOT / "data/openalex_derived/taxonomy"
SNAP_TOPICS = Path("/mnt/e/openalex-snapshot/data/jsonl/topics")
DIGEST_GLOB = str(ROOT / "data/openalex_derived/T_digest/*.parquet")
BACKUP = TAX / "backup_4482_20260924"

# дословно как в build_taxonomy (src/oa_snapshot.py) — одни и те же колонки/алиасы
SEL = ("SELECT id, display_name, description, keywords, "
       "subfield.id AS subfield_id, field.id AS field_id, domain.id AS domain_id, "
       "works_count, cited_by_count FROM ")


def snap_src() -> tuple[str, list[Path]]:
    fs = sorted(SNAP_TOPICS.glob("**/*.gz"))
    if not fs:
        sys.exit("FAIL: нет файлов дампа тем в snap")
    files = ", ".join(f"'{f}'" for f in fs)
    return (f"read_json([{files}], format='newline_delimited', "
            f"union_by_name=true, ignore_errors=true)"), fs


def i2_aliases(tf: dict, df: collections.Counter, n_topics: int) -> dict:
    """Замороженный метод И2-data (журнал 2026-09-24 19:25) — без изменений."""
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    out = {}
    for tid, c in tf.items():
        sc = [(v * math.log(n_topics / df[t]), t) for t, v in c.items() if df[t] <= 200]
        sc.sort(key=lambda x: (-x[0], x[1]))
        out[tid] = [t for _, t in sc[:6]]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="диагностика без записи")
    args = ap.parse_args()

    con = duckdb.connect()
    con.execute("SET threads=2; SET memory_limit='2GB'")
    old = con.execute(f"SELECT * FROM read_parquet('{TAX}/topics.parquet')").df()
    src, fs = snap_src()
    snap = con.execute(SEL + src).df()
    miss = snap[~snap["id"].isin(set(old["id"]))].sort_values("id")
    print(f"old={len(old)} snapshot_union={len(snap)} missing={len(miss)}", flush=True)
    if len(miss) == 0:
        print("уже 4516? проверь topics.parquet вручную — выхожу")
        return 1
    if len(miss) != 34:
        sys.exit(f"FAIL: ожидал 34 недостающих, найдено {len(miss)} — разобраться вручную")
    print("missing ids:", ", ".join(i.rsplit("/", 1)[-1] for i in miss["id"]), flush=True)
    print("dtypes ok:", dict(old.dtypes) == dict(miss.reindex(columns=old.columns).dtypes),
          "| keywords sample:", repr(miss["keywords"].iloc[0])[:80], flush=True)

    # digest-алиасы: есть ли работы 34 тем в digest (нет → алиасы пустые, это норм)
    tids_new = [int(re.search(r"(\d+)$", i).group(1)) for i in miss["id"]]
    dig_tids = set(r[0] for r in con.execute(
        f"SELECT DISTINCT tid FROM read_parquet('{DIGEST_GLOB}')").fetchall())
    in_dig = sum(1 for t in tids_new if t in dig_tids)
    print(f"digest: {in_dig}/{len(tids_new)} новых тем имеют работы (нет → алиасы пустые)",
          flush=True)

    if args.dry:
        print("DRY OK — ничего не записано")
        return 0

    # ---- 1. бэкап ----
    BACKUP.mkdir(exist_ok=True)
    for f in ("topics.parquet", "topic_ids.txt", "topic_vectors.npy",
              "topic_vectors_i2.npy", "topics_i2.parquet"):
        if (TAX / f).exists() and not (BACKUP / f).exists():
            shutil.copy2(TAX / f, BACKUP / f)
    print(f"бэкап: {BACKUP}", flush=True)

    # ---- 2. topics.parquet 4516 (SQL: старые строки ∪ 34 недостающих) ----
    con.register("miss_df", miss.reindex(columns=old.columns))
    con.execute("CREATE OR REPLACE TEMP TABLE miss AS SELECT * FROM miss_df")
    con.execute("DROP VIEW IF EXISTS miss_df")  # register() создаёт VIEW, не TABLE (падение 24.09 23:38, фикс той же ночью)
    tmp = TAX / "topics_new.parquet"
    con.execute(f"""
      COPY (
        SELECT * FROM read_parquet('{TAX}/topics.parquet')
        UNION ALL BY NAME
        SELECT * FROM miss
        ORDER BY id
      ) TO '{tmp}' (FORMAT PARQUET, COMPRESSION ZSTD)""")
    os.replace(tmp, TAX / "topics.parquet")
    final = con.execute(f"SELECT * FROM read_parquet('{TAX}/topics.parquet')").df()
    assert len(final) == 4516, len(final)
    print(f"topics.parquet = {len(final)} строк", flush=True)

    # ---- 3. base blob (ТОЧНЫЙ шаблон build_topic_embeddings) + энкод ----
    def _kw(v):
        if v is None:
            return ""
        if isinstance(v, str):
            return " ".join(ast.literal_eval(v))
        return " ".join(v)

    base_texts = [f"{r.display_name}. {r.description if r.description else ''} {_kw(r.keywords)}"
                  for r in final.itertuples()]
    import sys as _s
    _s.path.insert(0, str(ROOT / "src"))
    import oa_snapshot as oa  # noqa: E402
    model = oa._get_embedder()
    print("энкод base 4516...", flush=True)
    vec_base = model.encode(base_texts, batch_size=32, normalize_embeddings=True,
                            show_progress_bar=False).astype("float32")
    assert vec_base.shape == (4516, 768), vec_base.shape
    np.save(TAX / "topic_vectors.npy.tmp.npy", vec_base)
    os.replace(TAX / "topic_vectors.npy.tmp.npy", TAX / "topic_vectors.npy")
    (TAX / "topic_ids.txt").write_text("\n".join(final["id"]))
    print("base npy + txt перезаписаны", flush=True)

    # ---- 4. i2: алиасы из СОБСТВЕННЫХ работ (замороженный метод) ----
    titles = con.execute(
        f"SELECT tid, title FROM read_parquet('{DIGEST_GLOB}') WHERE title IS NOT NULL").df()
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    def toks(s):
        out = set()
        ws = [w for w in re.findall(r"[a-z0-9]+", s.lower())
              if len(w) >= 4 and w not in ENGLISH_STOP_WORDS]
        out.update(ws)
        for a, b in zip(ws, ws[1:]):
            bg = a + " " + b
            if len(bg) >= 6:
                out.add(bg)
        return out
    tf, dfc = {}, collections.Counter()
    for tid, grp in titles.groupby("tid"):
        cnt = collections.Counter()
        for t in grp["title"].dropna():
            cnt.update(toks(t))
        tf[int(tid)] = cnt
    for c in tf.values():
        for t in c:
            dfc[t] += 1
    aliases = i2_aliases(tf, dfc, n_topics=4516)
    i2_texts, n_al = [], []
    n_with = 0
    for r in final.itertuples():
        tid = int(re.search(r"(\d+)$", r.id).group(1))
        al = aliases.get(tid, [])
        i2_texts.append(base_texts[len(i2_texts)] + (" | " + " ".join(al) if al else ""))
        n_al.append(len(al))
        n_with += bool(al)
    print(f"i2: {n_with}/4516 тем с алиасами", flush=True)
    print("энкод i2 4516...", flush=True)
    vec_i2 = model.encode(i2_texts, batch_size=32, normalize_embeddings=True,
                          show_progress_bar=False).astype("float32")
    assert vec_i2.shape == (4516, 768), vec_i2.shape
    np.save(TAX / "topic_vectors_i2.npy.tmp.npy", vec_i2)
    os.replace(TAX / "topic_vectors_i2.npy.tmp.npy", TAX / "topic_vectors_i2.npy")
    con.register("i2_df", __import__("pandas").DataFrame(
        {"id": final["id"], "blob": i2_texts, "n_alias": n_al}))
    con.execute(f"COPY (SELECT * FROM i2_df) TO '{TAX}/topics_i2.parquet' "
                f"(FORMAT PARQUET, COMPRESSION ZSTD, OVERWRITE_OR_IGNORE)")
    con.execute("DROP VIEW IF EXISTS i2_df")  # register() = VIEW, не TABLE (тот же фикс, что miss_df)
    print("i2 npy + topics_i2.parquet записаны", flush=True)

    # ---- 5. верификация ----
    txt = (TAX / "topic_ids.txt").read_text().split("\n")
    assert txt == list(final["id"]), "порядок txt != parquet"
    vb = np.load(TAX / "topic_vectors.npy")
    vi = np.load(TAX / "topic_vectors_i2.npy")
    assert vb.shape == vi.shape == (4516, 768)
    assert not np.isnan(vb).any() and not np.isnan(vi).any()
    old_v = np.load(BACKUP / "topic_vectors.npy")
    old_ids = (BACKUP / "topic_ids.txt").read_text().split("\n")
    pos = {v: i for i, v in enumerate(txt)}
    rng = np.random.default_rng(42)
    sample = rng.choice(len(old_ids), size=20, replace=False)
    cos = [float(vb[pos[old_ids[i]]] @ old_v[i]) for i in sample]
    print(f"косинус new-vs-old base (20 случайных старых): min={min(cos):.6f} "
          f"mean={float(np.mean(cos)):.6f}", flush=True)
    assert min(cos) > 0.999, f"blob-шаблон разошёлся! min cos={min(cos)} — ОТКАТ из backup"
    print(f"OK 4516. Следующий шаг (одиночно!): HF_HUB_OFFLINE=1 .venv/bin/python "
          f"scripts/qa_regress.py --route --embed-variant i2", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
