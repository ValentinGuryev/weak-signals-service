#!/usr/bin/env python3
"""Уровень 2 retro-покрытия (NIGHT_PLAN D2 / NJ-11): маркеры сигналов
`retro_signals/parsed/trends_<year>.json` против терминов TermTech-срезов.

Антиподгонка: сигналы НЕ участвуют в построении конвейера — только проверка.
Матчинг v0 — лексический, без ручных синонимов (чтобы не подгонять):
  сигнал считается НАЙДЕННЫМ, если существует кандидат-термин, содержащий
  ФРАЗУ сигнала (после нормализации) ИЛИ все «содержательные» слова сигнала
  (длина ≥5 симв., вне стоп-листа), причём хотя бы одно — «редкое»
  (длина ≥6 или с дефисом/цифрой: mgb2, lk-99, ni-coil…).

Выход:
  results/retro_coverage/coverage.json / coverage.md
    по каждому домену: {year: {signal: {found: bool, terms: [...]}}}

Запуск:
  .venv/bin/python scripts/retro_coverage.py \
      --domain sp=results/termtech \
      [--domain quantum=/mnt/e/openalex_derived/termtech_quantum] ... \
      [--years 2018,2020,2024,2026]
"""
import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RETRO = ROOT / "retro_signals/parsed"
OUTDIR = ROOT / "results/retro_coverage"

STOP = set("""the a an and or of to in for on with from by at as is are be been being
this that these those it its our your their can could may might will would should
must not no do does did new two three one using use used based study paper research
towards into over under after before between through more most other such same all
any some each both how what when where which who whom why while about above across
developments development emerging technologies technology systems system""".split())
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-+#.][a-z0-9]+)*")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def content_tokens(signal: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(signal.lower())
            if t not in STOP and len(t) >= 3]


def rare(t: str) -> bool:
    return len(t) >= 6 or any(c.isdigit() for c in t) or "-" in t


def load_signals(years: set[str] | None) -> dict:
    out: dict = {}
    for f in sorted(RETRO.glob("trends_*.json")):
        y = f.stem.split("_")[1]
        if years and y not in years:
            continue
        data = json.loads(f.read_text())
        for src, blk in data.items():
            for item in blk.get("items", []):
                out.setdefault(y, []).append({"signal": item, "src": src})
    return out


def match_signal(signal: str, term_index: dict) -> list[str]:
    """term_index: norm(term) -> term. Возвращает найденные термины."""
    ns = norm(signal)
    hits = []
    toks = content_tokens(signal)
    if not toks:
        return hits
    rare_toks = [t for t in toks if rare(t)]
    if not rare_toks:
        rare_toks = toks[:1]
    for nt, orig in term_index.items():
        if ns in nt:                      # полная фраза внутри термина
            hits.append(orig)
            if len(hits) >= 5:
                break
            continue
        if all(f" {t} " in f" {nt} " or nt.startswith(t + " ")
               or nt.endswith(" " + t) for t in toks):   # все содержательные слова
            if any(f" {t} " in f" {nt} " or nt.startswith(t + " ")
                   or nt.endswith(" " + t) for t in rare_toks):
                hits.append(orig)
                if len(hits) >= 5:
                    break
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", action="append", required=True,
                    help="имя=каталог с candidates_clean.parquet (можно несколько)")
    ap.add_argument("--years", default=None, help="через запятую, напр. 2018,2020,2024,2026")
    args = ap.parse_args()

    years = set(args.years.split(",")) if args.years else None
    signals = load_signals(years)
    if not signals:
        print("нет сигналов в", RETRO)
        return 1

    OUTDIR.mkdir(parents=True, exist_ok=True)
    report: dict = {"domains": {}, "signals_by_year": {y: len(v) for y, v in signals.items()}}

    for spec in args.domain:
        name, _, path = spec.partition("=")
        cand = Path(path) / "candidates_clean.parquet"
        if not cand.exists():
            print(f"[skip] {name}: нет {cand}")
            report["domains"][name] = {"error": f"нет {cand}"}
            continue
        df = pd.read_parquet(cand, columns=["term"])
        term_index = {norm(t): t for t in df["term"]}
        dom: dict = {}
        for y, items in sorted(signals.items()):
            found = 0
            det = {}
            for it in items:
                hits = match_signal(it["signal"], term_index)
                det[it["signal"]] = {"src": it["src"], "found": bool(hits),
                                     "terms": hits[:3]}
                found += 1 if hits else 0
            dom[y] = {"n_signals": len(items), "n_found": found,
                      "coverage": round(found / max(len(items), 1), 3),
                      "detail": det}
        report["domains"][name] = dom
        cov = {y: f"{v['n_found']}/{v['n_signals']}" for y, v in dom.items()}
        print(f"{name:12s} покрытие сигналов: {cov}", flush=True)

    (OUTDIR / "coverage.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1))

    lines = ["# Retro-покрытие терминами (уровень 2)", "",
             "Матчинг лексический, без ручных синонимов (антиподгонка).", "",
             "| домен | " + " | ".join(sorted(report["signals_by_year"])) + " |",
             "|---|" + "---|" * len(report["signals_by_year"])]
    for name, dom in report["domains"].items():
        if "error" in dom:
            lines.append(f"| {name} | " + " — " * len(report["signals_by_year"]) + " |")
            continue
        lines.append(f"| {name} | " +
                     " | ".join(f"{dom[y]['n_found']}/{dom[y]['n_signals']}"
                                if y in dom else "—" for y in sorted(report["signals_by_year"])) + " |")
    lines += ["", "Детали: coverage.json (по каждому сигналу — найденные термины)."]
    (OUTDIR / "coverage.md").write_text("\n".join(lines) + "\n")
    print("→ results/retro_coverage/coverage.{json,md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
