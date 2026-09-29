#!/usr/bin/env python3
"""Lens-сбор патентов SNSPD (кейс 006) v3 — пагинация как в lens_patents (рабочая).

Уроки v1/v2 (2026-09-03):
- v1 искал в abstract + строгий фильтр → 78;
- v2 искал в title, но сломанная пагинация (брал 1 стр.) → 86;
- Доказано (corc_cables=300, ibad_tapes_wide=600): offset в Lens РАБОТАЕТ, если
  цикл как в lens_patents.py: offset += PAGE_SIZE (50), пауза random 5-8с, ретрай 3x при 429.
v3: копия рабочего цикла lens_patents, запросы по стратегии 006.

Запросы (title.search, релевантнее чем abstract):
  T1: title содержит "superconducting" И "single-photon"       (total ~287)
  T2: title содержит "nanowire" И "superconducting"            (total ~251)
  C1: abstract "InGaAs" + "single-photon detector"              (SPAD, ~18)
  C2: abstract "transition edge sensor" + "photon"              (TES, ~59)
Выход: data/raw/patents/topics/snspd_lens.json (SNSPD), snspd_competitors_lens.json (SPAD+TES)
"""
from __future__ import annotations

import json
import os
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LENS_API = "https://api.lens.org/patent/search"

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

PAGE_SIZE = 50
MAX_OFFSET = 5000


def must_and(field_phrases: list[tuple[str, str]]) -> dict:
    return {"bool": {"must": [
        {"match_phrase": {f: t}} for f, t in field_phrases
    ]}}


# (tech, query, target, окно не ограничено — все годы)
QUERIES: list[tuple[str, dict, int]] = [
    ("T1_sc_singlephoton", must_and([("title", "superconducting"), ("title", "single-photon")]), 287),
    ("T2_nanowire_sc", must_and([("title", "nanowire"), ("title", "superconducting")]), 251),
    ("C1_ingaas_spad", must_and([("abstract", "InGaAs"), ("abstract", "single-photon detector")]), 60),
    ("C2_tes", must_and([("abstract", "transition edge sensor"), ("abstract", "photon")]), 60),
]


def lens_search(query: dict, offset: int) -> dict | None:
    payload = {
        "query": query, "size": PAGE_SIZE, "offset": offset,
        "include": ["biblio.publication_reference", "biblio.application_reference",
                    "biblio.priority_claims", "biblio.invention_title", "biblio.parties",
                    "abstract"],
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(LENS_API, data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[lens] HTTP {e.code}")
        time.sleep(20) if e.code == 429 else None
        return None
    except Exception as e:
        print(f"[lens] ошибка: {str(e)[:80]}")
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


# --- Классификация (после сбора, локально) ---
SC_NW_RE = re.compile(r"superconducting nanowire|nanowire.*superconduct|superconduct.*nanowire|SNSPD|SSPD", re.I)
SC_RE = re.compile(r"superconduct", re.I)
PHOTON_RE = re.compile(r"single[- ]photon|photon[- ]?count|photon detector", re.I)
SEMI_RE = re.compile(r"InGaAs|silicon|Si nanowire|GaN|CMOS|SPAD|APD\b|avalanche|InP\b", re.I)


def classify(title: str, abstract: str, tag: str) -> str | None:
    t = re.sub(r"<[^>]+>", "", f"{title} {abstract}")
    low = t.lower()
    is_tes = "transition edge sensor" in low or "transition-edge sensor" in low
    is_nw_sc = bool(SC_NW_RE.search(t))
    is_sc = bool(SC_RE.search(t))
    is_photon = bool(PHOTON_RE.search(t))
    is_semi = bool(SEMI_RE.search(t)) and not is_nw_sc

    if tag.startswith("T"):
        # из title-запросов ядра: только сверхпроводящие однофотонные/nanowire
        if is_tes and "photon" in low:
            return "TES" if is_tes and not is_nw_sc else None
        if is_nw_sc:
            return "SNSPD"
        if is_sc and is_photon and not is_semi:
            return "SNSPD"
        if is_semi and is_photon:
            return "SPAD"
        return None
    if tag == "C1_ingaas_spad":
        if ("ingaas" in low or "inp" in low) and is_photon and not is_nw_sc:
            return "SPAD"
        return None
    if tag == "C2_tes":
        if is_tes and not is_nw_sc:
            return "TES"
        return None
    return None


def main() -> None:
    all_pats: dict[str, dict] = {}
    for tag, query, target in QUERIES:
        print(f"\n=== {tag} (target {target}) ===")
        seen_local: set[str] = set()
        offset = 0
        total = None
        while offset < MAX_OFFSET:
            data = None
            for attempt in range(3):
                data = lens_search(query, offset)
                if data:
                    break
                print(f"  ретрай {attempt+1}/3 (offset {offset})")
                time.sleep(15)
            if not data:
                break
            total = data.get("total", 0)
            items = data.get("data", []) or []
            if not items:
                break
            if offset >= total:
                break
            new_on_page = 0
            for p in items:
                rec = extract(p)
                if not rec:
                    continue
                pub = rec["publication_number"]
                if pub in all_pats or pub in seen_local:
                    continue
                seen_local.add(pub)
                cls = classify(rec.get("title", ""), rec.get("abstract", ""), tag)
                if cls is None:
                    continue
                rec["topic"] = cls
                all_pats[pub] = rec
                new_on_page += 1
            print(f"  offset {offset} → +{new_on_page} (всего {len(all_pats)}, total={total})")
            if len(all_pats) >= sum(t for _, _, t in QUERIES) * 2:
                break
            offset += PAGE_SIZE
            time.sleep(random.randint(5, 8))
        print(f"  Итог {tag}: в базе {len([r for r in all_pats.values() if r['topic'] in ('SNSPD','SPAD','TES')])}")

    # Разложить
    groups = {"SNSPD": {}, "SPAD": {}, "TES": {}}
    for pub, rec in all_pats.items():
        if rec["topic"] in groups:
            groups[rec["topic"]][pub] = rec

    out_dir = PROJECT_ROOT / "data/raw/patents/topics"
    out_dir.mkdir(parents=True, exist_ok=True)
    dt = time.strftime("%Y-%m-%d")
    snspd = list(groups["SNSPD"].values())
    (out_dir / "snspd_lens.json").write_text(json.dumps({
        "query": "T1+T2 title (Lens v3, полная пагинация)", "downloaded": dt,
        "source": "lens.org", "patents": snspd}, ensure_ascii=False, indent=1), encoding="utf-8")
    comp = list(groups["SPAD"].values()) + list(groups["TES"].values())
    (out_dir / "snspd_competitors_lens.json").write_text(json.dumps({
        "query": "C1+C2 (Lens v3)", "downloaded": dt, "source": "lens.org",
        "patents": comp}, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n=== ИТОГ v3 ===")
    for g, d in groups.items():
        print(f"  {g}: {len(d)}")
    print(f"SNSPD → {out_dir/'snspd_lens.json'}")
    print(f"Компет. → {out_dir/'snspd_competitors_lens.json'}")


if __name__ == "__main__":
    main()
