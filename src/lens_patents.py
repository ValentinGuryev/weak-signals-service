#!/usr/bin/env python3
"""ДОКАЧКА патентов IBAD-семейства через Lens.org Patent API.

Проблема: Google Patents блокирует все каналы (direct/VPS/SOCKS-прокси).
Решение: Lens.org Patent API (api.lens.org/patent/search) — легальный API,
  покрывает все юрисдикции (US/WO/EP/CN/JP/KR), даёт полные данные.

Токен: env LENS_TOKEN (задаётся при запуске).
  Пример: LENS_TOKEN=xxx setsid nohup .venv/bin/python src/lens_patents.py ...

Запросы — как в ninja_ibad_technologies.py (узкие, по 4 технологиям):
  - ibad_mgo:   "IBAD-MgO" template
  - ibad_mgo2:  "ion beam assisted deposition" "MgO"
  - ibad_ysz:   "ion beam assisted deposition" "YSZ"
  - rabits:     "RABiTS"
  - isd:        "inclined substrate deposition" superconductor
с ПОСТ-ФИЛЬТРОМ релевантности (технологический маркер И сверхпроводимость).

Правила ниньзя:
  - Пауза 2-4 сек между запросами (Lens API rate limit: ~5 req/s, но вежливо).
  - НЕ перезаписывать уже скачанные файлы (>1000 байт), накопительное сохранение.
  - Пишет в data/raw/patents/topics_window/ (как Google-версия).

Формат сохранения — СОВМЕСТИМ с ibad_tapes_wide.json:
  {publication_number, title, abstract, assignee, priority_date, filing_date,
   inventor, tech, url}
  (publication_number = doc_key, url = https://www.lens.org/lens/patent/<lens_id>)
"""
from __future__ import annotations

import json
import logging
import os
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

LENS_API = "https://api.lens.org/patent/search"
TOKEN = os.environ.get("LENS_TOKEN", "")
if not TOKEN:
    logger.error("Нет LENS_TOKEN в env! Запуск: LENS_TOKEN=xxx ...")
    sys.exit(1)

OUT_DIR = PROJECT_ROOT / "data" / "raw" / "patents" / "topics_window"
GIT_DIR = PROJECT_ROOT / "experiment" / "runs" / "patents_window"

PAGE_SIZE = 50          # размер страницы Lens API
MAX_OFFSET = 5000       # макс. offset (Lens лимит)
PAUSE_MIN, PAUSE_MAX = 5, 8

# ---- Технологии: (query, целевое число, окно лет, имя файла) ----
# Запросы в формате Lens (bool/JSON), НЕ Google-строки.
# ⚠️ Lens ищет в title/abstract (не полный текст), поэтому запросы шире,
# а фильтр релевантности (tech_relevant) отсеивает лишнее.
TECHNOLOGIES: dict[str, tuple[dict, int, tuple[int, int], str]] = {
    "ibad_mgo": (
        {"bool": {"should": [
            {"match_phrase": {"title": "IBAD-MgO"}},
            {"match_phrase": {"title": "IBAD MgO"}},
            {"match_phrase": {"abstract": "IBAD-MgO"}},
            {"bool": {"must": [
                {"match": {"abstract": "IBAD"}},
                {"match": {"abstract": "MgO"}},
            ]}},
        ]}},
        100, (1995, 2026), "ibad_mgo_tech.json"),
    "ibad_mgo2": (
        {"bool": {"must": [
            {"match_phrase": {"abstract": "ion beam assisted deposition"}},
            {"match_phrase": {"abstract": "MgO"}},
        ]}},
        80, (1995, 2026), "ibad_mgo2_tech.json"),
    "ibad_ysz": (
        {"bool": {"must": [
            {"match_phrase": {"abstract": "ion beam assisted deposition"}},
            {"match": {"abstract": "YSZ"}},
        ]}},
        60, (1995, 2026), "ibad_ysz_tech.json"),
    "rabits": (
        {"bool": {"should": [
            {"match_phrase": {"title": "RABiTS"}},
            {"match_phrase": {"abstract": "RABiTS"}},
            {"match_phrase": {"abstract": "rolling assisted biaxially"}},
        ]}},
        60, (1995, 2026), "rabits_tech.json"),
    "isd": (
        {"bool": {"must": [
            {"match_phrase": {"abstract": "inclined substrate deposition"}},
            {"match": {"abstract": "superconductor"}},
        ]}},
        40, (1995, 2026), "isd_tech.json"),
    "ibad_full": (
        # Широкий запрос: IBAD в abstract + SC (докачка полного пула, 2026-08-31)
        {"bool": {"must": [
            {"match": {"abstract": "IBAD"}},
        ]}},
        200, (1995, 2026), "ibad_full_tech.json"),
}

