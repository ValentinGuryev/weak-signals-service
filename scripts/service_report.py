#!/usr/bin/env python3
"""Пилотный сервис v0: запрос → ТЕМЫ (T1) + ТЕХНОЛОГИИ (T2) → отчёт.

Состав пайплайна (всё локальное, без платных API):
  1. Ретривал   — scripts/oa_run_query.py (--route --fanout) → run.json,
                  либо берётся готовый --run (qa-прогоны).
  2. Темы T1    — N×G×I (scripts/rank_directions_ngi.py) + ГЕЙТ РЕЛЕВАНТНОСТИ
                  (P1: IDF-покрытие лексики запроса профилем темы — см. sim_gate).
  3. Технологии T2 — TermTech: срез работ тем запроса (termtech_sp_slice --topics)
                  → мининг n-грамм (termtech_mine --slice/--out)
                  → отбраковка мусора (termtech_filter) → релевантность к запросу.
                  Кэш: data/openalex_derived/slice_<slug> + results/termtech_<slug>.
  4. Отчёт      — results/service/<slug>/{report.md, report.json}:
                  для каждой технологии: динамика (first_year, growth, серия df),
                  кейс-пример (наиболее цитируемая работа с термином),
                  источник (OpenAlex URL).

Использование:
  .venv/bin/python scripts/service_report.py --query "..." [--run run.json]
      [--gate] [--top 15] [--tech 15] [--slug ai_protect] [--years 2016 2026]

Коды возврата: 0 — отчёт собран (возможны предупреждения), 1 — этап критически
упал (нет ретривала / нет данных). Предупреждения пишутся в отчёт явно
(правило §9: silent fallback запрещён).
"""
import argparse
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import rank_directions_ngi as ngi   # noqa: E402
import sim_gate as sg               # noqa: E402

OUT_ROOT = ROOT / "results/service"
SLICE_ROOT = ROOT / "data/openalex_derived"
TERM_ROOT = ROOT / "results"
BIRTH_CACHE = ROOT / "results/ngi_birth_cache.json"
ORACLE = ROOT / "results/qa_allowed_sets.json"
T_STATS_GLOB = str(ROOT / "data/openalex_derived/T_stats/year=*/*/*.parquet")
T_STATS_E = "/mnt/e/openalex_derived"   # для spill минга (E:/tmp_duck)


