#!/usr/bin/env python3
"""C2 (NIGHT_PLAN 25→26.09): TermTech webapp — FastAPI-сервис выдачи.

API-контракт (NIGHT_PLAN §2, блок C2):
  GET /api/query?q=...        (без токена — свободный доступ, директива 28.09)
    → {query, topics: [{tid, name, screen, rel, birth, series,
                        top_works[{title,year,cites}]}],
              techs:  [{term, growth, first_year, series, cases, domain}],
              retrieval: {model, ms}}
  GET /health → {status, model, mode, n_topics, n_terms}  (без токена)

Механика (заморожена по A0b/A2 победителю sim_gate 25.09):
  * ретривал: e5-small (C3, topic_vectors_e5m.npy) → косинус;
    win100 = окно ретривал-ранг ≤100 (победитель sim_gate), затем ранжирование
    N×G×I screen = novelty × growth × impact (окно Y=2025, NGI-кэш A0);
  * rel: IDF-покрытие лексики запроса профилем темы (имя + топ-работы digest);
  * techs: TermTech-кандидаты всех срезов в webapp/data (sp, q1ai после E0),
    score = IDF-доля запросных токенов в терме (по df терма);
  * фолбэк TF-IDF: MemAvailable < 400 МБ на старте ЛИБО ошибка модели
    (записывается в retrieval.model; честно виден автору).
Источники: webapp/data/{taxonomy,ngi,birth,digest,termtech_*}.
Память: parquet читаются pyarrow/pandas (< 150 МБ), duckdb НЕ используется
(файл NGI-кэша 0.1 МБ — лимит 512 МБ соблюдён без duckdb вообще).

Токен НЕ используется (решение команды: доступ свободный, по условиям хакатона
без токенов и заморочек; middleware аутентификации удалён).
Запуск: uvicorn app:app --host 127.0.0.1 --port 8000
"""
import json
import math
import os
import re
import sys
import threading
import time
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "scripts"))
sys.path.insert(0, str(ROOT.parent / "src"))
from rank_directions_ngi import GARBAGE_RE  # noqa: E402  (канон-regex, один источник)
from build_tech_ngi import (GENERIC_PHRASES, GENERIC_MODS_EXACT,  # noqa: E402
                            GENERIC_MODS_SUFFIX, is_snippet)
DATA = ROOT / "data"
WINDOW = 2025
TOP_TOPICS = 15
TOP_TECHS = 15
WIN_K = int(os.environ.get("WEBAPP_WIN_K", "1200"))
                     # окно кандидатов (Addendum №12: 100→1200 — из распределения
                     # e5-рангов целей; WEBAPP_WIN_K — харнесс замера baseline)
ORDER = os.environ.get("WEBAPP_ORDER", "rrf")  # rrf = дефолт по вердикту №15-2 (парето-доминирование над №13 от 28.09 13:45); rel = канон №13; screen = baseline 22:01
# ⭐ Addendum №17 (29.09, объявлен ДО правок): карточный режим формы 1 + серв-гейт З1.
# Дефолты = канон: без флагов поведение сервиса НЕ меняется (см. RANK_PROTOCOL №17).
CARDS_ENABLED = os.environ.get("WEBAPP_CARDS", "0") == "1"
GATE_ENABLED = os.environ.get("WEBAPP_GATE", "0") == "1"   # З1: фильтр мусора
W_BAL = float(os.environ.get("WEBAPP_W", "-1"))              # -1 = канон (−rel,−score)
TAU = float(os.environ.get("WEBAPP_TAU", "0.805"))           # косинус-гейт карточек
RELAX_TOK = os.environ.get("WEBAPP_RELAX_TOK", "0") == "1"  # RU-запрос без токен-гейта
BRIDGE_GATE = os.environ.get("WEBAPP_BRIDGE_GATE", "0") == "1"  # №20: карточка → топ-15 тем
# ⭐ Серв-гейт llm_valid (план fix_two_problems_plan_20260929, поправка 3/P1-3):
# в выдачу формы 1 попадают ТОЛЬКО llm_valid==1 (K2=100%); без флага — канон (дефолт 0,
# поведение не меняется). Лестница τ продолжает спускаться, но невалидных НЕ добавляет.
LLM_GATE = os.environ.get("WEBAPP_LLM_GATE", "0") == "1"
# №14 (провален 28.09 11:35): batch-ретривал сохранён за ОПЫТНЫМ флагом;
# дефолт 0 = канон №13 ступень 2 (run=None → окно WIN_K, лексика без субзапросов)
BATCH_ENABLED = os.environ.get("WEBAPP_BATCH", "0") == "1"
# №15-1 (провален 28.09 13:42): child-e5 канал сохранён за опытным флагом;
# дефолт 0 = канон №13 ступень 2 (вердикт 15-1 + уточнение №15а в протоколе)
CHILD_ENABLED = os.environ.get("WEBAPP_CHILD", "0") == "1"
TOP_WORKS_N = 5
SERIES_YEARS_N = 10
MIN_AVAIL_MB = 400    # ниже → TF-IDF-фолбэк (C2)

TOKEN_RE = re.compile(r"[a-zа-яё0-9]{2,}", re.I)
STOP = set("""
выдай темы по защите года году и о на для от с к как при что это эти или же не нет
да все очень более самый можно нужно через про между
a an the and or of to in for on with from by at as is are be been being this that
these those it its our your their can could may might will would should must not no
do does did study paper analysis research method methods using use used data results
result new two three one artificial intelligence models model based
""".split())


