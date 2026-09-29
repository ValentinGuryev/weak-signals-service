"""Построить графики тем (количество статей по годам) для всех тем BERTopic.

Темы: data/processed/topics_fine.json (199 тем + outlier, quarterly_counts 2006-2026).
Выход: experiment/topic_plots/*.png (по одной на тему) + summary.csv + топ-лист
       тем с экспоненциальным ростом ≥5 лет (как superconducting diode).
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from utils import PROJECT_ROOT

TOPICS = PROJECT_ROOT / "data" / "processed" / "topics_fine.json"
OUT_DIR = PROJECT_ROOT / "experiment" / "topic_plots"


def quarterly_to_yearly(qc: dict) -> dict[str, int]:
    """Свернуть quarterly_counts в годовые."""
    yearly: dict[str, int] = {}
    for q, n in qc.items():
        year = q.split("-")[0]
        yearly[year] = yearly.get(year, 0) + n
    return yearly


def growth_metrics(yearly: dict[str, int], min_horizon: int = 5) -> dict:
    """Метрики роста: экспоненциальный рост на горизонте >= min_horizon лет."""
    years = sorted(yearly.keys())
    if len(years) < min_horizon + 2:
        return {"exp_growth_5y": False, "best_growth": 0, "best_start": None, "best_end": None}

    best_growth = 0
    best_start = best_end = None
    exp_growth = False
    # скользящее окно min_horizon лет: рост конца окна vs начала
    for i in range(len(years) - min_horizon):
        start_y = years[i]
        end_y = years[i + min_horizon]
        n_start = sum(yearly.get(str(y), 0) for y in range(int(start_y), int(start_y) + 1))
        n_end = sum(yearly.get(str(y), 0) for y in range(int(end_y) - 1, int(end_y)))
        n_mid = sum(yearly.get(str(y), 0) for y in range(int(start_y), int(end_y)))
        # рост: последний год окна vs первый, с учётом размера
        if n_start >= 5 and n_end >= 2 * n_start:
            ratio = n_end / max(n_start, 1)
            if ratio > best_growth:
                best_growth = ratio
                best_start, best_end = start_y, end_y
    # экспоненциальный: рост > 2x за окно И ускорение (рост нарастает)
    if best_start and best_end:
        exp_growth = best_growth > 2.0
    return {"exp_growth_5y": exp_growth, "best_growth": round(best_growth, 2),
            "best_start": best_start, "best_end": best_end}


def current_state(yearly: dict[str, int]) -> str:
    """Текущее состояние темы (2024-2026): рост / спад / плато."""
    years = sorted(yearly.keys())
    if len(years) < 4:
        return "мало данных"
    last3 = sum(yearly.get(y, 0) for y in years[-3:])
    prev3_years = years[-6:-3]
    prev3 = sum(yearly.get(y, 0) for y in prev3_years) if len(prev3_years) == 3 else 1
    if prev3 <= 0:
        return "мало данных"
    ratio = last3 / max(prev3, 1)
    if ratio > 1.3:
        return "рост"
    if ratio < 0.7:
        return "спад"
    return "плато"


def main() -> None:
    topics_data = json.loads(TOPICS.read_text(encoding="utf-8"))
    topics = topics_data["topics"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    exp_topics: list[dict] = []

    for t in topics:
        if t["topic_id"] == -1:  # outlier
            continue
        label = t.get("label") or f"topic_{t['topic_id']}"
        top_words = ", ".join(t.get("top_words", [])[:8])
        qc = t.get("quarterly_counts", {})
        yearly = quarterly_to_yearly(qc)
        if not yearly:
            continue
        g = growth_metrics(yearly)
        state = current_state(yearly)
        rows.append({
            "topic_id": t["topic_id"], "label": label, "top_words": top_words,
            "size": t.get("size", 0), "current_state": state, **g,
        })
        if g["exp_growth_5y"]:
            exp_topics.append({"topic_id": t["topic_id"], "label": label,
                               "top_words": top_words, "size": t.get("size", 0),
                               "current_state": state, **g})

        # график: статьи по годам
        ys = sorted(yearly.keys())
        counts = [yearly[y] for y in ys]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(ys, counts, color="#4C72B0")
        ax.set_title(f"#{t['topic_id']} {label}\n{top_words}", fontsize=10)
        ax.set_xlabel("Год")
        ax.set_ylabel("Статей")
        ax.tick_params(axis="x", rotation=45)
        plt.tight_layout()
        plt.savefig(OUT_DIR / f"topic_{t['topic_id']:03d}_{re.sub(r'[^a-zA-Z0-9]+', '_', label).strip('_').lower()}.png", dpi=80)
        plt.close(fig)

    # summary.csv
    with open(OUT_DIR / "summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # топ экспоненциальных тем
    exp_topics.sort(key=lambda x: -x["best_growth"])
    with open(OUT_DIR / "exp_growth_topics.json", "w", encoding="utf-8") as f:
        json.dump(exp_topics, f, ensure_ascii=False, indent=2)

    print(f"Тем всего: {len(rows)}, экспоненциальный рост >=5 лет: {len(exp_topics)}")
    print("\n=== ТОП-20 тем с экспоненциальным ростом (как superconducting diode) ===")
    for e in exp_topics[:20]:
        print(f"  #{e['topic_id']:3d} {e['label'][:45]:47s} рост {e['best_growth']}x | {e['best_start']}→{e['best_end']} | size={e['size']}")


if __name__ == "__main__":
    main()
