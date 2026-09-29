#!/usr/bin/env python3
"""D1a (NIGHT_PLAN): Уровень-1 retro-покрытия — сигналы 2026 через ретривал сервиса.

Каждый сигнал 2026 (Gartner 10 + MIT 5 + CBI 3; WEF отложен §1c) → топ-20 тем
ретривалом В ПРИЛОЖЕНИИ (e5-small ONNX, тот же что в C2/деплое; НЕ LaBSE) →
сигнал считается покрытым, если ХОТЯ БЫ ОДНА тема топ-20 имеет rel ≥ 0.1
(rel = IDF-покрытие лексики сигнала профилем темы — как в сервисе).

Критерий (NIGHT_PLAN D1a): ≥8/34 сигналов 2026 в топ-20 с rel ≥0.1.
34 = плановый объём (WEF 10 + MIT до 10 + CBI до 14 не вошли: paywall/504);
фактический объём сейчас 18 — отчёт даёт ОБА знаменателя (антиподгонка).

Выход: results/retro_coverage/l1_2026.json (+ печать таблицы).
Запуск: .venv/bin/python scripts/retro_l1.py
"""
import json
import math
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from vps_embed import E5Onnx, TAX, VEC_OUT  # noqa: E402

RETRO = ROOT / "retro_signals/parsed"
OUTDIR = ROOT / "results/retro_coverage"
REL_MIN = 0.1          # заморожено NIGHT_PLAN D1a
TOPK = 20              # заморожено NIGHT_PLAN D1a
TOKEN_RE = re.compile(r"[a-zа-яё0-9]{2,}", re.I)
STOP = set("""the a an and or of to in for on with from by at as is are be been being
this that these those it its our your their can could may might will would should
must not no do does did study paper analysis research method methods using use used
data results result new two three one using based""".split())


def load_signals() -> dict[str, list[str]]:
    out = {}
    data = json.loads((RETRO / "trends_2026.json").read_text())
    for src, blk in data.items():
        items = blk.get("items") or []
        if items:
            out[src] = items
    return out


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    import pyarrow.parquet as pq
    topics = pq.read_table(TAX / "topics.parquet",
                           columns=["id", "display_name"]).to_pylist()
    digest = pq.read_table(ROOT / "webapp/data/digest/digest.parquet",
                           columns=["tid", "title"])
    titles: dict[int, list[str]] = {}
    for tid, title in zip(digest["tid"].to_pylist(), digest["title"].to_pylist()):
        titles.setdefault(int(tid), []).append(str(title))
        if len(titles[int(tid)]) >= 100:
            continue
    del digest

    V = np.load(VEC_OUT)
    model = E5Onnx()
    signals = load_signals()
    report = {"year": 2026, "rel_min": REL_MIN, "topk": TOPK,
              "criterion": ">=8/34 (план); фактический объём считаем отсюда",
              "sources": {}}
    total = found = 0
    lines = ["# L1 retro-покрытие 2026 (ретривал e5 → топ-20, rel ≥0.1)", "",
             f"Критерий: ≥8/34. Сигналов фактически: суммарно см. табл.",
             f"Ретривал: e5-small ONNX (тот же, что в деплое). Время: "
             f"{time.strftime('%Y-%m-%d %H:%M')}", ""]
    for src, items in signals.items():
        lines += [f"## {src}", "", "| сигнал | покрыт | лучшая тема (rel) |", "|---|---|---|"]
        src_found = 0
        for sig in items:
            total += 1
            qv = next(iter(model.embed([sig])))
            sim = V @ qv
            top = np.argsort(-sim)[:TOPK]
            # rel по профилю (имя + топ-100 работ), IDF — по топ-20 профилям
            profs = []
            for i in top:
                tid = int(str(topics[int(i)]["id"]).rstrip("/").split("T")[-1])
                profs.append((tid, (str(topics[int(i)]["display_name"]) + " " +
                                    " ".join(titles.get(tid, []))).lower()))
            qt = [t for t in TOKEN_RE.findall(sig.lower())
                  if t not in STOP and not t.isdigit()]
            n = len(profs)
            if not qt:
                rels = [(tid, 0.0) for tid, _ in profs]
            else:
                df = {t: sum(1 for _, p in profs if t in p) for t in qt}
                idf = {t: math.log((n + 1) / (df[t] + 1)) + 1.0 for t in qt}
                tot = sum(idf.values()) or 1.0
                rels = [(tid, sum(idf[t] for t in qt if t in p) / tot)
                        for tid, p in profs]
            best_tid, best_rel = max(rels, key=lambda x: x[1])
            hit = best_rel >= REL_MIN
            if hit:
                found += 1
                src_found += 1
            name = dict((int(str(t["id"]).rstrip("/").split("T")[-1]),
                         t["display_name"]) for t in
                        [topics[int(i)] for i in top]).get(best_tid, "")
            lines.append(f"| {sig} | {'✅' if hit else '❌'} | "
                         f"T{best_tid} {name[:50]} ({best_rel:.3f}) |")
            print(f"  {'✅' if hit else '❌'} {best_rel:.3f}  {sig[:60]}", flush=True)
        report["sources"][src] = {"n": len(items), "found": src_found}
        lines.append("")
        print(f"{src}: {src_found}/{len(items)}", flush=True)
    report["total"] = total
    report["found"] = found
    report["pass_plan"] = found >= 8   # планка ≥8 (знаменатель 34 — фактический меньше)
    lines += ["", f"**ИТОГО: {found}/{total} сигналов 2026 (планка ≥8 из 34; "
              f"фактический объём {total} — WEF/paywall не вошли). "
              f"{'PASS ✅' if found >= 8 else 'FAIL ❌'}**"]
    (OUTDIR / "l1_2026.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    (OUTDIR / "l1_2026.md").write_text("\n".join(lines) + "\n")
    print(f"\nИТОГО {found}/{total} (планка ≥8/34) → "
          f"{'PASS' if found >= 8 else 'FAIL'}; {OUTDIR}/l1_2026.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
