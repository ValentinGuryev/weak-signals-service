#!/usr/bin/env python3
"""Доскачка абстрактов OpenAlex по IBAD-семейству (1997-2026) для дискриминации.

Кейс 001_ibad_mgo, сигнал S2. Применяем семантический дискриминатор к АБСТРАКТАМ
научных работ (не полным текстам SNF) — нужна полная база релевантных абстрактов.

Источник: OpenAlex (бесплатный, abstract_inverted_index). Фильтр релевантности —
технология текстурирования (IBAD/RABiTS/ISD) ∩ сверхпроводимость (как в train-скрипте).

Годы: 1997-2026 (решение автора: 1991 излишен — начало с 1997, Wang 1997 якорь).

Выход: data/raw/openalex/ibad_abstracts_corpus.json
  {works: [{id, doi, title, year, abstract, cited_by_count, journal, tech}], meta}
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "data" / "raw" / "openalex" / "ibad_abstracts_corpus.json"

HEADERS = {"User-Agent": "hackathon-research (mailto:research@example.com)"}

# Запросы по технологиям IBAD-семейства (широкие, чтобы поймать все синонимы)
QUERIES = {
    "ibad_mgo": "IBAD MgO coated conductor template",
    "ibad_ysz": "IBAD YSZ buffer layer coated conductor",
    "rabits": "RABiTS biaxially textured substrate coated conductor",
    "isd": "inclined substrate deposition MgO coated conductor",
    "mgo_modern": "IBAD MgO template production reel-to-reel coated conductor",
    "mgo_commercial": "IBAD MgO buffer 2G HTS tape manufacturing",
    "rabits_modern": "RABiTS tape production commercialization coated conductor",
    "isz_modern": "IBAD YSZ GZO buffer production superconducting tape",
    # Дополнительные формулировки для ранних якорей (search не находит по первому запросу)
    "mgo_early": "in-plane textured MgO ion beam assisted deposition template",
    "ysz_early": "biaxially aligned YSZ ion beam assisted deposition buffer",
    "rabits_early": "rolling assisted biaxially textured nickel tape substrate",
    "r2r_early": "reel-to-reel ion beam assisted deposition coated conductor",
    "textured_ysz": "textured yttria stabilized zirconia buffer coated conductor",
}

# Якорные работы (точно релевантны IBAD-семейству) — добавляются по DOI вручную,
# т.к. OpenAlex search не всегда возвращает их по текстовым запросам.
ANCHOR_DOIS = {
    "10.1063/1.120227": "ibad_mgo",      # Wang 1997 — in-plane MgO на Si3N4 (295 цит)
    "10.1109/77.784682": "ibad_mgo",      # Foltyn 1999 — meter-long YBCO/IBAD
    "10.1088/0953-2048/17/5/008": "ibad_mgo",  # Kreiskott 2004 — R2R IBAD-MgO
    "10.1557/jmr.2009.0036": "ibad_mgo",  # Matias 2009 — very fast biaxial texture
    "10.1063/1.106514": "ibad_mgo",      # Iijima 1992 — in-plane aligned YBCO
    "10.1063/1.105807": "ibad_ysz",      # Iijima 1991 — first IBAD-YSZ
    "10.1016/j.physc.2005.02.080": "ibad_mgo",  # Hühne 2005 — IBAD-MgO PLD
    "10.1088/0953-2048/17/2/065": "ibad_mgo",   # Yamada 2004 — PLD/IBAD SRL
    "10.1088/1757-899X/502/1/012001": "ibad_ysz",  # Usoskin 2018/19 — Bruker ABAD
}

# Окно по годам
FROM_YEAR = 1997
TO_YEAR = 2026


def oa_works(query: str, cursor: str | None = None) -> dict:
    """Одна страница OpenAlex (курсорная пагинация).

    ВАЖНО: free-text search нельзя комбинировать с фильтрами дат (HTTP 400).
    Годы фильтруем постфактум (как в openalex_ibad_train.py).
    """
    params = {
        "search": query,
        "per-page": "100",
        "mailto": "research@example.com",
        "select": "id,doi,title,publication_year,abstract_inverted_index,cited_by_count,"
                  "primary_location,type",
    }
    if cursor:
        params["cursor"] = cursor
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())


def inv_index_to_text(inv: dict | None) -> str:
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


# Жёсткий фильтр релевантности (расширен: +in-plane textured, biaxially aligned,
# +textured yttria/zirconia, +reel-to-reel — чтобы ловить ранние якоря)
RELEV_RE = re.compile(
    r"ibad|ion[\s-]?beam[\s-]?assisted|rabits|rolling[\s-]?assisted[\s-]?biaxially|\binclined[\s-]?substrate\b|"
    r"biaxially[\s-]?textured|biaxially[\s-]?aligned|in[\s-]?plane[\s-]?textured|"
    r"textured[\s-]?(template|substrate|buffer|layer|yttria|zirconia|magnesium)|"
    r"textur[\s-]?(template|substrate|layer)|"
    r"buffer[\s-]?layer|\bmgo[\s-]?template\b|"
    r"\bysz\b[\s-]?(buffer|template|layer)|gzo[\s-]?(buffer|template|layer)|"
    r"reel[\s-]?to[\s-]?reel[^.]{0,60}(ibad|deposition)", re.I)
SC_RE = re.compile(
    r"superconduct|coated[\s-]?conductor|\bhts\b|\brebco\b|\bybco\b|\b2g\b[\s-]?(tape|wire)|"
    r"critical[\s-]?current[\s-]?density|\bJc\b|flux[\s-]?pinning|tape|wire", re.I)


def relevant(w: dict) -> bool:
    t = f"{w.get('title') or ''} {inv_index_to_text(w.get('abstract_inverted_index'))}"
    return bool(RELEV_RE.search(t) and SC_RE.search(t))


def oa_by_doi(doi: str) -> dict | None:
    """Работа OpenAlex по DOI (для якорных работ, не найденных search'ем)."""
    url = (f"https://api.openalex.org/works/https://doi.org/{doi}?select="
           f"id,doi,title,publication_year,abstract_inverted_index,cited_by_count,"
           f"primary_location,type")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"  DOI {doi}: ошибка {e}")
        return None


