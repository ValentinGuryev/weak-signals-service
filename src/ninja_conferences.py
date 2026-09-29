#!/usr/bin/env python3
"""НИНЗЯ-СКАЧКА конференционных статей: 1 (источник, ключевое слово) за запуск.

Докачивает то, что НЕ скачал ночной процесс (умер от перезагрузки Windows):
- iop_jpcs (J.Phys.Conf.Ser, EuCAS) — НЕ было в conference_hits.json
- ieee_tasc_prev (IEEE TASC 1986) — НЕ было

Отличия от conference_mining.py (пулемёт):
- ОДНА пара (source, keyword) за запуск.
- Паузы между страницами 5-10 сек.
- При 429 — сразу выход (не долбить).
- Кумулятивное сохранение в ninja_conf_hits.json (не перезаписывает существующий
  conference_hits.json с 2175 статьями IEEE TAS).
- Выполненные (source, keyword) помечаются в summary — повторно не идут.
- Вызывается планировщиком 1 раз в 15 мин.
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

OUT_FILE = PROJECT_ROOT / "data" / "raw" / "conferences" / "ninja_conf_hits.json"
STATUS = PROJECT_ROOT / "results" / "ninja_conf_status.md"
CONF_DONE = PROJECT_ROOT / "results" / ".ninja_conf_done"

# Источники: (имя, OpenAlex source id) — в порядке приоритета
SOURCES: list[tuple[str, str]] = [
    ("iop_jpcs", "S4210187594"),      # J.Phys.Conf.Ser (EuCAS) — исправлен ID 2026-08-19 (был S4390939671 → 0 статей)
    ("ieee_tasc_prev", "S4363608361"), # IEEE TASC 1986 (ретро)
]

KEYWORDS_FAIL = [
    "lesson learned", "lessons learned", "discontinued", "decommissioned",
    "terminated", "cancelled", "abandoned", "unsuccessful", "failed project",
    "end of life", "shut down", "shutdown", "withdrawn", "not completed",
    "cost overrun", "schedule delay", "technical challenge",
]

KEYWORDS_SUCCESS = [
    "operational experience", "operation experience", "in operation since",
    "operating since", "successfully operated", "successful operation",
    "commissioning and operation", "long-term operation", "long-term reliability",
    "field demonstration", "field test results", "grid-connected",
    "grid connection", "commercial deployment", "commercial operation",
    "cost-effective", "economically viable", "return on investment",
    "payback period", "technology readiness", "in service",
]

KEYWORDS = KEYWORDS_FAIL + KEYWORDS_SUCCESS


def get(url: str, retries: int = 3) -> dict | None:
    """Один GET с ограниченными ретраями. 429 → None (выход, не долбить)."""
    for i in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "hackathon-research/1.0 (mailto:test@example.com)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                logger.warning("  [429] rate limit — НЕ долбим, выходим")
                return None
            if i == retries - 1:
                logger.warning("  [HTTP %d]", e.code)
                return None
            time.sleep(5 * (i + 1))
        except Exception as e:
            if i == retries - 1:
                logger.warning("  [err] %s", str(e)[:60])
                return None
            time.sleep(5 * (i + 1))
    return None


def search(source_id: str, keyword: str, per_page: int = 100) -> list | None:
    """Поиск по абстракту + пагинация. Возвращает None при 429 (проблема)."""
    kw = urllib.parse.quote(keyword)
    results, page = [], 1
    while True:
        url = (f"https://api.openalex.org/works?"
               f"filter=primary_location.source.id:{source_id},abstract.search:{kw}"
               f"&per-page={per_page}&page={page}&mailto=test@example.com")
        d = get(url)
        if d is None:
            return None if page == 1 else results
        batch = d.get("results", [])
        if not batch:
            break
        results.extend(batch)
        meta = d.get("meta", {})
        if page >= meta.get("count", 0) // per_page + 1 or len(batch) < per_page:
            break
        page += 1
        time.sleep(random.randint(5, 10))  # ниндзя-пауза между страницами
    return results


def invert(inv: dict) -> str:
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def load_state() -> dict:
    if OUT_FILE.exists():
        try:
            return json.loads(OUT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"summary": {}, "total": 0, "items": []}


def save_state(state: dict) -> None:
    OUT_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def write_status(msg: str) -> None:
    state = load_state()
    done_pairs = []
    for src, kws in state.get("summary", {}).items():
        for kw, cnt in kws.items():
            done_pairs.append(f"{src}|{kw}({cnt})")
    remaining = []
    for src, _ in SOURCES:
        for kw in KEYWORDS:
            if f"{src}|{kw}" not in [p.split("(")[0] for p in done_pairs]:
                remaining.append(f"{src}|{kw}")
    STATUS.write_text(
        f"# Ниндзя-конференции ({time.strftime('%Y-%m-%d %H:%M')})\n\n"
        f"{msg}\n\n"
        f"## Сделано ({len(done_pairs)}/{len(SOURCES)*len(KEYWORDS)} пар)\n"
        f"{chr(10).join(done_pairs[:40])}\n\n"
        f"## Осталось ({len(remaining)} пар)\n{chr(10).join(remaining[:40])}\n\n"
        f"## Итого статей: {state.get('total', 0)}\n",
        encoding="utf-8")


def next_pair(state: dict) -> tuple[str, str, str] | None:
    """Следующая (src_name, src_id, keyword) пара, ещё не сделанная."""
    done = set()
    for src, kws in state.get("summary", {}).items():
        for kw in kws:
            done.add(f"{src}|{kw}")
    for src_name, src_id in SOURCES:
        for kw in KEYWORDS:
            if f"{src_name}|{kw}" not in done:
                return src_name, src_id, kw
    return None


def main() -> None:
    state = load_state()
    pair = next_pair(state)
    if pair is None:
        write_status("ВСЕ КОНФЕРЕНЦИИ СКАЧАНЫ 🎉")
        CONF_DONE.write_text("done\n", encoding="utf-8")
        logger.info("Все конференции скачаны. Выход.")
        return

    src_name, src_id, kw = pair
    logger.info("=== Ниндзя-конференции: %s | '%s' ===", src_name, kw)
    hits = search(src_id, kw)
    if hits is None:
        write_status(f"{src_name}|{kw}: 429 rate limit — ждём следующий цикл.")
        logger.warning("429 — выходим, повторим в следующем цикле.")
        return

    # обновить summary
    state.setdefault("summary", {}).setdefault(src_name, {})[kw] = len(hits)
    logger.info("  %s | '%s' → %d статей", src_name, kw, len(hits))

    # добавить статьи с дедупом
    seen = {i.get("doi") for i in state.get("items", [])}
    added = 0
    for w in hits:
        doi = w.get("doi")
        dkey = doi or (w.get("id"), w.get("title"))
        if dkey in seen:
            continue
        seen.add(dkey)
        state["items"].append({
            "source": src_name,
            "keywords": [kw],
            "title": w.get("title"),
            "year": w.get("publication_year"),
            "doi": doi,
            "authors": [a.get("author", {}).get("display_name") for a in w.get("authorships", [])][:10],
            "abstract": w.get("abstract_inverted_index") and invert(w["abstract_inverted_index"]) or None,
            "url": w.get("id"),
            "cited_by": w.get("cited_by_count"),
        })
        added += 1
    state["total"] = len(state["items"])
    save_state(state)
    write_status(f"{src_name}|{kw}: +{added} статей (всего {state['total']}).")
    logger.info("Добавлено %d (всего %d). Осталось пар: %s",
                added, state["total"],
                sum(1 for _ in [1] for _ in [0]) if next_pair(state) is not None else 0)


if __name__ == "__main__":
    main()
