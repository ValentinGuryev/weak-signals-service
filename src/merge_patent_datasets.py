#!/usr/bin/env python3
"""ОБЪЕДИНЕНИЕ патентных датасетов IBAD-семейства (Google + Lens) в единый.

Проблема: данные из 2 источников:
  - Google (ibad_tapes_wide.json, 600; релевантных 87) — поиск в ПОЛНОМ ТЕКСТЕ,
    хорош по JP/US; publication_number = "US10446294B2"
  - Lens (ibad_mgo_tech, ibad_mgo2, ibad_ysz, rabits, isd; 61) — поиск в
    title/abstract, хорош по CN/WO; publication_number = "WO_2006071543_A1_2006-07-06";
    есть cited_by/references (граф цитирования)

Решение:
  1. Нормализовать publication_number (юр+номер[+kind]) — ключ дедупликации.
  2. Объединить, отдавая приоритет источнику с БОЛЬШЕ данными:
     - если патент есть в обоих — взять Google (полный текст) + добавить
       cited_by/references из Lens
     - если только в Lens — взять Lens
  3. Фильтр релевантности (маркер IBAD/RABiTS/ISD + сверхпроводимость) — по обоим.
  4. Сохранить единый ibad_merged.json + статистику.

Запуск:
    .venv/bin/python src/merge_patent_datasets.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
PAT = ROOT / "data" / "raw" / "patents" / "topics_window"
OUT = ROOT / "data" / "raw" / "patents" / "topics_window" / "ibad_merged.json"
GIT = ROOT / "experiment" / "runs" / "patents_window" / "ibad_merged.json"

# ---- Нормализация publication_number ----
def norm_key(pub: str) -> str:
    """Юр + номер (без kind и даты): US10446294B2 -> US10446294, WO_..._A1_2006 -> WO2006071543."""
    s = (pub or "").replace("_", "")
    m = re.match(r"^([A-Z]{2})(\d+)", s)
    if not m:
        return s.upper()
    return m.group(1) + m.group(2)


def full_key(pub: str) -> str:
    """Юр + номер + kind (если есть): US10446294B2 -> US10446294B2; WO_..._A1_2006 -> WO2006071543A1."""
    s = (pub or "").replace("_", "")
    m = re.match(r"^([A-Z]{2})(\d+)([A-Z]\d*)?", s)
    if not m:
        return s.upper()
    return (m.group(1) + m.group(2) + (m.group(3) or "")).upper()


# ---- Релевантность ----
IBAD_RE = re.compile(r"\bibad\b|ion[\s-]?beam[\s-]?assisted", re.I)
RABITS_RE = re.compile(r"rabits|rolling[\s-]?assisted[\s-]?biaxially", re.I)
ISD_RE = re.compile(r"inclined[\s-]?substrate[\s-]?deposition", re.I)
SC_RE = re.compile(r"superconduct|coated[\s-]?conductor|\bhts\b|\brebco\b|\bybco\b|\b2g\b|tape|wire", re.I)
TAG_RE = re.compile(r"<[^>]+>")


def relevant(p: dict) -> bool:
    """Релевантность: маркер IBAD/RABiTS/ISD И SC-контекст.

    Вариант A (проверено 2026-08-31): SC-слово ОБЯЗАТЕЛЬНО при наличии маркера.
    Это даёт 0 ложных срабатываний (маркер IBAD используется и для GaN/стекла/
    солнечных батарей — без SC-фильтра они попадают в датасет).
    """
    t = TAG_RE.sub("", f"{p.get('title','')} {p.get('abstract','')}").lower()
    marker = bool(IBAD_RE.search(t) or RABITS_RE.search(t) or ISD_RE.search(t))
    if not marker:
        return False
    return bool(SC_RE.search(t))


def maybe(p: dict) -> bool:
    """Спорные: маркер есть, но SC-слова нет (буфер/подложка/текстура).
    Для ручного просмотра (не включаются в основной датасет)."""
    t = TAG_RE.sub("", f"{p.get('title','')} {p.get('abstract','')}").lower()
    marker = bool(IBAD_RE.search(t) or RABITS_RE.search(t) or ISD_RE.search(t))
    if not marker:
        return False
    return not bool(SC_RE.search(t))


# ---- Ручная классификация спорных (2026-08-31, просмотрено автором-ассистентом) ----
# Ключи = norm_key (юр+номер)
WHITELIST_MAYBE = {
    # Релевантные: IBAD-MgO/буферы/подложки для ВТСП
    "US6190752",   # Wang 1997, rock-salt IBAD — ОСНОВА IBAD-MgO
    "US6312819",   # UC, oriented oxide electrodes YSZ+IBAD
    "US6921741",   # UC, substrate for epitaxial layers (IBAD)
    "US6899928",   # UC, Dual IBAD biaxially textured template — ключевой
    "US7261776",   # AMSC, buffer layers on textured metal (IBAD)
    "US20070026136",  # UC, IBAD texturing continuous mode (R2R)
    "US20090110915",  # LANL, nucleation layer for IBAD
    "JP2011006751",   # Fujikura, oriented polycrystal substrate IBAD
    "JP5452216",      # Fujikura, three-fold MgO IBAD
    "WO2014183237",   # Shanghai SC, simplified isolation layer IBAD-MgO
    "CN114242335",    # SAMRI, km-IBAD-MgO — ключевой
}
BLACKLIST_MAYBE = {
    # Нерелевантные: IBAD для GaN/стекла/резисторов/покрытий
    "US8197941",   # Guardian, low-E стекло
    "WO2008048628",  # LANL, GaN на стекле
    "JP5641683",   # Heraeus, резистор 1200°C
    "JP2016508943",  # Muller, UV-реакция оксидов
    "JP6286553",   # Apple, покрытие зеркало
    "US10546976",  # iBeam, GaN на IBAD
    "JP6739452",   # iBeam, GaN на IBAD
    "JP2020533764",  # Dyson, аккумулятор
}


def load(name: str) -> list:
    f = PAT / name
    if not f.exists():
        return []
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
        return d.get("patents", [])
    except Exception:
        return []


def main() -> None:
    # 1. Загрузка
    google_all = load("ibad_tapes_wide.json")
    lens_files = ["ibad_mgo_tech.json", "ibad_mgo2_tech.json",
                  "ibad_ysz_tech.json", "rabits_tech.json", "isd_tech.json"]
    lens_all = []
    for f in lens_files:
        lens_all += load(f)

    # 2. Фильтр релевантности (A: SC обязателен) + спорные (maybe)
    google_rel = [p for p in google_all if relevant(p)]
    lens_rel = [p for p in lens_all if relevant(p)]
    google_maybe = [p for p in google_all if maybe(p)]
    lens_maybe = [p for p in lens_all if maybe(p)]

    # 3. Словари по norm_key
    g_by_key = {}
    for p in google_rel:
        k = norm_key(p.get("publication_number", ""))
        if k and k not in g_by_key:
            g_by_key[k] = p
    l_by_key = {}
    for p in lens_rel:
        k = norm_key(p.get("publication_number", ""))
        if k and k not in l_by_key:
            l_by_key[k] = p

    both = set(g_by_key) & set(l_by_key)
    only_g = set(g_by_key) - set(l_by_key)
    only_l = set(l_by_key) - set(g_by_key)

    merged = []
    # 4. Объединение
    for k in both:
        g = g_by_key[k]
        l = l_by_key[k]
        # приоритет Google, но берём цитирования из Lens
        m = dict(g)
        m["source"] = "google+lens"
        if l.get("cited_by"):
            m["cited_by"] = l["cited_by"]
        if l.get("references"):
            m["references"] = l["references"]
        m["lens_id"] = l.get("lens_id", "")
        merged.append(m)
    for k in only_g:
        m = dict(g_by_key[k])
        m["source"] = "google"
        merged.append(m)
    for k in only_l:
        m = dict(l_by_key[k])
        m["source"] = "lens"
        merged.append(m)

    # 4.5 Whitelist-патенты (ручная классификация спорных, 2026-08-31)
    whitelist_pats = []
    for p in google_maybe + lens_maybe:
        k = norm_key(p.get("publication_number", ""))
        if k in WHITELIST_MAYBE:
            m = dict(p)
            m["source"] = "google+lens" if k in g_by_key and k in l_by_key else \
                           ("lens" if k in l_by_key else "google")
            m["manual_review"] = True
            whitelist_pats.append(m)
    merged += whitelist_pats

    # 5. Сортировка по приоритетной дате
    merged.sort(key=lambda p: (p.get("priority_date") or "")[:10])

    # 6. Статистика — пересчёт ПОСЛЕ добавления whitelist
    src = Counter(m.get("source", "?") for m in merged)
    jur = Counter((m.get("publication_number", "") or "")[:2].upper() for m in merged)
    with_cites = sum(1 for m in merged if m.get("cited_by"))

    result = {
        "description": "Объединённый датасет IBAD-семейства (Google + Lens)",
        "source_counts": dict(src),
        "jurisdiction_counts": dict(jur),
        "with_citations": with_cites,
        "total": len(merged),
        "patents": merged,
    }
    for d in (PAT, GIT.parent):
        d.mkdir(parents=True, exist_ok=True)
        (d / "ibad_merged.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")

    # 7. Спорные (для ручного просмотра) — с whitelist/blacklist
    # Whitelist уже добавлены в merged (§4.5); здесь — только maybe (не whitelist, не blacklist)
    maybe_merged = {}
    for p in google_maybe + lens_maybe:
        k = norm_key(p.get("publication_number", ""))
        if k in BLACKLIST_MAYBE:
            continue  # ложные — отбрасываем
        if k in WHITELIST_MAYBE:
            continue  # уже добавлены в merged
        if k and k not in maybe_merged and k not in g_by_key and k not in l_by_key:
            maybe_merged[k] = p
    maybe_list = sorted(maybe_merged.values(), key=lambda p: (p.get("priority_date") or "")[:10])
    maybe_result = {
        "description": "Спорные патенты IBAD (маркер без SC-слова) — ручной просмотр",
        "total": len(maybe_list),
        "patents": maybe_list,
    }
    for d in (PAT, GIT.parent):
        (d / "ibad_maybe.json").write_text(
            json.dumps(maybe_result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Спорных (ibad_maybe.json): {len(maybe_list)}")


if __name__ == "__main__":
    main()
