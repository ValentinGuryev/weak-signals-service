"""Этап 1: данные. Загрузка метаданных и аннотаций arXiv по сверхпроводимости.

Контракты (внутренний контракт, разделы 3, 4.4; docs/DATA.md):
- Источник: arXiv API (REST, без ключа), HTTPS. Лимит ~1 запрос/3 сек.
- Категории: cond-mat.supr-con + смежные (mtrl-sci, mes-hall, str-el, app-ph, quant-ph).
- Временное окно: 2006-01 … 2026-08.
- Выход: data/raw/*.json (сырые дампы, НЕ удалять) + data/processed/papers.parquet.
- Кэш ответов: data/cache/ (можно удалять).

Запуск: python src/stage1_ingest.py [--limit N] [--no-cache]
  --limit N    скачать максимум N статей (для dry/smoke; по умолчанию — всё)
  --no-cache   игнорировать кэш и перекачать
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import feedparser
import pandas as pd

from utils import data_cache, data_processed, data_raw, setup_logging

logger = setup_logging()

# --- Параметры (контракт docs/DATA.md) ---
API_URL = "https://export.arxiv.org/api/query"
BATCH_SIZE = 2000          # максимум arXiv отдаёт за один запрос
RATE_LIMIT_SEC = 3.0       # arXiv: ~1 запрос / 3 сек
RETRIES = 3                # попыток на сетевой сбой
RETRY_BACKOFF_SEC = 5.0    # стартовая задержка ретраев (5 -> 15 -> 45)
# Окно данных. ВАЖНО: arXiv принимает submittedDate только в формате YYYYMMDDHHMM.
DATE_FROM = "200601010000"
DATE_TO = "202612312359"

# Категории: основная + смежные (docs/DATA.md, раздел 3).
# Смежные категории загружаются с текстовым фильтром по маркерам сверхпроводимости.
# Решение: physics.acc-ph — берём (RF-резонаторы, магниты
# ускорителей = прикладная сверхпроводимость); physics.ins-det — НЕ берём.
CATEGORIES = [
    "cond-mat.supr-con",
    "cond-mat.mtrl-sci",
    "cond-mat.mes-hall",
    "cond-mat.str-el",
    "physics.app-ph",
    "physics.acc-ph",
    "quant-ph",
]

# Маркеры сверхпроводимости для title/abstract (docs/DATA.md, раздел 3).
SUPERCONDUCTIVITY_MARKERS = [
    "superconduct", "superconductor", "critical current", "flux pinning",
    "vortex pinning", "josephson", "mgb2", "ybco", "rebco", "cuprate",
    "pnictide", "iron-based superconductor", "hydride superconductor",
    "high-temperature superconductor", "hts ", "lts ",
    "superconducting qubit", "superconducting quantum",
]

# Категории, которые загружаем целиком (без текстового фильтра).
FULL_CATEGORIES = {"cond-mat.supr-con"}

# Годы окна 2006..2026. Пагинация идёт по годам (arXiv-рекомендация):
# при глубоком start (>10000) API с sortBy=submittedDate возвращает
# totalResults=1 — ложный выход из пагинации. Оконная пагинация это обходит.
YEARS = list(range(2006, 2027))
MAX_PAGES_PER_YEAR = 12  # защита: 12*2000 = 24000 >> любой год категории


def build_query(category: str, start: int, max_results: int, year: int | None = None) -> str:
    """Построить query-строку arXiv API для категории и окна дат.

    Формат дат — YYYYMMDDHHMM (arXiv не принимает ISO в submittedDate).
    Если задан year — запрос идёт по одному году (оконная пагинация).
    """
    if year is not None:
        date_range = f"submittedDate:[{year}01010000 TO {year}12312359]"
    else:
        date_range = f"submittedDate:[{DATE_FROM} TO {DATE_TO}]"
    # URL-кодирование обязательно: пробелы и ':' в query ломают URL.
    search = f"cat:{category} AND {date_range}"
    params = {
        "search_query": search,
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "ascending",
    }
    return urlencode(params)


def fetch_page(category: str, start: int, use_cache: bool, year: int | None = None) -> dict[str, Any]:
    """Скачать одну страницу (до 2000 записей) с кэшированием в data/cache/.

    Сетевые сбои (DNS, таймаут, 5xx) — транзиентные: до RETRIES попыток
    с экспоненциальной задержкой (5 -> 15 -> 45 сек).
    """
    query = build_query(category, start, BATCH_SIZE, year=year)
    year_tag = f"{year}_" if year is not None else ""
    cache_file = data_cache() / f"arxiv_{category.replace('.', '_')}_{year_tag}{start:06d}.json"

    if use_cache and cache_file.exists():
        logger.debug("cache hit: %s", cache_file.name)
        with cache_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        data["from_cache"] = True
        return data

    url = f"{API_URL}?{query}"
    feed = None
    last_err: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        try:
            logger.info("GET %s (попытка %d/%d)", url, attempt, RETRIES)
            feed = feedparser.parse(url)
            break
        except Exception as exc:  # транзиентные сетевые сбои
            last_err = exc
            wait = RETRY_BACKOFF_SEC * (2 ** (attempt - 1))
            logger.warning(
                "Сбой сети (попытка %d/%d): %s. Повтор через %.0f сек",
                attempt, RETRIES, exc, wait,
            )
            time.sleep(wait)
    if feed is None:
        raise RuntimeError(
            f"arXiv недоступен после {RETRIES} попыток (category={category}, start={start}): {last_err}"
        )

    if feed.bozo and feed.bozo_exception:
        raise RuntimeError(
            f"Ошибка парсинга arXiv (category={category}, start={start}): {feed.bozo_exception}"
        )

    data = {
        "query": query,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_results": int(feed.feed.get("opensearch_totalresults", 0)),
        "entries": [entry_to_dict(e) for e in feed.entries],
        "from_cache": False,
    }

    with cache_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return data


def entry_to_dict(entry: Any) -> dict[str, Any]:
    """Преобразовать запись feedparser в плоский dict (сырой дамп)."""
    authors = [a.get("name", "") for a in entry.get("authors", [])]
    categories = [t.get("term", "") for t in entry.get("tags", [])]
    doi = ""
    for link in entry.get("links", []):
        if link.get("rel") == "related" and link.get("title") == "doi":
            doi = link.get("href", "")
            break
    return {
        "id": entry.get("id", ""),
        "title": entry.get("title", ""),
        "summary": entry.get("summary", ""),
        "published": entry.get("published", ""),
        "updated": entry.get("updated", ""),
        "authors": authors,
        "categories": categories,
        "doi": doi,
        "comment": entry.get("arxiv_comment", ""),
        "journal_ref": entry.get("arxiv_journal_ref", ""),
    }


def parse_arxiv_id(entry_id: str) -> str:
    """Извлечь короткий arXiv id из полного URL."""
    return entry_id.rsplit("/", 1)[-1]


def is_superconductivity_relevant(rec: dict[str, Any]) -> bool:
    """Релевантность сверхпроводимости (docs/DATA.md, раздел 3)."""
    text = f"{rec['title']} {rec['summary']}".lower()
    return any(marker.lower() in text for marker in SUPERCONDUCTIVITY_MARKERS)


def deduplicate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Дедупликация по arXiv id (сохраняем первую запись)."""
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for rec in records:
        if rec["arxiv_id"] in seen:
            continue
        seen.add(rec["arxiv_id"])
        out.append(rec)
    return out


