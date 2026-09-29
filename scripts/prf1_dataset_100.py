#!/usr/bin/env python3
"""P/R/F1 по датасету заказчика (100 слабых сигналов) — прогон 28.09.

Политика негативов №3 (гибрид, автор 28.09):
  позитивы = allowed-темы оракулов (100 сигналов xlsx → mapped);
  негативы = ВСЯ таксономия − позитивы (фон, включает зрелое/шум);
  + отдельная аннотация шумовых FP по GARBAGE_RE (показать состав мусора).

Score = NGI stage-1: novelty × growth × impact — ФОРМУЛА ТА ЖЕ, что screen
в webapp/app.py (Y=2025, birth-правило «затишье сбрасывает», imp_n=1-e^(-imp/40)).
Модель НЕ обучалась на датасете заказчика (внешний test-set).

Выход: results/runtime/prf1_dataset_100_20260928.md + stdout-сводка.
Запуск: .venv/bin/python scripts/prf1_dataset_100.py
"""
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "webapp"))

from eval_stage9 import load_oracles  # noqa: E402
import app as webapp  # noqa: E402
from rank_directions_ngi import GARBAGE_RE  # noqa: E402

OUT = ROOT / "results" / "runtime" / "prf1_dataset_100_20260928.md"


def score_all() -> dict[int, float]:
    """NGI screen по ВСЕМ темам таксономии (дубль формулы screen_rows, Y=2025)."""
    Y = webapp.WINDOW
    out: dict[int, float] = {}
    for i in range(len(webapp.TOPICS)):
        rec = webapp.TOPICS.iloc[i]
        tid = int(str(rec["id"]).rstrip("/").split("T")[-1])
        ser = webapp.NGI_SERIES.get(tid, {})
        n_late = sum(ser.get(y, 0) for y in (Y - 2, Y - 1, Y))
        n_early = sum(ser.get(y, 0) for y in (Y - 4, Y - 3))
        if n_late == 0 and n_early == 0:
            out[tid] = 0.0
            continue
        growth_n = 1.0 if n_early == 0 else (
            (n_late / n_early) / (n_late / n_early + 1.0))
        b = webapp.birth_of(tid)
        if b is None:
            out[tid] = 0.0
            continue
        nov = 1.0 - webapp.sigmoid((max(Y - b, 0) - 15) / 5.0)
        imp_n = 1.0 - math.exp(-webapp.NGI_IMPACT.get(tid, 0) / 40.0)
        out[tid] = nov * growth_n * imp_n
    return out


def main() -> int:
    t0 = time.time()
    oracles = load_oracles()
    signals = []  # (slug, n, allowed)
    for slug, orc in oracles.items():
        for t in orc["targets"]:
            signals.append((slug, str(t.get("n")), {int(x) for x in t["allowed"]}))
    P = set().union(*[a for _, _, a in signals])

    scores = score_all()
    ranked = sorted(scores, key=lambda t: (-scores[t], t))  # детерминированно
    rank_of = {t: i + 1 for i, t in enumerate(ranked)}
    name_of = {int(str(v).rstrip("/").split("T")[-1]): str(n)
               for v, n in zip(webapp.TOPICS["id"], webapp.TOPICS["display_name"])}

    # --- AUC (rank-sum) P vs фон; ранги = позиция по УБЫВАНИЮ score (1 = лучший),
    # поэтому классическая формула даёт зеркало → AUC = 1 - raw
    n_pos, n_neg = len(P), len(scores) - len(P)
    sum_ranks = sum(rank_of[t] for t in P)
    auc = 1 - (sum_ranks - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)

    def pr_at(k: int, skip_noise: bool = False):
        top = []
        for t in ranked:
            if skip_noise and GARBAGE_RE.search(name_of.get(t, "")):
                continue
            top.append(t)
            if len(top) == k:
                break
        tp = len(set(top) & P)
        prec, rec = tp / k, tp / len(P)
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        sig_rec = sum(1 for _, _, a in signals if a & set(top)) / len(signals)
        return prec, rec, f1, sig_rec

    # --- F1-max по порогу (потолок; в проде порог с калибровки)
    best = (0.0, 0.0, 0.0, 0.0)  # f1, thr, prec, rec
    for thr in sorted({scores[t] for t in scores})[::1]:
        flagged = [t for t in scores if scores[t] >= thr and thr > 0]
        if not flagged:
            continue
        tp = len(set(flagged) & P)
        prec, rec = tp / len(flagged), tp / len(P)
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        if f1 > best[0]:
            best = (f1, thr, prec, rec)

    # --- шумовые FP (политика №3: аннотация)
    top_p = len(P)
    fp_noise = [t for t in ranked[:top_p] if t not in P and GARBAGE_RE.search(name_of.get(t, ""))]

    lines = [f"# P/R/F1 на датасете заказчика — прогон {time.strftime('%Y-%m-%d %H:%M')}",
             "",
             f"- позитивы: {len(signals)} сигналов → {len(P)} distinct allowed-тем "
             f"(из 100 строк xlsx; unmapped/out_of_scope = {100 - len(signals)})",
             f"- негативы (политика №3): фон = таксономия − позитивы = {n_neg} тем "
             f"(зрелое/шум внутри фона; явный шум-контроль — по GARBAGE_RE)",
             f"- score = NGI stage-1 (novelty×growth×impact, Y=2025), модель на датасете НЕ обучалась",
             f"- AUC(P vs фон) = **{auc:.3f}**",
             f"- F1-max по порогу = **{best[0]:.3f}** (thr={best[1]:.4f}, P={best[2]:.3f}, R={best[3]:.3f}) "
             f"— показан ПОТОЛОК; рабочий порог в проде берётся с калибровки, не подгоняется",
             "", "## PR по top-K", "",
             "| K | Precision | Recall (темы) | **F1** | Recall (сигналы, any-hit) |", "|---|---|---|---|---|"]
    for k in (100, top_p, 150, 200, 300, 500, 1000):
        p, r, f1, sr = pr_at(k)
        lines.append(f"| {k} | {p:.3f} | {r:.3f} | **{f1:.3f}** | {sr:.3f} |")
    lines += ["", "## PR по top-K (после снятия GARBAGE_RE-шума — политика №3)", "",
              "| K | Precision | Recall (темы) | **F1** | Recall (сигналы) |", "|---|---|---|---|---|"]
    for k in (100, top_p, 150, 200, 300, 500):
        p, r, f1, sr = pr_at(k, skip_noise=True)
        lines.append(f"| {k} | {p:.3f} | {r:.3f} | **{f1:.3f}** | {sr:.3f} |")
    lines += ["", f"## Шумовые FP в топ-{top_p} (GARBAGE_RE): {len(fp_noise)}",
              ""]
    lines += [f"- `{t}` {name_of.get(t, '?')}" for t in fp_noise[:15]]
    # разделение P vs фон (медианы)
    import statistics as st
    sp = sorted(scores[t] for t in P)
    sn = sorted(t for t in scores.values() if True)
    lines += ["", "## Разделение score", "",
              f"- позитивы: медиана {st.median(sp):.4f}, >0: {sum(1 for x in sp if x > 0)}/{len(sp)}",
              f"- фон: медиана {st.median(sn):.4f}, >0: {sum(1 for x in sn if x > 0)}/{len(sn)}"]
    OUT.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\n[ok] {OUT} ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
