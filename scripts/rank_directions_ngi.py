#!/usr/bin/env python3
"""Этап-1 ранжирование подтем выдачи по ядру novelty × growth × impact.

Берёт JSON прогона query_directions (results/qa_*/...json) и ранжирует ВСЕ кандидат-темы
скором screen = novelty_n × growth_n × impact_n — точно по канону методологии:
  growth_n = g/(g+1),  g = N(Y-2..Y)/N(Y-4..Y-3)   (суммы работ, ESCORE_RECALC §3,
             GLOSSARY §2.3а; рождение в окне: N_раннее=0, N_позднее>0 → growth_n=1.0;
             оба 0 → тема вне окна, не ранжируется)
  novelty_n = 1 − sigmoid((age−15)/5),  age = Y − birth
             (GLOSSARY §2.4; birth — правило «перерыв ≥2 лет сбрасывает», решение
             автора 2026-09-14: идём назад от последнего года с работами, разрыв
             ровно в 1 год допустим)
  impact_n = 1 − exp(−impact/40)   (MODEL_SYNTHESIS §3a, τ=40)
             impact = max накопленных входящих цитат одной работы темы
             (аналог S3_incoming_max «ядра»), считается по counts_by_year ровно ДО конца
             окна Y (без look-ahead)

ОКНО Y (по умолчанию 2025): последний ПОЛНЫЙ год. Снапшот 2026 неполон (до 2026-06-26,
R-NEW-4) → год Y+1 в расчёты не входит (иначе growth для всех занижен ~вдвое).

Данные:
  * локально: T_stats year=*/*/*.parquet (работы 2016..Y), фильтр type IN (белый список
    из журнала 24.09 09:30 — БЕЗ dataset/other), NOT is_paratext, NOT is_retracted;
  * birth: OpenAlex API group_by=publication_year по теме (полная история с 1800-х;
    левый цензинг T_stats 2016+ съедал бы novelty). Кэш — results/ngi_birth_cache.json
    (повторные запуски без запросов). Запросы логируются в results/runtime/api_budget.md.

Выход: <prefix>.md (топ-N таблица), <prefix>.csv, <prefix>_full.json (все кандидаты).

Использование:
  .venv/bin/python scripts/rank_directions_ngi.py --run results/qa_i2/q1_ru_canonical.json \
      [--window 2025] [--top 50] [--prefix results/qa_i2/q1_ru_canonical_ngi]
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# regex «мусора» — единый источник (перенесён из sim_gate 27.09, текст БЕЗ ИЗМЕНЕНИЙ;
# sim_gate импортирует отсюда). A1b (25.09, заморожен): расширен до всех
# education/learning/covid/health-форм; «learning» исключает ML-составные
# (machine/deep/federated… learning) — иначе ложный мусор в темах про ИИ.
# Порогов/подгонки нет.
GARBAGE_RE = re.compile(
    r"educat|covid|pandemic|social impacts|"
    r"(?<!machine )(?<!deep )(?<!federated )(?<!reinforcement )"
    r"(?<!supervised )(?<!unsupervised )(?<!representation )"
    r"(?<!transfer )(?<!continual )(?<!contrastive )(?<!adversarial )"
    r"(?<!multimodal )(?<!multi-modal )(?<!dialog )(?<!speech )"
    r"(?<!meta )(?<!self )(?<!supervised )learning|"
    r"\bschools?\b|\bstudents?\b|\bteachers?\b|\bteaching\b|"
    r"\bclassrooms?\b|\bcurriculums?\b|\bpedagog|\bmoocs?\b|"
    r"\buniversit(y|ies)\b|\bhealth\b|sustainab|\bwell-being\b|"
    r"\bkill[ -]?defense\b|\bquiz\b|\bexam",
    re.I)
LOCAL = ROOT / "data/openalex_derived"
BIRTH_CACHE = ROOT / "results/ngi_birth_cache.json"
API_BUDGET = ROOT / "results/runtime/api_budget.md"
# A0b (25.09): кэш NJ-2 — series+impact по ВСЕМ темам таксономии, пишет --prefill
CACHE_META = ROOT / "data/openalex_derived/taxonomy/topic_ngi_cache_meta.json"
CACHE_SER = ROOT / "data/openalex_derived/taxonomy/topic_ngi_cache.parquet"
CACHE_IMP = ROOT / "data/openalex_derived/taxonomy/topic_ngi_cache_impact.parquet"


def _taxonomy_tids() -> list[int]:
    import pyarrow.parquet as pq
    raw = pq.read_table(ROOT / "data/openalex_derived/taxonomy/topics.parquet",
                        columns=["id"]).column("id").to_pylist()
    return sorted(int(str(t).rstrip("/").split("T")[-1]) for t in raw)


def _tids_sha1(tids: list[int]) -> str:
    return hashlib.sha1(",".join(map(str, sorted(tids))).encode()).hexdigest()


def _cache_stats(tids: list[int], win: int):
    """A0b (25.09): чтение кэша NJ-2 вместо 40+ мин DuckDB-прохода T_stats.
    Валидность: окно == кэшному И sha1 таксономии совпадает И все запрошенные
    темы ⊆ таксономия. Темы без строк в кэше = пустая серия (как в DuckDB-пути:
    prefill проходил ВСЕ темы таксономии). None → кэша нет, идём в DuckDB.
    """
    if not (CACHE_META.exists() and CACHE_SER.exists() and CACHE_IMP.exists()):
        return None
    try:
        meta = json.loads(CACHE_META.read_text())
        if int(meta.get("window", -1)) != int(win):
            return None
        tax = _taxonomy_tids()
        if meta.get("tids_sha1") != _tids_sha1(tax):
            return None
        want = {int(t) for t in tids}
        if not want.issubset(set(tax)):
            return None
        import pyarrow.parquet as pq
        ts = pq.read_table(CACHE_SER, columns=["tid", "year", "n"])
        series: dict = {}
        for tid, y, n in zip(ts.column(0).to_pylist(), ts.column(1).to_pylist(),
                             ts.column(2).to_pylist()):
            tid = int(tid)
            if tid in want and 2016 <= int(y) <= win:
                series.setdefault(tid, {})[int(y)] = int(n)
        ti = pq.read_table(CACHE_IMP, columns=["tid", "impact"])
        impact = {int(a): int(b) for a, b in zip(ti.column(0).to_pylist(),
                                                 ti.column(1).to_pylist())
                  if int(a) in want}
        return series, impact
    except Exception as e:  # любой сбой кэша → честный fallback на DuckDB
        print(f"кэш NGI не прочитан ({e}); fallback → DuckDB", flush=True)
        return None

# белый список типов (журнал 24.09 09:30: без dataset/other — иначе ложный рост ×10-50)
TYPE_OK = ("article", "review", "preprint", "book-chapter", "dissertation", "book",
           "letter", "editorial", "erratum", "standard", "report")


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def birth_from_histogram(hist: dict, cap_year: int) -> int | None:
    """Правило «затишье сбрасывает birth» (автор 2026-09-14): назад от последнего года
    с работами (≤ cap_year); разрыв ≤1 года допустим (разница лет ≤2), ≥2 пропущенных
    лет подряд (разница ≥3) — стоп, birth = первый год текущего непрерывного отрезка."""
    # ключи из JSON-кэша — строки (инцидент 25.09: sim_gate упал через 1 ч на
    # str<=int); приводим к int — покрывает и in-memory (int) и JSON (str)
    years = sorted(int(y) for y in hist if int(y) <= cap_year and hist[y] > 0)
    if not years:
        return None
    seg = years[-1]
    for y in reversed(years[:-1]):
        if seg - y >= 3:
            break
        seg = y
    return seg


def fetch_births(tids: list[int], cache: dict, cap_year: int) -> tuple[dict, int]:
    """group_by=publication_year по каждой теме. Кэшируем. Возвращает {tid: birth}, n_req."""
    need = [t for t in tids if str(t) not in cache]
    n_req = 0
    # Опциональный SOCKS5-канал: OPENALEX_SOCKS=host:port; '' (по умолчанию) →
    # direct; затем локальный T_stats-fallback.
    socks_ep = os.environ.get("OPENALEX_SOCKS", "")
    if socks_ep:
        import socket as _socket
        import socks as _socks
        if not getattr(_socks, "_openalex_patched", False):
            _h, _p = socks_ep.rsplit(":", 1)
            _socks.set_default_proxy(_socks.SOCKS5, _h, int(_p), rdns=True)
            _socket.socket = _socks.socksocket
            _socks._openalex_patched = True
    # LOCAL-FIRST (addendum №9-INFRA, ДО прогона): снапшот T_stats закрывает
    # почти все QA-темы мгновенно; API-прокси — только для остатка (27.09).
    missing = [t for t in need if str(t) not in cache]
    if missing:
        print(f"  birth: локальный проход для {len(missing)} тем (T_stats)...", flush=True)
        import duckdb
        con = duckdb.connect()
        con.execute("SET memory_limit='3GB'; SET threads=2")
        con.execute("SET preserve_insertion_order=false")  # OOM-фикс 27.09: UNNEST на 2.3ГБ снапшота
        con.execute("SET temp_directory='/mnt/e/openalex_derived/tmp_duck'")
        tids_sql = ", ".join(map(str, missing))
        rows = con.execute(f"""
            SELECT t.unnest AS tid, w.publication_year AS yr, count(*) AS n
            FROM read_parquet('{LOCAL}/T_stats/year=*/*/*.parquet') w,
                 UNNEST(w.topic_ids) AS t
            WHERE w.publication_year BETWEEN 2016 AND {cap_year}
              AND t.unnest IN ({tids_sql})
            GROUP BY 1, 2""").fetchall()
        con.close()
        hist_map: dict = {}
        for tid, yr, n in rows:
            hist_map.setdefault(int(tid), {})[int(yr)] = int(n)
        for t in missing:
            if t in hist_map:
                cache[str(t)] = hist_map[t]
        if hist_map:
            BIRTH_CACHE.write_text(json.dumps(cache))
        print(f"  birth: локально закрыто {len(hist_map)}/{len(missing)}", flush=True)
    need = [t for t in need if str(t) not in cache]  # остаток → API-прокси
    for i, tid in enumerate(need, 1):
        url = (f"https://api.openalex.org/works?filter=topics.id:T{tid}"
               f"&group_by=publication_year&per-page=200&mailto=research@hackathon.local")
        hist = {}
        time.sleep(0.25)  # polite-pool pacing против HTTP 429 (27.09, инфра-фикс)
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "hackathon-research (mailto=research@hackathon.local)"})
                with urllib.request.urlopen(req, timeout=25) as r:
                    d = json.load(r)
                n_req += 1
                for g in d.get("group_by", []):
                    if re.fullmatch(r"\d{4}", str(g.get("key", ""))):
                        hist[int(g["key"])] = int(g.get("count", 0))
                break
            except Exception as e:  # noqa: BLE001
                if attempt == 2:
                    print(f"[warn] T{tid}: API не ответил ({e})", file=sys.stderr)
                    hist = {}
                else:
                    time.sleep(1.5 * (attempt + 1))
        # фикс 27.09: НЕ кэшируем провал (429 → hist={}) — иначе тема отравлена
        # навсегда и будет no_birth в каждом будущем прогоне
        if hist:
            cache[str(tid)] = hist
            print(f"  birth: {i}/{len(need)} запросов")
            BIRTH_CACHE.write_text(json.dumps(cache))
        time.sleep(0.06)  # polite rate ~12 req/s
    if need:
        BIRTH_CACHE.write_text(json.dumps(cache))
        with API_BUDGET.open("a") as f:
            f.write(f"\n- {time.strftime('%Y-%m-%d %H:%M')} | OpenAlex (group_by=publication_year) "
                    f"| {n_req} запросов | ранжирование N×G×I кандидатов QA-выдачи "
                    f"(scripts/rank_directions_ngi.py) | кэш: results/ngi_birth_cache.json")
    # (локальный проход теперь ВЫШЕ — local-first по addendum №9-INFRA 27.09)
    births = {t: birth_from_histogram(cache.get(str(t), {}), cap_year) for t in tids}
    return births, n_req


def local_stats(tids: list[int], win: int) -> tuple[dict, dict]:
    """T_stats 2016..Y: серия работ по годам + impact (max накопл. цитат работы ≤Y).
    A0b: если есть валидный кэш NJ-2 — читаем его (~секунды), иначе DuckDB."""
    cached = _cache_stats(tids, win)
    if cached is not None:
        return cached
    import duckdb
    con = duckdb.connect()
    # NGI_MEM/NGI_THREADS — оверрайды для офлайн-прогонов (по умолчанию как раньше);
    # урок 25.09: лимит 2ГБ < рабочего множества T_stats (2.3ГБ) → постоянный спилл
    # на 9p и ~1 ч на один local_stats вместо ~5-10 мин
    con.execute(f"SET threads={os.environ.get('NGI_THREADS', '2')}; "
                f"SET memory_limit='{os.environ.get('NGI_MEM', '2GB')}'")
    con.execute("SET preserve_insertion_order=false")
    # NGI_SPILL — чтобы параллельные офлайн-прогоны (sim_gate) не деррались
    # за одни temp-файлы DuckDB (инцидент 25.09 13:34: truncate conflict)
    spill = Path(os.environ.get("NGI_SPILL", "/mnt/e/openalex_derived/tmp_duck"))
    spill.mkdir(parents=True, exist_ok=True)
    con.execute(f"SET temp_directory='{spill}'")
    glob = f"{LOCAL}/T_stats/year=*/*/*.parquet"
    tids_sql = ", ".join(map(str, tids))
    types_sql = ", ".join(f"'{t}'" for t in TYPE_OK)
    q1 = f"""
      SELECT t.unnest AS tid, w.publication_year AS yr, count(*) AS n
      FROM read_parquet('{glob}') w, UNNEST(w.topic_ids) AS t
      WHERE w.publication_year BETWEEN 2016 AND {win}
        AND w.type IN ({types_sql}) AND NOT w.is_paratext AND NOT w.is_retracted
        AND t.unnest IN ({tids_sql})
      GROUP BY 1, 2"""
    series: dict = {}
    for row in con.execute(q1).fetchall():
        series.setdefault(int(row[0]), {})[int(row[1])] = int(row[2])
    # q2 (OOM-фикс 25.09, верифицирован бит-в-бит против старого варианта):
    # cum(work) НЕ зависит от темы → list-fold НА СТРОКЕ (без разворота JSON в
    # десятки млн строк и без агрегата GROUP BY tid,id, который не спилился и
    # убивал prefill attempts 1-3), затем UNNEST(topics) → GROUP BY tid → max
    # (хеш = O(число тем)). list_has_any — предфильтр работ по темам чанка.
    q2 = f"""
      SELECT t.unnest AS tid, max(w.cum) AS imp
      FROM (
        SELECT w.id, w.topic_ids,
               list_sum(list_transform(list_filter(
                 json_transform(w.counts_by_year,
                                '[{{"year":"INTEGER","cited_by_count":"INTEGER"}}]'),
                 e -> e.year <= {win}), e -> e.cited_by_count)) AS cum
        FROM read_parquet('{glob}') w
        WHERE w.publication_year BETWEEN 2016 AND {win}
          AND w.type IN ({types_sql}) AND NOT w.is_paratext AND NOT w.is_retracted
          AND w.cited_by_count > 0
          AND list_has_any(w.topic_ids, [{tids_sql}])
      ) w, UNNEST(w.topic_ids) AS t
      WHERE t.unnest IN ({tids_sql})
      GROUP BY 1"""
    print(f"  q1 (series): {len(series)} тем; q2 (impact) ...", flush=True)
    impact = {int(a): int(b) for a, b in con.execute(q2).fetchall()}
    con.close()
    return series, impact


_TOK_RE = re.compile(r"[a-zа-яё0-9]{2,}", re.I)
_REL_STOP = set("""выдай темы по в защите года году и о на для от с к как при что это
эти или же не нет да все очень более самый можно нужно через про между
a an the and or of to in for on with from by at as is are be been being this
that these those it its our your their can could may might will would should
must not no do does did study paper analysis research method methods using use
used data results result new two three one artificial intelligence models model
based""".split())


def _query_tokens(run: dict) -> list[str]:
    """Лексика запроса: исходный запрос + EN-фасеты фаноута (то, чем реально
    искала система). RU/EN различие сохраняем: токены просто складываются."""
    qs = [run.get("query", "")]
    for sq in (run.get("fanout") or {}).get("subqueries") or []:
        qs.append(sq.get("text", ""))
    out, seen = [], set()
    for q in qs:
        for t in _TOK_RE.findall(str(q)):
            t = t.lower()
            if t in _REL_STOP or t.isdigit() or t in seen:
                continue
            seen.add(t)
            out.append(t)
    return out


def add_relevance(run: dict, rows: list) -> None:
    """P1 (25.09): rel = доля IDF-массы лексики запроса, покрытая профилем темы
    (имя темы + названия её топ-работ). IDF — по профилям кандидатов запроса:
    частые в базе слова («ai», «model») несут малый вес. Порогов нет.
    """
    qt = _query_tokens(run)
    tw = run.get("top_works") or {}
    profs = []
    for r in rows:
        t = tw.get(str(r["topic_id"]))
        titles = t[1] if t and len(t) > 1 else []
        profs.append((r["name"] + " " + " ".join(map(str, titles))).lower())
    n = max(len(rows), 1)
    df = {t: sum(1 for p in profs if t in p) for t in qt}
    idf = {t: math.log((n + 1) / (df[t] + 1)) + 1.0 for t in qt}
    total = sum(idf.values()) or 1.0
    for r, p in zip(rows, profs):
        hit = [t for t in qt if t in p]
        r["rel"] = sum(idf[t] for t in hit) / total
        r["n_hit"] = len(hit)
    return qt, idf, total


def _load_children() -> dict:
    """child-темы (V1/V4; сборка scripts/build_children_store.py): tid → [profile]."""
    import pandas as pd
    p = ROOT / "webapp/data/children/children.parquet"
    if not p.exists():
        return {}
    df = pd.read_parquet(p, columns=["parent_tid", "profile"])
    d: dict = {}
    for tid, prof in zip(df["parent_tid"], df["profile"]):
        d.setdefault(int(tid), []).append(str(prof))
    return d


def compute_child_rel(rows, qt, idf, total) -> None:
    """child_rel = макс по детям IDF-покрытие qt профилем ребёнка (те же qt/idf,
    что parent-rel; канон = прод-путь, addendum №3 к протоколу 27.09)."""
    children = _load_children()
    n_par = sum(1 for r in rows if r["topic_id"] in children)
    for r in rows:
        best = 0.0
        for prof in children.get(r["topic_id"], []):
            v = sum(idf[t] for t in qt if t in prof) / total
            if v > best:
                best = v
        r["child_rel"] = best
    vals = [r["child_rel"] for r in rows]
    print(f"child_rel: parents-с-детьми {n_par}/{len(rows)}, "
          f"max={max(vals):.4f}, >0: {sum(1 for v in vals if v > 0)}", flush=True)


def prefill(args) -> int:
    """NJ-2: series (tid×year×n) + impact по ВСЕМ темам таксономии.
    Выход: taxonomy/topic_ngi_cache.parquet + topic_ngi_cache_impact.parquet.
    То, что ранжировщик считает под каждый запрос, — теперь один раз локально
    (спилл E:/tmp_duck; ~20-40 мин; mem задаётся NGI_MEM, по умолчанию 2GB).
    """
    import pyarrow as pa
    import pyarrow.parquet as pq
    topics_p = ROOT / "data/openalex_derived/taxonomy/topics.parquet"
    raw = pq.read_table(topics_p, columns=["id"]).column("id").to_pylist()
    tids = [int(str(t).rstrip("/").split("T")[-1]) for t in raw]
    print(f"prefill: {len(tids)} тем, окно {args.window}, чанк={args.batch} ...", flush=True)
    t0 = time.time()
    # OOM-фикс 25.09 18:47 (attempt 1, 4516 тем одним проходом → 3.7/3.7GiB):
    # чанки дисджоинтны по tid → series/impact мержатся без перекрытий
    series: dict = {}
    impact: dict = {}
    n_b = (len(tids) + args.batch - 1) // args.batch
    for bi in range(0, len(tids), args.batch):
        chunk = tids[bi:bi + args.batch]
        tb = time.time()
        s, im = local_stats(chunk, args.window)
        series.update(s)
        impact.update(im)
        print(f"prefill batch {bi // args.batch + 1}/{n_b}: {len(chunk)} тем, "
              f"{len(s)} серий, {len(im)} impact; за {time.time() - tb:.0f} с "
              f"(суммарно {time.time() - t0:.0f} с)", flush=True)
    print(f"local_stats за {time.time()-t0:.0f} с; пишу ...", flush=True)
    tt, yy, nn = [], [], []
    for tid, ser in series.items():
        for y, n in ser.items():
            tt.append(tid); yy.append(y); nn.append(n)
    out = ROOT / "data/openalex_derived/taxonomy/topic_ngi_cache.parquet"
    pq.write_table(pa.table({"tid": pa.array(tt, pa.int32()),
                             "year": pa.array(yy, pa.int32()),
                             "n": pa.array(nn, pa.int32())}),
                   out, compression="zstd")
    out_i = ROOT / "data/openalex_derived/taxonomy/topic_ngi_cache_impact.parquet"
    pq.write_table(pa.table({"tid": pa.array(list(impact.keys()), pa.int32()),
                             "impact": pa.array(list(impact.values()), pa.int32())}),
                   out_i, compression="zstd")
    # A0b: мета-файл — окно + sha1 таксономии; local_stats читает кэш только при
    # полном совпадении (иначе fallback DuckDB — защита от устаревшего кэша)
    CACHE_META.write_text(json.dumps({
        "window": int(args.window), "n_tids": len(tids),
        "tids_sha1": _tids_sha1(tids),
        "created": time.strftime("%Y-%m-%d %H:%M:%S")}, ensure_ascii=False))
    print(f"prefill DONE: {len(nn)} строк series, {len(impact)} тем с impact; "
          f"{time.time()-t0:.0f} с", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None,
                    help="JSON прогона query_directions (обязателен, кроме --prefill)")
    ap.add_argument("--window", type=int, default=2025,
                    help="год окна Y (дефолт 2025 = последний полный год снапшота)")
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--win-rank", type=int, default=100,
                    help="win-обрезка по retr_rank (default 100 = канон; "
                         "addendum №5 использует 130)")
    ap.add_argument("--garbage", choices=["none", "demote"], default="none",
                    help="честный фильтр мусора (прототип 27.09, локальный): "
                         "demote = темы с GARBAGE_RE-именем И n_hit==0 (нет "
                         "токенов запроса в профиле) ДЕМОТИРУЮТСЯ в конец списка, "
                         "не удаляются — покрытие меряется честно")
    ap.add_argument("--prefix", default=None, help="префикс выходов (дефолт <run>_ngi)")
    ap.add_argument("--relevance", choices=["none", "gate", "fusion", "win", "childall"],                    default="none",
                    help="P1 (25.09): none — прежнее поведение; gate — отброс тем "
                         "без пересечения с лексикой запроса; fusion — "
                         "screen × rel_norm (релевантность как член скоринга); "
                         "win — A2: окно ретривала retr_rank≤100 (win100 из "
                         "sim_gate), порядок по screen, без NGI-членов скоринга")
    ap.add_argument("--prefill", action="store_true",
                    help="NJ-2: series+impact по всем темам таксономии → "
                         "taxonomy/topic_ngi_cache*.parquet")
    ap.add_argument("--batch", type=int, default=1150,
                    help="prefill: размер чанка тем (OOM-фикс 25.09: полные 4516 "
                         "тем дают агрегаты > 4ГБ; чанки дисджоинтны → merge = "
                         "dict.update; пик памяти ∝ чанку)")
    args = ap.parse_args()
    if args.prefill:
        return prefill(args)
    if not args.run:
        ap.error("--run обязателен (кроме режима --prefill)")

    run_path = Path(args.run)
    run = json.loads(run_path.read_text())
    cands = run["directions"]
    tids = [int(c["topic_id"]) for c in cands]
    name_of = {int(c["topic_id"]): c["display_name"] for c in cands}
    retr_rank = {int(c["topic_id"]): i + 1 for i, c in enumerate(cands)}
    print(f"кандидатов из выдачи: {len(tids)} (routing={(run.get('routing') or {}).get('profile')})")

    # allowed-цели оракула — только для пометки в таблице (не влияет на скор)
    oracle_path = ROOT / "results/qa_allowed_sets.json"
    allowed: set = set()
    if oracle_path.exists():
        o = json.loads(oracle_path.read_text())
        _bonus = o.get("bonus") or []
        if isinstance(_bonus, dict):
            _bonus = [_bonus]
        for v in (o.get("targets") or []) + _bonus:
            ids = v.get("allowed") if isinstance(v, dict) else None
            if ids:
                allowed.update(int(x) for x in ids)

    print("локальные статистики T_stats (2016..%d)..." % args.window)
    series, impact = local_stats(tids, args.window)
    cache = json.loads(BIRTH_CACHE.read_text()) if BIRTH_CACHE.exists() else {}
    print("birth через OpenAlex API (кэш %d тем)..." % len(cache))
    births, n_req = fetch_births(tids, cache, args.window)
    print(f"API-запросов в этом запуске: {n_req}")

    Y = args.window
    rows, out_of_window = [], []
    for tid in tids:
        s = series.get(tid, {})
        n_late = sum(s.get(y, 0) for y in (Y - 2, Y - 1, Y))      # N(Y-2..Y)
        n_early = sum(s.get(y, 0) for y in (Y - 4, Y - 3))        # N(Y-4..Y-3)
        if n_late == 0 and n_early == 0:
            out_of_window.append(tid)
            continue
        if n_early == 0:                       # рождение в окне
            g, growth_n = None, 1.0
        else:
            g = n_late / n_early
            growth_n = g / (g + 1.0)
        birth = births.get(tid)
        if birth is None:
            nov = None
            age = None
        else:
            age = max(Y - birth, 0)
            nov = 1.0 - sigmoid((age - 15) / 5.0)
        imp = impact.get(tid, 0)
        imp_n = 1.0 - math.exp(-imp / 40.0)
        screen = None if nov is None else nov * growth_n * imp_n
        rows.append({"topic_id": tid, "name": name_of[tid], "birth": birth, "age": age,
                     "novelty_n": nov, "n_late": n_late, "n_early": n_early, "g": g,
                     "growth_n": growth_n, "impact": imp, "impact_n": imp_n,
                     "screen": screen, "retr_rank": retr_rank[tid],
                     "oracle": tid in allowed})

    # --- P1: релевантность запросу (25.09) -------------------------------
    if args.relevance in ("gate", "fusion", "win", "childall"):
        qt, idf, tot = add_relevance(run, rows)
        if args.relevance == "childall":
            compute_child_rel(rows, qt, idf, tot)
        if args.relevance == "gate":
            kept = [r for r in rows if r["n_hit"] > 0]
            print(f"гейт: {len(rows)} → {len(kept)} тем (отброшено "
                  f"{len(rows) - len(kept)} без пересечения с лексикой запроса)")
            rows = kept
        elif args.relevance == "win":
            # A2 (25.09): портированный win100 из sim_gate — кандидаты с
            # ретривал-рангом ≤100, порядок по screen (без NGI-членов скоринга)
            before = len(rows)
            rows = [r for r in rows if r["retr_rank"] <= args.win_rank]
            print(f"win: {before} → {len(rows)} кандидатов (retr_rank ≤ {args.win_rank})")
    else:
        for r in rows:
            r["rel"], r["n_hit"] = 0.0, 0

    scored = [r for r in rows if r["screen"] is not None]
    unscored = [r for r in rows if r["screen"] is None]

    # rel_norm нужен gr50-демоту и fusion (считаем один раз по всем scored)
    _mx = max((r.get("rel", 0.0) for r in scored), default=0.0) or 1.0
    for r in scored:
        r["rel_norm"] = r.get("rel", 0.0) / _mx

    def _gf(r):
        # М1 (штурм 27.09, семантика gr50 — ЗАМЕНА бесполезного n_hit-флага):
        # «имя матчит GARBAGE_RE И rel_norm<0.5» → конец списка (демот, не удаление).
        # ⚠ числа инструменто-зависимы (верификатор 27.09): sim_gate → 0/0/0 при
        # 8/8/7; прод-путь → 1/1/0 при 8/8/8 (разный базис rel_norm). Порог 0.5
        # зафиксирован протоколом ДО прогона (results/runtime/RANK_PROTOCOL_20260927.md).
        # Без флага всегда 0 → поведение по умолчанию не меняется.
        return 1 if (args.garbage == "demote" and r["rel_norm"] < 0.5
                     and GARBAGE_RE.search(r["name"])) else 0

    if args.relevance == "childall" and scored:
        # D1/D2 (канон = прод-путь): окно ВСЕ кандидаты, порядок screen × child_rel;
        # при --garbage demote поверх — gr50-демот (D2)
        scored.sort(key=lambda r: (_gf(r), -(r["screen"] * r["child_rel"]),
                                   r["topic_id"]))
    elif args.relevance == "fusion" and scored:
        scored.sort(key=lambda r: (_gf(r), -(r["screen"] * r["rel_norm"])))
    else:
        scored.sort(key=lambda r: (_gf(r), -r["screen"], r["topic_id"]))
    top = scored[: args.top]

    # ---- выходы ----
    prefix = Path(args.prefix) if args.prefix else run_path.with_suffix("")
    md_path = Path(str(prefix) + "_ngi_top%d.md" % args.top)
    csv_path = Path(str(prefix) + "_ngi.csv")
    json_path = Path(str(prefix) + "_ngi_full.json")

    def fmt(v, nd=3):
        return "—" if v is None else f"{v:.{nd}f}"

    lines = [f"# Подтемы «{run['query'][:60]}» — ранжирование novelty × growth × impact "
             f"(окно Y={Y})",
             "",
             f"Выдача: `{run_path}` ({len(cands)} кандидатов; routing={(run.get('routing') or {}).get('profile')}, "
             f"embed={'i2' if 'i2' in str(run_path) else 'base'}). "
             f"Канон: growth_n=g/(g+1) [g=N{Y-2}-{Y}/N{Y-4}-{Y-3}], "
             f"novelty_n=1−sigmoid((age−15)/5) [birth по правилу «перерыв ≥2 лет»], "
             f"impact_n=1−exp(−impact/40), screen=N×G×I. "
             f"Фильтр type IN (без dataset/other). Oracle = тема из allowed-набора QA-теста (справочно).",
             "",
             f"## Топ-{len(top)}",
             "",
             "| # | T-ID | направление | birth | age | novelty | N{0}-{1} | N{2}-{3} | g | growth | impact | imp_n | screen | retr | oracle |".format(
                 Y - 2, Y, Y - 4, Y - 3),
             "|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:-:|"]
    for i, r in enumerate(top, 1):
        g_s = "∞*" if r["g"] is None else f"{r['g']:.2f}"
        lines.append(
            f"| {i} | {r['topic_id']} | {r['name'][:58]} | {r['birth'] or '—'} | "
            f"{r['age'] if r['age'] is not None else '—'} | {fmt(r['novelty_n'])} | "
            f"{r['n_late']} | {r['n_early']} | {g_s} | {fmt(r['growth_n'])} | "
            f"{r['impact']} | {fmt(r['impact_n'])} | **{fmt(r['screen'])}** | "
            f"{r['retr_rank']} | {'✓' if r['oracle'] else ''} |")
    if out_of_window:
        lines += ["", f"*Вне окна (нет работ и в раннем, и в позднем окне): {len(out_of_window)} тем.*"]
    if unscored:
        lines += [f"*Без birth (API не ответил): {len(unscored)} тем — не ранжированы.*"]
    lines.append("")
    md_path.write_text("\n".join(lines))

    import csv as csv_mod
    with csv_path.open("w", newline="") as f:
        w = csv_mod.DictWriter(f, fieldnames=list(scored[0].keys()) if scored else
                               ["topic_id", "name"])
        w.writeheader()
        w.writerows(scored)
    json_path.write_text(json.dumps(
        {"window": Y, "run": str(run_path), "n_candidates": len(cands),
         "n_scored": len(scored), "out_of_window": out_of_window,
         "no_birth": [r["topic_id"] for r in unscored], "top": top, "all": scored},
        ensure_ascii=False, indent=1))

    print(f"\n=== Топ-{len(top)} (из {len(scored)} скоренных; вне окна {len(out_of_window)}, "
          f"без birth {len(unscored)}) ===")
    print(f"{'#':>3} {'T-ID':>6} {'screen':>6} {'nov':>5} {'g':>5} {'grw':>5} "
          f"{'imp':>6} {'birth':>5} {'retr':>4} o  направление")
    for i, r in enumerate(top, 1):
        g_s = "—" if r["g"] is None else f"{r['g']:.2f}"
        print(f"{i:>3} {r['topic_id']:>6} {r['screen']:>6.3f} {r['novelty_n']:>5.2f} "
              f"{g_s:>5} {r['growth_n']:>5.2f} {r['impact']:>6} {r['birth'] or '?':>5} "
              f"{r['retr_rank']:>4} {'✓' if r['oracle'] else ' '}  {r['name'][:52]}")
    print(f"\nвыходы: {md_path} | {csv_path} | {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
