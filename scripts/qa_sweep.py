#!/usr/bin/env python3
"""QA-sweep: параметрический тюнинг выдачи (--topics/--topk, match) ДО шагов И5/И1.

Зачем: покрытие оракула монотонно растёт с --topics (больше кандидатов в embedding-top-N),
а --topk < topics обрезает кандидатов невидимым фильтром ORDER BY n_works LIMIT topk
(фикс аудита A.5). Свип мерит оба эффекта на всех 4 кейсах q1-q4.

Состав:
  1) Ранговая диагностика: позиции 18 allowed-тем в порядке косинуса (с учётом mega-маски)
     для 3 формулировок → «потолок покрытия» при каждом --topics (цель покрывается, ЕСЛИ
     ЛЮБАЯ из её allowed-тем вошла в top-N кандидатов).
  2) Свип конфигураций: match × topics × topk на q1-q4 (qa_protect_score v2, тема по topic_id).
  3) precision: q4 «Квантовые сенсоры» — покрытие «Защиты ИИ» ≤2/16 (§7.10).

Все прогоны логируются БЕЗ выбора лучших: results/qa_sweep/<cfg>__<case>.json{,.score.json}
+ results/qa_sweep_summary.json.

Использование:
  .venv/bin/python scripts/qa_sweep.py            # полный свип (~15 мин)
  .venv/bin/python scripts/qa_sweep.py --ranks    # только ранговая диагностика (~1 мин)
  .venv/bin/python scripts/qa_sweep.py --gate 3,2 # И5: доменный гейт вместо regex-маски
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import oa_snapshot as oa  # noqa: E402

LOCAL = ROOT / "data/openalex_derived"
E = Path("/mnt/e/openalex_derived")
OUTDIR = ROOT / "results/qa_sweep"
SCORE = ROOT / "scripts/qa_protect_score.py"
ORACLE = ROOT / "results/qa_allowed_sets.json"
PRECISION_MAX = 2

# --- кейсы (как в qa_regress: окно QA = 2026) ---
CASES = [
    {"id": "q1_ru_canonical", "qa": True,
     "query": "Выдай темы по защите ИИ в 2026 году", "years": (2026, 2026)},
    {"id": "q2_ru_long", "qa": True,
     "query": "Безопасность искусственного интеллекта: защита языковых моделей от атак "
              "и инъекций промптов, приватность данных, регулирование и надёжность ИИ-систем",
     "years": (2026, 2026)},
    {"id": "q3_en", "qa": True,
     "query": "AI security and safety: protecting language models from attacks, prompt "
              "injection defense, privacy-preserving AI, AI governance and regulation, "
              "reliable trustworthy AI",
     "years": (2026, 2026)},
    {"id": "q4_offtopic_quant_sensors", "qa": True, "precision": True,
     "query": "Квантовые сенсоры и квантовая метрология", "years": (2026, 2026)},
]

# --- сет конфигураций: (match, topics, topk) ---
# topk == topics => невидимого фильтра нет (все кандидаты с работами в окне в выдаче);
# emb_t600k50 — контроль урона A.5 (topk=50 при 600 кандидатах).
CONFIGS = [
    ("embed", 60, 50),      # baseline (прогон 1 / регресс)
    ("embed", 60, 60),
    ("embed", 150, 150),
    ("embed", 300, 300),
    ("embed", 600, 600),
    ("embed", 600, 50),     # A.5: сколько теряется фильтром
    ("embed", 500, 500),
    ("embed", 1200, 1200),
    ("tfidf", 300, 300),    # лексический канал (предвестник И3)
    ("tfidf", 600, 600),
]


def cfg_name(match, topics, topk, gate=None, fanout=False):
    base = f"{match[:3]}_t{topics}k{topk}"
    if gate:
        base += "_g" + "".join(str(d) for d in gate)
    if fanout:
        base += "_fo"
    return base


# ---------------------------------------------------------------- ранговая диагностика

def rank_diag(con, P, queries: list, gate=None) -> dict:
    """Позиции allowed-тем в порядке косинуса (embed, с mega-маской и без)."""
    import numpy as np
    tax = P.taxonomy()
    topics = con.execute(f"""
      SELECT id, display_name, coalesce(description,'') AS descr, keywords, domain_id
      FROM read_parquet('{tax}/topics.parquet')""").df()
    if gate is not None:
        dom_num = topics["domain_id"].str.extract(r"domains/(\d+)")[0]
        mega = (~dom_num.isin([str(d) for d in gate]) | dom_num.isna()).to_numpy()
    else:
        mega = topics["display_name"].str.contains(
        "Linguistic, Cultural|Legal and Regulatory|Military Technology|Electrical and Electromagnetic"
        "|Social Sciences and Policies|Diverse Approaches|Educational Systems|Healthcare and Education"
        "|Medicine and Dentistry|General |Interdisciplinary|Multidisciplinary", regex=True, na=False).to_numpy()
    vecs = np.load(tax / "topic_vectors.npy")
    vids = (tax / "topic_ids.txt").read_text().split("\n")
    import re
    vid_num = np.array([int(re.search(r"(\d+)$", v).group(1)) for v in vids])
    pos = topics["id"].map({v: i for i, v in enumerate(vids)}).to_numpy()

    oracle = json.loads(ORACLE.read_text())
    targets = {int(t["n"]): t for t in oracle["targets"]}
    allowed = sorted({tid for t in targets.values() for tid in t["allowed"]})

    model = oa._get_embedder()
    out = {}
    for q in queries:
        qv = model.encode([q], normalize_embeddings=True, show_progress_bar=False)[0]
        sim_masked = np.where(mega, -1.0, vecs[pos] @ qv)
        order = np.argsort(-sim_masked)                      # позиции после маски
        rank_of = {}
        for tid in allowed:
            idxs = np.where(vid_num[pos[order]] == tid)[0]
            rank_of[str(tid)] = int(idxs[0]) if len(idxs) else None
        # потолок покрытия: цель покрыта, если ЛЮБАЯ её allowed-тема имеет rank < topics
        ceilings = {}
        for n, t in targets.items():
            rs = [rank_of[str(a)] for a in t["allowed"] if rank_of.get(str(a)) is not None]
            ceilings[str(n)] = min(rs) if rs else None      # лучшая позиция среди allowed
        present = [r for r in ceilings.values() if r is not None]
        grid = {}
        for T in (60, 150, 300, 600, 1200, 4516):
            grid[str(T)] = sum(1 for r in present if r < T)
        out[q] = {
            "allowed_ranks": rank_of,
            "target_best_rank": ceilings,
            "ceiling_by_topics": grid,     # сколько из 12 целей ВХОДИТ в top-T кандидатов
            "n_mega_masked": int(mega.sum()),
        }
        print(f"  потолок (из 12) по --topics: " +
              "  ".join(f"T={k}: {v}" for k, v in grid.items()))
    return out


# ---------------------------------------------------------------- свип

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranks", action="store_true", help="только ранговая диагностика")
    ap.add_argument("--configs", help="подмножество конфигов через запятую (имена emb_t300k300,...)")
    ap.add_argument("--gate", default=None,
                    help="И5: доменный гейт через запятую (напр. 3,2); без флага — legacy regex-маска")
    ap.add_argument("--fanout", action="store_true",
                    help="И1 стратегия A: кластеризация top-M + RRF (замороженный конфиг 16:05)")
    ap.add_argument("--fanout-source", choices=["cluster", "lexicon"], default="cluster",
                    help="источник подзапросов фан-аута: cluster (A) | lexicon (C, замороженный)")
    ap.add_argument("--route", action="store_true",
                    help="§4а: лексический routing → matched(gate+C+t500)/fallback(legacy t60k50)")
    ap.add_argument("--embed-variant", choices=["base", "i2"], default="base",
                    help="вектора matched-профиля: base | i2 (И2 data-driven aliases, шаг 5)")
    args = ap.parse_args()
    gate = [int(x) for x in args.gate.split(",")] if args.gate else None
    fanout_cfg = ({"m": 240, "k": 12, "ktop": 25, "rrf_c": 60, "seed": 42,
                   "source": args.fanout_source,
                   "lexicon_path": str(ROOT / "results/qa_facet_lexicon_v1.json")}
                  if args.fanout else None)
    routing_cfg = {"profiles": {
        "matched": {"gate": [3, 2], "topics": 500, "topk": 500,
                    "vectors": ("topic_vectors_i2.npy" if args.embed_variant == "i2" else None),
                    "fanout": {"m": 240, "k": 12, "ktop": 25, "rrf_c": 60, "seed": 42,
                               "source": "lexicon",
                               "lexicon_path": str(ROOT / "results/qa_facet_lexicon_v1.json")}},
        "fallback": {"gate": None, "topics": 60, "topk": 50, "fanout": None}}} if args.route else None

    OUTDIR.mkdir(parents=True, exist_ok=True)
    P = oa.Paths(local=LOCAL, e=E, staging=Path("/mnt/c/oa_tmp"))
    (E / "tmp_duck").mkdir(parents=True, exist_ok=True)
    import duckdb
    con = duckdb.connect()
    con.execute("SET threads=4; SET memory_limit='2GB'")
    con.execute(f"SET temp_directory='{E}/tmp_duck'")

    summary = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "runs": []}
    t0 = time.time()

    print("=== ранговая диагностика (embed, " + (f"domain-gate {gate}" if gate else "mega-маска") + ") ===")
    summary["gate"] = gate
    summary["fanout"] = fanout_cfg
    summary["routing"] = bool(routing_cfg)
    summary["rank_diag"] = rank_diag(con, P, [c["query"] for c in CASES if c["qa"] and "precision" not in c], gate=gate)
    if args.ranks:
        (ROOT / "results/qa_sweep_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=1))
        print("only-ranks: summary записан")
        return 0

    configs = CONFIGS
    if args.configs:
        want = set(args.configs.split(","))
        configs = [c for c in CONFIGS if cfg_name(*c) in want]

    for match, topics, topk in configs:
        cname = cfg_name(match, topics, topk, gate, bool(fanout_cfg))
        if routing_cfg:
            cname += "_rt"
            if args.embed_variant == "i2":
                cname += "_i2"
        for c in CASES:
            t1 = time.time()
            print(f"\n=== {cname} / {c['id']}: «{c['query'][:60]}» ===")
            res = oa.query_directions(con, P, c["query"], topk=topk, n_topics=topics,
                                      match=match, years=c["years"], gate_domains=gate,
                                      fanout=fanout_cfg, routing=routing_cfg)
            if routing_cfg:
                _p = routing_cfg["profiles"][res["routing"]["profile"]]
                topk, topics = _p["topk"], _p["topics"]
            run_path = OUTDIR / f"{cname}__{c['id']}.json"
            run_path.write_text(json.dumps(res, ensure_ascii=False, indent=1))
            row = {"cfg": cname, "match": match, "topics": topics, "topk": topk,
                   "case": c["id"], "query": c["query"],
                   "routing": (res.get("routing") or {}).get("profile"),
                   "run": str(run_path.relative_to(ROOT)),
                   "n_directions": len(res["directions"]),
                   "sec": round(time.time() - t1, 1)}
            if c.get("qa"):
                r = subprocess.run([sys.executable, str(SCORE), "--run", str(run_path)],
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    raise RuntimeError(f"скорер упал: {r.stderr[-400:]}")
                sc = json.loads(run_path.with_suffix(".score.json").read_text())
                row.update({"covered": sc["covered"], "tier_A": sc["tier_A"],
                            "tier_B": sc["tier_B"], "pass": sc["pass"]})
                if c.get("precision"):
                    row["precision_ok"] = sc["covered"] <= PRECISION_MAX
                print(f"  -> {sc['covered']}/16 (A {sc['tier_A']} B {sc['tier_B']}) "
                      f"{'PASS✅' if sc['pass'] else 'fail'} | {row['sec']}с | выдано {row['n_directions']}")
            summary["runs"].append(row)
            # инкрементальный сброс (падение не теряет прогон)
            summary["total_sec"] = round(time.time() - t0, 1)
            summary["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
            (ROOT / "results/qa_sweep_summary.json").write_text(
                json.dumps(summary, ensure_ascii=False, indent=1))

    # --- итоговая таблица ---
    print("\n" + "=" * 96)
    print(f"{'config':<14} {'q1':>6} {'q2':>6} {'q3':>6} {'min(q1-3)':>9} {'q4prec':>7} {'статус'}")
    by_cfg: dict = {}
    for r in summary["runs"]:
        by_cfg.setdefault(r["cfg"], {})[r["case"]] = r
    for cname, rows in by_cfg.items():
        q = [rows[c]["covered"] for c in ("q1_ru_canonical", "q2_ru_long", "q3_en")
             if c in rows]
        prec = rows.get("q4_offtopic_quant_sensors", {})
        p_ok = prec.get("precision_ok", False)
        mn = min(q) if q else -1
        flag = "PREC_OK✅" if p_ok else "PREC_FAIL❌"
        print(f"{cname:<14} {rows.get('q1_ru_canonical',{}).get('covered','-'):>6} "
              f"{rows.get('q2_ru_long',{}).get('covered','-'):>6} "
              f"{rows.get('q3_en',{}).get('covered','-'):>6} {mn:>9} "
              f"{prec.get('covered','-'):>4}/16 {flag}")
    print(f"\n{summary['total_sec']}с. Отчёт: results/qa_sweep_summary.json")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
