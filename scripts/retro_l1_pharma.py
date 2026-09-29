#!/usr/bin/env python3
"""L1 retro-покрытие для 16 фарма/health сигналов — СЕРВИСНЫЙ уровень (e5 → топ-20,
rel ≥ 0.1), те же замороженные константы, что D1a (REL_MIN=0.1, TOPK=20).

Зачем: замер 27.09 показал, что ЛЕКСИЧЕСКИЙ пробник по доменам даёт 5/16 (потолок
12 из-за 4 джунк-строк), но реальный сервис использует e5-ретривал — как D1a дал
17/18 на 2026. Здесь — честный сервисный ответ по фарме без подгонки.

Выход: results/retro_coverage/l1_pharma.{json,md}
Запуск: .venv/bin/python scripts/retro_l1_pharma.py
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

OUTDIR = ROOT / "results" / "retro_coverage"
REL_MIN = 0.1          # заморожено NIGHT_PLAN D1a
TOPK = 20              # заморожено NIGHT_PLAN D1a
TOKEN_RE = re.compile(r"[a-zа-яё0-9]{2,}", re.I)
STOP = set("""the a an and or of to in for on with from by at as is are be been being
this that these those it its our your their can could may might will would should
must not no do does did study paper analysis research method methods using use used
data results result new two three one using based""".split())


def load_pharma_signals() -> list[str]:
    md = (ROOT / "results/retro_signals_topics_by_domain.md").read_text(encoding="utf-8")
    m = re.search(r"## фарма/health/bio — \d+\n(.*?)(?=\n## )", md, re.S)
    return [re.match(r"- \(\d{4}, [^)]+\) (.+)$", l.strip()).group(1)
            for l in m.group(1).strip().splitlines()
            if re.match(r"- \(\d{4}, [^)]+\) (.+)$", l.strip())]


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
    del digest

    V = np.load(VEC_OUT)
    model = E5Onnx()
    sigs = load_pharma_signals()
    # джунк-строки (антиподгонка: считаем и показываем ОБА знаменателя)
    junk = [s for s in sigs if "paywall" in s or "Apple" in s
            or "Transparently immersive" in s]
    report = {"rel_min": REL_MIN, "topk": TOPK, "n_total": len(sigs),
              "n_junk": len(junk), "n_real": len(sigs) - len(junk),
              "rows": []}
    lines = ["# L1 фарма-покрытие (СЕРВИСНЫЙ уровень: e5 → топ-20, rel ≥0.1)", "",
             f"Сигналов: {len(sigs)} (из них джунк-несопоставимых {len(junk)} → "
             f"реальный знаменатель {len(sigs)-len(junk)}). Константы D1a заморожены.",
             ""]
    found = found_real = 0
    for sig in sigs:
        qv = next(iter(model.embed([sig])))
        sim = V @ qv
        top = np.argsort(-sim)[:TOPK]
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
        is_junk = sig in junk
        found += hit
        found_real += (hit and not is_junk)
        name = next((str(topics[int(i)]["display_name"])
                     for i in top
                     if int(str(topics[int(i)]["id"]).rstrip("/").split("T")[-1]) == best_tid), "")
        report["rows"].append({"signal": sig, "junk": is_junk, "hit": bool(hit),
                               "best_tid": best_tid, "best_rel": round(best_rel, 3)})
        lines.append(f"| {'✅' if hit else '❌'} | {'[джунк] ' if is_junk else ''}"
                     f"{sig[:60]} | T{best_tid} {name[:44]} ({best_rel:.3f}) |")
        print(f"  {'✅' if hit else '❌'} {best_rel:.3f} {sig[:60]}", flush=True)

    report["found"] = found
    report["found_real"] = found_real
    lines += ["", f"**ИТОГО: {found}/{len(sigs)} всего; {found_real}/{len(sigs)-len(junk)} "
              f"без джунк-строк.**"]
    (OUTDIR / "l1_pharma.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    (OUTDIR / "l1_pharma.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nИТОГО {found}/{len(sigs)} (без джунка {found_real}/{len(sigs)-len(junk)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
