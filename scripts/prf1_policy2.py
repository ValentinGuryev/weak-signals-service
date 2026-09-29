#!/usr/bin/env python3
"""P/R/F1 на датасете заказчика — политика негативов №2 (собранные), прогон 28.09.

Состав негативов ЗАФИКСИРОВАН ДО ПРОГОНА (детерминированные правила, без подгонки):
  N1 «шум»: все темы таксономии, матчащие GARBAGE_RE (тот же канон-regex, что в приёмке);
  N2 «ретро-кейсы»: строки CASE_REGISTRY §1, чей «Исход 2026» содержит
     провал|ниш|лаборатор|фундамент|успех (= состоявшиеся к 2026 = зрелые, или
     провалы = мёртвый хайп); кейсы с исходом «тренд/перспектива/подтверждено/
     водоочистка» ИСКЛЮЧЕНЫ (амбивалентны); маппинг кейс→темы по ключевым словам
     (CASE_KEYWORDS, ниже) по display_name;
  N3 «зрелые»: birth_of ≤ 2010, не позитив и не N1/N2, добор по IMPACT desc
     до |N| = |позитивы| (баланс 1:1).
Позитивы: 142 allowed-темы 96 сигналов xlsx (как в prf1_dataset_100).
Score: NGI stage-1 (novelty×growth×impact, Y=2025) — та же формула, модель на
датасете НЕ обучалась. Политика №3 (фон=вся таксономия) считается для сравнения.

Выход: results/runtime/prf1_policy2_20260928.md + stdout.
Запуск: .venv/bin/python scripts/prf1_policy2.py
"""
import math
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "webapp"))

from eval_stage9 import load_oracles  # noqa: E402
import app as webapp  # noqa: E402
from rank_directions_ngi import GARBAGE_RE  # noqa: E402

OUT = ROOT / "results" / "runtime" / "prf1_policy2_20260928.md"
REGISTRY = ROOT / "results" / "calibration" / "CASE_REGISTRY.md"

# маппинг кейс → ключевые слова имени темы (прозрачно, правится вручную)
CASE_KEYWORDS = [
    ("SMES", ["superconducting magnetic energy storage", "smes"]),
    ("Fluxonics", ["fluxonic", "single flux quantum", "sfq"]),
    ("ВТСП-ленты", ["rebco", "coated conductor", "ybco", "2g hts"]),
    ("Термояд-магниты", ["fusion magnet", "tokamak", "fusion energy"]),
    ("Джозефсоновские", ["quantum error correction", "superconducting qubit"]),
    ("MgB", ["mgb2", "magnesium diboride"]),
    ("авиадвигатели", ["superconducting motor", "electric aircraft"]),
    ("HTS AC кабели", ["superconducting cable", "hts cable"]),
    ("Nb3Sn", ["nb3sn", "niobium-tin", "niobium tin"]),
    ("Пниктиды", ["pnictide", "iron-based superconductor"]),
    ("Халькогениды", ["iron selenide", "fese", "chalcogenide"]),
    ("холодильник", ["magnetic refrigeration", "magnetocaloric"]),
    ("сепарация", ["magnetic separation"]),
    ("Flux pump", ["flux pump"]),
    ("SDE", ["superconducting diode"]),
]
NEG_VERDICT = re.compile(r"провал|ниш|лаборатор|фундамент|успех", re.I)


def score_all() -> dict[int, float]:
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


def auc_of(P: set, N: set, scores: dict[int, float]) -> float:
    """AUC внутри базы P∪N; ранги по УБЫВАНИЮ score (1 = лучший) → зеркало формулы."""
    n1, n0 = len(P), len(N)
    if not n0:
        return float("nan")
    base = sorted(P | N, key=lambda t: (-scores[t], t))
    rank = {t: i + 1 for i, t in enumerate(base)}
    sr = sum(rank[t] for t in P)
    return 1 - (sr - n1 * (n1 + 1) / 2) / (n1 * n0)


