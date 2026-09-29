#!/usr/bin/env python3
"""Симулятор P1 — гейт релевантности в слое ранжирования N×G×I (офлайн).

Проблема: rank_directions_ngi ранжирует кандидатов ТОЛЬКО по novelty×growth×impact
и не учитывает запрос → в топ-50 вылезает быстрорастущий мусор (Education/COVID).

Варианты (все считаются локально, без API — берём birth из кэша):
  base   — текущее поведение: сортировка по screen
  gate   — отбрасываем темы без пересечения с лексикой запроса (rel == 0)
  winK   — окно ретривала: оставляем retr_rank <= K (вариант B из STATUS)
  fusion — screen × rel_norm (вариант C: релевантность как член скоринга)
  gate+fusion — комбинация

rel(тема) = (сумма IDF запросных токенов, найденных в профиле темы)
            / (сумма IDF всех запросных токенов)
Профиль темы = display_name + названия топ-100 её работ (run.json → top_works).
Запросные токены = исходный запрос + EN-фасеты фаноута (run.fanout.subqueries).
IDF считается по профилям кандидатов → «дифференцирующие» токены (частые в базе,
напр. «ai», «model», несут малый вес), тюнинга порогов НЕТ.

Метрики на каждом варианте:
  - покрытие 12 целей (любая allowed-тема в топ-50);
  - число «мусора» в топ-50 (regex Education/COVID — эвристика только для отчёта);
  - первые 15 имён для ручного просмотра.

Запуск: .venv/bin/python scripts/sim_gate.py [--window 2025] [--top 50]
Выход: results/gate_sim/report.md + report.json
"""
import argparse
import json
import math
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import rank_directions_ngi as ngi  # noqa: E402

QA_DIR = ROOT / "results/qa_regress"
ORACLE = ROOT / "results/qa_allowed_sets.json"
BIRTH_CACHE = ROOT / "results/ngi_birth_cache.json"
OUTDIR = ROOT / "results/gate_sim"

# child-темы (V1/V4, штурм 27.09): parent_tid → [profile ребёнка]
CHILDREN: dict[int, list[str]] = {}
_cp = ROOT / "webapp/data/children/children.parquet"
if _cp.exists():
    import pandas as pd
    _cht = pd.read_parquet(_cp, columns=["parent_tid", "profile"])
    for _tid, _prof in zip(_cht["parent_tid"], _cht["profile"]):
        CHILDREN.setdefault(int(_tid), []).append(str(_prof))
    del _cht

# regex «мусора» — единый источник перенесён в rank_directions_ngi (27.09);
# текст идентичен замороженному A1b (25.09). Здесь — alias для метрики отчёта.
GARBAGE_RE = ngi.GARBAGE_RE

TOKEN_RE = re.compile(r"[a-zа-яё0-9]{2,}", re.I)

# A1b итерация 2 (25.09, заявлена в NIGHT_PLAN ДО прогона): минус-лексика
# Education/COVID/Higher-Ed В ПРОФИЛЕ темы — пересчёт rel на профиле с вычёркнутой
# лексикой (влияет только на порядок fusion-вариантов; метрика мусора — GARBAGE_RE)
PROFILE_MINUS_RE = re.compile(
    r"educat\w*|e-?learning|online learning|covid[\w\s-]*|pandemics?|"
    r"higher education|university|schools?|students?|teachers?|"
    r"classrooms?|pedagog\w*|curriculums?|moocs?",
    re.I)
RU_STOP = set("""выдай темы по в защите года году и о на для от с к как при
что это эти или же не нет да все очень более самый можно нужно через про между
those these their our your which what when where while with""".split())
EN_STOP = set("""a an the and or of to in for on with from by at as is are be
been being this that these those it its our your their can could may might
will would should must not no do does did study paper analysis research
method methods using use used data results result new two three one
artificial intelligence intelligence models model based""".split())
STOP = RU_STOP | EN_STOP

CASES = ["q1_ru_canonical", "q2_ru_long", "q3_en"]


def toks(s: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(s)]


def load_case(cid: str) -> dict:
    run = json.loads((QA_DIR / f"{cid}.json").read_text())
    return run


def query_tokens(run: dict) -> list[str]:
    """Запросные токены: исходный запрос + тексты EN-фасетов фаноута."""
    qs = [run.get("query", "")]
    for sq in (run.get("fanout", {}) or {}).get("subqueries", []) or []:
        qs.append(sq.get("text", ""))
    seen, out = set(), []
    for q in qs:
        for t in toks(q):
            if t in STOP or t.isdigit() or t in seen:
                continue
            seen.add(t)
            out.append(t)
    return out


