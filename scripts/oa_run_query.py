#!/usr/bin/env python3
"""CLI: направление исследований → ~50 тем/направлений + топ-работы.

Пример:
  oa_run_query.py --query "защита систем искусственного интеллекта" \
      --local /tmp/oa_loc/derived --e /tmp/oa_loc/derived_e --json out.json
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import oa_snapshot as oa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--local", required=True)
    ap.add_argument("--e", required=True)
    ap.add_argument("--topk", type=int, default=50)
    ap.add_argument("--topics", type=int, default=60)
    ap.add_argument("--match", choices=["embed", "tfidf"], default="embed")
    ap.add_argument("--years", nargs=2, type=int, default=None,
                    metavar=("FROM", "TO"), help="окно лет, напр. 2026 2026")
    ap.add_argument("--gate", default=None,
                    help="И5: доменный гейт, номера доменов через запятую (напр. 3,2 = "
                         "Physical+Social) — ЕДИНСТВЕННАЯ механика отсева вместо regex-маски")
    ap.add_argument("--fanout", action="store_true",
                    help="И1 стратегия A: кластеризация top-M + RRF (замороженный конфиг)")
    ap.add_argument("--route", action="store_true",
                    help="§4а routing: лексические ключи → профиль matched (gate+C+t500) / "
                         "fallback (legacy t60k50) — профили заморожены журнал 18:15")
    ap.add_argument("--embed-variant", choices=["base", "i2"], default="base",
                    help="вектора matched-профиля: base | i2 (И2 data-driven aliases, шаг 5)")
    ap.add_argument("--json", help="выходной JSON-файл")
    args = ap.parse_args()
    ROUTE = {"profiles": {
        "matched": {"gate": [3, 2], "topics": 500, "topk": 500,
                    "vectors": ("topic_vectors_i2.npy" if args.embed_variant == "i2" else None),
                    "fanout": {"m": 240, "k": 12, "ktop": 25, "rrf_c": 60, "seed": 42,
                               "source": "lexicon",
                               "lexicon_path": str(Path(__file__).resolve().parent.parent /
                                                    "results/qa_facet_lexicon_v1.json")}},
        "fallback": {"gate": None, "topics": 60, "topk": 50, "fanout": None}}}
    routing = ROUTE if args.route else None

    P = oa.Paths(local=Path(args.local), e=Path(args.e), staging=Path("/mnt/c/oa_tmp"))
    import duckdb
    con = duckdb.connect()
    # память урезана под машину 7.4ГБ (урок ENOMEM 24.09); spill — только на E:
    con.execute("SET threads=2; SET memory_limit='1GB'")
    Path("/mnt/e/openalex_derived/tmp_duck").mkdir(parents=True, exist_ok=True)
    con.execute("SET temp_directory='/mnt/e/openalex_derived/tmp_duck'")
    res = oa.query_directions(con, P, args.query, topk=args.topk, match=args.match,
                              n_topics=args.topics,
                              years=tuple(args.years) if args.years else (2016, 2026),
                              gate_domains=[int(x) for x in args.gate.split(",")] if args.gate else None,
                              fanout={"m": 240, "k": 12, "ktop": 25, "rrf_c": 60, "seed": 42}
                              if args.fanout else None,
                              routing=routing)
    con.close()

    if args.json:
        Path(args.json).write_text(json.dumps(res, ensure_ascii=False, indent=1))
        print(f"[ok] записано: {args.json}  ({len(res['directions'])} направлений)")
        return

    print(f"Запрос: «{res['query']}»  (match={res['match']})")
    print(f"{'#':>2} {'T-ID':>6} {'работ':>7} {'цит.':>9} {'годы':>9}  направление")
    for i, d in enumerate(res["directions"], 1):
        top = res["top_works"].get(int(d["topic_id"]), ([], []))[1]
        print(f"{i:>2} T{d['topic_id']:<5} {d['n_works']:>7,} {d['n_cites']:>9,.0f} "
              f"{d['y0']}-{d['y1']}  {str(d.get('display_name') or '?')[:52]}")
        for t in top[:2]:
            print(f"      • {str(t)[:88]}")


if __name__ == "__main__":
    main()