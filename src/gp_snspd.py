#!/usr/bin/env python3
"""Google Patents (XHR) — добор патентов SNSPD (кейс 006).

Lens дал только 86 (проблема пагинации offset). Google Patents XHR работает без ключа
и отдаёт записи с полями. Ищет по ВСЕМУ тексту (не title), поэтому берём фразы-ядра
(полное название = релевантность), пост-фильтр локально.

Запросы (фразы, total проверены 2026-09-03):
  G1: "superconducting nanowire single photon"   (3124)
  G2: "SNSPD"                                     (1724)
  G3: "SSPD" (superconducting single-photon detector контекст) — отдельно
  C1: "InGaAs" AND "single photon detector"       (1433) — конкурент
  C2: "transition edge sensor" AND photon         (823) — конкурент TES

Выход: data/raw/patents/topics/snspd_gp.json (ядро SNSPD)
       data/raw/patents/topics/snspd_competitors_gp.json (C1+C2)
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "data/raw/patents/topics"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "application/json",
}

# (tag, query, max_pages)
QUERIES = [
    ("G1_nw_sp", '"superconducting nanowire single photon"', 25),
    ("G2_snspd", '"SNSPD"', 15),
    ("C1_ingaas", '"InGaAs" AND "single photon detector"', 10),
    ("C2_tes", '"transition edge sensor" AND photon', 8),
]

SC_NW_RE = re.compile(r"superconducting nanowire|SNSPD|SSPD|nanowire.*superconduct|superconduct.*nanowire", re.I)
SC_RE = re.compile(r"superconduct|NbN|NbTiN|WSi|MoSi", re.I)
PHOTON_RE = re.compile(r"single[- ]photon|photon[- ]?count|photon detector|nanowire", re.I)
SEMI_RE = re.compile(r"InGaAs|silicon|Si\b|GaN|CMOS|SPAD|APD\b|avalanche|InP\b", re.I)
TES_RE = re.compile(r"transition[- ]edge sensor", re.I)


def clean(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "")


def classify(title: str, snippet: str, tag: str) -> str | None:
    t = clean(f"{title} {snippet}").lower()
    is_nw_sc = bool(SC_NW_RE.search(t))
    is_sc = bool(SC_RE.search(t))
    is_photon = bool(PHOTON_RE.search(t))
    is_tes = bool(TES_RE.search(t))
    is_semi = bool(SEMI_RE.search(t)) and not is_nw_sc

    if tag.startswith("G"):
        if is_tes and is_photon and not is_nw_sc:
            return None  # TES попал в ядро — это конкурент, отсечь от SNSPD
        if is_nw_sc and is_sc:
            return "SNSPD"
        if is_sc and is_photon and not is_semi:
            return "SNSPD"
        if is_semi and is_photon:
            return "SPAD"
        return None
    if tag == "C1_ingaas":
        if ("ingaas" in t or "inp" in t) and is_photon and not is_nw_sc:
            return "SPAD"
        return None
    if tag == "C2_tes":
        if is_tes and not is_nw_sc:
            return "TES"
        return None
    return None


def gp_fetch(query: str, page: int = 1, num: int = 50) -> dict | None:
    url = ("https://patents.google.com/xhr/query?url=" +
           urllib.parse.quote(f"q={query}&page={page}&num={num}", safe=""))
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wait = 20 * (attempt + 1)
                time.sleep(wait)
            else:
                print(f"[gp] HTTP {e.code}")
                return None
        except Exception as e:
            print(f"[gp] ошибка: {str(e)[:80]}")
            time.sleep(5)
    return None


def main() -> None:
    collected: dict[str, dict] = {}
    for tag, query, max_pages in QUERIES:
        print(f"\n=== {tag}: {query} ===")
        total = None
        for page in range(1, max_pages + 1):
            d = gp_fetch(query, page=page)
            if not d:
                print(f"  page {page}: нет ответа, стоп")
                break
            res = d.get("results", {})
            total = res.get("total_num_results")
            results = (res.get("cluster") or [{}])[0].get("result", []) if res.get("cluster") else []
            if not results:
                print(f"  page {page}: пусто (total={total})")
                break
            new = 0
            for r in results:
                p = r.get("patent") or {}
                pub = p.get("publication_number") or r.get("id")
                if not pub or pub in collected:
                    continue
                title = p.get("title") or ""
                snippet = (p.get("snippet") or "")[:600]
                cls = classify(title, snippet, tag)
                if cls is None:
                    continue
                assignee = p.get("assignee") or ""
                # assignee иногда список
                if isinstance(assignee, list):
                    assignee = ", ".join(assignee[:3])
                collected[pub] = {
                    "publication_number": pub,
                    "title": title,
                    "assignee": assignee,
                    "priority_date": (p.get("priority_date") or "")[:10],
                    "publication_date": (p.get("publication_date") or "")[:10],
                    "topic": cls,
                    "url": f"https://patents.google.com/patent/{pub}/en",
                }
                new += 1
            print(f"  page {page}: +{new} (всего {len(collected)}, total={total})")
            if page * 50 >= total:
                break
            time.sleep(2.5)
        print(f"  Итог {tag}")

    # Разложить по группам
    groups = {"SNSPD": {}, "SPAD": {}, "TES": {}}
    for pub, rec in collected.items():
        if rec["topic"] in groups:
            groups[rec["topic"]][pub] = rec

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dt = time.strftime("%Y-%m-%d")
    snspd = list(groups["SNSPD"].values())
    (OUT_DIR / "snspd_gp.json").write_text(json.dumps({
        "query": "G1 nanowire single photon + G2 SNSPD (Google Patents)",
        "downloaded": dt, "source": "google_patents_xhr", "patents": snspd},
        ensure_ascii=False, indent=1), encoding="utf-8")
    comp = list(groups["SPAD"].values()) + list(groups["TES"].values())
    (OUT_DIR / "snspd_competitors_gp.json").write_text(json.dumps({
        "query": "C1 InGaAs + C2 TES (Google Patents)",
        "downloaded": dt, "source": "google_patents_xhr", "patents": comp},
        ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n=== ИТОГ Google Patents ===")
    for g, d in groups.items():
        print(f"  {g}: {len(d)}")
    print(f"SNSPD → {OUT_DIR/'snspd_gp.json'}")
    print(f"Компет. → {OUT_DIR/'snspd_competitors_gp.json'}")


if __name__ == "__main__":
    main()
