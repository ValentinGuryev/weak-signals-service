"""Общие утилиты пайплайна: логгирование, конфиги, пути.

Конвенции (внутренний контракт, раздел 9):
- Python 3.11+, type hints обязательны.
- Логирование через `logging`, не `print`.
- Конфиги: YAML в experiment/configs/.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import yaml

# Корень проекта: src/utils.py -> уровень проекта
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Настроить корневой логгер: один handler, формат с временем и уровнем."""
    logger = logging.getLogger("trends")
    if not logger.handlers:  # не дублировать handler при повторных вызовах
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def load_config(path: str | Path) -> dict[str, Any]:
    """Загрузить YAML-конфиг из experiment/configs/."""
    p = Path(path)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    if not p.exists():
        raise FileNotFoundError(f"Конфиг не найден: {p}")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def data_raw() -> Path:
    """Путь к data/raw/ (сырые дампы, НЕ удалять)."""
    p = PROJECT_ROOT / "data" / "raw"
    p.mkdir(parents=True, exist_ok=True)
    return p


def data_processed() -> Path:
    """Путь к data/processed/ (очищенные данные)."""
    p = PROJECT_ROOT / "data" / "processed"
    p.mkdir(parents=True, exist_ok=True)
    return p


def data_cache() -> Path:
    """Путь к data/cache/ (кэш API, можно удалять)."""
    p = PROJECT_ROOT / "data" / "cache"
    p.mkdir(parents=True, exist_ok=True)
    return p


def results_dir() -> Path:
    """Путь к results/ (итоговые артефакты)."""
    p = PROJECT_ROOT / "results"
    p.mkdir(parents=True, exist_ok=True)
    return p


def ensure_parent(path: str | Path) -> Path:
    """Создать родительские директории для файла и вернуть Path."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p