# ---- Фильтр релевантности (совместим с ninja_ibad_technologies.py) ----
IBAD_RE = re.compile(r"\bibad\b|ion[\s-]?beam[\s-]?assisted", re.I)
RABITS_RE = re.compile(r"rabits|rolling[\s-]?assisted[\s-]?biaxially", re.I)
ISD_RE = re.compile(r"inclined[\s-]?substrate[\s-]?deposition|\binclined[\s-]?substrate\b", re.I)
MGO_RE = re.compile(r"\bmgo\b|magnesium[\s-]?oxide", re.I)
YSZ_RE = re.compile(r"\bysz\b|yttria[\s-]?stabilized[\s-]?zirconia|\bgzo\b|gadolinium[\s-]?zirconate", re.I)
SC_RE = re.compile(r"superconduct|coated[\s-]?conductor|\bhts\b|\brebco\b|\bybco\b|\b2g\b|tape|wire", re.I)

TAG_RE = re.compile(r"<[^>]+>")


def tech_relevant(title: str, abstract: str, tech: str) -> bool:
    t = TAG_RE.sub("", f"{title} {abstract}").lower()
    sc = bool(SC_RE.search(t))
    if not sc:
        return False
    if tech == "ibad_mgo":
        return bool(IBAD_RE.search(t)) and bool(MGO_RE.search(t))
    if tech == "ibad_mgo2":
        return bool(IBAD_RE.search(t)) and bool(MGO_RE.search(t))
    if tech == "ibad_full":
        return bool(IBAD_RE.search(t)) and bool(SC_RE.search(t))
    if tech == "ibad_ysz":
        return bool(IBAD_RE.search(t)) and bool(YSZ_RE.search(t))
    if tech == "rabits":
        return bool(RABITS_RE.search(t))
    if tech == "isd":
        return bool(ISD_RE.search(t))
    return False


