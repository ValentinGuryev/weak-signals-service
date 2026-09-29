#!/usr/bin/env python3
"""Фарма-покрытие: 16 сигналов фарма/health из retro_signals × кандидаты biomed.

Порог автора (27.09): ≥13/16 → NJ-13 НЕ нужен; <13 → NJ-13 pharma в очередь ночью.
Запуск ПОСЛЕ NJ-6 (нужен candidates_clean) и ПОСЛЕ E7-прогона retro_coverage
(нужен results/retro_coverage/coverage.json с доменом biomed).

Выход: results/retro_coverage/pharma_check.md + stdout; копия coverage.json.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "results" / "retro_signals_topics_by_domain.md"
COV = ROOT / "results" / "retro_coverage" / "coverage.json"
OUT = ROOT / "results" / "retro_coverage"
THRESHOLD = 13
N_EXPECT = 16


def pharma_signals() -> list[str]:
    txt = MD.read_text(encoding="utf-8")
    m = re.search(r"## фарма/health/bio — \d+\n(.*?)(?=\n## )", txt, re.S)
    if not m:
        print("секция фармы не найдена в", MD)
        sys.exit(2)
    out = []
    for line in m.group(1).strip().splitlines():
        mm = re.match(r"- \(\d{4}, [^)]+\) (.+)$", line.strip())
        if mm:
            out.append(mm.group(1).strip())
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default="biomed",
                    help="имя домена в coverage.json (biomed | pharma | …)")
    ap.add_argument("--threshold", type=int, default=THRESHOLD)
    args = ap.parse_args()
    sigs = pharma_signals()
    print(f"фарма-сигналов: {len(sigs)} (ожидается {N_EXPECT}), домен: {args.domain}")
    if not COV.exists():
        print("нет coverage.json — сначала retro_coverage --domain ...")
        return 2
    cov = json.loads(COV.read_text())
    shutil.copy(COV, OUT / f"coverage_{args.domain}_snapshot.json")  # защита от перезаписи E7
    dom = cov.get("domains", {}).get(args.domain)
    if dom is None or "error" in (dom or {}):
        print(f"в coverage.json нет домена {args.domain}:", list(cov.get("domains", {})))
        return 2

    # собираем detail по всем годам
    detail = {}
    for y, blk in dom.items():
        if isinstance(blk, dict) and "detail" in blk:
            detail.update(blk["detail"])

    found, missed = [], []
    rows = []
    for s in sigs:
        d = detail.get(s)
        ok = bool(d and d.get("found"))
        (found if ok else missed).append(s)
        rows.append(f"| {'✅' if ok else '❌'} | {s} | {', '.join((d or {}).get('terms', []))[:90]} |")

    n = len(found)
    verdict = "PASS — NJ-13 НЕ нужен" if n >= args.threshold else "FAIL — нужен NJ-13 pharma в очередь"
    report = [
        f"# Фарма-покрытие ({args.domain} candidates)", "",
        f"Порог автора: ≥{args.threshold}/{len(sigs)}. **Результат: {n}/{len(sigs)} → {verdict}**", "",
        "| ✓ | сигнал | термины-доказательства |", "|---|---|---|",
        *rows, "",
        f"Пропущены ({len(missed)}): " + ("; ".join(missed) if missed else "нет"),
    ]
    (OUT / f"pharma_check_{args.domain}.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report[2:4]))
    for s in missed:
        print("  MISS:", s)
    print(f"→ results/retro_coverage/pharma_check_{args.domain}.md")
    return 0 if n >= args.threshold else 1


if __name__ == "__main__":
    sys.exit(main())
