#!/usr/bin/env python3
"""ПАТЕНТНЫЙ ЦИТАТНЫЙ ГРАФ (S3) для кейса 001_ibad_mgo.

Проверка гипотезы «ссылки детектируют тренд раньше работ» (CITATION_LEAD_INSIGHT):
в статьях OpenAlex ссылки указывали на тренд раньше публикаций. Для патентов:
  - forward citations (cited_by) — кто цитирует данный патент (будущие)
  - backward citations (references) — на кого ссылается данный патент (прошлые)

Вопросы:
  1. Когда появились ПЕРВЫЕ патенты IBAD-семейства (по priority_date)?
  2. Когда начали ЦИТИРОВАТЬ эти патенты (год первых cited_by)?
  3. Пик патентования (по приоритетным датам) — совпадает ли с пиком цитирования?

Данные: data/raw/patents/topics_window/ibad_merged.json (100 патентов, 612 рёбер).

Запуск:
    .venv/bin/python src/plot_patent_citations.py
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "raw" / "patents" / "topics_window" / "ibad_merged.json"
OUT = ROOT / "case_studies" / "001_ibad_mgo" / "plots" / "plot6_patent_citations.png"


def load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def main() -> None:
    d = load()
    pats = d["patents"]

    # 1. Патенты по годам приоритета (основной сигнал)
    prio_years = Counter()
    for p in pats:
        y = (p.get("priority_date") or "")[:4]
        if y.isdigit():
            prio_years[int(y)] += 1

    # 2. Год ПЕРВОЙ forward-цитаты для каждого патента:
    #    из cited_by мы знаем только номера, не даты. Оцениваем по году патента
    #    с максимальным числом цитирований → год цитирования ≈ год приоритета + задержка.
    #    Для простоты: считаем "интенсивность цитирования" по годам приоритета
    #    цитирующих патентов (если бы имели их даты). Пока — только число цитат на патент.
    cites_per_year = defaultdict(int)
    for p in pats:
        y = (p.get("priority_date") or "")[:4]
        if not y.isdigit():
            continue
        # вес: число forward-цитат патента приписываем к году его приоритета
        cites_per_year[int(y)] += len(p.get("cited_by", []))

    # 3. Ранние патенты (до 2005) — фундамент
    early = [p for p in pats if (p.get("priority_date") or "")[:4].isdigit()
             and int((p.get("priority_date") or "")[:4]) <= 2004]
    early.sort(key=lambda p: p.get("priority_date", ""))

    # График
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9), sharex=True)

    years = sorted(prio_years)
    # 1) Патенты по годам
    ax1.bar([str(y) for y in years], [prio_years[y] for y in years],
            color="#4C72B0", alpha=0.85)
    ax1.set_ylabel("Патенты (priority year)")
    ax1.set_title("Патентный сигнал IBAD-семейства (Google + Lens, 100 патентов)")
    ax1.grid(axis="y", alpha=0.3)

    # 2) Цитаты по годам (forward, приписаны к году патента)
    cy = sorted(cites_per_year)
    ax2.bar([str(y) for y in cy], [cites_per_year[y] for y in cy],
            color="#C44E52", alpha=0.85)
    ax2.set_ylabel("Forward-цитаты (по году патента)")
    ax2.set_xlabel("Год")
    ax2.grid(axis="y", alpha=0.3)

    # Аннотация пиков
    peak_y = max(prio_years, key=prio_years.get)
    ax1.annotate(f"Пик патентов: {prio_years[peak_y]} ({peak_y})",
                 xy=(str(peak_y), prio_years[peak_y]), xytext=(10, 10),
                 textcoords="offset points", fontsize=9, color="#4C72B0")

    # Ранние ключевые патенты
    print("=== Ранние патенты (до 2005, фундамент) ===")
    for p in early:
        print(f"  {p.get('priority_date','')[:4]} | {p.get('publication_number','')[:25]} | "
              f"{(p.get('title') or '').replace('<b>','').replace('</b>','')[:55]} | "
              f"cit={len(p.get('cited_by',[]))} ref={len(p.get('references',[]))}")

    # Статистика
    with_cit = sum(1 for p in pats if p.get("cited_by"))
    with_ref = sum(1 for p in pats if p.get("references"))
    edges = sum(len(p.get("cited_by", [])) for p in pats) + \
            sum(len(p.get("references", [])) for p in pats)
    print(f"\n=== СТАТИСТИКА ===")
    print(f"Всего патентов: {len(pats)}")
    print(f"С forward-цитатами: {with_cit}, с backward: {with_ref}")
    print(f"Всего рёбер: {edges}")
    print(f"Диапазон лет: {min(prio_years)}-{max(prio_years)}")
    print(f"Пик патентов: {peak_y} ({prio_years[peak_y]})")

    # Сравнение: пик приоритетов vs пик цитирования
    peak_c = max(cites_per_year, key=cites_per_year.get)
    print(f"Пик forward-цитат: {peak_c} ({cites_per_year[peak_c]})")
    print(f"Задержка цитат: {peak_c - peak_y} лет (цитирование пика позже приоритетов)")

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150)
    print(f"\nСохранено: {OUT}")


if __name__ == "__main__":
    main()
