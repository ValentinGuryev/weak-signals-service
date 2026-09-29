#!/usr/bin/env python3
"""Универсальный сбор корпуса OpenAlex для кейса (оптимизированный, правило 2026-09-07).

⭐ ОДИН проход с ПОЛНЫМ select: абстракты (S2), referenced_works (S3/S3-cross),
authorships-страны (гео) приходят БЕСПЛАТНО тем же запросом. НЕ качать дважды (как *_full.py в 006/007).

⚠️ OpenAlex лимитирует ЧИСЛО запросов (с 2026-09). Расходовать экономно:
   - ядро: точные фразы в кавычках, полный select, 1-3 запроса;
   - разведка/конкуренты: только group_by (counts), БЕЗ скачивания работ;
   - классификация шума — инлайн в скрипте (ценз), не отдельными запросами.

Использование (подставить тему/запросы/классы):
    cp src/openalex_collect.py src/openalex_<case>.py   # затем отредактировать CONFIG
    .venv/bin/python src/openalex_<case>.py

Выход:
- data/raw/openalex/<case>_corpus.json   полные записи (с абстрактами, references, авторами)
- data/raw/openalex/<case>_counts.json   counts по годам (group_by)
+ паспорт пишется рядом (см. signals/data_passports/ примеры)

По умолчанию НЕ выполняет запросы (--dry-run): сначала покажи CONFIG пользователю.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

# ============================ КОНФИГ (редактировать под кейс) =================
CASE = "CASE"            # имя кейса (для файлов)
TOPIC = "тема кейса"     # человекочитаемо
# Ядро: точные фразы (кавычки!) — title_and_abstract.search; пробел = AND
Q_CORE = ['"example phrase" keyword']
# Доп. классы (соседи/конкуренты), если нужен их полный корпус (S3-cross) — редко
Q_CLASSES = {}           # {"class_name": ["query1", ...]}
# Разведка/конкуренты — ТОЛЬКО counts (group_by), работы НЕ качаем
Q_COUNTS = ["wide term A", "competitor term B"]
# Строгий фильтр релевантности по тексту (title+abstract) — вернуть класс или None
def classify(text: str) -> str | None:
    """Вернуть класс ('core'/'<class>') если релевантно, None если шум. Подставить паттерны."""
    t = text.lower()
    # if not re.search(r'superconduct', t): return None
    # if re.search(r'superconduct', t) and re.search(r'motor|machine', t): return 'core'
    return 'core'  # по умолчанию всё релевантно — УТОЧНИТЬ!
# =============================================================================

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
SELECT = ("id,title,publication_year,cited_by_count,abstract_inverted_index,"
          "referenced_works,authorships,primary_location,concepts")
MAX_PAGES = 60  # ~6000 работ максимум на класс


def abstract_text(work: dict) -> str:
    inv = work.get("abstract_inverted_index") or {}
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


def simplify(work: dict) -> dict:
    """Сжать запись (полный select → нужные поля)."""
    auths = []
    for a in (work.get("authorships") or []):
        au = a.get("author") or {}
        inst = (a.get("institutions") or [{}])[0]
        auths.append({
            "name": au.get("display_name"),
            "id": au.get("id"),
            "country": inst.get("country_code"),
            "inst": inst.get("display_name"),
        })
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    return {
        "id": work.get("id"),
        "title": work.get("title"),
        "year": work.get("publication_year"),
        "cited_by": work.get("cited_by_count"),
        "abstract": abstract_text(work),              # S2, ценз
        "referenced_works": work.get("referenced_works") or [],  # S3/S3-cross БЕСПЛАТНО
        "authors": auths,                             # гео
        "source": src.get("display_name"),
        "doi": loc.get("doi"),
        "concepts": [c.get("display_name") for c in (work.get("concepts") or [])[:5]],
    }


def fetch(filter_str: str, select: str = SELECT) -> list[dict]:
    results, cursor, pages = [], "*", 0
    while cursor and pages < MAX_PAGES:
        params = {"filter": filter_str, "per-page": "100", "cursor": cursor,
                  "mailto": MAILTO, "select": select}
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
        except Exception as e:
            print(f"  ! fetch error: {e}", file=sys.stderr)
            time.sleep(5)
            continue
        results.extend(data.get("results", []))
        cursor = data.get("meta", {}).get("next_cursor")
        pages += 1
        time.sleep(0.5)  # вежливость
    return results


def counts_by_year(query: str) -> dict:
    """Разведка: counts по годам БЕЗ скачивания работ (1 запрос)."""
    params = {"filter": "title_and_abstract.search:" + query,
              "group_by": "publication_year", "per-page": "50", "mailto": MAILTO}
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        return {g["key"]: g["count"] for g in data.get("group_by", [])}
    except Exception as e:
        print(f"  ! counts error: {e}", file=sys.stderr)
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="показать план запросов и выйти")
    args = ap.parse_args()

    print(f"=== Сбор корпуса OpenAlex: {TOPIC} (кейс {CASE}) ===")
    n_core = sum(1 for q in Q_CORE if q)
    plan = (f"Запросов: ядро {n_core} (полный select) + классы "
            f"{sum(len(v) for v in Q_CLASSES.values())} + counts {len(Q_COUNTS)}")
    print(plan)
    if args.dry_run:
        print("dry-run: показываю CONFIG (отредактируй Q_CORE/classify перед запуском).")
        return

    # 1) Ядро: полный select, дедуп, классификация инлайн
    out_dir = Path(__file__).resolve().parent.parent / "data" / "raw" / "openalex"
    out_dir.mkdir(exist_ok=True)
    works_by_class = defaultdict(list)
    seen = set()
    for q in Q_CORE:
        print(f"\n[core] {q}")
        for w in fetch(f'title_and_abstract.search:{q}'):
            text = f"{w.get('title') or ''} {abstract_text(w)}"
            cls = classify(text)
            if not cls:
                continue
            wid = w.get("id")
            if wid in seen:
                continue
            seen.add(wid)
            works_by_class[cls].append(simplify(w))
    for cname, qs in Q_CLASSES.items():
        for q in qs:
            print(f"\n[{cname}] {q}")
            for w in fetch(f'title_and_abstract.search:{q}'):
                text = f"{w.get('title') or ''} {abstract_text(w)}"
                cls = classify(text)
                if not cls:
                    continue
                wid = w.get("id")
                if wid in seen:
                    continue
                seen.add(wid)
                works_by_class[cname].append(simplify(w))

    # сохранить корпус
    corpus_path = out_dir / f"{CASE}_corpus.json"
    with open(corpus_path, "w") as f:
        json.dump({k: v for k, v in works_by_class.items()}, f, ensure_ascii=False, indent=1)
    print(f"\nКорпус: {sum(len(v) for v in works_by_class.values())} работ -> {corpus_path}")
    for k, v in works_by_class.items():
        print(f"  {k}: {len(v)}")

    # 2) counts по годам (group_by, дёшево) — для ядра (агрегат) и конкурентов
    counts = {}
    # агрегат по ядру: считаем по каждому ядерному запросу отдельно и суммируем с дедупом на уровне лет
    # (простая оценка: max по годам среди запросов ядра, чтобы не задвоить пересечения)
    core_by_year = Counter()
    for q in Q_CORE:
        cy = counts_by_year(q)
        for y, c in cy.items():
            core_by_year[y] = max(core_by_year[y], c)
    counts["core"] = dict(sorted(core_by_year.items()))
    time.sleep(0.5)
    for i, q in enumerate(Q_COUNTS):
        counts[f"q{i}_{q[:30]}"] = counts_by_year(q)
        time.sleep(0.5)

    counts_path = out_dir / f"{CASE}_counts.json"
    with open(counts_path, "w") as f:
        json.dump(counts, f, ensure_ascii=False, indent=1)
    print(f"Counts -> {counts_path}")

    # 3) паспорт (правило §4.5)
    passport = out_dir / f"{CASE}_passport.md"
    with open(passport, "w") as f:
        f.write(f"# Паспорт: корпус {CASE} (OpenAlex)\n\n"
                f"- Тема: {TOPIC}\n- Запросы ядра: {Q_CORE}\n- select: {SELECT}\n"
                f"- Работ: {sum(len(v) for v in works_by_class.values())}\n"
                f"- Дата: {time.strftime('%Y-%m-%d')}\n")
    print(f"Паспорт -> {passport}")


if __name__ == "__main__":
    main()
