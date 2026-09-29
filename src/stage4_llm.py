"""Этап 4: карточки трендов (шаблонно-эвристически; LLM — отложен).

Вход: results/top_trends.json (тренды с Score, компонентами, evidence).
Выход: results/trend_cards/*.md — карточки: проблема, преимущество, кейс, источник.

Решения (внутренний контракт §11.1, Фаза 4):
- Шаблонная генерация: топ-слова, репрезентативные статьи, темпы роста.
- LLM-место зарезервировано: интерфейс generate_card(trend) с try/except и таймаутом 60 сек.

Карточка (для жюри):
1. Название тренда (label + топ-слова)
2. Score и компоненты (GrowthRate, Novelty, Acceleration)
3. Проблема, которую решает (эвристически по топ-словам)
4. Преимущество/выгода
5. Кейс-пример (репрезентативные статьи из evidence)
6. Источник (arXiv id)
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from utils import PROJECT_ROOT, load_config, setup_logging

logger = setup_logging()

# Шаблонные «проблема/преимущество» по ключевым словам темы (эвристика).
# Если тема не матчится — общие формулировки.
PROBLEM_TEMPLATES: list[tuple[set[str], str, str]] = [
    ({"superconduct", "mgb2", "ybco", "rebco", "cuprate", "critical current", "pinning", "vortex"},
     "Повышение критических характеристик сверхпроводников (ток, поле, температура) для практических применений.",
     "Более эффективные и доступные сверхпроводящие материалы и устройства."),
    ({"quantum", "qubit", "quantum computing", "quantum codes", "error correction", "decoherence"},
     "Построение отказоустойчивых квантовых вычислений (борьба с декогеренцией и ошибками).",
     "Вычислительная мощность, недостижимая классическими компьютерами."),
    ({"machine", "learning", "ml", "neural", "materials", "prediction", "ai"},
     "Ускорение поиска и проектирования новых материалов (ML-предсказания свойств).",
     "Сокращение времени и стоимости разработки материалов."),
    ({"perovskite", "solar", "photovoltaic", "halide"},
     "Недорогие и эффективные солнечные элементы (перовскиты).",
     "Доступная солнечная энергетика."),
    ({"resonator", "microwave", "niobium", "cavity", "quality factor"},
     "Улучшение сверхпроводящих резонаторов (высокая добротность) для квантовых и RF-приложений.",
     "Качественные квантовые устройства и ускорители."),
    ({"detector", "nanowire", "single photon", "superconducting detector"},
     "Сверхчувствительные детекторы одиночных фотонов (SNSPD).",
     "Квантовая криптография, сенсорика, медицина."),
    ({"battery", "lithium", "li-ion", "energy storage"},
     "Улучшение литий-ионных аккумуляторов (ёмкость, срок службы, безопасность).",
     "Эффективное хранение энергии."),
    ({"nv", "diamond", "nitrogen vacancy", "quantum sensing"},
     "Квантовые сенсоры на NV-центрах в алмазе.",
     "Сверхточные измерения магнитных полей, температуры."),
    ({"magnetic", "ferromagnet", "magnetization", "spintronic"},
     "Управление магнитными свойствами (спинтроника).",
     "Новая электроника на спине, память."),
]

DEFAULT_PROBLEM = "Развитие перспективного направления в физике/материаловедении."
DEFAULT_ADVANTAGE = "Новые возможности и применения в науке и технике."


def generate_card(trend: dict[str, Any], n_evidence: int = 3) -> dict[str, str]:
    """Сгенерировать карточку тренда (шаблонно). Интерфейс для будущего LLM."""
    label = trend.get("label", "")
    top_words = trend.get("top_words", [])
    score = trend.get("score", 0.0)
    comps = trend.get("components", {})
    evidence = trend.get("evidence", [])[:n_evidence]

    # --- проблема/преимущество по топ-словам ---
    problem, advantage = DEFAULT_PROBLEM, DEFAULT_ADVANTAGE
    joined = " ".join(top_words).lower()
    for keywords, p, a in PROBLEM_TEMPLATES:
        if any(kw in joined for kw in keywords):
            problem, advantage = p, a
            break

    # --- кейс: репрезентативные статьи ---
    if evidence:
        case = "Представительные работы:\n" + "\n".join(f"- arXiv:{e}" for e in evidence)
    else:
        case = "Представительные работы: (нет данных по статьям в этой выборке)."

    return {
        "title": label[:80] if label else "Тренд",
        "score": f"{score:.3f}",
        "growth_rate": f"{comps.get('growth_rate', 0):.3f}",
        "novelty": f"{comps.get('novelty', 0):.3f}",
        "acceleration": f"{comps.get('acceleration', 0):.3f}",
        "problem": problem,
        "advantage": advantage,
        "case": case,
        "source": ", ".join(evidence) if evidence else "arXiv (аннотации)",
    }


def card_to_markdown(card: dict[str, str]) -> str:
    """Карточка в Markdown."""
    return f"""## {card['title']}

**Score:** {card['score']} (GrowthRate={card['growth_rate']}, Novelty={card['novelty']}, Acceleration={card['acceleration']})

**Проблема:** {card['problem']}

**Преимущество:** {card['advantage']}

**Кейс:**
{card['case']}

**Источник:** {card['source']}
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Этап 4: карточки трендов (шаблонно)")
    ap.add_argument("--config", default="experiment/configs/iter_004.yaml")
    args = ap.parse_args()

    cfg = load_config(args.config)
    trends_path = PROJECT_ROOT / cfg["input"]
    if not trends_path.exists():
        raise FileNotFoundError(f"Тренды не найдены: {trends_path}")
    data = json.loads(trends_path.read_text(encoding="utf-8"))
    trends = data["trends"]

    out_dir = PROJECT_ROOT / cfg["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Генерация карточек: %d трендов → %s", len(trends), out_dir)
    for i, trend in enumerate(trends, 1):
        card = generate_card(trend)
        fname = out_dir / f"trend_{i:02d}.md"
        fname.write_text(card_to_markdown(card), encoding="utf-8")
        logger.info("Карточка %s: %s", fname.name, card["title"])


if __name__ == "__main__":
    main()