def normalize_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())


def main() -> None:
    all_works: dict[str, dict] = {}
    for tech, q in QUERIES.items():
        cursor = "*"
        fetched = 0
        while cursor:
            try:
                d = oa_works(q, cursor=cursor)
            except Exception as e:
                print(f"[{tech}] ошибка: {e}")
                time.sleep(5)
                break
            for w in d.get("results", []):
                wid = w.get("id")
                if wid and wid not in all_works:
                    if not relevant(w):
                        continue
                    year = w.get("publication_year")
                    if not year or year < FROM_YEAR:
                        continue
                    all_works[wid] = {
                        "id": wid,
                        "doi": w.get("doi"),
                        "title": w.get("title"),
                        "year": year,
                        "abstract": inv_index_to_text(w.get("abstract_inverted_index")),
                        "cited_by_count": w.get("cited_by_count"),
                        "journal": ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
                                   if w.get("primary_location") else None,
                        "type": w.get("type"),
                        "tech": tech,
                    }
            fetched += len(d.get("results", []))
            cursor = d.get("meta", {}).get("next_cursor")
            print(f"[{tech}] {fetched} работ (уникальных всего {len(all_works)})")
            time.sleep(1.0)

    # Дозагрузка якорных работ по DOI (не найденных search'ем)
    print("\n=== Дозагрузка якорей по DOI ===")
    for doi, tech in ANCHOR_DOIS.items():
        w = oa_by_doi(doi)
        if not w:
            continue
        year = w.get("publication_year")
        if not year or year < FROM_YEAR:
            print(f"  {doi}: год {year} вне окна")
            continue
        wid = w.get("id")
        if wid in all_works:
            print(f"  {doi}: уже есть ({w.get('title','')[:40]})")
            continue
        all_works[wid] = {
            "id": wid,
            "doi": w.get("doi"),
            "title": w.get("title"),
            "year": year,
            "abstract": inv_index_to_text(w.get("abstract_inverted_index")),
            "cited_by_count": w.get("cited_by_count"),
            "journal": ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
                       if w.get("primary_location") else None,
            "type": w.get("type"),
            "tech": tech, "anchor": True,
        }
        print(f"  + {doi}: {w.get('title','')[:55]} ({year})")
        time.sleep(1.0)

    # Дедуп по нормализованному названию (оставляем с абстрактом / больше цитат)
    by_title: dict[str, list[dict]] = {}
    for w in all_works.values():
        by_title.setdefault(normalize_title(w.get("title") or ""), []).append(w)
    dup_removed = 0
    final: dict[str, dict] = {}
    for key, ws in by_title.items():
        if not key:
            continue
        if len(ws) == 1:
            final[ws[0]["id"]] = ws[0]
        else:
            # оставляем с абстрактом; если оба — с большим числом цитат
            ws.sort(key=lambda x: (bool(x.get("abstract")), x.get("cited_by_count") or 0), reverse=True)
            final[ws[0]["id"]] = ws[0]
            dup_removed += len(ws) - 1
    print(f"\nДедуп: удалено {dup_removed} дубликатов → {len(final)} работ")
    all_works = final

    # с абстрактами
    with_abs = [w for w in all_works.values() if w.get("abstract")]
    years = sorted(set(w["year"] for w in all_works.values()))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "method": "openalex_ibad_abstracts",
        "note": f"Релевантные абстракты IBAD-семейства (IBAD-MgO/YSZ/RABiTS/ISD), {FROM_YEAR}-{TO_YEAR}.",
        "queries": QUERIES,
        "from_year": FROM_YEAR, "to_year": TO_YEAR,
        "total_works": len(all_works),
        "with_abstract": len(with_abs),
        "year_range": [years[0], years[-1]] if years else None,
        "works": sorted(all_works.values(), key=lambda w: w["year"]),
        "meta": {
            "n": len(all_works), "n_with_abstract": len(with_abs),
            "by_tech": {t: sum(1 for w in all_works.values() if w["tech"] == t) for t in QUERIES},
        },
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nСохранено: {OUT}")
    print(f"Всего релевантных: {len(all_works)}, с абстрактами: {len(with_abs)}")
    print(f"Годы: {years[0]}-{years[-1]}")


if __name__ == "__main__":
    main()
