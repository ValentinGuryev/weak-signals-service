#!/usr/bin/env python3
"""Отслеживание возникновения компаний сверхпроводниковой отрасли через Wayback CDX.

Идея: первый снимок домена компании в Wayback Machine = маркер выхода компании
в публичное поле (появление сайта). Для каждой компании запрашиваем CDX API
(web.archive.org/cdx/search/cdx) — первый timestamp = «дата рождения» сайта.

Crunchbase/Tracxn напрямую недоступны (антибот/платно) — Wayback работает.

Выход: data/raw/investments/company_first_seen.json
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "data" / "raw" / "investments" / "company_first_seen.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120"}

# Компании: (название, домен, технология, категория)
COMPANIES = [
    # ВТСП-ленты/магниты/термояд
    ("Commonwealth Fusion Systems", "cfsenergy.com", "ВТСП-магниты термояд", "hts"),
    ("Tokamak Energy", "tokamakenergy.co.uk", "ВТСП-магниты термояд", "hts"),
    ("AMSC", "amsc.com", "ВТСП-ленты RABiTS", "hts"),
    ("SuperPower", "superpower-inc.com", "ВТСП-ленты IBAD", "hts"),
    ("Furukawa Electric", "furukawa.co.jp", "ВТСП-ленты IBAD-GZO", "hts"),
    ("Oxford Instruments", "oxinst.com", "СП-магниты/МРТ", "lts"),
    ("Bruker", "bruker.com", "СП-магниты/МРТ", "lts"),
    ("MetOx", "metoxtech.com", "ВТСП-ленты", "hts"),
    ("Faraday Factory", "faradayfactory.com", "ВТСП-ленты", "hts"),
    # Квантовые (сверхпроводящие кубиты)
    ("D-Wave", "dwavesys.com", "СП-кубиты", "quantum"),
    ("Rigetti", "rigetti.com", "СП-кубиты", "quantum"),
    ("Quantum Machines", "quantum-machines.co", "квант. контроль", "quantum"),
    ("IQM", "meetiqm.com", "СП-кубиты", "quantum"),
    ("QuantWare", "quantware.com", "СП-кубиты", "quantum"),
    ("Zurich Instruments", "zhinst.com", "квант. контроль", "quantum"),
    # Контроль (не СП)
    ("PsiQuantum", "psiquantum.com", "фотонные", "control"),
    ("QuEra", "quera.com", "нейтральные атомы", "control"),
    ("Atom Computing", "atom-computing.com", "нейтральные атомы", "control"),
]


def first_snapshot(domain: str, retries: int = 3) -> dict | None:
    """Первый снимок домена в Wayback (CDX, 1 запись, от 1996). С ретраями."""
    url = ("http://web.archive.org/cdx/search/cdx?url=" + urllib.parse.quote(domain) +
           "&output=json&limit=1&from=1996&filter=statuscode:200")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode())
            if len(data) > 1:  # [заголовок, запись]
                ts = data[1][1]
                original = data[1][2]
                return {"first_seen": ts, "date": f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}",
                        "url": original}
            return {"first_seen": None, "date": None, "url": None}
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(4 * (attempt + 1))
            else:
                return {"first_seen": f"ERR {str(e)[:40]}", "date": None, "url": None}
    return {"first_seen": None, "date": None, "url": None}


def main() -> None:
    results = []
    OUT.parent.mkdir(parents=True, exist_ok=True)
    for name, domain, tech, cat in COMPANIES:
        snap = first_snapshot(domain)
        entry = {"name": name, "domain": domain, "tech": tech, "category": cat, **snap}
        results.append(entry)
        d = entry.get("date") or entry.get("first_seen") or "?"
        print(f"  {name:<28} {domain:<28} первый снимок: {d}", flush=True)
        # накопительное сохранение (защита от таймаута)
        OUT.write_text(json.dumps({
            "method": "wayback_cdx_first_snapshot",
            "note": "Первый снимок домена в Wayback = маркер появления компании "
                    "в публичном поле. Crunchbase/Tracxn недоступны (антибот).",
            "companies": results}, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(1.5)  # вежливость к Wayback

    print(f"\nСохранено: {OUT}")


if __name__ == "__main__":
    main()
