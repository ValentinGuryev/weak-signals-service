"""Запросы к BigQuery Public Datasets (Google Patents + arXiv).

Требуется:
1. GCP-аккаунт (бесплатный, https://cloud.google.com) — создаёт автор;
2. `gcloud auth application-default login` ИЛИ env GOOGLE_APPLICATION_CREDENTIALS
   (сервис-аккаунт). Библиотека: pip install google-cloud-bigquery.

Примеры запросов:
- Патенты по ключевым словам тренда (Google Patents Public Dataset, bigquery-public-data.google_patents_research);
- Связка «статья arXiv ↔ патент» (если доступна);
- Динамика патентов по годам.

Внимание: credentials НЕ коммитить (в .gitignore).
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from google.cloud import bigquery

logger = logging.getLogger("bq")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Публичный проект Google
PROJECT = "bigquery-public-data"

# Известные таблицы Google Patents (проверить актуальные имена после подключения)
PATENT_TABLES = [
    "bigquery-public-data.google_patents_research.publications",
    "bigquery-public-data.patents.publications",
    "bigquery-public-data.google_patents.publications",
]


def check_connection() -> bool:
    """Проверить доступ и найти актуальные патентные таблицы."""
    client = bigquery.Client(project=PROJECT) if False else bigquery.Client()
    logger.info("Подключение к BigQuery…")
    # список датасетов bigquery-public-data
    datasets = list(client.list_datasets(project=PROJECT, max_results=200))
    names = sorted(d.dataset_id for d in datasets)
    logger.info("Датасетов в bigquery-public-data: %d", len(names))
    pat = [n for n in names if "patent" in n.lower()]
    arx = [n for n in names if "arxiv" in n.lower()]
    logger.info("Патентные датасеты: %s", pat)
    logger.info("arXiv датасеты: %s", arx)
    return True


def query_patents(client: bigquery.Client, keyword: str, limit: int = 10) -> None:
    """Поиск патентов по ключевому слову в title/abstract (Google Patents)."""
    # Таблица может отличаться — пробуем по очереди
    for table in PATENT_TABLES:
        sql = f"""
        SELECT publication_number, title, filing_date, grant_date
        FROM `{table}`
        WHERE LOWER(title) LIKE '%{keyword.lower()}%'
        LIMIT {limit}
        """
        try:
            rows = client.query(sql).result()
            data = [dict(r) for r in rows]
            logger.info("Таблица %s: %d патентов по '%s'", table, len(data), keyword)
            for d in data[:5]:
                logger.info("  - %s %s %s", d.get("filing_date"), d.get("publication_number"), str(d.get("title"))[:60])
            return
        except Exception as e:
            logger.warning("Таблица %s не сработала: %s", table, str(e)[:100])
    logger.error("Не удалось найти рабочую таблицу патентов")


def main() -> None:
    ap = argparse.ArgumentParser(description="BigQuery: Google Patents / arXiv")
    ap.add_argument("--check", action="store_true", help="проверить подключение и список датасетов")
    ap.add_argument("--keyword", default="superconducting diode", help="ключевое слово для поиска патентов")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()

    client = bigquery.Client()
    if args.check:
        check_connection()
    else:
        query_patents(client, args.keyword, args.limit)


if __name__ == "__main__":
    main()
