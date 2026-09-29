"""Массовая скачка патентов по калибровочным темам (для обучения модели).

Темы: SDE, ВТСП-ленты, термояд-магниты, QEC, MgB2-МРТ, SMES, fluxonics, AC-кабели, авиамоторы.
Метод: Google Patents XHR (метаданные) + HTML (abstract) для первых N.
Сохраняет: data/raw/patents/<topic>.json + копию в experiment/runs/patents/ (в git!).
"""
from __future__ import annotations

import json
import logging
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

# Темы: запрос (точная фраза) + сколько патентов скачать
TOPICS = {
    # === Основные калибровочные темы ===
    "hts_tapes": {"query": '"coated conductor" OR "REBCO tape"', "n": 100},
    "fusion_magnets": {"query": '"fusion magnet" OR "tokamak magnet"', "n": 100},
    "qec": {"query": '"quantum error correction"', "n": 100},
    "mgb2_mri": {"query": '"MgB2 MRI" OR "magnesium diboride MRI"', "n": 100},
    "smes": {"query": '"superconducting magnetic energy storage"', "n": 100},
    "fluxonics": {"query": '"single flux quantum logic"', "n": 100},
    "ac_cables": {"query": '"superconducting cable"', "n": 100},
    "sc_motors": {"query": '"superconducting motor"', "n": 100},
    "chiral_phonon": {"query": '"chiral phonon"', "n": 50},
    "sde": {"query": '"superconducting diode"', "n": 100},
    # === Расширенный список (добавлено 2026-08-18 ночью) ===
    "nb3sn": {"query": '"Nb3Sn" OR "niobium tin"', "n": 100},
    "sfcl": {"query": '"superconducting fault current limiter" OR "SFCL"', "n": 100},
    "sc_transformers": {"query": '"superconducting transformer"', "n": 100},
    "maglev": {"query": '"superconducting maglev" OR "magnetic levitation train"', "n": 100},
    "current_leads": {"query": '"superconducting current lead" OR "HTS current lead"', "n": 100},
    "hts_cables": {"query": '"HTS cable" OR "high temperature superconducting cable"', "n": 100},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json",
}


def xhr_page(query: str, num: int, page: int) -> dict | None:
    url = "https://patents.google.com/xhr/query?url=" + urllib.parse.quote(f"q={query}&num={num}&page={page}", safe="")
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            wait = 30 * (attempt + 1)
            logger.warning("XHR retry %d: %s → ждём %ds", attempt + 1, str(e)[:60], wait)
            time.sleep(wait)
    return None


def html_abstract(pub: str) -> str | None:
    """Полный abstract из HTML-страницы (НЕ использовать — триггерит капчу).
    Используем snippet из XHR как основной текст."""
    return None


def fetch_topic(name: str, query: str, n: int, out_dir: Path, git_dir: Path) -> int:
    """Скачать n патентов по теме. Возвращает число с абстрактом."""
    all_pats: list[dict] = []
    pages = (n + 24) // 25
    for page in range(pages):
        data = xhr_page(query, 25, page)
        if not data:
            break
        for cluster in data.get("results", {}).get("cluster", []):
            for r in cluster.get("result", []):
                p = r.get("patent", {})
                if not p:
                    continue
                all_pats.append({
                    "publication_number": p.get("publication_number"),
                    "title": p.get("title"),
                    "abstract": "",  # заполним ниже
                    "assignee": p.get("assignee"),
                    "priority_date": p.get("priority_date"),
                    "filing_date": p.get("filing_date"),
                    "inventor": p.get("inventor"),
                    "snippet": (p.get("snippet") or "")[:800],
                    "url": f"https://patents.google.com/patent/{p.get('publication_number')}",
                })
        logger.info("  %s: страница %d → %d патентов", name, page, len(all_pats))
        time.sleep(20)  # анти-капча
        if len(all_pats) >= n:
            break

    # дедуп
    seen = set()
    uniq = []
    for p in all_pats:
        if p["publication_number"] in seen:
            continue
        seen.add(p["publication_number"])
        uniq.append(p)
    uniq = uniq[:n]

    # абстракты: НЕ использовать HTML (капча) — snippet уже в данных из XHR.
    # snippet = текст патента (фрагмент). Считаем его "абстрактом" (усечённым).
    with_abs = sum(1 for p in uniq if p.get("snippet"))
    for p in uniq:
        if p.get("snippet"):
            p["abstract"] = p["snippet"][:1500]
    time.sleep(5)

    # сохранить: НЕ перезаписывать пустышку, если уже есть данные (защита от капчи)
    result = {"query": query, "downloaded": len(uniq), "with_abstract": with_abs, "patents": uniq}
    out_dir.mkdir(parents=True, exist_ok=True)
    git_dir.mkdir(parents=True, exist_ok=True)
    for d in (out_dir, git_dir):
        f = d / f"{name}.json"
        if f.exists() and len(uniq) == 0:
            logger.warning("  %s: 0 патентов (капча?) — НЕ перезаписываю существующий файл", name)
            continue
        f.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("  %s: сохранено %d (абстрактов %d)", name, len(uniq), with_abs)
    return with_abs


def main() -> None:
    out_dir = PROJECT_ROOT / "data" / "raw" / "patents" / "topics"
    git_dir = PROJECT_ROOT / "experiment" / "runs" / "patents"
    total_abs = 0
    for name, cfg in TOPICS.items():
        git_f = git_dir / f"{name}.json"
        if git_f.exists() and git_f.stat().st_size > 1000:
            logger.info("=== Тема: %s — ПРОПУСК (уже есть данные) ===", name)
            continue
        logger.info("=== Тема: %s ===", name)
        n_abs = fetch_topic(name, cfg["query"], cfg["n"], out_dir, git_dir)
        total_abs += n_abs
        time.sleep(90)  # пауза между темами (анти-капча)
    logger.info("ИТОГО абстрактов: %d", total_abs)


if __name__ == "__main__":
    main()
