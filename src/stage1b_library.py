"""Этап 1b: интеграция локальной библиотеки MD-выжимок в датасет.

Источник: MD-выжимки статей по всем проектам /home/user/projects (кроме Hackathon),
первая строка которых начинается с "(Год)" — это выжимки статей (не аналитические заметки).
Формат имени: (Год)[!!!] Автор — Название (как в Hackathon/literature).

Выход: data/processed/library_meta.json + дополнение papers.parquet колонками source.
Правило (внутренний контракт): не менять data/raw, models, literature. Пишем только в data/processed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from utils import data_processed, setup_logging

logger = setup_logging()

PROJECTS_ROOT = Path("/home/user/projects")
EXCLUDE_DIRS = {"Hackathon", "node_modules", "__pycache__", ".git"}

# Паттерн первой строки выжимки: # (Год)[маркеры] Авторы — Название
# Год может быть в начале ((2014) Xu ...) или в конце (... (2022)).
HEADER_RE = re.compile(
    r"^\s*#\s*(?:Выжимка|Аннотация)?\s*:?\s*"
    r"(?P<before>.*?)\s*"
    r"\((?P<year>\d{4})\)\s*"
    r"(?P<rel>[!_]*) "
    r"(?P<after>.*?)\s*$"
)


def find_summaries(root: Path) -> list[Path]:
    """Найти все .md-выжимки: первая непустая строка содержит (Год)."""
    out: list[Path] = []
    for p in root.rglob("*.md"):
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        try:
            first = next(
                (l for l in p.read_text(encoding="utf-8", errors="replace").splitlines()
                 if l.strip()),
                "",
            )
        except OSError:
            continue
        if re.search(r"\(\d{4}\)", first):
            out.append(p)
    return out


def parse_summary(path: Path) -> dict[str, Any] | None:
    """Спарсить метаданные выжимки: год, авторы, название, библиография, DOI + полный текст."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    nonempty = [l.strip() for l in lines if l.strip()]
    if not nonempty:
        return None
    first = nonempty[0]
    m = HEADER_RE.match(first)
    if not m:
        return None
    year = int(m.group("year"))
    rel = m.group("rel").replace("_", "").replace("!", "").strip()
    # Название: объединяем всё, что до и после (Год), убирая маркеры и префиксы
    before = re.sub(r"^(Выжимка|Аннотация)\s*:?\s*", "", m.group("before")).strip()
    after = re.sub(r"^(?:[!_]+\s*)+|^(?:[!_])\s*", "", m.group("after")).strip()
    title = (before + " " + after).strip()
    title = re.sub(r"\s+", " ", title)
    title = title.strip("# ").strip()

    # Полный текст выжимки: минус служебные секции.
    # Служебные секции могут быть:
    #   (а) в КОНЦЕ: "## Связь с проектом" после контента -> тело ДО них;
    #   (б) в НАЧАЛЕ: "**Релевантность проекту...**" сразу после заголовка -> тело ПОСЛЕ.
    CUT_MARKERS = [
        "связь с проектом", "применение к проекту", "релевантность проекту",
        "применение в проекте", "значение для проекта", "использование в проекте",
        "проектные выводы", "выводы для проекта", "значимость для нашего проекта",
        "значимость для проекта", "для нашего проекта", "применение в нашем проекте",
    ]

    def _is_cut(l: str) -> bool:
        ll = l.lower()
        return any(m in ll for m in CUT_MARKERS) and (
            l.startswith("#") or l.startswith("**") or l.startswith("---")
        )

    # Первая служебная секция
    first_cut = next((i for i, l in enumerate(nonempty) if _is_cut(l)), None)

    def _body(begin: int, end: int) -> str:
        return "\n".join(
            l for l in nonempty[begin:end] if not l.startswith("---")
        ).strip()

    if first_cut is None:
        # Служебных нет: тело = всё после заголовка+библиографии
        body = _body(3, len(nonempty))
    elif first_cut <= 4:
        # Служебная сразу после заголовка: тело ПОСЛЕ неё
        body = _body(first_cut + 1, len(nonempty))
    else:
        # Служебная в конце: тело ДО неё (от 3-й строки)
        body = _body(3, first_cut)
    # Если после служебной в начале снова есть служебные — обрезать хвост
    if first_cut is not None and first_cut <= 4:
        body_lines = body.split("\n")
        end = next((i for i, l in enumerate(body_lines) if _is_cut(l)), len(body_lines))
        body = "\n".join(body_lines[:end]).strip()

    rec: dict[str, Any] = {
        "file": str(path.relative_to(PROJECTS_ROOT)),
        "project": path.parts[len(PROJECTS_ROOT.parts)],
        "year": year,
        "title": title,
        "relevance": len(rel),  # число '!' = релевантность 0..5 (приблизительно)
        "source": "local_library",
        "summary": body,  # полный текст выжимки (контент для этапа 2)
    }
    # Библиография (2-3-я непустые строки) — ищем авторов и DOI
    meta_lines = " ".join(nonempty[1:4])
    # DOI
    doi = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", meta_lines, re.IGNORECASE)
    if doi:
        rec["doi"] = doi.group(0).rstrip(".,;")
    # Авторы из библиографии: строка с инициалами/фамилиями
    authors_match = re.search(
        r"(?:\b[A-ZА-ЯЁ][a-zа-яё]+(?:\s+[A-ZА-ЯЁ]\.?)+[,;]?\s*){2,}",
        meta_lines,
    )
    if authors_match:
        rec["authors_biblio"] = authors_match.group(0).strip().rstrip(",")
    # Год из библиографии (если в первой строке нет — из журнала)
    if "year_biblio" not in rec and rec.get("year"):
        pass
    return rec