def main() -> int:
    t0 = time.time()
    name_of = {int(str(v).rstrip("/").split("T")[-1]): str(n)
               for v, n in zip(webapp.TOPICS["id"], webapp.TOPICS["display_name"])}
    oracles = load_oracles()
    P = set()
    for orc in oracles.values():
        for t in orc["targets"]:
            P |= {int(x) for x in t["allowed"]}

    scores = score_all()
    ranked = sorted(scores, key=lambda t: (-scores[t], t))

    # ---- N1 шум
    N1 = {t for t, n in name_of.items() if GARBAGE_RE.search(n)} - P
    # ---- N2 ретро-кейсы
    N2, used_cases = set(), []
    for line in REGISTRY.read_text().splitlines():
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 5 or not cols[0].isdigit():
            continue
        case_name, outcome = cols[1], cols[4]
        if not NEG_VERDICT.search(outcome):
            continue
        for key, kws in CASE_KEYWORDS:
            if key.lower() in case_name.lower():
                hits = {t for t, n in name_of.items()
                        if any(k in n.lower() for k in kws)} - P
                N2 |= hits
                used_cases.append((case_name[:40], outcome[:30], len(hits)))
                break
    # ---- N3 зрелые (birth≤2010, добор по impact до баланса)
    target_n = len(P)
    n12 = (N1 | N2)
    need = max(0, target_n - len(n12))
    mature = sorted(
        (t for t in scores
         if t not in n12 and t not in P and (webapp.birth_of(t) or 9999) <= 2010),
        key=lambda t: -webapp.NGI_IMPACT.get(t, 0))
    N3 = set(mature[:need])
    N = N1 | N2 | N3

    # ---- метрики
    def prf_at(baseP: set, baseN: set, k: int):
        top = [t for t in ranked if t in baseP or t in baseN][:k]
        tp = len(set(top) & baseP)
        prec = tp / k if k else 0.0
        rec = tp / len(baseP) if baseP else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        return prec, rec, f1

    best = (0.0, 0.0, 0.0, 0.0)
    base = P | N
    for thr in sorted({scores[t] for t in base}):
        if thr <= 0:
            continue
        fl = [t for t in base if scores[t] >= thr]
        tp = len(set(fl) & P)
        prec, rec = tp / len(fl), tp / len(P)
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        if f1 > best[0]:
            best = (f1, thr, prec, rec)

    lines = [f"# P/R/F1 — политика №2 (собранные негативы) — {time.strftime('%Y-%m-%d %H:%M')}",
             "",
             f"- позитивы: {len(P)} тем (96 сигналов xlsx)",
             f"- негативы ВСЕГО: {len(N)} → N1 шум GARBAGE_RE: {len(N1)}, "
             f"N2 ретро-кейсы: {len(N2)} ({len(used_cases)} кейсов замаплено), "
             f"N3 зрелые birth≤2010 (добор): {len(N3)}",
             f"- базовая ставка: {len(P)}/({len(P)}+{len(N)}) = {len(P)/len(base):.2f}",
             f"- AUC(P vs N) = **{auc_of(P, N, scores):.3f}**",
             f"- **F1-max = {best[0]:.3f}** (thr={best[1]:.4f}, P={best[2]:.3f}, R={best[3]:.3f})",
             "", "## Замапленные ретро-кейсы (N2)", ""]
    for c, o, nh in used_cases:
        lines.append(f"- {c} | исход: {o} | тем найдено: {nh}")
    lines += ["", "## PR по top-K (внутри базы P∪N)", "",
              "| K | Precision | Recall | **F1** |", "|---|---|---|---|"]
    for k in (100, len(P), 200, 300):
        p, r, f1 = prf_at(P, N, k)
        lines.append(f"| {k} | {p:.3f} | {r:.3f} | **{f1:.3f}** |")
    lines += ["", "## AUC по стратам (где NGI путает)", ""]
    for nm, st in (("N1 шум", N1), ("N2 ретро-кейсы", N2), ("N3 зрелые", N3)):
        if st:
            lines.append(f"- vs {nm}: AUC = {auc_of(P, st, scores):.3f}")
    # сравнение с №3 (пересчёт на лету: фон = всё минус P)
    allN = set(scores) - P
    lines += ["", "## Сравнение с политикой №3 (фон = вся таксономия)", "",
              f"- №3: AUC = {auc_of(P, allN, scores):.3f} (справочно; F1-max №3 = 0.136, см. prf1_dataset_100)", ""]
    OUT.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"[ok] {OUT} ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
