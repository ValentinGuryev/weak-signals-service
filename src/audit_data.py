"""Аудит данных Фазы 1: целостность, полнота, покрытие прикладных тем.

Запуск: .venv/bin/python src/audit_data.py [--verbose]

Набор проверок:
  1. Схема и типы колонок.
  2. Дубликаты: arxiv_id, версии одного ID (v1/v2), заголовки.
  3. Даты: диапазон, невозможные значения, распределение по годам/месяцам.
  4. Формат arXiv ID (старый YYMMNNNN / новый YYYYMM.NNNNN).
  5. Целостность текста: пустые abstract/title, HTML-сущности, мусор, язык.
  6. Авторы: пустые списки.
  7. Категории: покрытие 7 целевых, «мусорные» категории.
  8. Ошибки API: записи-заглушки arXiv (api/errors).
  9. Покрытие прикладных тем (coated conductors, термоядерная энергетика,
     облучение ВТСП частицами) + тренды по годам.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

from utils import data_processed, setup_logging

logger = setup_logging()

TARGET_CATEGORIES = [
    "cond-mat.supr-con",
    "cond-mat.mtrl-sci",
    "cond-mat.mes-hall",
    "cond-mat.str-el",
    "physics.app-ph",
    "physics.acc-ph",
    "quant-ph",
]

# --- Зонды прикладных тем (title+abstract, lower-case regex) ---
PROBES: dict[str, str] = {
    "coated conductors (REBCO/YBCO-ленты)": (
        r"coated conductor|(re)?bco (tape|tapes)|rebco (film|layer|wire)|"
        r"2g (hts|wire|tape)|(1g|2g) conductor"
    ),
    "REBCO-ленты (любой контекст)": r"\brebco\b",
    "YBCO (любой контекст)": r"\bybco\b",
    "HTS-провода/ленты (REBCO, Bi-2223, MgB2)": (
        r"(re)bco|bi-?2223|bi2sr2cacu2o|mgb2|(hts|high-temperature) (wire|tape|conductor)s?"
    ),
    "термоядерная энергетика (fusion/tokamak/ITER)": (
        r"\bfusion\b|\btokamak\b|\biter\b|\bdemo\b|\bstellarator\b|\bsparc\b|"
        r"\bfusion magnet|magnet system"
    ),
    "облучение: нейтроны": (
        r"neutron irradiat\w*|irradiat\w* (with|by) neutron|irradiat\w*.*neutron"
    ),
    "облучение: ионы/протоны": (
        r"ion irradiat\w*|proton irradiat\w*|heavy-?ion irradiat\w*|"
        r"irradiat\w* (with|by) (ion|proton)s?"
    ),
    "облучение: электроны": r"electron irradiat\w*|irradiat\w* (with|by) electron",
    "облучение: гамма": r"gamma irradiat\w*|γ-?irradiat\w*|irradiat\w* (with|by) gamma",
    "радиационные повреждения (общее)": (
        r"radiation damage|displacement damage|irradiation damage|radiation-?induced defect"
    ),
    # "ВТСП + облучение" — двухпроходная проверка (см. check_topics):
    # маска1 И маска2, без lookahead (lookahead вызывает катастрофический backtracking).
    "_combo_supercond": r"\b(superconduct\w*|hts|rebco|ybco)\b",
    "_combo_rad": r"\b(irradiat\w*|radiation)\b",
}

# --- Маркеры известных трендов (валидация узнаваемости) ---
LANDMARKS: dict[str, str] = {
    "no-insulation (NI) катушки": r"\bno-?insulation\b|\bni\s+(coil|magnet)",
    "flux pump / flux pumping": r"\bflux\s+pump",
    "quench (защита магнитов)": r"\bquench\b",
    "HTS-кабели (cable)": r"\bhts\s+cable|\bhigh-?temperature\s+superconducting\s+cable",
    "HTS-магниты": r"\bhts\s+magnet|\bhigh-?temperature\s+superconducting\s+magnet",
    "critical current (крит. ток)": r"\bcritical\s+current\b",
    "flux pinning (пиннинг)": r"\bflux\s+pinning\b|\bvortex\s+pinning\b",
    "водородные сверхпроводники (hydrides)": r"\bhydride\b|\bhydrides\b",
    "сверхпроводящие кубиты": r"\bsuperconducting\s+qubit",
    "майорановские моды": r"\b(majorana|topological\s+superconduct\w*)",
}


def _text(df: pd.DataFrame) -> pd.Series:
    return (df["title"].fillna("") + " " + df["abstract"].fillna("")).str.lower()


def check_schema(df: pd.DataFrame) -> None:
    print("\n=== 1. СХЕМА ===")
    print(f"shape: {df.shape}")
    print(f"columns: {list(df.columns)}")
    print(f"dtypes: {dict(df.dtypes.astype(str))}")


def check_duplicates(df: pd.DataFrame) -> None:
    print("\n=== 2. ДУБЛИКАТЫ ===")
    print(f"дублей arxiv_id (точное): {df['arxiv_id'].duplicated().sum()}")
    base = df["arxiv_id"].str.replace(r"v\d+$", "", regex=True)
    print(f"дублей по базовому ID (v1/v2 одной статьи): {len(df) - base.nunique()}")
    t = df["title"].str.strip().str.lower()
    print(f"дублей заголовков: {t.duplicated().sum()}")
    if t.duplicated().sum():
        dup_titles = df[t.duplicated(keep=False)]["title"].head(5).tolist()
        for d in dup_titles:
            print(f"  пример: {d[:80]}")


def check_dates(df: pd.DataFrame) -> None:
    print("\n=== 3. ДАТЫ ===")
    dates = pd.to_datetime(df["published"], errors="coerce")
    print(f"null дат: {dates.isna().sum()}")
    print(f"диапазон: {dates.min()} .. {dates.max()}")
    print(f"до 2006-01-01: {(dates < '2006-01-01').sum()}")
    print(f"после 2026-08-12: {(dates > '2026-08-12').sum()}")
    by_year = dates.dt.year.value_counts().sort_index()
    print("по годам:", dict(by_year))
    by_month = dates.dt.to_period("M").value_counts().sort_index()
    print(f"месяцев в ряду: {len(by_month)} (ожидаем ~247 за 2006-01..2026-07)")


def check_ids(df: pd.DataFrame) -> None:
    print("\n=== 4. ФОРМАТ ARXIV ID ===")
    pat_new = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
    # Старый формат YYMMNNNNN (до 2007-03): 6-7 цифр, опционально версия.
    # Пример: 0601011v1. НЕ путать с новым форматом (точка обязательна).
    pat_old = re.compile(r"^\d{6,7}(v\d+)?$")
    bad = df["arxiv_id"].apply(lambda x: not (pat_new.match(str(x)) or pat_old.match(str(x))))
    print(f"ID не по формату: {bad.sum()}")
    if bad.sum():
        print("примеры:", df[bad]["arxiv_id"].head(5).tolist())


def check_text(df: pd.DataFrame) -> None:
    print("\n=== 5. ЦЕЛОСТНОСТЬ ТЕКСТА ===")
    abs_ = df["abstract"].fillna("")
    print(f"null abstract: {df['abstract'].isna().sum()}, пустых (strip): {(abs_.str.strip()=='').sum()}")
    print(f"null title: {df['title'].isna().sum()}, пустых title: {(df['title'].fillna('').str.strip()=='').sum()}")
    html = abs_.str.contains(r"&(?:amp|lt|gt|quot|#\d+);", regex=True)
    print(f"с HTML-сущностями: {html.sum()}")
    print(f"abstract короче 20 символов: {(abs_.str.len()<20).sum()}")
    # грубая оценка языка: доля не-ASCII
    def non_ascii_ratio(s: str) -> float:
        if not s:
            return 0.0
        return sum(1 for c in s if ord(c) > 127) / len(s)
    non_latin = abs_.apply(non_ascii_ratio) > 0.5
    print(f"abstract в основном не-латиница (>50% не-ASCII): {non_latin.sum()}")


def check_authors(df: pd.DataFrame) -> None:
    print("\n=== 6. АВТОРЫ ===")
    print(f"пустых списков авторов: {df['authors'].apply(lambda a: len(a)==0).sum()}")


def check_categories(df: pd.DataFrame) -> None:
    print("\n=== 7. КАТЕГОРИИ ===")
    c = Counter(x for cs in df["categories"] for x in cs)
    print("ТОП-15 категорий:", c.most_common(15))
    print("доля статей без целевой категории (только кросс-листинг):",
          round(df["categories"].apply(lambda cs: not any(x in TARGET_CATEGORIES for x in cs)).mean() * 100, 2), "%")
    # доля статей с первичной (первой) категорией вне целевых
    primary = df["categories"].apply(lambda cs: list(cs)[0] if len(cs) else "—")
    non_target = primary.apply(lambda x: x not in TARGET_CATEGORIES)
    print(f"первичная категория вне 7 целевых: {non_target.sum()} ({round(non_target.mean()*100,1)}%)")


def check_api_errors(df: pd.DataFrame) -> None:
    print("\n=== 8. ОШИБКИ API (заглушки arXiv) ===")
    err = df["arxiv_id"].str.contains("api/errors", na=False) | df["title"].str.contains(
        "^Error$|^arXiv Query", na=False, regex=True
    )
    print(f"записей-заглушек: {err.sum()}")


def check_topics(df: pd.DataFrame) -> None:
    print("\n=== 9. ПОКРЫТИЕ ПРИКЛАДНЫХ ТЕМ ===")
    text = _text(df)
    dates = pd.to_datetime(df["published"], errors="coerce")
    year = dates.dt.year
    for name, pat in PROBES.items():
        if name.startswith("_combo"):
            continue  # обрабатываются ниже отдельно
        m = text.str.contains(pat, regex=True)
        n = int(m.sum())
        print(f"\n--- {name}: {n} статей ---")
        if n:
            yc = df[m].assign(y=year[m]).groupby("y").size()
            span = f"{yc.index.min()}-{yc.index.max()}" if len(yc) else "—"
            growth = ""
            if len(yc) >= 4:
                first3 = yc.iloc[:3].sum()
                last3 = yc.iloc[-3:].sum()
                if first3:
                    growth = f" | рост последние 3 г. vs первые 3 г.: {last3/first3:.1f}×"
            print(f"  период: {span}{growth}")
            if "--verbose" in sys.argv:
                print("  по годам:", dict(yc))
                print("  примеры (id | год | title):")
                for _, r in df[m].head(4).iterrows():
                    print(f"    {r['arxiv_id']} | {r['published'][:10]} | {r['title'][:80]}")
    # Комбинация "ВТСП + облучение" (двухпроходно, без lookahead)
    if "_combo_supercond" in PROBES and "_combo_rad" in PROBES:
        m1 = text.str.contains(PROBES["_combo_supercond"], regex=True)
        m2 = text.str.contains(PROBES["_combo_rad"], regex=True)
        n = int((m1 & m2).sum())
        print(f"\n--- ВТСП + облучение (комбинация): {n} статей ---")
        if n:
            yc = df[m1 & m2].assign(y=year[m1 & m2]).groupby("y").size()
            print(f"  период: {yc.index.min()}-{yc.index.max()}", dict(yc) if "--verbose" in sys.argv else "")
    print("\n--- Маркеры известных трендов (валидация узнаваемости) ---")
    for name, pat in LANDMARKS.items():
        m = text.str.contains(pat, regex=True)
        print(f"  {name}: {int(m.sum())} статей")


def main() -> None:
    path = data_processed() / "papers.parquet"
    if not path.exists():
        logger.error("Нет %s — сначала Фаза 1", path)
        sys.exit(1)
    df = pd.read_parquet(path)
    logger.info("Аудит %s (%d строк)", path, len(df))
    check_schema(df)
    check_duplicates(df)
    check_dates(df)
    check_ids(df)
    check_text(df)
    check_authors(df)
    check_categories(df)
    check_api_errors(df)
    check_topics(df)


if __name__ == "__main__":
    main()