def fetch_category(category: str, use_cache: bool, limit: int | None) -> list[dict[str, Any]]:
    """Скачать категорию целиком: оконная пагинация по годам (YEARS).

    Ограничение arXiv: при глубоком start с sortBy=submittedDate API возвращает
    totalResults=1 (глюк) — поэтому пагинация по годам + защита MAX_PAGES_PER_YEAR.
    limit — предохранитель для dry/smoke (глобальный лимит применяется в main()).
    """
    records: list[dict[str, Any]] = []
    for year in YEARS:
        start = 0
        pages = 0
        while True:
            page = fetch_page(category, start, use_cache, year=year)
            entries = page["entries"]
            total = page["total_results"]
            logger.info(
                "category=%s year=%d start=%d got=%d total=%d",
                category, year, start, len(entries), total,
            )
            records.extend(entries)
            if limit is not None and len(records) >= limit:
                return records[:limit]
            pages += 1
            # Выход: пустая страница, достигнут total или защитный предел страниц.
            if not entries or start + BATCH_SIZE >= total or pages >= MAX_PAGES_PER_YEAR:
                break
            start += BATCH_SIZE
            if not page.get("from_cache"):
                time.sleep(RATE_LIMIT_SEC)  # лимит arXiv: пауза только после реального запроса
        if not page.get("from_cache"):
            time.sleep(RATE_LIMIT_SEC)  # пауза между годами
    return records


