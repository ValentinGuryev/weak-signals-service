#!/usr/bin/env python3
"""НИНЬЗЯ-СКАЧКА патентов: 1 попытка за 15 минут, чтобы НЕ словить капчу Google.

Отличие от patents_by_topic.py (пулемёт):
- ОДНА тема за запуск (не все 16 подряд).
- Пауза между страницами 45-90 сек (не 20).
- При 503/капче — сразу выходим, НЕ долбим дальше.
- Никогда не перезаписываем уже скачанный файл (>1000 байт).
- Статус пишется в results/ninja_status.md.
- Вызывается планировщиком (ninja_scheduler.py) 1 раз в 15 мин.

Темы (16): очередность по приоритету — сначала старые 9 пустых,
потом 6 новых (добавлены ночью 18.08), hts_tapes уже скачан (пропуск).
"""
from __future__ import annotations

import json
import logging
import random
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

# Тема -> (запрос, сколько патентов). Порядок = приоритет скачки.
TOPICS: dict[str, tuple[str, int]] = {
    # === Старые калибровочные (9 пустых файлов) ===
    "sde":            ('"superconducting diode"', 100),
    "smes":           ('"superconducting magnetic energy storage"', 100),
    "fluxonics":      ('"single flux quantum logic"', 100),
    "fusion_magnets": ('"fusion magnet" OR "tokamak magnet"', 100),
    "qec":            ('"quantum error correction"', 100),
    "mgb2_mri":       ('"MgB2 MRI" OR "magnesium diboride MRI"', 100),
    "ac_cables":      ('"superconducting cable"', 100),
    "sc_motors":      ('"superconducting motor"', 100),
    "chiral_phonon":  ('"chiral phonon"', 50),
    # === Новые темы (добавлены ночью 18.08) ===
    "nb3sn":          ('"Nb3Sn" OR "niobium tin"', 100),
    "sfcl":           ('"superconducting fault current limiter" OR "SFCL"', 100),
    "sc_transformers":('"superconducting transformer"', 100),
    "maglev":         ('"superconducting maglev" OR "magnetic levitation train"', 100),
    "current_leads":  ('"superconducting current lead" OR "HTS current lead"', 100),
    "hts_cables":     ('"HTS cable" OR "high temperature superconducting cable"', 100),
    # hts_tapes уже скачан (98 KB) — пропускается автоматически
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

OUT_DIR = PROJECT_ROOT / "data" / "raw" / "patents" / "topics"
GIT_DIR = PROJECT_ROOT / "experiment" / "runs" / "patents"
STATUS = PROJECT_ROOT / "results" / "runtime" / "ninja_status.md"

DONE_FLAG = PROJECT_ROOT / "results" / ".ninja_done"


def xhr_page(query: str, num: int, page: int, topic: str) -> dict | None:
    """Один запрос XHR. При 503/капче — вернуть None (не ретраить долго)."""
    url = "https://patents.google.com/xhr/query?url=" + urllib.parse.quote(
        f"q={query}&num={num}&page={page}", safe="")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        code = e.code
        if code in (403, 429, 503):
            logger.warning("[%s] HTTP %d (капча/лимит) — НЕ долбим, выходим", topic, code)
        else:
            logger.warning("[%s] HTTP %d", topic, code)
        return None
    except Exception as e:
        logger.warning("[%s] ошибка: %s", topic, str(e)[:80])
        return None


def fetch_topic(name: str, query: str, n: int) -> int:
    """Скачать n патентов по теме с ОЧЕНЬ большими паузами. Возвращает число с абстрактом."""
    all_pats: list[dict] = []
    pages = (n + 24) // 25
    for page in range(pages):
        data = xhr_page(query, 25, page, name)
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
                    "abstract": "",
                    "assignee": p.get("assignee"),
                    "priority_date": p.get("priority_date"),
                    "filing_date": p.get("filing_date"),
                    "inventor": p.get("inventor"),
                    "snippet": (p.get("snippet") or "")[:800],
                    "url": f"https://patents.google.com/patent/{p.get('publication_number')}",
                })
        logger.info("  %s: страница %d → %d патентов", name, page, len(all_pats))
        # Ниньзя-пауза между страницами: 45-90 сек (случайно)
        if page < pages - 1:
            pause = random.randint(45, 90)
            logger.info("  %s: ниньзя-пауза %ds перед страницей %d", name, pause, page + 2)
            time.sleep(pause)
        if len(all_pats) >= n:
            break

    # дедуп
    seen, uniq = set(), []
    for p in all_pats:
        if p["publication_number"] in seen:
            continue
        seen.add(p["publication_number"])
        uniq.append(p)
    uniq = uniq[:n]

    with_abs = sum(1 for p in uniq if p.get("snippet"))
    for p in uniq:
        if p.get("snippet"):
            p["abstract"] = p["snippet"][:1500]

    # сохранить с защитой: НЕ перезаписывать существующий нормальный файл
    result = {"query": query, "downloaded": len(uniq), "with_abstract": with_abs, "patents": uniq}
    for d in (OUT_DIR, GIT_DIR):
        d.mkdir(parents=True, exist_ok=True)
        f = d / f"{name}.json"
        if f.exists() and f.stat().st_size > 1000:
            logger.info("  %s: файл уже есть (%d байт) — пропуск", name, f.stat().st_size)
            continue
        if len(uniq) == 0:
            logger.warning("  %s: 0 патентов — НЕ перезаписываю", name)
            continue
        f.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("  %s: сохранено %d (абстрактов %d)", name, len(uniq), with_abs)
    return with_abs


def pending_topics() -> list[str]:
    """Темы, которые ещё не скачаны (файл <1000 байт или отсутствует)."""
    out, git = [], []
    for name in TOPICS:
        g = GIT_DIR / f"{name}.json"
        if g.exists() and g.stat().st_size > 1000:
            continue  # уже скачана
        out.append(name)
    return out


def write_status(msg: str) -> None:
    sizes = {f.name: f.stat().st_size for f in sorted(GIT_DIR.glob("*.json"))} if GIT_DIR.exists() else {}
    done = [n for n in TOPICS if (GIT_DIR / f"{n}.json").exists() and (GIT_DIR / f"{n}.json").stat().st_size > 1000]
    pending = [n for n in TOPICS if n not in done]
    STATUS.write_text(
        f"# Ниньзя-статус ({time.strftime('%Y-%m-%d %H:%M')})\n\n"
        f"{msg}\n\n"
        f"## Скачано ({len(done)}/{len(TOPICS)})\n{done}\n\n"
        f"## Осталось ({len(pending)})\n{pending}\n\n"
        f"## Размеры файлов\n{json.dumps(sizes, indent=1)}\n",
        encoding="utf-8")


def main() -> None:
    pending = pending_topics()
    if not pending:
        write_status("ВСЕ ТЕМЫ СКАЧАНЫ 🎉")
        DONE_FLAG.write_text("done\n", encoding="utf-8")
        logger.info("Все темы скачаны. Выход.")
        return

    name = pending[0]  # только ОДНА тема за запуск
    query, n = TOPICS[name]
    logger.info("=== Ниньзя: тема %s (%d патентов) — осталось %d тем ===", name, n, len(pending))
    n_abs = fetch_topic(name, query, n)
    write_status(f"Тема {name}: сохранено {n_abs} абстрактов.")
    logger.info("Готово: %s (%d абстрактов). Осталось: %s", name, n_abs, pending_topics())


if __name__ == "__main__":
    main()
