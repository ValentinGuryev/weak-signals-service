#!/usr/bin/env python3
"""Precompute retro-2026 для демо (Addendum №16).

Для 18 пунктов trends_2026.json: e5-вектор (query:) + mapped-темы
(механика retro_l1, заморожена: e5 top-20 → rel ≥ 0.1, rel = IDF-покрытие
лексики пункта профилем темы). Выход: webapp/data/retro2026.json + vectors npy.

Запуск: .venv/bin/python scripts/build_retro2026.py [--metric]
--metric: дополнительно БАЗОВЫЙ замер retro-coverage@15 (текущий конвейер,
запрос = пункт тренда) — baseline для №16-2.
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
sys.path.insert(0, str(ROOT / "webapp"))
from vps_embed import E5Onnx, embed, TAX, VEC_OUT  # noqa: E402

DEST = ROOT / "webapp" / "data"
RETRO = ROOT / "retro_signals" / "parsed"
TOKEN_RE = re.compile(r"[a-zа-яё0-9]{2,}", re.I)
STOP = set("""the a an and or of to in for on with from by at as is are be been being
this that these those it its our your their can could may might will would should
must not no do does did study paper analysis research method methods using use used
data results result new two three one based""".split())


def rel_of(tokens: list[str], profile: str, idf: dict, total: float) -> float:
    return sum(idf[t] for t in tokens if t in profile) / (total or 1.0)


def main() -> int:
    t0 = time.time()
    data = json.loads((RETRO / "trends_2026.json").read_text())
    items = [(src, it) for src, blk in data.items()
             for it in (blk.get("items") or [])]

    import pyarrow.parquet as pq
    topics = pq.read_table(TAX / "topics.parquet",
                           columns=["id", "display_name"]).to_pylist()
    tids = [int(str(t["id"]).rstrip("/").split("T")[-1]) for t in topics]
    names = [str(t["display_name"]) for t in topics]
    V = np.load(Path(VEC_OUT) if Path(VEC_OUT).exists()
                else ROOT / "webapp/data/embed/topic_vectors_e5m.npy")
    V = V / np.clip(np.linalg.norm(V, axis=1, keepdims=True), 1e-9, None)

    # профили тем: имя + топ-титулы digest (как в сервисе)
    digest = pq.read_table(ROOT / "webapp/data/digest/digest.parquet",
                           columns=["tid", "title"])
    titles: dict[int, list[str]] = {}
    for tid, title in zip(digest["tid"].to_pylist(), digest["title"].to_pylist()):
        titles.setdefault(int(tid), []).append(str(title))
    profiles = [f"{n} {' '.join(titles.get(t, [])[:50])}".lower()
                for t, n in zip(tids, names)]

    enc = E5Onnx()
    out, vecs = [], np.zeros((len(items), 384), dtype=np.float32)
    for i, (src, it) in enumerate(items):
        qv = embed(enc, ["query: " + it])[0]
        vecs[i] = qv
        sim = V @ qv
        top20 = np.argsort(-sim)[:20]
        toks = [t for t in TOKEN_RE.findall(it.lower())
                if t not in STOP and not t.isdigit()]
        n = len(top20)
        df = {t: sum(1 for j in top20 if t in profiles[j]) for t in toks}
        idf = {t: math.log((n + 1) / (df[t] + 1)) + 1.0 for t in toks}
        total = sum(idf.values()) or 1.0
        mapped = []
        for j in top20:
            r = rel_of(toks, profiles[j], idf, total)
            if r >= 0.1:  # заморожено retro_l1 (D1a)
                mapped.append({"tid": tids[j], "name": names[j],
                               "rel": round(r, 3), "e5": round(float(sim[j]), 3)})
        out.append({"item": it, "source": src, "mapped": mapped,
                    "vec_row": i})
    np.save(DEST / "retro2026_vectors.npy", vecs)
    (DEST / "retro2026.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    n_mapped = sum(1 for o in out if o["mapped"])
    print(f"[ok] {len(out)} пунктов, mapped>0: {n_mapped}; {time.time()-t0:.0f}s")

    if "--metric" in sys.argv:
        import app as webapp
        webapp.TOP_TOPICS = 10 ** 6
        hits = 0
        print("\nБАЗОВЫЙ retro-coverage@15 (конвейер без правок №16):")
        for o in out:
            if not o["mapped"]:
                print(f"  — {o['item'][:44]:46s} (нет mapped-тем)")
                continue
            r = webapp.api_query(o["item"])
            ids15 = {int(x["tid"]) for x in r["topics"][:15]}
            mt = {m["tid"] for m in o["mapped"]}
            ok = bool(ids15 & mt)
            hits += ok
            print(f"  {'✅' if ok else '—'} {o['item'][:44]:46s} "
                  f"(mapped {len(mt)}, лучший rel {max(m['rel'] for m in o['mapped']):.2f})")
        print(f"\nBASELINE retro-coverage@15 = {hits}/{len(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