def topic_profile(run: dict, tid: int, name: str) -> str:
    tw = (run.get("top_works") or {}).get(str(tid))
    titles = tw[1] if tw and len(tw) > 1 else []
    return name + " " + " ".join(titles)


def build_rows(run: dict, cache: dict, window: int, stats=None) -> list[dict]:
    """Эквивалент main() rank_directions_ngi: screen + retr_rank + rel.
    stats=(series, impact) — предсчитанные ОДИН раз на объединение тем всех
    кейсов (урок 25.09: отдельный local_stats на кейс занимал ~1 ч из-за спилла).
    """
    cands = run["directions"]
    tids = [int(c["topic_id"]) for c in cands]
    name_of = {int(c["topic_id"]): c["display_name"] for c in cands}
    retr_rank = {int(c["topic_id"]): i + 1 for i, c in enumerate(cands)}

    series, impact = stats if stats is not None else ngi.local_stats(tids, window)
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
        if n_early == 0:
            g, growth_n = None, 1.0
        else:
            g = n_late / n_early
            growth_n = g / (g + 1.0)
        birth = births.get(tid)
        if birth is None:
            continue
        age = max(Y - birth, 0)
        nov = 1.0 - ngi.sigmoid((age - 15) / 5.0)
        imp = impact.get(tid, 0)
        imp_n = 1.0 - math.exp(-imp / 40.0)
        rows.append({"tid": tid, "name": name_of[tid], "birth": birth,
                     "screen": nov * growth_n * imp_n,
                     "retr_rank": retr_rank[tid],
                     "profile": topic_profile(run, tid, name_of[tid])})
    return rows


def add_rel(rows: list[dict], qt: list[str], key: str = "rel",
            profile_of=None) -> None:
    """rel = покрытие IDF-массы запроса профилем темы.
    key/профиль: по умолчанию как раньше (r['rel'], r['n_hit'], r['hits']);
    key='rel_mlex' + profile_of — A1b итерация 2 (профиль с минус-лексикой).
    """
    get = profile_of or (lambda r: r["profile"])
    n = len(rows)
    df = {t: 0 for t in qt}
    for r in rows:
        prof = get(r).lower()
        for t in qt:
            if t in prof:
                df[t] += 1
    idf = {t: math.log((n + 1) / (df[t] + 1)) + 1.0 for t in qt}
    total = sum(idf.values()) or 1.0
    for r in rows:
        prof = get(r).lower()
        hit = [t for t in qt if t in prof]
        val = sum(idf[t] for t in hit) / total
        if key == "rel":
            r["rel"], r["n_hit"], r["hits"] = val, len(hit), hit
        else:
            r[key], r[key + "_n_hit"] = val, len(hit)


def compute_child_rel(rows: list[dict], qt: list[str]) -> None:
    """child_rel = макс по детям IDF-покрытие qt профилем ребёнка (протокол-
    расширение 27.09, C1 childwin). idf — те же, что в add_rel по профилям
    parents; без children → child_rel=0 у всех."""
    n = len(rows)
    df = {t: 0 for t in qt}
    for r in rows:
        prof = str(r.get("profile", "")).lower()
        for t in qt:
            if t in prof:
                df[t] += 1
    idf = {t: math.log((n + 1) / (df[t] + 1)) + 1.0 for t in qt}
    total = sum(idf.values()) or 1.0
    for r in rows:
        best = 0.0
        for prof in CHILDREN.get(r["tid"], []):
            v = sum(idf[t] for t in qt if t in prof) / total
            if v > best:
                best = v
        r["child_rel"] = best