def apply_global_limit(records: list[dict[str, Any]], limit: int | None) -> list[dict[str, Any]]:
    """Обрезать итоговый датасет до глобального лимита (dry/smoke)."""
    if limit is not None and len(records) > limit:
        logger.info("global limit: %d -> %d", len(records), limit)
        return records[:limit]
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Этап 1: данные arXiv по сверхпроводимости")
    parser.add_argument("--limit", type=int, default=None, help="макс. число статей (dry/smoke)")
    parser.add_argument("--no-cache", action="store_true", help="игнорировать кэш")
    parser.add_argument("--categories", type=str, default=None,
                        help="категории через запятую (по умолчанию — все)")
    args = parser.parse_args()

    selected = args.categories.split(",") if args.categories else CATEGORIES
    unknown = set(selected) - set(CATEGORIES)
    if unknown:
        raise SystemExit(f"Неизвестные категории: {sorted(unknown)}")

    raw_dir = data_raw()
    processed_dir = data_processed()

    all_records: list[dict[str, Any]] = []
    for category in CATEGORIES:
        dump_file = raw_dir / f"arxiv_{category.replace('.', '_')}.json"
        if category not in selected:
            # Невыбранные категории берём из сырых дампов (data/raw/, НЕ перезаписываем).
            if dump_file.exists():
                with dump_file.open("r", encoding="utf-8") as f:
                    records = json.load(f)["entries"]
                logger.info("=== Категория: %s (из сырого дампа, %d) ===", category, len(records))
            else:
                logger.warning("Нет сырого дампа для %s — пропуск", category)
                continue
        else:
            logger.info("=== Категория: %s (загрузка) ===", category)
            raw_entries = fetch_category(category, use_cache=not args.no_cache, limit=args.limit)
            # Фильтрация: supr-con берём целиком, смежные — по маркерам.
            records = raw_entries if category in FULL_CATEGORIES else [
                r for r in raw_entries if is_superconductivity_relevant(r)]
            logger.info("category=%s raw=%d после фильтра=%d",
                        category, len(raw_entries), len(records))
            # Сырой дамп пишем только при полном прогоне (не затираем в dry/smoke).
            if args.limit is None:
                with dump_file.open("w", encoding="utf-8") as f:
                    json.dump({"category": category,
                               "fetched_at": datetime.now(timezone.utc).isoformat(),
                               "total": len(records), "entries": records},
                              f, ensure_ascii=False)
                logger.info("raw dump: %s (%d записей)", dump_file.name, len(records))
        all_records.extend(records)

    all_records = apply_global_limit(all_records, args.limit)

    # Единый нормализованный датасет.
    rows = []
    for rec in all_records:
        published = rec.get("published", "")
        try:
            pub_date = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ").date()
        except (ValueError, TypeError):
            pub_date = None
        rows.append({
            "arxiv_id": parse_arxiv_id(rec["id"]),
            "title": rec["title"],
            "abstract": rec["summary"],
            "published": pub_date,
            "authors": rec["authors"],
            "categories": rec["categories"],
            "doi": rec["doi"],
            "keywords": [],  # arXiv не даёт ключевых слов в API
        })

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["published"])
    df = deduplicate(df.to_dict("records"))

    out_path = processed_dir / "papers.parquet"
    pd.DataFrame(df).to_parquet(out_path, index=False)
    logger.info("ИТОГ: %d уникальных публикаций -> %s", len(df), out_path)
    if df:
        logger.info("Диапазон дат: %s .. %s", df[0]["published"], df[-1]["published"])
    else:
        logger.warning("Датасет пуст — проверьте фильтры и доступность arXiv API.")


if __name__ == "__main__":
    main()