def lens_search(query: dict, offset: int) -> dict | None:
    """Один запрос к Lens API. Возвращает JSON или None при ошибке."""
    payload = {
        "query": query,
        "size": PAGE_SIZE,
        "offset": offset,
        "include": [
            "biblio.publication_reference",
            "biblio.application_reference",
            "biblio.priority_claims",
            "biblio.invention_title",
            "biblio.parties",
            "biblio.cited_by",
            "biblio.references_cited",
            "abstract",
        ],
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        LENS_API, data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            logger.error("[lens] HTTP %d — проверь токен", e.code)
            return None
        if e.code == 429:
            logger.warning("[lens] HTTP 429 (rate limit) — пауза 15 сек")
            time.sleep(15)
            return None
        logger.warning("[lens] HTTP %d", e.code)
        return None
    except Exception as e:
        logger.warning("[lens] ошибка: %s", str(e)[:80])
        return None


def extract(p: dict) -> dict | None:
    """Извлечь патент из Lens-ответа в совместимый формат."""
    lens_id = p.get("lens_id") or ""
    biblio = p.get("biblio", {})
    # Doc key из publication_reference
    pr = biblio.get("publication_reference", {})
    jur = pr.get("jurisdiction") or ""
    doc = pr.get("doc_number") or ""
    kind = pr.get("kind") or ""
    pdate = pr.get("date") or ""
    if not (jur and doc):
        return None
    doc_key = f"{jur}_{doc}_{kind}_{pdate}" if kind else f"{jur}_{doc}"
    # Заголовок (en)
    title = ""
    for t in biblio.get("invention_title", []):
        if t.get("lang") == "en" or t.get("text"):
            title = t.get("text", "")
            break
    # Абстракт
    abstract = ""
    for a in p.get("abstract", []) or []:
        if a.get("lang") == "en":
            abstract = a.get("text", "")
            break
    # Приоритетная дата
    priority_date = ""
    pc = biblio.get("priority_claims", {})
    earliest = pc.get("earliest_claim", {}).get("date") or ""
    if earliest:
        priority_date = earliest[:10]
    # Дата подачи
    filing_date = ""
    ar = biblio.get("application_reference", {})
    if ar.get("date"):
        filing_date = ar["date"][:10]
    # Заявители
    applicants = []
    for ap in biblio.get("parties", {}).get("applicants", []):
        name = ap.get("extracted_name", {}).get("value", "")
        if name:
            applicants.append(name)
    assignee = ", ".join(applicants[:3]) if applicants else ""
    # Изобретатели
    inventors = []
    for inv in biblio.get("parties", {}).get("inventors", []):
        name = inv.get("extracted_name", {}).get("value", "")
        if name:
            inventors.append(name)
    url = f"https://www.lens.org/lens/patent/{lens_id}" if lens_id else ""
    # Цитирования (для графа S3)
    cited_by = []
    cb = biblio.get("cited_by", {})
    for c in cb.get("patents", []) or []:
        doc = c.get("document_id", {})
        j = doc.get("jurisdiction") or ""
        n = doc.get("doc_number") or ""
        if j and n:
            cited_by.append(f"{j}_{n}")
    references = []
    rc = biblio.get("references_cited", {})
    for c in rc.get("citations", []) or []:
        # формат: {"patcit": {"document_id": {...}}}
        doc = c.get("patcit", {}).get("document_id", {}) or {}
        j = doc.get("jurisdiction") or ""
        n = doc.get("doc_number") or ""
        if j and n:
            references.append(f"{j}_{n}")
    return {
        "publication_number": doc_key,
        "title": title,
        "abstract": abstract,
        "assignee": assignee,
        "priority_date": priority_date,
        "filing_date": filing_date,
        "inventor": ", ".join(inventors[:5]) if inventors else "",
        "tech": "",
        "cited_by": cited_by,
        "references": references,
        "url": url,
    }


def in_window(p: dict, win: tuple[int, int]) -> bool:
    pd = p.get("priority_date") or ""
    if not pd or len(pd) < 4 or not pd[:4].isdigit():
        return False
    return win[0] <= int(pd[:4]) <= win[1]


def save_progress(tech: str, query_desc: str, win: tuple[int, int],
                  uniq: list[dict], scanned: int, out_name: str, target: int) -> None:
    result = {
        "query": query_desc, "window": f"{win[0]}-{win[1]}",
        "downloaded": len(uniq), "scanned_raw": scanned, "patents": uniq,
        "source": "lens.org",
    }
    for d in (OUT_DIR, GIT_DIR):
        d.mkdir(parents=True, exist_ok=True)
        f = d / out_name
        if f.exists() and f.stat().st_size > 1000:
            try:
                existing = json.loads(f.read_text(encoding="utf-8"))
                if len(existing.get("patents", [])) >= target:
                    logger.info("  %s: файл уже содержит %d (цель %d) — пропуск", tech,
                                len(existing.get("patents", [])), target)
                    continue
            except Exception:
                pass
        if not uniq:
            logger.warning("  %s: 0 релевантных — НЕ перезаписываю", tech)
            continue
        f.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_tech(tech: str, query: dict, target: int, win: tuple[int, int], out_name: str) -> int:
    """Докачать target релевантных патентов по технологии через Lens."""
    all_pats: list[dict] = []
    seen: set[str] = set()
    offset = 0
    # Resume из существующих файлов
    for d in (OUT_DIR, GIT_DIR):
        f = d / out_name
        if f.exists() and f.stat().st_size > 1000:
            try:
                existing = json.loads(f.read_text(encoding="utf-8"))
                k = len(existing.get("patents", []))
                if 0 < k < target:
                    offset = (k // PAGE_SIZE) * PAGE_SIZE
                    all_pats = existing.get("patents", [])
                    seen = {p.get("publication_number") for p in all_pats}
                    logger.info("  %s: resume с %d, offset=%d (цель %d)",
                                tech, k, offset, target)
            except Exception:
                pass
            break

    while offset < MAX_OFFSET:
        # Ретрай при 429 (rate limit)
        data = None
        for attempt in range(3):
            data = lens_search(query, offset)
            if data:
                break
            logger.info("  %s: ретрай %d/3 после ошибки (offset %d)", tech, attempt+1, offset)
            time.sleep(15)
        if not data:
            break
        total = data.get("total", 0)
        items = data.get("data", [])
        if not items:
            break
        # Не листать дальше total
        if offset >= total:
            break
        new_on_page = 0
        for p in items:
            ep = extract(p)
            if not ep:
                continue
            pub = ep["publication_number"]
            if pub in seen:
                continue
            seen.add(pub)
            if not in_window(ep, win):
                continue
            ep["tech"] = tech
            if not tech_relevant(ep.get("title", ""), ep.get("abstract", ""), tech):
                continue
            all_pats.append(ep)
            new_on_page += 1
        logger.info("  %s: offset %d → %d релевантных (всего %d/%d, total=%d)",
                    tech, offset, new_on_page, len(all_pats), target, total)
        save_progress(tech, str(query)[:80], win, all_pats[:target], len(seen), out_name, target)
        if len(all_pats) >= target:
            break
        offset += PAGE_SIZE
        if offset < MAX_OFFSET:
            pause = random.randint(PAUSE_MIN, PAUSE_MAX)
            logger.info("  %s: пауза %ds", tech, pause)
            time.sleep(pause)

    uniq = all_pats[:target]
    save_progress(tech, str(query)[:80], win, uniq, len(seen), out_name, target)
    logger.info("  %s: сохранено %d релевантных (окно %d-%d, просканировано %d)",
                tech, len(uniq), win[0], win[1], len(seen))
    return len(uniq)


def main() -> None:
    pending = []
    for tech, (query, target, win, out_name) in TECHNOLOGIES.items():
        done = 0
        for d in (OUT_DIR, GIT_DIR):
            f = d / out_name
            if f.exists() and f.stat().st_size > 1000:
                try:
                    done = len(json.loads(f.read_text(encoding="utf-8")).get("patents", []))
                except Exception:
                    done = 0
                break
        if done < target:
            pending.append(tech)
    if not pending:
        logger.info("Все технологии IBAD-семейства докачаны. Выход.")
        return
    logger.info("=== Lens-докачка IBAD: %s, осталось: %s ===", pending[0], pending)
    for tech in pending:
        query, target, win, out_name = TECHNOLOGIES[tech]
        n = fetch_tech(tech, query, target, win, out_name)
        logger.info("Готово: %s (%d релевантных)", tech, n)


if __name__ == "__main__":
    main()