def variants(rows: list[dict]) -> dict[str, list[dict]]:
    out = {}
    out["base"] = sorted(rows, key=lambda r: -r["screen"])
    out["gate"] = sorted([r for r in rows if r["n_hit"] > 0],
                         key=lambda r: -r["screen"])
    for K in (100, 250, 400):
        # окно ретривала (вариант B): оставляем retr_rank <= K, порядок по screen
        out[f"win{K}"] = sorted([r for r in rows if r["retr_rank"] <= K],
                                key=lambda r: -r["screen"])
    maxrel = max((r["rel"] for r in rows), default=1.0) or 1.0
    for r in rows:
        r["rel_norm"] = r["rel"] / maxrel
    out["fusion"] = sorted(rows, key=lambda r: -(r["screen"] * (0.0 + r["rel_norm"])))
    gf = [r for r in rows if r["n_hit"] > 0]
    out["gate+fusion"] = sorted(gf, key=lambda r: -(r["screen"] * r["rel_norm"]))
    # --- A1b итерация 2 (25.09, заявлена в плане ДО прогона) ----------------
    # win50∩fusion (и диагностика win100∩fusion) на обоих профилях rel
    if "rel_mlex" in rows[0]:
        mx2 = max((r["rel_mlex"] for r in rows), default=1.0) or 1.0
        for r in rows:
            r["rel_mlex_norm"] = r["rel_mlex"] / mx2
    for K in (50, 100):
        w = [r for r in rows if r["retr_rank"] <= K]
        out[f"win{K}fusion"] = sorted(
            w, key=lambda r: -(r["screen"] * r["rel_norm"]))
        if w and "rel_mlex_norm" in w[0]:
            out[f"win{K}fusion_mlex"] = sorted(
                w, key=lambda r: -(r["screen"] * r["rel_mlex_norm"]))
    # --- Честный (query-относительный) фильтр мусора — прототип 27.09 ---------
    # Решение автора (а)+(б), локально (деплой НЕ делаем): имя матчит GARBAGE_RE
    # И n_hit==0 (в профиле нет ни одного токена запроса) → тема ДЕМОТИРУЕТСЯ в
    # конец win-окна (не удаляется): мусор уходит из топ-50, а покрытие целей
    # меряется честно (цель с n_hit==0 тоже может быть демотирована — увидим в отчёте).
    for K in (100, 250):
        w = [r for r in rows if r["retr_rank"] <= K]
        out[f"win{K}qgf"] = sorted(
            w, key=lambda r: (
                1 if (r["n_hit"] == 0 and GARBAGE_RE.search(r["name"])) else 0,
                -r["screen"], r["tid"]))
    # Диагностика «потолка» механики (БЕЗ выбора порога по покрытию — антиподгонка):
    # win100gfd — демот ТОЛЬКО по мусорному имени (вариант (б)-в-чистом-виде);
    # win100gr50 — мусорное имя И rel_norm<0.5 (показать, даст ли релевантность
    # хоть что-то сверх имени). Оба — для решения автора, не для прод-выдачи.
    w100 = [r for r in rows if r["retr_rank"] <= 100]
    out["win100gfd"] = sorted(
        w100, key=lambda r: (1 if GARBAGE_RE.search(r["name"]) else 0,
                             -r["screen"], r["tid"]))
    out["win100gr50"] = sorted(
        w100, key=lambda r: (
            1 if (GARBAGE_RE.search(r["name"]) and r["rel_norm"] < 0.5) else 0,
            -r["screen"], r["tid"]))
    # --- ПРОТОКОЛ 27.09 (RANK_PROTOCOL_20260927.md, зафиксирован ДО прогона) ----
    # V2 = win400 × fusion: окно 400 впускает цели на ретривал-позициях 170–470,
    #     сортировка screen×rel_norm поднимает rel-богатые узкие темы;
    # V3 = win400 × fusion × gr50: всё вместе (демот имя ∧ rel_norm<0.5 → хвост).
    def _gr50(r):
        return 1 if (GARBAGE_RE.search(r["name"]) and r["rel_norm"] < 0.5) else 0
    w400 = [r for r in rows if r["retr_rank"] <= 400]
    out["win400fusion"] = sorted(
        w400, key=lambda r: -(r["screen"] * r["rel_norm"]))
    out["win400fusion_gr50"] = sorted(
        w400, key=lambda r: (_gr50(r), -(r["screen"] * r["rel_norm"])))
    # C1 childwin (РАСШИРЕНИЕ протокола 27.09 09:35, ДО прогона): в окно — только
    # parent'ы с child_rel ≥ 0.1 (τ из D1a), порядок screen × child_rel (raw).
    if rows and "child_rel" in rows[0]:
        cw = [r for r in rows if r["child_rel"] >= 0.1]
        out["childwin"] = sorted(
            cw, key=lambda r: -(r["screen"] * r["child_rel"]))
    # D1 childall — ADDENDUM №2 (ДО прогона, согласовано): окно = ВСЕ
    # кандидаты, БЕЗ порога, порядок screen × child_rel (raw), tie-break tid.
    if rows and "child_rel" in rows[0]:
        out["childall"] = sorted(
            rows, key=lambda r: (-(r["screen"] * r["child_rel"]), r["tid"]))
    # D2 childall_gr50 — ADDENDUM №3 (ДО прогона, согласовано):
    # D1-порядок + gr50-демот (имя ∧ rel_norm<0.5 → хвост, не удаляя).
    if rows and "child_rel" in rows[0]:
        out["childall_gr50"] = sorted(
            rows, key=lambda r: (_gr50(r),
                                 -(r["screen"] * r["child_rel"]), r["tid"]))
    return out