def log(m: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def slugify(q: str) -> str:
    s = re.sub(r"[^a-zа-яё0-9]+", "_", q.lower(), flags=re.I).strip("_")
    return s[:40] or "query"


# ---------------------------------------------------------------- 1. ретривал
def get_run(args) -> tuple[dict, str]:
    """Готовый run.json либо новый прогон через oa_run_query."""
    if args.run:
        return json.loads(Path(args.run).read_text()), f"run={args.run}"
    outdir = OUT_ROOT / args.slug
    outdir.mkdir(parents=True, exist_ok=True)
    run_path = outdir / "run.json"
    cmd = [sys.executable, str(ROOT / "scripts/oa_run_query.py"),
           "--query", args.query,
           "--local", str(ROOT / "data/openalex_derived"),
           "--e", "/mnt/e/openalex_derived",
           "--route", "--fanout", "--json", str(run_path)]
    if args.years:
        cmd += ["--years", str(args.years[0]), str(args.years[1])]
    log("ретривал: " + " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not run_path.exists():
        log(f"ОШИБКА ретривала: {(r.stderr or r.stdout)[-800:]}")
        return {}, "failed"
    return json.loads(run_path.read_text()), f"run={run_path}"


# ---------------------------------------------------------------- 2. темы T1
def topic_rows(run: dict, window: int) -> list[dict]:
    cands = run["directions"]
    tids = [int(c["topic_id"]) for c in cands]
    name_of = {int(c["topic_id"]): c["display_name"] for c in cands}
    retr = {int(c["topic_id"]): i + 1 for i, c in enumerate(cands)}
    cache = json.loads(BIRTH_CACHE.read_text()) if BIRTH_CACHE.exists() else {}
    series, impact = ngi.local_stats(tids, window)
    births = {t: ngi.birth_from_histogram(cache.get(str(t), {}), window)
              for t in tids}
    Y = window
    rows = []
    for tid in tids:
        s = series.get(tid, {})
        n_late = sum(s.get(y, 0) for y in (Y - 2, Y - 1, Y))
        n_early = sum(s.get(y, 0) for y in (Y - 4, Y - 3))
        if n_late == 0 and n_early == 0:
            continue
        growth_n = 1.0 if n_early == 0 else (n_late / n_early) / (n_late / n_early + 1)
        birth = births.get(tid)
        if birth is None:
            continue
        nov = 1.0 - ngi.sigmoid((max(Y - birth, 0) - 15) / 5.0)
        imp = impact.get(tid, 0)
        imp_n = 1.0 - math.exp(-imp / 40.0)
        rows.append({"tid": tid, "name": name_of[tid], "birth": birth,
                     "screen": nov * growth_n * imp_n,
                     "retr_rank": retr[tid],
                     "profile": sg.topic_profile(run, tid, name_of[tid])})
    return rows


def topic_stage(run: dict, window: int, relevance: str, top: int) -> tuple[list, dict]:
    rows = topic_rows(run, window)
    if not rows:
        return [], {"warn": "нет скоренных тем (пустой ретривал или нет birth)"}
    qt = sg.query_tokens(run)
    sg.add_rel(rows, qt)
    if relevance == "gate":
        dropped = [r for r in rows if r["n_hit"] == 0]
        rows = [r for r in rows if r["n_hit"] > 0]
        log(f"гейт: отброшено {len(dropped)} тем без пересечения с лексикой запроса")
    elif relevance == "win":
        # A2b (25.09): win100 — окно ретривала retr_rank≤100 (победитель sim_gate
        # 25.09), порядок по screen; NGI-screen НЕ участвует в фильтрации
        before = len(rows)
        rows = [r for r in rows if r["retr_rank"] <= 100]
        log(f"win100: {before} → {len(rows)} кандидатов (retr_rank ≤ 100)")
    rows.sort(key=lambda r: -r["screen"])
    telem = {"n_scored": len(rows), "relevance": relevance,
             "gate": relevance == "gate",
             "query_tokens": qt[:30]}
    return rows[:top], telem


# ------------------------------------------------------- 3. технологии T2
def load_term_data(slug: str):
    """Читает кэш TermTech для набора тем; None, если среза/мина ещё нет."""
    tdir = TERM_ROOT / f"termtech_{slug}"
    sdir = SLICE_ROOT / f"slice_{slug}"
    if not (tdir / "candidates_clean.parquet").exists():
        return None, None, None
    import pandas as pd
    cand = pd.read_parquet(tdir / "candidates_clean.parquet")
    yeardir = tdir / "_yeardf"
    return cand, (sdir if sdir.exists() else None), yeardir


def term_relevance(cand, run: dict, qt: list[str], window: int):
    """rel-термина: токенное пересечение с лексикой запроса (IDF-доля)."""
    import pandas as pd
    if not qt:
        return cand.assign(rel=0.0)
    sub = cand[cand["df"] >= 20].copy()
    # IDF считаем по самим терминам среза (стандартная коллокационная мера)
    n = max(len(sub), 1)
    df_map = {}
    for t in qt:
        df_map[t] = int(sub["term"].str.contains(rf"\b{re.escape(t)}\b",
                                                 regex=True).sum())
    idf = {t: math.log((n + 1) / (df_map[t] + 1)) + 1.0 for t in qt}
    total = sum(idf.values()) or 1.0

    def rel(term: str) -> float:
        tl = term.lower()
        return sum(idf[t] for t in qt if re.search(rf"\b{re.escape(t)}\b", tl)) / total

    sub["rel"] = sub["term"].map(rel)
    return sub


def term_series(yeardir: Path, terms: list[str]) -> dict:
    """Серия df по годам для короткого списка терминов (DuckDB IN)."""
    import duckdb
    parts = sorted(yeardir.glob("year=*.parquet"))
    if not parts:
        return {}
    glob_sql = ", ".join(f"'{p}'" for p in parts)
    vals = ", ".join("'" + t.replace("'", "''") + "'" for t in terms)
    con = duckdb.connect(config={"memory_limit": "1GB"})
    try:
        df = con.execute(f"""
            SELECT term, year, sum(df) AS df FROM read_parquet([{glob_sql}])
            WHERE term IN ({vals}) GROUP BY 1, 2 ORDER BY 1, 2
        """).fetchdf()
    finally:
        con.close()
    out: dict = {}
    for t, g in df.groupby("term"):
        out[t] = {int(r.year): int(r.df) for r in g.itertuples()}
    return out


def term_sources(slice_dir: Path, terms: list[str], top_n: int = 3) -> dict:
    """Кейс-пример: наиболее цитируемые работы, где встречается термин."""
    import duckdb
    if slice_dir is None:
        return {}
    parts = sorted(slice_dir.glob("year=*.parquet"))
    if not parts:
        return {}
    glob_sql = ", ".join(f"'{p}'" for p in parts)
    out = {}
    con = duckdb.connect(config={"memory_limit": "1.5GB",
                                 "temp_directory": str(T_STATS_E) + "/tmp_duck"})
    try:
        for t in terms:
            pat = f"%{t}%"
            try:
                rows = con.execute(f"""
                    WITH s AS (
                      SELECT id, publication_year, title,
                             coalesce(title,'') || ' ' || coalesce(abstract,'') AS txt
                      FROM read_parquet([{glob_sql}])
                      WHERE lower(coalesce(title,'') || ' ' || coalesce(abstract,''))
                            LIKE lower('%' || ? || '%')
                    )
                    SELECT s.publication_year, s.title, s.id, w.cited_by_count
                    FROM s LEFT JOIN read_parquet('{T_STATS_GLOB}') w ON w.id = s.id
                    ORDER BY coalesce(w.cited_by_count, 0) DESC NULLS LAST
                    LIMIT ?
                """, [t, top_n]).fetchall()
                out[t] = [{"year": r[0], "title": r[1],
                           "url": "https://openalex.org/" + str(r[2]).split("/")[-1],
                           "cited_by": int(r[3] or 0)} for r in rows]
            except Exception as e:  # noqa: BLE001
                out[t] = [{"error": str(e)[:200]}]
    finally:
        con.close()
    return out


def tech_stage(run: dict, slug: str, qt: list[str], top: int, window: int) -> tuple[list, dict]:
    cand, slice_dir, yeardir = load_term_data(slug)
    if cand is None:
        return [], {"error": f"кэш TermTech для '{slug}' не найден — запустите "
                             f"termtech_sp_slice --topics ... --out slice_{slug}, "
                             f"затем termtech_mine --slice ... --out termtech_{slug} "
                             f"и termtech_filter"}
    sub = term_relevance(cand, run, qt, window)
    emerging = sub[(sub["first_year"].fillna(9999) >= 2018)
                   & (sub["n_recent"] >= 5)].copy()
    # отбор: релевантные запросу (rel>0) вперёди, затем по growth
    rel_pos = emerging[emerging["rel"] > 0].sort_values(
        ["rel", "growth"], ascending=[False, False])
    order = list(rel_pos["term"])
    if len(order) < top:
        rest = emerging[~emerging["term"].isin(order)].sort_values(
            "growth", ascending=False)
        order += list(rest["term"])[: top - len(order)]
    short = order[:top]
    import pandas as pd
    sel = sub[sub["term"].isin(short)].copy()
    order = {t: i for i, t in enumerate(short)}
    sel["_o"] = sel["term"].map(order)
    sel = sel.sort_values("_o")
    series = term_series(yeardir, short) if yeardir else {}
    sources = term_sources(slice_dir, short) if slice_dir else {}
    items = []
    for r in sel.itertuples():
        items.append({
            "term": r.term, "df": int(r.df),
            "first_year": None if pd.isna(r.first_year) else int(r.first_year),
            "growth": round(float(r.growth), 2),
            "kpmi": None if pd.isna(r.kpmi) else round(float(r.kpmi), 3),
            "rel": round(float(r.rel), 4),
            "series": series.get(r.term, {}),
            "cases": sources.get(r.term, []),
        })
    telem = {"n_candidates": int(len(cand)), "n_emerging": int(len(emerging)),
             "n_rel": int((emerging["rel"] > 0).sum())}
    return items, telem


# ---------------------------------------------------------------- 4. отчёт
def render(slug: str, query: str, topics: list, techs: list,
           telem_t: dict, telem_h: dict, meta: dict) -> str:
    L = [f"# Отчёт сервиса — «{query}»", "",
         f"Слуг: `{slug}`; окно тем {meta.get('window')}; "
         f"этапы: {meta.get('stages')}", ""]
    L += ["## 1. Зарождающиеся технологии (T2, TermTech)", "",
          "| # | технология | df | с какого года | growth | релев. | "
          "серия df (годы) | кейс-пример (топ по цитатам) |",
          "|---|---|---|---|---|---|---|---|"]
    for i, t in enumerate(techs, 1):
        ser = ",".join(f"{y}:{v}" for y, v in sorted(t["series"].items()))
        case = ""
        if t["cases"] and "error" not in t["cases"][0]:
            c = t["cases"][0]
            case = f"{c['year']} «{c['title'][:80]}» ({c['cited_by']} цит., {c['url']})"
        elif t["cases"]:
            case = "⚠️ " + t["cases"][0].get("error", "")[:60]
        fy = t["first_year"] if t["first_year"] is not None else "-"
        L.append(f"| {i} | **{t['term']}** | {t['df']} | {fy} | {t['growth']} | "
                 f"{t['rel']} | {ser} | {case} |")
    if not techs:
        L += ["", "⚠️ технологии не получены: " + json.dumps(telem_h, ensure_ascii=False)[:300]]
    gate_note = {"gate": " + гейт релевантности",
                 "win": " + окно релевантности win100"}.get(
                     telem_t.get("relevance"), "")
    L += ["", f"## 2. Темы контекста (T1, N×G×I{gate_note})", "",
          "| # | тема | screen | birth | релев. |", "|---|---|---|---|---|"]
    for i, r in enumerate(topics, 1):
        L.append(f"| {i} | T{r['tid']} {r['name']} | {r['screen']:.4f} | "
                 f"{r['birth']} | {r['rel']:.3f} |")
    L += ["", "## Телеметрия", "",
          "```json", json.dumps({"topics": telem_t, "tech": telem_h, "meta": meta},
                                ensure_ascii=False, indent=1), "```"]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--run", default=None, help="готовый run.json (без ретривала)")
    ap.add_argument("--slug", default=None)
    ap.add_argument("--years", nargs=2, type=int, default=None)
    ap.add_argument("--window", type=int, default=2025)
    ap.add_argument("--top", type=int, default=15, help="тем в отчёте")
    ap.add_argument("--tech", type=int, default=15, help="технологий в отчёте")
    ap.add_argument("--relevance", choices=["none", "gate", "win"], default="win",
                    help="P1/A2b (25.09): win — окно ретривала win100 (дефолт, "
                         "победитель sim_gate 25.09); gate — прежний гейт; none")
    ap.add_argument("--gate", action="store_true",
                    help="упрощённый алиас --relevance=gate (обратная совместимость)")
    ap.add_argument("--no-retrieve", action="store_true",
                    help="не запускать ретривал, --run обязателен")
    args = ap.parse_args()
    args.slug = args.slug or slugify(args.query)
    if args.gate:
        args.relevance = "gate"

    outdir = OUT_ROOT / args.slug
    outdir.mkdir(parents=True, exist_ok=True)
    stages = []

    run, meta_run = get_run(args)
    if not run:
        log("КРИТИЧНО: нет ретривала — отчёт не собрать")
        return 1
    stages.append(meta_run)
    qt = sg.query_tokens(run)

    topics, telem_t = topic_stage(run, args.window, args.relevance, args.top)
    stages.append("topics(relevance=%s)" % args.relevance)
    log(f"тем: {len(topics)} (телеметрия: {json.dumps({k: v for k, v in telem_t.items() if k != 'query_tokens'}, ensure_ascii=False)})")

    techs, telem_h = tech_stage(run, args.slug, qt, args.tech, args.window)
    stages.append("tech(%s)" % ("ok" if techs else "нет кэша"))
    log(f"технологий: {len(techs)}")

    meta = {"window": args.window, "stages": stages, "query": args.query,
            "slug": args.slug, "relevance": args.relevance,
            "gate": args.relevance == "gate"}
    md = render(args.slug, args.query, topics, techs, telem_t, telem_h, meta)
    (outdir / "report.md").write_text(md)
    (outdir / "report.json").write_text(json.dumps(
        {"query": args.query, "slug": args.slug, "topics": topics,
         "techs": techs, "telem": {"topics": telem_t, "tech": telem_h},
         "meta": meta}, ensure_ascii=False, indent=1, default=str))
    log(f"отчёт: {outdir}/report.md (+.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
