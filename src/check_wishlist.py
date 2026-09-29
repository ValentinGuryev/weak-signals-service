#!/usr/bin/env python3
"""Сверка wishlist.md с literature/ — найти строки wishlist, уже покрытые PDF (нарушение §4.2a).

Правило §4.2a: wishlist = ТОЛЬКО то, чего НЕТ. Скачанные документы НЕЛЬЗЯ упоминать
в wishlist (даже с пометкой «✅ скачан»). Если PDF есть в literature/ — строка о нём
должна быть УДАЛЕНА из таблиц wishlist (в конце — одна строка «> Вычищено: ...»).

Скрипт: для каждого PDF в literature/ извлекает (год, фамилия автора) из имени файла
(формат "(ГГГГ) [уровень] Author — Title") и ищет эти ключи в wishlist.md.
Выводит строки wishlist, которые УЖЕ покрыты PDF → кандидаты на удаление.

Использование: .venv/bin/python src/check_wishlist.py [путь_к_кейсу]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def authors_from_name(fname: str) -> list[str]:
    """Из "(2015) !! Bornmann, Mutz — Title.pdf" -> ["bornmann", "mutz"]."""
    m = re.match(r"^\(\d{4}\)\s*[^A-Za-zА-Я]*([^—]+)—", fname)
    if not m:
        return []
    au_part = m.group(1)
    # убрать уровень (_!!_/!!! и т.п.)
    au_part = re.sub(r"^[_!]*\s*", "", au_part)
    return [a.strip().lower() for a in re.split(r"[,;&]| and ", au_part) if a.strip()]


def main():
    case_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "case_studies" / "008_sc_aircraft_motors"
    lit = case_dir / "literature"
    wish = case_dir / "wishlist.md"
    if not lit.is_dir() or not wish.is_file():
        print(f"Нет literature/ или wishlist.md в {case_dir}")
        return

    # 1) собрать ключи из PDF (год + автор)
    covered = []  # (pdf_name, [keys])
    for pdf in sorted(lit.glob("*.pdf")):
        aus = authors_from_name(pdf.name)
        ym = re.match(r"^\((\d{4})\)", pdf.name)
        year = ym.group(1) if ym else ""
        keys = [a for a in aus if len(a) > 3] + ([year] if year else [])
        covered.append((pdf.name, keys))

    # 2) строки wishlist
    lines = wish.read_text(encoding="utf-8").split("\n")
    print(f"PDF в literature/: {len(covered)}")
    print(f"Строк в wishlist.md: {len(lines)}\n")
    print("=== Строки wishlist, которые УЖЕ покрыты PDF (кандидаты на удаление) ===")
    found = 0
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        low = line.lower()
        for pdf_name, keys in covered:
            # совпадение: год + хотя бы 1 автор (длина >3) есть в строке
            year = next((k for k in keys if re.match(r"^\d{4}$", k)), None)
            auth = [k for k in keys if not re.match(r"^\d{4}$", k)]
            hit_auth = sum(1 for a in auth if a in low)
            hit_year = (year in low) if year else True
            if hit_auth >= 1 and hit_year and hit_auth + (1 if hit_year else 0) >= 2:
                print(f"  строка {i+1}: {line.strip()[:100]}")
                print(f"      <- покрыто PDF: {pdf_name[:80]}")
                found += 1
                break
    if found == 0:
        print("  (нет — wishlist чист)")


if __name__ == "__main__":
    main()