def evaluate(top: list[dict], allowed: dict, topn: int, bonus: set | None = None) -> dict:
    """allowed: {tech: set(topic_ids)} — 12 целей.
    A1b-фикс метрики (25.09): allowed-цель НЕ может быть «мусором» — ложные
    срабатывания regex на целевых темах (T10883 Ethics «social impacts»)
    исключаются из счётчика. RE не менялся (заморожен).
    """
    ids = [r["tid"] for r in top[:topn]]
    idset = set(ids)
    cov = {tech: sorted(idset & tids) for tech, tids in allowed.items()}
    covered = sum(1 for v in cov.values() if v)
    good = set().union(*allowed.values()) | (bonus or set())
    garbage = [r for r in top[:topn]
               if r["tid"] not in good and GARBAGE_RE.search(r["name"])]
    return {"covered": covered, "total": len(allowed),
            "missing": [t for t, v in cov.items() if not v],
            "garbage_n": len(garbage),
            "garbage": [f"T{r['tid']} {r['name']}" for r in garbage]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=2025)
    ap.add_argument("--top", type=int, default=50)
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    cache = json.loads(BIRTH_CACHE.read_text())
    oracle = json.loads(ORACLE.read_text())
    allowed = {}
    for t in oracle["targets"]:
        key = f"#{t['n']} {t['tech']}"
        allowed[key] = {int(x) for x in t.get("allowed", [])}
    bonus_ids = {int(x) for t in (oracle.get("bonus") or [])
                 for x in (t.get("allowed") or [])}

    report = {"window": args.window, "top": args.top, "cases": {}}
    # --- ОДИН local_stats на объединение ВСЕХ кейсов (память: NGI_MEM) ---
    runs = {cid: load_case(cid) for cid in CASES}
    all_tids = sorted({int(c["topic_id"]) for r in runs.values()
                       for c in r["directions"]})
    print(f"local_stats: объединение {len(all_tids)} тем (один прогон) ...",
          flush=True)
    t0 = time.time()
    stats = ngi.local_stats(all_tids, args.window)
    print(f"local_stats готов за {time.time()-t0:.0f} с", flush=True)
    lines = ["# Симуляция гейта релевантности (P1)", "",
             f"Окно Y={args.window}, топ-{args.top}. rel = IDF-покрытие лексики "
             f"запроса профилем темы (имя + топ-100 работ).", ""]

    for cid in CASES:
        run = runs[cid]
        rows = build_rows(run, cache, args.window, stats)
        qt = query_tokens(run)
        add_rel(rows, qt)
        compute_child_rel(rows, qt)
        # A1b итерация 2: rel на профиле с минус-лексикой Education/COVID/Higher-Ed
        add_rel(rows, qt, key="rel_mlex",
                profile_of=lambda r: PROFILE_MINUS_RE.sub(" ", r["profile"]))
        vs = variants(rows)
        print(f"\n=== {cid}: {len(run['directions'])} кандидатов → "
              f"{len(rows)} скоренных, запросных токенов {len(qt)} ===",
              flush=True)
        print("  токены запроса:", ", ".join(qt[:20]))
        case_rep = {"query": run["query"], "n_cand": len(run["directions"]),
                    "n_scored": len(rows), "qtokens": qt, "variants": {}}
        lines += [f"## {cid}", "", f"Запрос: {run['query']}", "",
                  "| вариант | покрытие | мусор в топ-50 |", "|---|---|---|"]
        for vname, lst in vs.items():
            ev = evaluate(lst, allowed, args.top, bonus_ids)
            case_rep["variants"][vname] = ev
            print(f"  {vname:<12} покрытие {ev['covered']}/{ev['total']} "
                  f"мусор {ev['garbage_n']}  missing={len(ev['missing'])}",
                  flush=True)
            lines.append(f"| {vname} | {ev['covered']}/{ev['total']} "
                         f"{'✅' if ev['covered'] >= 12 else '❌'} | {ev['garbage_n']} |")
        # детали для базового и лучшего варианта
        lines += ["", "### Топ-15 (base)", ""]
        for i, r in enumerate(vs["base"][:15], 1):
            lines.append(f"{i}. T{r['tid']} {r['name']} — screen={r['screen']:.4f}, "
                         f"rel={r['rel']:.3f}, retr_rank={r['retr_rank']}")
        best = max(vs.items(),
                   key=lambda kv: (evaluate(kv[1], allowed, args.top, bonus_ids)["covered"],
                                   -evaluate(kv[1], allowed, args.top, bonus_ids)["garbage_n"]))
        lines += ["", f"### Топ-15 ({best[0]})", ""]
        for i, r in enumerate(best[1][:15], 1):
            lines.append(f"{i}. T{r['tid']} {r['name']} — screen={r['screen']:.4f}, "
                         f"rel={r['rel']:.3f}, retr_rank={r['retr_rank']}")
        lines.append("")
        report["cases"][cid] = case_rep

    (OUTDIR / "report.md").write_text("\n".join(lines) + "\n")
    (OUTDIR / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1))
    print(f"\nВыход: {OUTDIR}/report.md, report.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
