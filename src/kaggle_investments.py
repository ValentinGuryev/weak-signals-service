"""Kaggle-инвестиции: поиск сверхпроводящих/квантовых компаний в датасетах.

Загрузка и фильтрация Crunchbase-датасета инвестиций (Kaggle).
Данные до 2020 — базис; свежие раунды — ручной сбор (data/superconducting_investments.md).

Требует: kaggle-keys/kaggle-token.txt (токен KGAT_, в .gitignore).
Запуск: KAGGLE_API_TOKEN=... python src/kaggle_investments.py
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger("kaggle_inv")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOKEN_PATH = PROJECT_ROOT / "kaggle-keys" / "kaggle-token.txt"
DATASET = "arindam235/startup-investments-crunchbase"
LOCAL_CSV = PROJECT_ROOT / "data/kaggle/investments_VC.csv"

# Ключевые слова (без 'semiconductor' — слишком широко)
KEYWORDS = ["quantum", "superconduct", "cryogen", "magnetics"]


def read_token() -> str:
    if not TOKEN_PATH.exists():
        raise FileNotFoundError(f"Токен Kaggle не найден: {TOKEN_PATH}")
    m = re.search(r"KGAT_[a-f0-9]+", TOKEN_PATH.read_text(encoding="utf-8"))
    if not m:
        raise ValueError("Токен KGAT_ не найден в файле")
    return m.group(0)


def download() -> None:
    """Скачать датасет, если CSV ещё нет."""
    if LOCAL_CSV.exists():
        logger.info("CSV уже есть: %s", LOCAL_CSV)
        return
    token = read_token()
    os.environ["KAGGLE_API_TOKEN"] = token
    (PROJECT_ROOT / "data/kaggle").mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "-m", "kaggle", "datasets", "download", "-d", DATASET, "-p", str(PROJECT_ROOT / "data/kaggle")], check=True)
    import zipfile
    zips = list((PROJECT_ROOT / "data/kaggle").glob("*.zip"))
    for z in zips:
        with zipfile.ZipFile(z) as zf:
            zf.extractall(PROJECT_ROOT / "data/kaggle")
    logger.info("Скачано и распаковано")


def filter_investments(limit: int = 30) -> list[dict]:
    """Найти сверхпроводящие/квантовые компании с финансированием."""
    rows = list(csv.DictReader(open(LOCAL_CSV, encoding="utf-8", errors="ignore")))
    out = []
    for r in rows:
        blob = " ".join(str(r.get(k, "") or "") for k in ["name", "category_list", " market "]).lower()
        if any(k in blob for k in KEYWORDS):
            out.append(r)
    # сортировка по funding
    def fund(r):
        try:
            return float((r.get(" funding_total_usd ", "") or "0").replace(",", ""))
        except Exception:
            return 0.0
    out.sort(key=fund, reverse=True)
    return out[:limit]


def main() -> None:
    ap = argparse.ArgumentParser(description="Kaggle-инвестиции")
    ap.add_argument("--download", action="store_true", help="скачать датасет")
    ap.add_argument("--out", default="data/raw/investments/kaggle_investments_results.json")
    args = ap.parse_args()

    if args.download:
        download()

    hits = filter_investments()
    result = []
    for h in hits:
        result.append({
            "name": h.get("name", ""),
            "funding_total_usd": h.get(" funding_total_usd ", ""),
            "status": h.get("status", ""),
            "country": h.get("country_code", ""),
            "category": h.get("category_list", ""),
            "founded_year": h.get("founded_year", ""),
        })
    out_path = PROJECT_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"method": "kaggle_crunchbase_2020", "count": len(result), "companies": result},
                                   ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Найдено: %d компаний → %s", len(result), out_path)


if __name__ == "__main__":
    main()