def log(m: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def mem_avail_mb() -> float:
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1024
    except Exception:
        pass
    return 9999.0


# ------------------------------------------------------------- данные
TOPICS = pd.read_parquet(DATA / "taxonomy" / "topics.parquet")
VECTORS = np.load(DATA / "embed" / "topic_vectors_e5m.npy")
assert len(TOPICS) == len(VECTORS), "topics/вектора не совпадают"
# Русские названия тем (решение команды: «рус. (EN)»); кэш перевода 4516 имён,
# собран офлайн scripts-проходом; отсутствие файла → показываем оригинал
_TN_RU = DATA / "topic_names_ru.json"
TOPIC_RU: dict[str, str] = json.loads(_TN_RU.read_text()) if _TN_RU.exists() else {}
if not TOPIC_RU:
    log("topic_names_ru.json нет — темы будут на английском")

_ngi_s = pd.read_parquet(DATA / "ngi" / "topic_ngi_cache.parquet")
NGI_SERIES: dict[int, dict[int, int]] = (
    _ngi_s.groupby("tid")["year"].apply(list).to_dict())
NGI_SERIES = {int(t): dict(zip(ys, _ngi_s[_ngi_s.tid == t]["n"].tolist()))
              for t, ys in NGI_SERIES.items()}
_ngi_i = pd.read_parquet(DATA / "ngi" / "topic_ngi_cache_impact.parquet")
NGI_IMPACT = dict(zip(_ngi_i.tid.astype(int), _ngi_i.impact.astype(int)))
BIRTH = json.loads((DATA / "birth" / "ngi_birth_cache.json").read_text())

# позиции тем по T-ID — направления batch-движка приходят по topic_id (№14)
TID2POS = {int(str(v).rstrip("/").split("T")[-1]): i
           for i, v in enumerate(TOPICS["id"])}
TID2NAME = {t: str(TOPICS.iloc[p]["display_name"]) for t, p in TID2POS.items()}

# ---- child-темы (V1-показ, штурм 27.09): узкие подтемы под parent'ами ----
# Ранжирование НЕ трогаем — чистый показ (протокол ранжирования не нужен).
_cp = DATA / "children" / "children.parquet"
if _cp.exists():
    _ch = pd.read_parquet(_cp)
    CHILDREN: dict[int, list[dict]] = {}
    for r in _ch.sort_values("df_sum", ascending=False).itertuples():
        CHILDREN.setdefault(int(r.parent_tid), []).append(
            {"term": str(r.rep_term), "n_terms": int(r.n_terms),
             "df_sum": int(r.df_sum), "profile": str(r.profile)})
    log(f"child-темы: {len(_ch)} на {len(CHILDREN)} parent'ов")
    del _ch
else:
    CHILDREN = {}
    log("child-темы: нет children.parquet — показ подтем отключён")

# ---- Child-e5 канал (Addendum №15, ступень 15-1): доставка + rel-лексика ----
# Вектора/ids в порядке строк children.parquet (scripts/build_child_vectors.py);
# параметры заморожены №15: top-300 доставка, top-30 лексика.
CHILD_TOP = 300
CHILD_LEX = 30
_cv, _ci = (DATA / "children" / "child_vectors_e5m.npy",
            DATA / "children" / "child_ids.json")
CHVEC = None
CH_PARENT = None
CHTXT: list[str] = []
if _cv.exists() and _ci.exists():
    import json as _json
    _ch2 = pd.read_parquet(DATA / "children" / "children.parquet",
                           columns=["child_id", "parent_tid", "rep_term", "profile"])
    if list(_ch2["child_id"].astype(str)) == _json.loads(_ci.read_text()):
        CHVEC = np.load(_cv)
        CH_PARENT = _ch2["parent_tid"].to_numpy(np.int64)
        CHTXT = [f"{a} {b}" for a, b in zip(_ch2["rep_term"], _ch2["profile"])]
        log(f"child-e5 канал: {len(CHVEC)} векторов, окно {CHILD_TOP}, лексика {CHILD_LEX}")
    else:
        log("child-e5 канал: child_ids не сошлись с parquet — отключён")
    del _ch2
else:
    log("child-e5 канал: векторов нет — отключён")

# ---- Retro-2026 блок (Addendum №16, ступень 16-1) ----
# Данные: scripts/build_retro2026.py; τ=0.82 заморожен ДО (7 пар: POS 0.84-0.92 / NEG 0.76-0.79)
RETRO_TAU = 0.82
RETRO_MAX = 3
_rj, _rv = DATA / "retro2026.json", DATA / "retro2026_vectors.npy"
if _rj.exists() and _rv.exists():
    RETRO_ITEMS = json.loads(_rj.read_text())
    RETRO_VECS = np.load(_rv)
    log(f"retro-2026: {len(RETRO_ITEMS)} пунктов")
else:
    RETRO_ITEMS, RETRO_VECS = [], None
    log("retro-2026: нет данных — блок отключён")

# ---- Weak-signal 2026: тема ↔ пункты Gartner/MIT TR/CBI (для карточки темы) ----
# Источник: retro2026.json mapped (retro_l1: e5 top-20 → rel ≥0.1, механика заморожена).
_RU_PATH = DATA / "retro2026_ru.json"
ITEM_RU = json.loads(_RU_PATH.read_text()) if _RU_PATH.exists() else {}
SIGNAL2026: dict[int, list[dict]] = {}
# порог отображения rel≥0.3 (28.09): связки 0.12–0.21 шумные (тема ↔ далёкий пункт);
# механика retro_l1 (rel≥0.1) для coverage-метрики НЕ тронута — это только бейдж
for _it in RETRO_ITEMS:
    for _m in _it.get("mapped") or []:
        if float(_m.get("rel", 0)) < 0.3:
            continue
        SIGNAL2026.setdefault(int(_m["tid"]), []).append(
            {"item": _it["item"], "item_ru": ITEM_RU.get(_it["item"]),
             "source": _it["source"], "rel": round(float(_m["rel"]), 2)})
for _tid in SIGNAL2026:
    SIGNAL2026[_tid].sort(key=lambda s: -s["rel"])
    del SIGNAL2026[_tid][3:]          # максимум 3 бейджа на тему
log(f"weak-signal-2026: {len(SIGNAL2026)} тем связаны с пунктами-2026 (rel≥0.3)")

_digest = pd.read_parquet(DATA / "digest" / "digest.parquet",
                          columns=["tid", "publication_year",
                                   "cited_by_count", "title"])
_digest["tid"] = _digest["tid"].astype(int)
_digest["publication_year"] = _digest["publication_year"].astype(int)
_digest["cited_by_count"] = _digest["cited_by_count"].astype(int)
DIGEST_TOP: dict[int, list] = {}
for tid, grp in _digest.groupby("tid"):
    grp = grp.sort_values("cited_by_count", ascending=False).head(TOP_WORKS_N)
    DIGEST_TOP[int(tid)] = [
        {"title": str(r.title)[:160], "year": int(r.publication_year),
         "cites": int(r.cited_by_count)} for r in grp.itertuples()]
del _digest

# Технологии (Идея 1+2, 28.09): emerging-термы (fy≥2018, n_recent≥5) со связью на
# крупную тему; series/birth/Оценка — канон NGI из _yeardf (scripts/build_tech_ngi.py)
TECH = pd.read_parquet(DATA / "tech_ngi.parquet")
TECH_TERMS: list[str] = TECH["term"].astype(str).tolist()
TECH_LOWER = [t.lower() for t in TECH_TERMS]
TECH_SCORE = TECH["score"].to_numpy(float)
TECH_NOV = TECH["novelty"].to_numpy(float)
TECH_GRO = TECH["growth"].to_numpy(float)
TECH_IMP = TECH["impact"].to_numpy(float)
TECH_BIRTH = TECH["birth"].to_numpy(int)
TECH_NREC = TECH["n_recent"].to_numpy(int)
TECH_DF = TECH["df"].to_numpy(int)
TECH_SERIES = [json.loads(s) for s in TECH["series_json"]]
TECH_LINKED = [json.loads(s) for s in TECH["linked_json"]]
_tru = DATA / "tech_terms_ru.json"
TECH_RU: dict[str, str] = json.loads(_tru.read_text()) if _tru.exists() else {}
# Семантический ретривал технологий (фикс 28.09): косинус e5 + токен-гейт
# (границы слов). τ=0.805 — калибровка 28.09 по демо-запросам: легитимный минимум
# «fintech» = 0.807 (RU→EN), мусор «finite element/nietzsche» ≤ 0.800;
# при τ=0.78 проходил «finite element approach» (e5 путает похожие префиксы)
TECH_TAU = 0.805
_tv = DATA / "tech_ngi_vectors.npy"
if _tv.exists():
    TECH_VEC = np.load(_tv)
    assert len(TECH_VEC) == len(TECH), "вектора/термы не совпадают"
else:
    TECH_VEC = None
    log("tech_ngi_vectors нет — технологии по токен-фолбэку")
N_TERMS = len(TECH)
log(f"технологии (tech_ngi): {N_TERMS} в пуле, переводов {len(TECH_RU)}")

# TF-IDF-фолбэк (лексический, по blob темы; считается один раз)
def _blob(i: int) -> str:
    r = TOPICS.iloc[i]
    kw = r["keywords"]
    if not isinstance(kw, str):
        kw = " ".join(map(str, kw)) if kw is not None else ""
    return f"{r['display_name']} {str(r['description'])[:400]} {kw[:300]}".lower()


TFIDF = None
E5 = None          # глобальный до всех веток (fix VPS: TF-IDF-путь не определял E5 → NameError)
if mem_avail_mb() < MIN_AVAIL_MB:
    log(f"MemAvailable={mem_avail_mb():.0f} МБ < {MIN_AVAIL_MB} → TF-IDF-режим")
else:
    try:
        from tokenizers import Tokenizer
        import onnxruntime as ort
        # TT_ONNX_DIR: на VPS модель лежит в /opt/termtech-web/e5m_onnx;
        # TT_ONNX_MODEL: на VPS можно model_int8.onnx (113МБ вместо 449МБ)
        ONNX_DIR = Path(os.environ.get("TT_ONNX_DIR", "/mnt/e/openalex_derived/e5m_onnx"))
        ONNX_MODEL = os.environ.get("TT_ONNX_MODEL", "model.onnx")
        _tok = Tokenizer.from_file(str(ONNX_DIR / "tokenizer.json"))
        _tok.enable_truncation(max_length=512)
        _tok.enable_padding()
        _so = ort.SessionOptions()
        _so.intra_op_num_threads = 2
        E5 = ort.InferenceSession(str(ONNX_DIR / ONNX_MODEL), _so,
                                  providers=["CPUExecutionProvider"])
        log(f"e5-small ONNX загружен (MemAvailable={mem_avail_mb():.0f} МБ)")
    except Exception as e:
        E5 = None
        log(f"модель недоступна ({e}) → TF-IDF-режим")

if True:  # lexicon-TFIDF (нужен и как фолбэк): токен→idf по корпусу тем
    from collections import Counter
    dfc: Counter = Counter()
    _blobs = []
    for i in range(len(TOPICS)):
        b = _blob(i)
        _blobs.append(b)
        dfc.update(set(t for t in TOKEN_RE.findall(b)))
    _N = len(TOPICS)
    TFIDF = ({t: math.log((_N + 1) / (c + 1)) + 1.0 for t, c in dfc.items()},
             _blobs)

_emb_lock = threading.Lock()


def e5_embed(texts: list[str], is_query: bool = True) -> np.ndarray:
    prefix = "query: " if is_query else "passage: "
    enc = _tok.encode_batch([prefix + t for t in texts])
    ids = np.array([e.ids for e in enc], dtype=np.int64)
    mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
    tti = np.array([e.type_ids for e in enc], dtype=np.int64)
    with _emb_lock:
        hs = E5.run(None, {"input_ids": ids, "attention_mask": mask,
                           "token_type_ids": tti})[0]
    m = mask.astype(np.float32)[:, :, None]
    pooled = (hs * m).sum(axis=1) / np.clip(m.sum(axis=1), 1, None)
    pooled /= np.clip(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9, None)
    return pooled


def qtokens(q: str) -> list[str]:
    out, seen = [], set()
    for t in TOKEN_RE.findall(q.lower()):
        if t in STOP or t.isdigit() or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


# ---- Batch-направления (Addendum №14, протокол 28.09: порт fanout из batch) ----
# Параметры заморожены №14: gate [3,2], n_topics=topk=2000, years (2026,2026),
# fanout {m:1500,k:12,ktop:50,rrf_c:60,seed:42}, source по matcher'у route_query.
BATCH: dict = {"oa": None, "P": None, "con": None, "err": None}
_batch_lock = threading.Lock()
_GATE_DOMAINS = [3, 2]
_BATCH_YEARS = (2026, 2026)
_BATCH_N = 2000
_FANOUT_CFG = {"m": 1500, "k": 12, "ktop": 50, "rrf_c": 60, "seed": 42}
_LEXICON_PATH = DATA / "lexicon" / "qa_facet_lexicon_v1.json"


def _batch_init() -> bool:
    """Ленивая инициализация query_directions (№14). Ошибка — ЯВНЫЙ лог (§9)."""
    if BATCH["oa"] is not None:
        return True
    if BATCH["err"] is not None:
        return False
    try:
        import duckdb
        import oa_snapshot as oa
        P = oa.Paths(local=ROOT.parent / "data" / "openalex_derived",
                     e=Path("/mnt/e/openalex_derived"),
                     staging=Path("/mnt/c/oa_tmp"))
        if not (P.taxonomy() / "topic_vectors.npy").exists():
            raise FileNotFoundError(f"нет {P.taxonomy()}/topic_vectors.npy (LaBSE)")
        con = duckdb.connect()
        con.execute("SET threads=2; SET memory_limit='1GB'")
        Path("/mnt/e/openalex_derived/tmp_duck").mkdir(parents=True, exist_ok=True)
        con.execute("SET temp_directory='/mnt/e/openalex_derived/tmp_duck'")
        BATCH.update(oa=oa, P=P, con=con)
        log(f"batch-движок query_directions готов (mem={mem_avail_mb():.0f} МБ)")
        return True
    except Exception as e:
        BATCH["err"] = str(e)
        log(f"batch-движок НЕДОСТУПЕН ({e}) → ретривал остаётся на e5/TF-IDF")
        return False


def batch_directions(query: str):
    """→ (cand_idx по позициям TOPICS, model, run) | None.
    Ошибка движка → честный фолбэк на e5-путь (лог выше)."""
    if not BATCH_ENABLED:
        return None
    if not _batch_init():
        return None
    oa = BATCH["oa"]
    src = ("lexicon"
           if oa.route_query(query).get("matched") and _LEXICON_PATH.exists()
           else "cluster")
    fanout = {**_FANOUT_CFG, "n_topics": _BATCH_N, "source": src,
              "lexicon_path": str(_LEXICON_PATH)}
    try:
        with _batch_lock:
            run = oa.query_directions(
                BATCH["con"], BATCH["P"], query, topk=_BATCH_N,
                years=_BATCH_YEARS, n_topics=_BATCH_N, match="embed",
                gate_domains=_GATE_DOMAINS, fanout=fanout)
        idx = []
        for d in run.get("directions") or []:
            pos = TID2POS.get(int(d["topic_id"]))
            if pos is not None:
                idx.append(pos)
        if not idx:
            raise RuntimeError("направления не отобразились в таксономию")
        return idx, f"batch-fanout-{src}", run
    except Exception as e:
        BATCH["err"] = str(e)
        log(f"batch-ретривал упал ({e}) → e5-фолбэк")
        return None


def retrieve(query: str) -> tuple[list[int], str, dict | None]:
    """→ (кандидаты по ретривал-рангу, model-строка, run batch | None).
    №14: сначала batch-направления (fanout), e5/TF-IDF — фолбэк при ошибке."""
    b = batch_directions(query)
    if b is not None:
        return b
    if E5 is not None:
        try:
            qv = e5_embed([query])[0]
            sim = VECTORS @ qv
            order = np.argsort(-sim)[:WIN_K]
            return [int(i) for i in order], "e5-small-onnx", None
        except Exception as e:
            log(f"ошибка модели ({e}) → TF-IDF")
    idf, blobs = TFIDF
    qt = qtokens(query)
    scores = []
    for i, b in enumerate(blobs):
        s = sum(idf[t] for t in qt if t in b)
        scores.append(s)
    order = np.argsort(-np.array(scores))[:WIN_K]
    return [int(i) for i in order], "tfidf", None


def birth_of(tid: int) -> int | None:
    hist = BIRTH.get(str(tid))
    if not hist:
        return None
    # Правило «затишье сбрасывает» (автор 2026-09-14) — ЗЕРКАЛО КАНОНА
    # rank_directions_ngi.birth_from_histogram: назад от последнего года с работами
    # (≤ WINDOW); разрыв ≤1 года допустим (разница лет ≤2), ≥2 пропущенных лет
    # подряд (разница ≥3) — стоп, birth = первый год текущего непрерывного отрезка.
    # ⚠️ ФИКС бага 28.09 (заметил автор: «birth всегда 2025»): прежний код
    # (birth=ys[0]; `if y - birth >= 2`) не мог сработать никогда → birth ≡ последний
    # активный год, новизна у всех активных тем была ≈0.95.
    years = sorted(int(y) for y in hist if int(y) <= WINDOW and hist[y] > 0)
    if not years:
        return None
    seg = years[-1]
    for y in reversed(years[:-1]):
        if seg - y >= 3:
            break
        seg = y
    return seg


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def profile(tid: int, name: str) -> str:
    titles = " ".join(w["title"] for w in DIGEST_TOP.get(tid, []))
    return f"{name} {titles}".lower()


def add_rel(rows: list[dict], qt: list[str]) -> None:
    n = max(len(rows), 1)
    df = {t: sum(1 for r in rows if t in r["_prof"]) for t in qt}
    idf = {t: math.log((n + 1) / (df[t] + 1)) + 1.0 for t in qt}
    total = sum(idf.values()) or 1.0
    for r in rows:
        hit = [t for t in qt if t in r["_prof"]]
        r["rel"] = sum(idf[t] for t in hit) / total


def screen_rows(cand_idx: list[int], run_qt: list[str],
                win_k: int | None = None) -> list[dict]:
    # win_k (№14): batch-пул — без доп. обрезки (весь пул направлений); e5 — WIN_K
    Y = WINDOW
    rows = []
    for rank, i in enumerate(cand_idx, 1):
        rec = TOPICS.iloc[i]
        tid = int(str(rec["id"]).rstrip("/").split("T")[-1])
        ser = NGI_SERIES.get(tid, {})
        n_late = sum(ser.get(y, 0) for y in (Y - 2, Y - 1, Y))
        n_early = sum(ser.get(y, 0) for y in (Y - 4, Y - 3))
        if n_late == 0 and n_early == 0:
            continue
        growth_n = 1.0 if n_early == 0 else (
            (n_late / n_early) / (n_late / n_early + 1.0))
        b = birth_of(tid)
        if b is None:
            continue
        nov = 1.0 - sigmoid((max(Y - b, 0) - 15) / 5.0)
        imp = NGI_IMPACT.get(tid, 0)
        imp_n = 1.0 - math.exp(-imp / 40.0)
        name = str(rec["display_name"])
        rows.append({"tid": tid, "name": name,
                     "name_ru": TOPIC_RU.get(name, name),
                     "retr_rank": rank,
                     "screen": nov * growth_n * imp_n, "birth": b,
                     # компоненты оценки — для детальной карточки темы (28.09)
                     "novelty": round(nov, 3), "growth": round(growth_n, 3),
                     "impact": round(imp_n, 3),
                     "series": {str(y): ser[y]
                                for y in sorted(ser) if y >= 2016},
                     "signal2026": SIGNAL2026.get(tid),
                     "_prof": profile(tid, name)})
    add_rel(rows, run_qt)
    # win100 (A2): окно ретривала, порядок по screen
    kept = [r for r in rows if r["retr_rank"] <= (WIN_K if win_k is None else win_k)]
    kept.sort(key=lambda r: (-r["screen"], r["tid"]))
    # ⭐ Addendum №13 ступень 1 (ночь 27→28, объявлен ДО): демот БЕЗ порога rel —
    # мусор edge/fintech держался в топ-15 именно rel_norm≥0.5; allowed-темы топ-15
    # GARBAGE_RE не матчат → покрытие не падает. ORDER=screen — замер baseline.
    _mx = max((r["rel"] for r in kept), default=0.0) or 1.0
    if ORDER == "screen":
        kept.sort(key=lambda r: (
            1 if (r["rel"] / _mx < 0.5 and GARBAGE_RE.search(r["name"])) else 0,
            -r["screen"], r["tid"]))
    elif ORDER == "rrf":
        # ⭐ Ступень 15-2 (объявлена заранее, №15/№15а): RRF(c=60) по
        # (retr_rank = e5-ранг, rel_rank), tie → −screen, tid; гейт GARBAGE сохраняется.
        _rrf_c = 60  # та же константа, что в замороженном fanout-конфиге
        _rel_rank = {r["tid"]: i + 1 for i, r in enumerate(
            sorted(kept, key=lambda r: (-r["rel"], r["tid"])))}
        kept.sort(key=lambda r: (
            1 if GARBAGE_RE.search(r["name"]) else 0,
            -(1.0 / (_rrf_c + r["retr_rank"]) + 1.0 / (_rrf_c + _rel_rank[r["tid"]])),
            -r["screen"], r["tid"]))
    else:
        kept.sort(key=lambda r: (
            1 if GARBAGE_RE.search(r["name"]) else 0,
            -(r["rel"] / _mx), -r["screen"], r["tid"]))
    # V1-показ: query-релевантные дети parent'а (покрытие лексики запроса профилем
    # ребёнка — та же механика, что add_rel; топ-3 по (покрытие, df_sum)).
    # Без совпадений лексики → не показываем (не выдумываем релевантность).
    for r in kept:
        hits_best = []
        for c in CHILDREN.get(r["tid"], []):
            n_hit = sum(1 for t in run_qt if t in c["profile"])
            if n_hit > 0:
                hits_best.append((n_hit, c["df_sum"], c["term"], c["n_terms"]))
        hits_best.sort(key=lambda x: (-x[0], -x[1]))
        r["children"] = [{"term": t, "n_terms": n, "hits": h}
                         for h, _d, t, n in hits_best[:3]]
    for r in kept:
        r.pop("_prof", None)
        r["top_works"] = DIGEST_TOP.get(r["tid"], [])
    return kept[:TOP_TOPICS]


def tech_rows(qt: list[str], qv=None) -> list[dict]:
    """Зарождающиеся технологии (Идея 1+2, 28.09): пул tech_ngi
    (fy≥2018 + связь с крупной темой). Релевантность:
      * основной путь — косинус e5 (запрос↔терм) ≥ TECH_TAU И ≥1 токен запроса
        по ГРАНИЦАМ СЛОВ (двойной гейт: семантика + намерение запроса);
      * фолбэк (нет E5) — прежний IDF-покрытие токенов.
    Сортировка: по релевантности (tie — Оценка) — зеркало логики тем."""
    n = max(len(TECH_TERMS), 1)
    df_map = dict(zip(TECH_TERMS, TECH_DF))
    idf = {t: math.log((n + 1) / (df_map.get(t, n) + 1)) + 1.0 for t in qt}
    total = sum(idf.values()) or 1.0
    pats = {t: re.compile(r"\b" + re.escape(t) + r"\b") for t in qt}
    semantic = TECH_VEC is not None and qv is not None
    cos_all = (TECH_VEC @ qv) if semantic else None
    out: list[dict] = []
    for i, tl in enumerate(TECH_LOWER):
        hit = 0.0
        for t in qt:
            if t in tl and pats[t].search(tl):   # substring → быстрый фильтр, затем границы слов
                hit += idf[t]
        if hit <= 0:
            continue
        if semantic:
            c = float(cos_all[i])
            if c < TECH_TAU:
                continue
            rel = c
        else:
            rel = hit / total
        term = TECH_TERMS[i]
        topics = []
        for tid in TECH_LINKED[i][:3]:
            nm = TID2NAME.get(tid)
            if nm:
                topics.append({"tid": tid, "name": nm,
                               "name_ru": TOPIC_RU.get(nm, nm)})
        out.append({"term": term, "term_ru": TECH_RU.get(term, term),
                    "score": float(TECH_SCORE[i]),
                    "novelty": float(TECH_NOV[i]), "growth": float(TECH_GRO[i]),
                    "impact": float(TECH_IMP[i]),
                    "rel": round(rel, 3), "birth": int(TECH_BIRTH[i]),
                    "n_recent": int(TECH_NREC[i]),
                    "series": TECH_SERIES[i], "topics": topics})
    out.sort(key=lambda r: (-r["rel"], -r["score"]))
    return out[:TOP_TECHS]


# ---- CARDS-режим формы 1 (Addendum №17, ступень Д; 29.09) ----
CARDS: dict = {"df": None, "vec": None, "low": None, "ru": None, "bad": None,
               "linked": None}


def _cards_init() -> bool:
    if not CARDS_ENABLED:
        return False
    if CARDS["df"] is not None:
        return True
    try:
        df = pd.read_parquet(DATA / "cards" / "tech_cards.parquet")
        vec = np.load(DATA / "cards" / "tech_cards_vectors.npy")
        assert len(df) == len(vec), "карточки/вектора не совпадают"
        nm = df["name_en"].fillna(df["term"])
        low = nm.str.lower().to_numpy()
        ru = df["name_ru"].fillna("").str.lower().to_numpy()
        # серв-гейт З1: маска мусора (один раз при загрузке).
        # №23: ТОЧНОЕ зеркало вердикта stage0 (GR ∪ GEN ∪ MOD ∪ SNIP);
        # bridge=0 закрывается гейтом №20 отдельно.
        _tok = re.compile(r"[a-zа-яё0-9]{2,}", re.I)
        bad = np.array([
            bool(GARBAGE_RE.search(n))
            or n.lower() in GENERIC_PHRASES
            or is_snippet(n)
            or any(t in GENERIC_MODS_EXACT or t.endswith(GENERIC_MODS_SUFFIX)
                   for t in _tok.findall(n.lower()))
            for n in nm.to_numpy()], dtype=bool)
        CARDS.update(df=df, vec=vec, low=low, ru=ru, bad=bad)
        # №20: linked-сети один раз при загрузке (bridge-гейт)
        def _lk(x):
            try:
                return frozenset(json.loads(x)) if isinstance(x, str) and x.startswith("[") \
                    else frozenset()
            except (json.JSONDecodeError, TypeError):
                return frozenset()
        CARDS["linked"] = [_lk(x) for x in df["linked_json"].tolist()]
        CARDS["good"] = np.nonzero(~bad)[0]   # индексы не-мусора (№22, быстрый пул)
        log(f"карточки: {len(df)} в пуле, llm_valid={int(df['llm_valid'].sum())}, "
            f"гейт-кандидатов(мусор)={int(bad.sum())}, LLM_GATE={int(LLM_GATE)}")
        return True
    except Exception as e:  # noqa: BLE001 — явный фолбэк + лог (§9)
        log(f"карточный стор недоступен ({e}) → форма 1 на tech_ngi")
        return False


def tech_rows_cards(qt: list[str], qv=None, q0: str | None = None,
                    top_topics: set[int] | None = None) -> list[dict] | None:
    """→ list (карточный режим) | None (фолбэчит на tech_rows на вызывающей стороне).
    Ключ (№17): гибрид (llm_valid DESC) → баланс (W_BAL>=0) или канон (−rel,−score).
    q0 — исходный запрос (№18.2: кириллица проверяется и по нему, qt_exp может
    потерять RU-токены при фан-ауте). top_topics — №20: bridge-гейт."""
    if not _cards_init():
        return None
    df, vec = CARDS["df"], CARDS["vec"]
    llm_arr = df["llm_valid"].to_numpy(dtype=int)
    rel_all = vec @ qv if qv is not None else np.zeros(len(df), dtype=np.float32)
    # токен-гейт: ≥1 токен запроса в name_en ИЛИ name_ru (границы слов);
    # RELAX_TOK + кириллица в запросе → требование снято (№17.5)
    has_cyr = any(re.search(r"[а-яё]", t, re.I) for t in qt) or \
        (q0 is not None and re.search(r"[а-яё]", q0, re.I) is not None)
    skip_tok = RELAX_TOK and has_cyr
    pats = {t: re.compile(r"\b" + re.escape(t) + r"\b") for t in qt}

    def _select(tau: float) -> np.ndarray:
        """полная цепочка фильтров при пороге tau (№22: гейт∪bridge∪токены)."""
        cand = CARDS["good"][rel_all[CARDS["good"]] >= tau]
        if GATE_ENABLED is False:                   # GATE всегда включён в конфигах ночи
            cand = np.nonzero(rel_all >= tau)[0]
        if LLM_GATE:                                # K2: только именованные (llm_valid==1)
            cand = cand[llm_arr[cand] == 1]
        if BRIDGE_GATE and top_topics:              # №20: только карточки с мостом в топ-15
            cand = np.asarray([i for i in cand
                               if CARDS["linked"][i] & top_topics], dtype=int)
        keep = []
        for i in cand:
            if not skip_tok:
                n_en, n_ru = CARDS["low"][i], CARDS["ru"][i]
                if not any((t in n_en and pats[t].search(n_en)) or
                           (n_ru and t in n_ru and pats[t].search(n_ru)) for t in qt):
                    continue
            keep.append(i)
        return np.asarray(keep, dtype=int)

    # №22: лестница τ — спуск до первого уровня с ≥15 кандидатами;
    # богатые запросы остаются на TAU → presence-механизм не затрагивается.
    ladder = [TAU] + [t for t in (0.80, 0.77, 0.0) if t < TAU]
    keep: np.ndarray = np.asarray([], dtype=int)
    for tau in ladder:
        keep = _select(tau)
        if len(keep) >= 15:
            break
    if len(keep) == 0:
        return []
    idx = keep
    rel = rel_all[idx]
    sc = df["score_ngi"].to_numpy(dtype=float)[idx]
    valid = llm_arr[idx]
    tier = np.where(valid > 0, 0, 1)                # гибрид: valid первым слоем
    if W_BAL >= 0:
        secondary = -((1.0 - W_BAL) * rel + W_BAL * sc)
        order = np.lexsort((secondary, tier))
    else:
        order = np.lexsort((-sc, -rel, tier))        # канон (−rel, −score)
    top = idx[order[:TOP_TECHS]]
    out: list[dict] = []
    import math

    def _f(x, d: float = 0.0) -> float:
        v = float(x)
        return v if math.isfinite(v) else d   # NaN/inf → дефолт (fix 500: JSON)

    def _s(x, d: str = "") -> str:
        return x if isinstance(x, str) else d  # NaN в str-колонках parquet → ""
    for i in top:
        r = df.iloc[int(i)]
        try:
            linked = json.loads(r["linked_json"]) if isinstance(r["linked_json"], str) else []
        except (json.JSONDecodeError, TypeError):
            linked = []
        # №22.2: мостовые tid первыми, cap=6 — топ-3 stage0 видит мост
        if top_topics:
            linked = sorted(linked, key=lambda t: 0 if t in top_topics else 1)
        topics = [{"tid": t, "name": TID2NAME.get(t, str(t)),
                   "name_ru": TOPIC_RU.get(TID2NAME.get(t, ""), "")}
                  for t in linked[:6] if t in TID2NAME]
        try:
            anchors = json.loads(r["anchors_json"]) if isinstance(r["anchors_json"], str) else []
        except (json.JSONDecodeError, TypeError):
            anchors = []
        out.append({"term": r["name_en"],
                    "term_raw": r["term"],   # стабильный id для заморож. золота (Е)
                    "term_ru": _s(r["name_ru"]) or r["name_en"],
                    "score": round(_f(r["score_ngi"]), 4),
                    "novelty": round(_f(r["novelty"]), 3),
                    "growth": round(_f(r["growth_n"]), 3),
                    "impact": round(_f(r["impact"]), 3),
                    "rel": round(_f(rel_all[i]), 3),
                    "birth": int(r["birth"]) if math.isfinite(float(r["birth"])) else 0,
                    "n_recent": int(r["n_recent"]) if math.isfinite(float(r["n_recent"])) else 0,
                    "series": {}, "topics": topics,
                    "llm_valid": int(r["llm_valid"]),
                    "problem_ru": _s(r["problem_ru"]),
                    "problem_en": _s(r["problem_en"]),
                    "anchors": anchors})
    return out

# ---------------------------------------------------------------- app
app = FastAPI(title="termtech-web", docs_url=None, redoc_url=None)


@app.get("/health")
def health():
    batch_st = ("off" if not BATCH_ENABLED else
                "ready" if BATCH["oa"] is not None else
                ("err: " + str(BATCH["err"])) if BATCH["err"] else "lazy")
    return {"status": "ok",
            "mode": "e5-small-onnx" if E5 is not None else "tfidf",
            "batch": batch_st,
            "n_topics": int(len(TOPICS)), "n_terms": int(N_TERMS),
            "mem_avail_mb": round(mem_avail_mb())}


@app.get("/api/query")
def api_query(q: str = ""):
    q = q.strip()
    if not q:
        raise HTTPException(422, "пустой q")
    t0 = time.time()
    cand, model, run = retrieve(q)
    qt = qtokens(q)
    # №14: EN-субзапросы фаноута — та лексика, которой реально искала система
    # (зеркало _query_tokens раннера: запрос + subqueries; токенизация app/STOP)
    for sq in ((run or {}).get("fanout") or {}).get("subqueries") or []:
        for t in qtokens(str(sq.get("text", ""))):
            if t not in qt:
                qt.append(t)
    # ⭐ №15-1 (объявлен ДО правок): child-e5 канал — top-300 children → доставка
    # parent'ов в пул + rel-лексика из top-30 children ВМЕСТО токенов топ-30
    # parent-имён №13 (отравление «nietzsche/philosophy» шло от parent-хабов).
    # Фолбэк: канал недоступен → прежний механизм по parent-именам (транспорт).
    delivered: list[int] = []
    lex_str = ""
    if CHILD_ENABLED and CHVEC is not None and E5 is not None:
        try:
            qv_c = e5_embed([q])[0]
            top_c = np.argsort(-(CHVEC @ qv_c))[:CHILD_TOP]
            lex_str = " ".join(CHTXT[j] for j in top_c[:CHILD_LEX]
                               if not GARBAGE_RE.search(CHTXT[j]))
            have = set(cand)
            seen_p: set[int] = set()
            for j in top_c:
                p = int(CH_PARENT[j])
                if p in seen_p:
                    continue
                seen_p.add(p)
                pos = TID2POS.get(p)
                if pos is not None and pos not in have:
                    have.add(pos)
                    delivered.append(pos)
        except Exception as e:
            log(f"child-e5 канал упал ({e}) — работаем без него")
            delivered, lex_str = [], ""
    cand = cand + delivered
    # qt_exp (№15-1): токены top-30 CHILDREN при активном канале, иначе прежнее
    # расширение по parent-именам (фолбэк); GARBAGE_RE-фильтр сохраняется (№13 ст.2)
    if lex_str:
        qt_exp = qt + [t for t in qtokens(lex_str) if t not in qt]
    else:
        qt_exp = qt + [t for t in qtokens(" ".join(
            str(TOPICS.iloc[i]["display_name"]) for i in cand[:30]
            if not GARBAGE_RE.search(str(TOPICS.iloc[i]["display_name"])))) if t not in qt]
    # окно = весь объединённый пул (№15-1): без доставки len(cand)==WIN_K — идентично №13
    topics = screen_rows(cand, qt_exp, win_k=len(cand))
    qv_t = e5_embed([q])[0] if E5 is not None else None
    techs = tech_rows_cards(qt_exp, qv_t, q0=q,
                            top_topics={int(t["tid"]) for t in topics[:15]})
    if techs is None:
        techs = tech_rows(qt_exp, qv_t)
    # ⭐ №16-1: retro-2026 блок — совпадение запрос↔пункт (τ=0.82 заморожен ДО);
    # ранжирование НЕ меняется (токены пунктов в qt/rel не входят — №16)
    retro_hits: list[dict] = []
    if RETRO_VECS is not None and E5 is not None and RETRO_ITEMS:
        try:
            sims = RETRO_VECS @ e5_embed([q])[0]
            for i in np.argsort(-sims):
                if float(sims[i]) < RETRO_TAU or len(retro_hits) >= RETRO_MAX:
                    break
                o = RETRO_ITEMS[int(i)]
                retro_hits.append({"item": o["item"], "source": o["source"],
                                   "sim": round(float(sims[i]), 3),
                                   "topics": [m["name"] for m in o["mapped"][:3]]})
        except Exception as e:
            log(f"retro-2026 канал упал ({e}) — блок пуст")
    ret: dict = {"model": model, "ms": int((time.time() - t0) * 1000)}
    if delivered:
        ret["child_delivered"] = len(delivered)
    if run is not None:
        ret["directions"] = len(cand)
        ret["fanout"] = ((run.get("fanout") or {}).get("mode"))
    elif BATCH["err"] is not None:
        ret["batch_err"] = BATCH["err"]
    return {"query": q,
            "topics": topics,
            "techs": techs,
            "retro2026": retro_hits,
            "retrieval": ret}


@app.get("/")
def index():
    return FileResponse(ROOT / "index.html")


# лёгкий self-test: python app.py --selftest
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        import urllib.request
        r = api_query("защита искусственного интеллекта")
        print("topics:", len(r["topics"]), "top3:",
              [(t["tid"], t["name"][:40], round(t["screen"], 5),
                round(t["rel"], 3)) for t in r["topics"][:3]])
        print("techs:", len(r["techs"]), "top3:",
              [(t["term"], round(t["score"], 3)) for t in r["techs"][:3]])
        print("retrieval:", r["retrieval"])
        assert r["topics"] and r["retrieval"]["model"]
        print("SELFTEST OK")
    else:
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8000)