def main() -> None:
    files = find_summaries(PROJECTS_ROOT)
    logger.info("Найдено MD-выжимок: %d", len(files))
    records: list[dict[str, Any]] = []
    skipped = 0
    for p in files:
        rec = parse_summary(p)
        if rec:
            records.append(rec)
        else:
            skipped += 1
    logger.info("Спарсено: %d, пропущено (не выжимки): %d", len(records), skipped)

    # Дедупликация по (year, title_lower)
    seen: set[tuple[int, str]] = set()
    unique: list[dict[str, Any]] = []
    for r in records:
        key = (r["year"], r["title"].lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    logger.info("Уникальных выжимок: %d", len(unique))

    # Классификация: core (маркеры сверхпроводимости в названии) / related (смежные)
    MARKERS = ["superconduct", "superconductor", "critical current", "flux pinning",
               "josephson", "mgb2", "ybco", "rebco", "cuprate", "pnictide",
               "hydride", "hts", "lts", "втсп", "сверхпровод", "крит", "лент",
               "coated conductor", "ibad", "провод"]
    for r in unique:
        t = (r["title"] + " ").lower()
        r["tier"] = "core" if any(m in t for m in MARKERS) else "related"
    n_core = sum(1 for r in unique if r["tier"] == "core")
    n_rel = sum(1 for r in unique if r["tier"] == "related")
    logger.info("Классификация: core=%d, related=%d", n_core, n_rel)

    out_path = data_processed() / "library_meta.json"
    out_path.write_text(
        json.dumps({"source": "local_library", "count": len(unique),
                    "records": unique}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Реестр -> %s", out_path)

    # Единый корпус для этапа 2: та же схема, что papers.parquet, + source/tier.
    # В корпус идут только выжимки с непустым телом (короткие карточки без контента
    # остаются в реестре метаданных, но не попадают в моделирование трендов).
    corpus_rows = []
    for i, r in enumerate(unique):
        body = r.get("summary", "").strip()
        if not body:
            continue
        corpus_rows.append({
            "arxiv_id": f"lib-{r['year']}-{i:04d}",
            "title": r["title"],
            "abstract": body,
            "published": pd.Timestamp(year=r["year"], month=6, day=15),  # mid-year (нет месяца)
            "authors": [],
            "categories": [],
            "doi": r.get("doi", ""),
            "keywords": [],
            "source": "local_library",
            "tier": r.get("tier", "related"),
        })
    corpus = pd.DataFrame(corpus_rows)
    corpus_path = data_processed() / "library_corpus.parquet"
    corpus.to_parquet(corpus_path, index=False)
    logger.info("Корпус -> %s (%d строк)", corpus_path, len(corpus))
    # Размеры контента
    lens = corpus["abstract"].str.len()
    logger.info("Длина summary: mean=%.0f, median=%.0f, min=%d, max=%d",
                lens.mean(), lens.median(), lens.min(), lens.max())

    # Сводка по проектам
    from collections import Counter
    c = Counter(r["project"] for r in unique)
    logger.info("По проектам: %s", dict(c))


if __name__ == "__main__":
    main()
