#!/usr/bin/env python3
"""Докачка references для корпуса теплопроводной изоляции (B→A сторона перекрёстной проверки).

Контекст: проверка гипотезы «конкуренты одной проблемы почти не цитируют друг друга»
на паре NI-coils (004) vs теплопроводная электроизоляция (конкурент).

Локально уже есть ni_coils_references.json (A→B: NI→изоляция).
Здесь докачиваем references для работ изоляции (insulation_thermal+materials, все 125,
ВКЛЮЧАЯ пересекающиеся с NI-корпусом — «мосты», см. замечание автора),
чтобы посчитать B→A симметрично.

Метод: OpenAlex /works?filter=openalex_id:<id1>|<id2>|... (батчи по 25)
+ select=id,referenced_works. Прямой доступ. Сохраняет рядом паспорт данных (§4.5).

Выход: data/raw/openalex/insulation_references.json
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INS_CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "hts_insulation_rct_corpus.json"
NI_CORPUS = PROJECT_ROOT / "data" / "raw" / "openalex" / "ni_coils_corpus.json"
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "insulation_references.json"

HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
BATCH = 25


def fetch_batch(ids: list[str]) -> list[dict]:
    filter_str = "openalex_id:" + "|".join(ids)
    params = {
        "filter": filter_str, "per-page": "100", "mailto": MAILTO,
        "select": "id,referenced_works",
    }
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode()).get("results", [])
        except Exception as e:
            print(f"  [err] attempt {attempt}: {str(e)[:80]}")
            time.sleep(20 * (attempt + 1))
    return []


def main():
    ins = json.loads(INS_CORPUS.read_text(encoding="utf-8"))
    ni = json.loads(NI_CORPUS.read_text(encoding="utf-8"))
    ni_ids = {w["id"] for w in ni}

    # Все работы изоляции (thermal+materials) — включая «мосты» (одновременно в NI-корпусе).
    # Мосты НЕ выкидываем: работа в обоих корпусах = прямой сигнал о связи конкурентов
    # (отсутствии изоляции), см. замечание команды.
    pure = [w for w in ins
            if w.get("topic") in ("insulation_thermal", "insulation_materials")]
    print(f"Работ изоляции (thermal+materials, все, включая мосты): {len(pure)}")

    ids = [w["id"] for w in pure]
    results = {}
    for i in range(0, len(ids), BATCH):
        batch = ids[i:i + BATCH]
        print(f"  батч {i // BATCH + 1}/{(len(ids) + BATCH - 1) // BATCH}: {len(batch)} ID")
        for r in fetch_batch(batch):
            results[r["id"]] = r.get("referenced_works") or []
        time.sleep(1.2)

    out = {wid: refs for wid, refs in results.items() if refs}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    # Паспорт данных (§4.5)
    passport = PROJECT_ROOT / "case_studies" / "004_ni_coils" / "signals" / "data_passports" / "insulation_references.md"
    passport.parent.mkdir(parents=True, exist_ok=True)
    passport.write_text(
        f"# Паспорт: insulation_references.json\n\n"
        f"- **Файл:** `data/raw/openalex/insulation_references.json`\n"
        f"- **Скрипт:** `src/openalex_insulation_refs.py`\n"
        f"- **Запрос:** OpenAlex /works filter=ids.openalex:<id>|..., select=id,referenced_works; "
        f"батчи по {BATCH}; {len(ids)} работ изоляции (insulation_thermal+materials, ВСЕ,\nвключая пересекающиеся с NI — мосты)\n"
        f"- **Дата:** {time.strftime('%Y-%m-%d')}\n"
        f"- **Записей:** {len(out)} (с непустыми references)\n"
        f"- **Поля:** id -> [references...]\n"
        f"- **Цель:** B→A сторона перекрёстной проверки «изоляция цитирований» "
        f"(NI-coils vs теплопроводная изоляция)\n"
        f"- **Бюджет:** OpenAlex, ~{len(ids) // BATCH + 1} запросов (мягкие лимиты)\n",
        encoding="utf-8",
    )
    print(f"\nСохранено: {len(out)} работ с references → {OUT}")
    print(f"Паспорт: {passport}")


if __name__ == "__main__":
    main()
