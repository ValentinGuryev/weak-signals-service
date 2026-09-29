#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кейс 010 EcoSwing, ШАГ 5 (S3): ПОЛНЫЙ сбор корпусов конкурентов с references (v2 — с чекпоинтами).

Нужен для S3-графов взаимного цитирования конкурентов (GUIDE ШАГ 5/S3-cross).
Тот же БАЗИС класса-проблемы, что у SC-корпуса:
  <технология> AND (wind turbine OR wind generator)

v2 (2026-09-10, после 429-лимита OpenAlex):
- ЧЕКПОИНТЫ: каждые CHECKPOINT_EVERY страниц (5) сохраняем промежуточный JSON
  (data/raw/openalex/ecoswing_competitors_full.<CHECKPOINT_N>.json + .ckpt).
- ВОССТАНОВЛЕНИЕ: при старте загружает последний чекпоинт (файл ecoswing_competitors_full.ckpt.json),
  продолжает с того места (видел_работы не скачивает заново).
- При 429: 6 ретраев с паузой; после 6 — НЕ бросать корпус, а СОХРАНИТЬ чекпоинт и выйти с кодом 2
  (чтобы перезапустить позже с продолжением).
"""
from __future__ import annotations

import json
import os
import socket
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# SOCKS5-прокси (VPS/SOCKS-прокси): env SOCKS5_PROXY="ip:port" — напр. 127.0.0.1:9051
# (практика проекта: так качали OpenAlex 2026-08-31). Без env — прямое соединение.
_proxy = os.environ.get("SOCKS5_PROXY", "")
if _proxy:
    import socks  # PySocks (в .venv)

    host, port = _proxy.rsplit(":", 1)
    socks.set_default_proxy(socks.SOCKS5, host, int(port))
    socket.socket = socks.socksocket
    print(f"🌐 SOCKS5-прокси включён: {_proxy}", flush=True)

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "raw" / "openalex"
# чекпоинт: постепенный сохранённый корпус
CKPT = OUT_DIR / "ecoswing_competitors_full.ckpt.json"
FINAL = OUT_DIR / "ecoswing_competitors_full.json"
HEADERS = {"User-Agent": "research (mailto:research@example.com)"}
MAILTO = "research@example.com"
SELECT = ("id,doi,title,display_name,publication_year,cited_by_count,publication_date,"
          "abstract_inverted_index,authorships,referenced_works,type,concepts")
BASE = "(wind turbine OR wind generator)"
MEMBERS = {
 "PM_DD": f'("permanent magnet" OR PMSG OR "PM-DD") AND {BASE}',
 "DFIG": f'("doubly fed induction generator" OR DFIG) AND {BASE}',
 "hydraulic": f'("hydraulic transmission" OR "hydraulic drive") AND {BASE}',
 "magnetic_gear": f'("magnetic gear" OR "pseudo direct drive") AND {BASE}',
 "no_rare_earth": f'("rare earth free" OR "rare-earth-free" OR ferrite) AND {BASE}',
}
CHECKPOINT_EVERY = 5  # страниц

DONE = set()      # запросы, собранные ПОЛНОСТЬЮ (пропускаются при перезапуске)
CURSORS = {}      # незавершённые запросы: {name: next_cursor} для докачки с места


def api_get(url: str):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except Exception as e:
            print(f"    retry {attempt+1}: {e}", flush=True)
            time.sleep(3 + attempt * 5)
    return None  # после 6 попыток


def save_ckpt(seen: dict, note: str):
    CKPT.parent.mkdir(parents=True, exist_ok=True)
    with open(CKPT, "w", encoding="utf-8") as f:
        json.dump({"note": note, "n": len(seen), "works": seen,
                   "done": sorted(DONE), "cursors": CURSORS}, f, ensure_ascii=False)
    print(f"  💾 ЧЕКПОИНТ {note}: {len(seen)} работ | done={sorted(DONE)} -> {CKPT}", flush=True)


def fetch_all(query: str, seen: dict, name: str):
    enc = urllib.parse.quote(query)
    cursor = CURSORS.get(name, "*")
    pages = 0
    while cursor:
        url = (f"https://api.openalex.org/works?filter=title_and_abstract.search:{enc}"
               f"&per-page=200&select={SELECT}&cursor={cursor}&mailto={MAILTO}")
        d = api_get(url)
        if d is None:
            print("  ⛔ 6×429/ошибка — СОХРАНЯЮ чекпоинт и выхожу (перезапустить позже)", flush=True)
            save_ckpt(seen, f"after_429_query={query[:20]}")
            sys.exit(2)
        results = d.get("results", [])
        if not results:
            break
        for w in results:
            wid = w.get("id")
            if wid and wid not in seen:
                inv = w.get("abstract_inverted_index")
                abstract = None
                if inv:
                    pos = {}
                    for word, idxs in inv.items():
                        for i in idxs:
                            pos[i] = word
                    abstract = " ".join(pos[i] for i in sorted(pos))
                authors = []
                for a in (w.get("authorships") or []):
                    au = a.get("author") or {}
                    inst = ((a.get("institutions") or [{}])[0] or {}).get("display_name")
                    authors.append({"name": au.get("display_name"), "institution": inst})
                seen[wid] = {
                    "id": wid, "doi": w.get("doi"), "title": w.get("title") or w.get("display_name"),
                    "year": w.get("publication_year"), "date": w.get("publication_date"),
                    "cited_by": w.get("cited_by_count"), "abstract": abstract,
                    "authors": authors, "references": w.get("referenced_works"),
                    "type": w.get("type"),
                    "concepts": [c.get("display_name") for c in (w.get("concepts") or [])],
                }
        pages += 1
        cursor = d.get("meta", {}).get("next_cursor")
        CURSORS[name] = cursor
        if pages % CHECKPOINT_EVERY == 0:
            save_ckpt(seen, f"page{pages}_query={query[:20]}")
        print(f"    [{pages}] {len(results)} работ, накоплено {len(seen)} | query={query[:45]}", flush=True)
        time.sleep(1.5)
    # хвост обработан полностью
    DONE.add(name)
    CURSORS.pop(name, None)
    return seen


def main():
    # восстановление
    seen = {}
    if CKPT.exists():
        try:
            ck = json.load(open(CKPT, encoding="utf-8"))
            seen = ck.get("works", {})
            DONE.update(ck.get("done", []))
            CURSORS.update({k: v for k, v in ck.get("cursors", {}).items()})
            print(f"♻️ Восстановлено из чекпоинта: {len(seen)} работ | done={sorted(DONE)} | cursors={CURSORS}", flush=True)
        except Exception as e:
            print(f"⚠️ Чекпоинт повреждён ({e}), начинаю с нуля", flush=True)
            seen = {}

    for name, q in MEMBERS.items():
        if name in DONE:
            print(f"   ⏭ {name} уже собран полностью, пропуск", flush=True)
            continue
        print(f"\n=== {name}: {q}", flush=True)
        before = len(seen)
        fetch_all(q, seen, name)
        print(f"   {name}: +{len(seen)-before} работ", flush=True)
        save_ckpt(seen, f"done_{name}")
        time.sleep(1.5)

    # финал
    works = sorted(seen.values(), key=lambda w: (w["year"] or 0))
    corpus = {
        "case": "010_ecoswing_sc_wind", "signal": "s3_competitors_full", "date": "2026-09-10",
        "method": "OpenAlex title_and_abstract.search (базис класса-проблемы), полные записи, cursor per-page=200, чекпоинты",
        "members_queries": MEMBERS, "n_works": len(works), "works": works,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(FINAL, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False)
    print(f"\n✅ ГОТОВО: {len(works)} работ -> {FINAL}", flush=True)
    # удалить чекпоинт после успеха
    if CKPT.exists():
        os.remove(CKPT)
        print("🗑️ чекпоинт удалён (финал сохранён)")


if __name__ == "__main__":
    main()