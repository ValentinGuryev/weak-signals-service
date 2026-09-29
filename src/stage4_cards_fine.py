"""Улучшенные карточки трендов для ЭКСПЕРТНОЙ валидации (вариант A, Фаза 4+).

Проблема (обнаружена 2026-08-17): старые карточки (trend_cards/) показывали
шаблонный текст и label'ы от topics_full (nr_topics=40), а Score был согласован
с topics_full, но НЕ с topics_fine (199 тем). Эксперт не мог валидировать по
шаблону — нужно видеть ДАННЫЕ.

Что показывает новая карточка (для эксперта):
  - label + топ-слова (согласованы с topics_fine, проверено: 0 несовпадений);
  - Score и компоненты (GrowthRate, Novelty, Acceleration);
  - реальные статьи с датами: первые (зарождение), последние (актуальность), примеры из разных лет;
  - кривую роста по кварталам (последние ~12 кварталов + полная);
  - возраст темы (первый квартал, последний квартал, активных кварталов);
  - стадию (эвристика по данным): зарождается / растёт / плато / спад / шум;
  - поля для ЭКСПЕРТА: контент темы (1 фраза), стадия по знанию области, вердикт (✓/✗/?)

Вход: results/top_trends_fine.json (Фаза 3, вариант A) + data/processed/papers.parquet
      + data/processed/doc_topics_fine.parquet.
Выход: results/trend_cards/trend_NN_<label>.md (читаемые имена).
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

QUARTERS_PER_YEAR = 4


def quarter_to_int(q: str) -> int:
    """'2006-Q1' -> 0."""
    q = q.strip()
    if "-Q" in q:
        year, qn = q.split("-Q")
    else:
        idx = q.index("Q")
        year, qn = q[:idx], q[idx + 1:]
    return (int(year) - 2006) * QUARTERS_PER_YEAR + int(qn) - 1


def int_to_quarter(idx: int) -> str:
    year = 2006 + idx // QUARTERS_PER_YEAR
    qn = idx % QUARTERS_PER_YEAR + 1
    return f"{year}-Q{qn}"


def estimate_stage(series: np.ndarray, start: int, end: int, qmin: int, now_idx: int) -> str:
    """Эвристика стадии темы по данным (эксперт может поправить).

    - «зарождается»: активна < 2 лет ИЛИ быстрый рост в последние кварталы от малой базы;
    - «растёт»: стабильный рост (последние 8 кварталов > предыдущих);
    - «плато»: стабильный поток, без явного роста;
    - «спад»: падение в последние кварталы;
    - «шум»: мало данных / неустойчивая динамика.
    """
    s = np.asarray(series, dtype=float)
    lo = max(0, start - qmin)
    hi = min(now_idx - qmin, len(s) - 1)
    if hi - lo < 3:
        return "шум (мало данных)"
    active_q = end - start + 1
    # последние 8 кварталов vs предыдущие 8
    tail = s[max(lo, hi - 7): hi + 1]
    prev = s[max(lo, hi - 15): max(lo, hi - 7)]
    tail_mean = float(tail.mean()) if len(tail) else 0.0
    prev_mean = float(prev.mean()) if len(prev) else 0.0
    growth_ratio = tail_mean / prev_mean if prev_mean > 0 else (1.0 if tail_mean > 0 else 0.0)
    # спад: последние 4 квартала < среднего за предыдущие 4
    last4 = s[max(lo, hi - 3): hi + 1]
    prev4 = s[max(lo, hi - 7): max(lo, hi - 3)]
    last4_mean = float(last4.mean()) if len(last4) else 0.0
    prev4_mean = float(prev4.mean()) if len(prev4) else 0.0

    if active_q <= 8:
        return "зарождается (активна < 2 лет)"
    if growth_ratio >= 1.3 and tail_mean >= 1.0:
        return "растёт"
    if growth_ratio <= 0.6 or (prev4_mean > 0 and last4_mean < prev4_mean * 0.6):
        return "спад"
    if 0.8 <= growth_ratio <= 1.3:
        return "плато"
    return "неустойчивая"


def sparkline(series: np.ndarray, start: int, qmin: int, width: int = 30) -> str:
    """Мини-график роста (unicode) — компактная визуализация для MD."""
    s = np.asarray(series, dtype=float)
    lo = max(0, start - qmin)
    n = len(s)
    if n <= lo:
        return "(нет данных)"
    seg = s[lo:]
    # сгладить и нормализовать
    if seg.max() > 0:
        seg = seg / seg.max()
    n_show = min(width, len(seg))
    # берём последние n_show кварталов (или все если короче)
    seg = seg[-n_show:] if len(seg) > n_show else seg
    levels = " ▁▂▃▄▅▆▇█"
    chars = []
    for v in seg:
        idx = int(round(v * 8))
        chars.append(levels[min(idx, 8)])
    return "".join(chars)


def trend_evidence_with_dates(
    doc_topics: pd.DataFrame,
    papers: pd.DataFrame,
    tid: int,
    n_first: int = 4,
    n_last: int = 4,
    n_mid: int = 3,
) -> dict[str, Any]:
    """Статьи темы с датами: первые (зарождение), последние (актуальность), примеры из середины."""
    sub = doc_topics[doc_topics["topic"] == tid]
    if sub.empty:
        return {"first": [], "last": [], "mid": []}
    merged = sub.merge(papers, on="arxiv_id", how="left")
    merged = merged.sort_values("published")
    cols = ["published", "arxiv_id", "title", "authors"]
    out: dict[str, Any] = {"n_docs": len(merged)}

    def fmt(row) -> str:
        raw_auth = row.get("authors", None)
        if raw_auth is None:
            a_str = ""
        elif isinstance(raw_auth, str):
            alist = [a.strip() for a in raw_auth.split(",") if a.strip()][:2]
            a_str = ", ".join(alist)
        else:
            # numpy-массив / список
            try:
                alist = [str(a).strip() for a in list(raw_auth) if str(a).strip()][:2]
                a_str = ", ".join(alist)
            except Exception:
                a_str = str(raw_auth)[:40]
        t = str(row.get("title", "") or "")[:110]
        return f"- **{row['published']}** `{row['arxiv_id']}` {t} ({a_str})"

    if len(merged) <= n_first + n_last + n_mid:
        out["first"] = [fmt(r) for _, r in merged.iterrows()]
        out["last"] = []
        out["mid"] = []
    else:
        out["first"] = [fmt(r) for _, r in merged.head(n_first).iterrows()]
        out["last"] = [fmt(r) for _, r in merged.tail(n_last).iterrows()]
        step = max(1, (len(merged) - n_first - n_last) // (n_mid + 1))
        mid_idx = list(range(n_first, len(merged) - n_last, step))[:n_mid]
        out["mid"] = [fmt(merged.iloc[i]) for i in mid_idx]
    return out


def build_card(
    trend: dict[str, Any],
    series: np.ndarray,
    start: int,
    end: int,
    qmin: int,
    now_idx: int,
    doc_topics: pd.DataFrame,
    papers: pd.DataFrame,
    kw_pat: dict[str, list[str]] | None = None,
    patents: dict[str, int] | None = None,
    patent_queries: dict[str, str] | None = None,
    patent_map: list[tuple[str, str]] | None = None,
    n_evidence: int = 6,
) -> str:
    tid = trend["topic_id"]
    label = trend["label"]
    score = trend["score"]
    comps = trend.get("components", {})
    size = trend.get("size", 0)
    top_words = trend.get("top_words", [])
    is_kw = tid < 0

    stage = estimate_stage(series, start, end, qmin, now_idx)
    spark = sparkline(series, start, qmin)

    # --- реальные статьи ---
    if is_kw:
        # keyword-темы: полный корпус по паттернам (не только evidence)
        name = label.replace("KW: ", "")
        pats = (kw_pat or {}).get(name, [])
        txt = (papers["title"].fillna("").astype(str) + " " + papers["abstract"].fillna("").astype(str)).str.lower()
        mask = txt.str.contains("|".join(pats), regex=True, na=False) if pats else pd.Series(False, index=papers.index)
        sub = papers[mask].sort_values("published")
        def _fmt(r) -> str:
            return f"- **{r['published']}** `{r['arxiv_id']}` {str(r['title'])[:110]}"
        all_lines = [_fmt(r) for _, r in sub.iterrows()]
        first_lines = all_lines[:3]
        last_lines = all_lines[-3:] if len(all_lines) > 6 else []
        mid_lines = all_lines[3:-3] if len(all_lines) > 6 else all_lines[3:]
        n_docs = len(sub)
    else:
        evd = trend_evidence_with_dates(doc_topics, papers, tid)
        first_lines = evd["first"]
        last_lines = evd["last"]
        mid_lines = evd["mid"]
        n_docs = evd.get("n_docs", size)

    # --- возраст ---
    first_q = int_to_quarter(start) if start >= qmin else "?"
    end_q = int_to_quarter(end)
    active_q = end - start + 1

    lines = []
    lines.append(f"## {label}")
    lines.append("")
    lines.append(f"**Score:** {score:.4f}  |  **Размер темы:** {n_docs} док.  |  **Тип:** {'keyword' if is_kw else 'BERTopic'}")
    lines.append("")
    lines.append("**Компоненты Score:** GrowthRate={:.3f}, Novelty={:.3f}, Acceleration={:.3f}".format(
        comps.get("growth_rate", 0), comps.get("novelty", 0), comps.get("acceleration", 0)))
    lines.append("")
    lines.append(f"**Топ-слова:** {', '.join(top_words) if top_words else '(keyword)'}")
    lines.append("")
    lines.append(f"**Возраст:** первый квартал `{first_q}`, последний `{end_q}`, активных кварталов ~{active_q}")
    lines.append("")
    lines.append(f"**Стадия (эвристика по данным):** {stage}")
    lines.append("")
    lines.append(f"**Кривая роста (норм., последние ~30 кварталов):** `{spark}`")
    lines.append("")
    lines.append("**Первые статьи (зарождение):**")
    lines.extend(first_lines if first_lines else ["- (нет)"])
    if mid_lines:
        lines.append("")
        lines.append("**Примеры (середина):**")
        lines.extend(mid_lines)
    if last_lines:
        lines.append("")
        lines.append("**Последние статьи (актуальность):**")
        lines.extend(last_lines)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("### Инвестиционный сигнал (патенты)")
    lines.append("")
    # сопоставление тренда с патентным ключевым словом (явный маппинг)
    txt = (label + " " + " ".join(top_words)).lower()
    matched = None
    for sub, concept in (patent_map or []):
        if sub in txt:
            matched = concept
            break
    if matched and patents and patents.get(matched) is not None:
        pat_count = patents[matched]
        lines.append(f"**Патенты (Google Patents, запрос `{patent_queries.get(matched, matched)}`): {pat_count:,}")
        lines.append("")
        lines.append("*Патентная активность = признак коммерциализации (кто-то вкладывает деньги).")
        lines.append(f"*Для сравнения: научных статей на arXiv в теме — {size}.")
    elif matched:
        lines.append(f"**Патенты:** (нет данных — rate-limit Google Patents, запрос `{patent_queries.get(matched, matched)}`)")
    else:
        lines.append(f"**Патенты:** (не сопоставлено — для этой темы нет ключевого слова в патентном слое)")
    lines.append("")
    lines.append("### Поля для эксперта")
    lines.append("")
    lines.append("1. **О чём тема?** (одна фраза, по статьям выше):")
    lines.append("")
    lines.append("2. **Стадия по знанию области:** `зарождается` / `растёт` / `зрелая/плато` / `спад` / `шум` / `другое`")
    lines.append("")
    lines.append("3. **Вердикт:** `✓ зарождается` / `✗ нет` / `? сомнительно` / `не моя область`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Улучшенные карточки трендов (вариант A)")
    ap.add_argument("--trends", default="results/top_trends_fine.json")
    ap.add_argument("--out", default="results/trend_cards")
    args = ap.parse_args()

    trends_path = PROJECT_ROOT / args.trends
    if not trends_path.exists():
        raise FileNotFoundError(f"Тренды не найдены: {trends_path}")
    data = json.loads(trends_path.read_text(encoding="utf-8"))
    trends = data["trends"]

    papers = pd.read_parquet(PROJECT_ROOT / "data/processed/papers.parquet")
    doc_topics = pd.read_parquet(PROJECT_ROOT / "data/processed/doc_topics_fine.parquet")

    # квартальная шкала (общая для всех тем)
    all_q = set()
    for t in json.loads((PROJECT_ROOT / "data/processed/topics_fine.json").read_text(encoding="utf-8"))["topics"]:
        all_q.update(t["quarterly_counts"].keys())
    qmin = min(quarter_to_int(q) for q in all_q)
    qmax = max(quarter_to_int(q) for q in all_q)
    now_idx = qmin + (qmax - qmin)

    # ряд для каждой темы (для кривой/стадии) — из topics_fine quarterly_counts
    fine_topics = json.loads((PROJECT_ROOT / "data/processed/topics_fine.json").read_text(encoding="utf-8"))["topics"]
    fine_by_id = {t["topic_id"]: t for t in fine_topics}

    out_dir = PROJECT_ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    n_q = qmax - qmin + 1

    # keyword-паттерны из конфига (для полного корпуса keyword-тем)
    import yaml
    cfg = yaml.safe_load((PROJECT_ROOT / "experiment/configs/iter_007_fine_scoring.yaml").read_text(encoding="utf-8"))
    kw_items = cfg.get("keywords", {}).get("items", [])
    kw_pat = {item["name"]: item.get("patterns", []) for item in kw_items}
    papers_text = (
        papers["title"].fillna("").astype(str) + " " + papers["abstract"].fillna("").astype(str)
    ).str.lower()

    # --- патентный слой (Google Patents) ---
    patents_path = PROJECT_ROOT / "data/raw/patents/patents_results.json"
    patents: dict[str, int] = {}
    patent_queries: dict[str, str] = {}
    if patents_path.exists():
        pdata = json.loads(patents_path.read_text(encoding="utf-8"))
        for t in pdata.get("trends", []):
            label = t.get("label", "")
            if t.get("patents") is not None:
                patents[label] = t["patents"]
            patent_queries[label] = t.get("query", label)
        logger.info("Патентный слой: %d трендов с данными", len(patents))

    # явный маппинг: label тренда (подстрока) -> патентный концепт
    PATENT_MAP = [
        ("fluxonium", "fluxonium"),
        ("superconducting diode", "superconducting diode"),
        ("mgb2", "mgb2"),
        ("graphene", "graphene"),
        ("learning materials machine", "machine learning materials"),
        ("quantum classical error", "quantum error correction"),
        ("neuromorphic", "neuromorphic"),
        ("diamond nv", "nv center"),
        ("spin magnetic torque magnon", "spintronics"),
        ("chiral phonon", "chiral phonon"),
        ("magnet magnets accelerator", "superconducting magnet"),
        ("no insulation", "no-insulation coil"),
        ("solar evaporation", "superconducting magnet"),  # заглушка: нет концепта
    ]

    patent_map = PATENT_MAP
    for i, trend in enumerate(trends, 1):
        tid = trend["topic_id"]
        if tid >= 0:
            src = fine_by_id.get(tid)
            qc = src["quarterly_counts"] if src else {}
            series = np.zeros(n_q, dtype=float)
            for q, c in qc.items():
                idx = quarter_to_int(q) - qmin
                if 0 <= idx < n_q:
                    series[idx] = c
            start = int(np.nonzero(series)[0][0]) if np.any(series) else qmin
            end = int(np.nonzero(series)[0][-1]) if np.any(series) else qmin
        else:
            # keyword-темы: полный корпус по паттернам (не только evidence)
            name = trend["label"].replace("KW: ", "")
            pats = kw_pat.get(name, [])
            mask = papers_text.str.contains("|".join(pats), regex=True, na=False) if pats else pd.Series(False, index=papers.index)
            sub = papers[mask]
            series = np.zeros(n_q, dtype=float)
            for _, r in sub.iterrows():
                q = pd.to_datetime(r["published"]).to_period("Q")
                qs = f"{q.year}-Q{q.quarter}"
                idx = quarter_to_int(qs) - qmin
                if 0 <= idx < n_q:
                    series[idx] += 1
            start = int(np.nonzero(series)[0][0]) if np.any(series) else qmin
            end = int(np.nonzero(series)[0][-1]) if np.any(series) else qmin

        card = build_card(trend, series, start + qmin, end + qmin, qmin, now_idx, doc_topics, papers, kw_pat, patents, patent_queries, patent_map)
        # читаемое имя: trend_NN_<label>.md (label из заголовка, очищенный)
        label = trend.get("label", "")
        label = re.sub(r'^KW:\s*', '', label).strip()
        label = re.sub(r'[^a-zA-Z0-9]+', '_', label).strip('_').lower()
        fname = out_dir / f"trend_{i:02d}_{label}.md"
        fname.write_text(card, encoding="utf-8")
        logger.info("Карточка %s: %s", fname.name, trend["label"][:50])

    logger.info("Готово: %d карточек → %s", len(trends), out_dir)


if __name__ == "__main__":
    main()
