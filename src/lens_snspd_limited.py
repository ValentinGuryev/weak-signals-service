#!/usr/bin/env python3
"""Lens-сбор SNSPD (титульная технология) — жёсткий бюджет 9 вызовов, пауза 15с.

Запросы (title.search, все годы):
  T1: title superconducting + single-photon    (total 287)
  T2: title nanowire + superconducting         (total 251)
  T3: title SNSPD или SSPD                     (total 48)
Адаптивно: 2-й вызов T1 проверяет работу offset. Если offset работает — листаем
по 100; если нет — берём максимальный допустимый size (100, т.к. 300→400).
Никаких конкурентов. Сохранение после каждого вызова.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LENS_API = "https://api.lens.org/patent/search"
OUT_DIR = PROJECT_ROOT / "data/raw/patents/topics"
OUT_FILE = OUT_DIR / "snspd_lens.json"

env_path = PROJECT_ROOT / ".env"
TOKEN = os.environ.get("LENS_TOKEN", "")
if not TOKEN and env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.startswith("LENS_TOKEN="):
            TOKEN = line.split("=", 1)[1].strip()
            break
if not TOKEN:
    print("Нет LENS_TOKEN!")
    sys.exit(1)

BUDGET = 9
PAUSE = 15
PAGE = 100  # size=100 проверен (работает)

# title-phrase запросы
def must_and_title(terms: list[str]) -> dict:
    return {"bool": {"must": [{"match_phrase": {"title": t}} for t in terms]}}

def title_any(terms: list[str]) -> dict:
    return {"bool": {"must": [{"bool": {"should": [
        {"match_phrase": {"title": t}} for t in terms]}}]}}

# (tag, query, известный total)
TASKS = [
    ("T1_sc_singlephoton", must_and_title(["superconducting", "single-photon"]), 287),
    ("T2_nanowire_sc", must_and_title(["nanowire", "superconducting"]), 251),
    ("T3_abbr", title_any(["SNSPD", "SSPD"]), 48),
]


def lens_search(query: dict, offset: int, size: int = PAGE) -> dict | None:
    payload = {
        "query": query, "size": size, "offset": offset,
        "include": ["biblio.publication_reference", "biblio.application_reference",
                    "biblio.priority_claims", "biblio.invention_title", "biblio.parties",
                    "abstract"],
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(LENS_API, data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            print(f"[lens] HTTP {e.code}")
            if e.code == 429:
                time.sleep(30)
            else:
                return None
        except Exception as e:
            print(f"[lens] ошибка: {str(e)[:80]}")
            time.sleep(8)
    return None


def extract(p: dict) -> dict | None:
    biblio = p.get("biblio", {})
    pr = biblio.get("publication_reference", {})
    jur, doc = pr.get("jurisdiction") or "", pr.get("doc_number") or ""
    if not (jur and doc):
        return None
    kind, pdate = pr.get("kind") or "", pr.get("date") or ""
    doc_key = f"{jur}_{doc}_{kind}_{pdate}" if kind else f"{jur}_{doc}"
    title = ""
    for t in biblio.get("invention_title", []):
        if t.get("lang") == "en" or t.get("text"):
            title = t.get("text", ""); break
    abstract = ""
    for a in p.get("abstract", []) or []:
        if a.get("lang") == "en":
            abstract = a.get("text", ""); break
    applicants = []
    for ap in biblio.get("parties", {}).get("applicants", []):
        name = ap.get("extracted_name", {}).get("value", "")
        if name:
            applicants.append(name)
    pc = biblio.get("priority_claims", {})
    ar = biblio.get("application_reference", {})
    return {
        "publication_number": doc_key,
        "title": title,
        "abstract": abstract,
        "assignee": ", ".join(applicants[:3]),
        "priority_date": (pc.get("earliest_claim", {}).get("date") or "")[:10],
        "filing_date": (ar.get("date") or "")[:10] if ar.get("date") else "",
        "url": f"https://www.lens.org/lens/patent/{p.get('lens_id')}" if p.get("lens_id") else "",
    }


# SNSPD-релевантность (ядро, без конкурентов): title/abstract сверхпроводник+фотон/nanowire
SC_RE = re.compile(r"superconduct|NbN|NbTiN|WSi|MoSi|nanowire", re.I)
PH_RE = re.compile(r"single[- ]photon|photon detector|photon[- ]?count|nanowire", re.I)
SEMI_RE = re.compile(r"InGaAs|silicon|GaN|CMOS|SPAD|APD\b|avalanche", re.I)


def is_snspd(rec: dict) -> bool:
    t = re.sub(r"<[^>]+>", "", f"{rec.get('title','')} {rec.get('abstract','')}")
    low = t.lower()
    if "transition edge sensor" in low and "single-photon" not in low:
        return False
    sc = bool(SC_RE.search(t))
    ph = bool(PH_RE.search(t))
    semi = bool(SEMI_RE.search(t))
    # для title-запросов ядра достаточно SC-фотон контекста
    return sc and ph and not (semi and "nanowire" not in low)


def save(recs: dict, used: int) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "snspd_lens_tmp.json").write_text(json.dumps({
        "query": "T1+T2+T3 title (Lens, бюджет 9)", "downloaded": time.strftime("%Y-%m-%d"),
        "used_calls": used, "source": "lens.org", "patents": list(recs.values())},
        ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> None:
    used = 0
    collected: dict[str, dict] = {}

    for tag, query, total_known in TASKS:
        if used >= BUDGET:
            print(f"бюджет исчерпан на {tag}")
            break
        offset = 0
        while used < BUDGET:
            print(f"\n[{used+1}/{BUDGET}] {tag} offset={offset} size={PAGE}")
            resp = lens_search(query, offset, PAGE)
            used += 1
            if not resp:
                print("  нет ответа, стоп по задаче")
                break
            total = resp.get("total", 0)
            items = resp.get("data", []) or []
            print(f"  total={total}, получено записей={len(items)}")
            if not items:
                break
            before = len(collected)
            new = 0
            for p in items:
                rec = extract(p)
                if not rec:
                    continue
                pub = rec["publication_number"]
                if pub in collected:
                    continue
                if not is_snspd(rec):
                    continue
                rec["topic"] = tag
                collected[pub] = rec
                new += 1
            print(f"  → +{new} SNSPD (всего {len(collected)})")
            save(collected, used)
            if offset == 0 and len(collected) == before:
                # первая страница дала 0 релевантных — странно, но не паникуем
                pass
            # Проверка работы offset на 2-й итерации: если 0 новых на offset>0 — offset сломан
            if offset > 0 and new == 0:
                print("  offset, похоже, не листает (0 новых) — переключаюсь на след. задачу")
                break
            offset += PAGE
            if offset >= total:
                break
            if used >= BUDGET:
                break
            time.sleep(PAUSE)

    # Финальная запись
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "snspd_lens.json").write_text(json.dumps({
        "query": "T1+T2+T3 title (Lens)", "downloaded": time.strftime("%Y-%m-%d"),
        "used_calls": used, "source": "lens.org", "patents": list(collected.values())},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n=== ИТОГ: {len(collected)} SNSPD-патентов, вызовов {used}/{BUDGET} ===")
    # распределение по годам
    from collections import Counter
    yrs = Counter((r.get("priority_date") or "")[:4] for r in collected.values())
    print("по priority_date:", dict(sorted(yrs.items())))


if __name__ == "__main__":
    main()
