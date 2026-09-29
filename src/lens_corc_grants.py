#!/usr/bin/env python3
"""Lens: патентная база CORC по ГРАНТОПОЛУЧАТЕЛЯМ (кейс 009, грантовый поиск).

Цель: покрыть «грантовое поле» CORC через патенты ключевых финансируемых игроков.
Локальные грант-данные (NSF/CORDIS/РНФ + funding-блоки PDF = DE-SC0007660 и др.) —
потолок извлечения НОМЕРОВ грантов. Lens добавляет только: состав патентов по
грантополучателям (ACT=DOE SBIR, CERN, KIT, ВНИИКП/Курчатовский, Китай=NSFC/CRAFT),
их судьбу (legal_status) и импакт (cited_by) — т.е. коммерциализацию грантовой разработки.

План 13 запросов (разрешено командой):
  A1 title CORC
  A2 title|abstract "conductor on round core"
  B1 assignee ACT
  B2 inventor van der Laan + superconducting
  B3 assignee CERN + CORC/round core
  B4 assignee KIT/Karlsruhe + HTS cable/CORC
  B5 assignee ВНИИКП/VNIIKP + Sytnikov/Vysotsky
  B6 assignee Kurchatov + CORC/VTS
  C1 jurisdiction CN + CORC/round core
  C2 jurisdiction US + CORC-core
  C3 jurisdiction JP/KR/EP + CORC-core
  D1 CORC-core sort cited_by desc (топ-25)
  D2 CORC-core + legal_status (expired/lapsed)

Выход: data/raw/patents/cases/009_corc_grants.json + паспорт.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict, Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOKEN = os.environ.get("LENS_TOKEN", "")
if not TOKEN:
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("LENS_TOKEN="):
                TOKEN = line.split("=", 1)[1].strip()
                break
if not TOKEN:
    print("Нет LENS_TOKEN!")
    sys.exit(1)

LENS_API = "https://api.lens.org/patent/search"

INCLUDE = [
    "biblio.publication_reference",
    "biblio.application_reference",
    "biblio.priority_claims",
    "biblio.invention_title",
    "biblio.parties",
    "biblio.cited_by",
    "abstract",
]
# legal_status — попробуем отдельно; если API не знает поле — включим только в D2-запрос с retry.
INCLUDE_LS = INCLUDE + ["biblio.legal_status"]


def mp(field: str, phrase: str) -> dict:
    return {"match_phrase": {field: phrase}}


def m(field: str, term: str) -> dict:
    return {"match": {field: term}}


def corc_core() -> dict:
    """Ядро: CORC или conductor on round core в title/abstract."""
    return {"bool": {"should": [
        mp("title", "CORC"),
        mp("abstract", "CORC"),
        mp("title", "conductor on round core"),
        mp("abstract", "conductor on round core"),
    ]}}


# (tag, query_builder, desc)
def queries() -> list[tuple[str, dict, str]]:
    Q = []
    # A: точное ядро
    Q.append(("A1_title_corc", {"bool": {"must": [mp("title", "CORC")]}}, "title=COPC-ядро"))
    Q.append(("A2_round_core", {"bool": {"should": [mp("title", "conductor on round core"), mp("abstract", "conductor on round core")]}}, "conductor on round core"))
    # B: грантополучатели
    Q.append(("B1_act", {"bool": {"must": [m("applicants", "Advanced Conductor Technologies")]}}, "ACT (DOE SBIR/STTR)"))
    Q.append(("B2_vanderlaan", {"bool": {"must": [{"match": {"inventors": "van der Laan"}}, {"bool": {"should": [mp("title", "superconducting"), mp("abstract", "superconducting")]}}]}}, "van der Laan inventor"))
    Q.append(("B3_cern", {"bool": {"must": [m("applicants", "CERN"), {"bool": {"should": [mp("title", "CORC"), mp("abstract", "round core"), mp("title", "superconducting cable")]}}]}}, "CERN"))
    Q.append(("B4_kit", {"bool": {"must": [{"bool": {"should": [m("applicants", "Karlsruhe"), m("applicants", "KIT")]}}, {"bool": {"should": [mp("title", "HTS cable"), mp("title", "CORC"), mp("abstract", "coated conductor cable")]}}]}}, "KIT (EUROfusion)"))
    Q.append(("B5_vniikp", {"bool": {"must": [{"bool": {"should": [m("applicants", "VNIIKP"), m("applicants", "ВНИИКП"), m("applicants", "Cable Institute")]}}, {"bool": {"should": [mp("title", "superconducting cable"), mp("abstract", "superconducting cable"), mp("title", "HTS")]}}]}}, "ВНИИКП (РНФ/Росатом)"))
    Q.append(("B6_kurchatov", {"bool": {"must": [{"bool": {"should": [m("applicants", "Kurchatov"), m("applicants", "Курчатов")]}}, {"bool": {"should": [mp("title", "CORC"), mp("abstract", "superconducting"), mp("title", "HTS")]}}]}}, "Курчатовский (ТРТ)"))
    # C: география
    Q.append(("C1_cn", {"bool": {"must": [m("jurisdiction", "CN"), corc_core()]}}, "Китай NSFC/CRAFT"))
    Q.append(("C2_us", {"bool": {"must": [m("jurisdiction", "US"), corc_core()]}}, "США DOE"))
    Q.append(("C3_other", {"bool": {"must": [{"bool": {"should": [m("jurisdiction", "JP"), m("jurisdiction", "KR"), m("jurisdiction", "EP"), m("jurisdiction", "WO")]}}, corc_core()]}}, "JP/KR/EP/WO"))
    # D: импакт/судьба
    Q.append(("D1_top_cited", {"bool": {"must": [corc_core()]}}, "топ по цитированиям (импакт)"))
    Q.append(("D2_legal", {"bool": {"must": [corc_core()]}}, "legal_status"))
    return Q


def lens_search(query: dict, offset: int, size: int, include: list, sort: str | None = None) -> dict | None:
    payload: dict = {"query": query, "size": size, "offset": offset, "include": include}
    if sort:
        payload["sort"] = [{"cited_by_count": {"order": "desc"}}] if "cited" in sort else None
    body = json.dumps(payload).encode()
    req = urllib.request.Request(LENS_API, data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            print(f"[lens] HTTP {e.code}", flush=True)
            if e.code == 429:
                time.sleep(25)
            else:
                return None
        except Exception as e:
            print(f"[lens] ошибка: {str(e)[:80]}", flush=True)
            if attempt == 2:
                return None
            time.sleep(6)
    return None


def extract(p: dict, include_ls: bool = False) -> dict | None:
    lens_id = p.get("lens_id") or ""
    biblio = p.get("biblio", {})
    pr = biblio.get("publication_reference", {})
    jur = pr.get("jurisdiction") or ""
    doc = pr.get("doc_number") or ""
    kind = pr.get("kind") or ""
    pdate = pr.get("date") or ""
    if not (jur and doc):
        return None
    doc_key = f"{jur}_{doc}_{kind}_{pdate}" if kind else f"{jur}_{doc}"
    title = ""
    for t in biblio.get("invention_title", []):
        if t.get("lang") == "en" or t.get("text"):
            title = t.get("text", "")
            break
    abstract = ""
    for a in p.get("abstract", []) or []:
        if a.get("lang") == "en":
            abstract = a.get("text", "")
            break
    applicants = []
    for ap in biblio.get("parties", {}).get("applicants", []):
        name = ap.get("extracted_name", {}).get("value", "")
        if name:
            applicants.append(name)
    # цитирования
    cited_by = []
    cb = biblio.get("cited_by", {})
    for c in cb.get("patents", []) or []:
        d = c.get("document_id", {})
        j, n = d.get("jurisdiction") or "", d.get("doc_number") or ""
        if j and n:
            cited_by.append(f"{j}_{n}")
    rec = {
        "publication_number": doc_key,
        "title": title,
        "abstract": abstract[:1200],
        "assignee": ", ".join(applicants[:3]) if applicants else "",
        "priority_date": (biblio.get("priority_claims", {}).get("earliest_claim", {}).get("date") or "")[:10],
        "filing_date": (biblio.get("application_reference", {}).get("date") or "")[:10],
        "publication_date": pdate[:10],
        "inventor": "",
        "cited_by_n": len(cited_by),
        "url": f"https://www.lens.org/lens/patent/{lens_id}" if lens_id else "",
    }
    inventors = []
    for inv in biblio.get("parties", {}).get("inventors", []):
        name = inv.get("extracted_name", {}).get("value", "")
        if name:
            inventors.append(name)
    rec["inventor"] = ", ".join(inventors[:4])
    if include_ls:
        ls = biblio.get("legal_status", {})
        events = ls.get("events", []) if isinstance(ls, dict) else []
        rec["legal_status"] = [e.get("text") or e.get("type") for e in events[:3]] if events else []
    return rec


def main() -> None:
    grouped: dict[str, dict] = defaultdict(dict)
    calls = 0
    print("=== Lens: CORC по грантополучателям (кейс 009) ===", flush=True)
    for tag, query, desc in queries():
        # D1 — сортировка по цитированиям, size 25
        if tag == "D1_top_cited":
            resp = lens_search(query, 0, 25, INCLUDE)
            calls += 1
            if resp:
                for p in resp.get("data", []) or []:
                    rec = extract(p)
                    if rec:
                        grouped[tag][rec["publication_number"]] = rec
            print(f"  {tag} ({desc}): {len(grouped[tag])} (top-cited, 25)", flush=True)
            time.sleep(3)
            continue
        # D2 — с legal_status
        if tag == "D2_legal":
            resp = lens_search(query, 0, 100, INCLUDE_LS)
            calls += 1
            if resp:
                for p in resp.get("data", []) or []:
                    rec = extract(p, include_ls=True)
                    if rec:
                        grouped[tag][rec["publication_number"]] = rec
            print(f"  {tag} ({desc}): {len(grouped[tag])} (legal_status)", flush=True)
            time.sleep(3)
            continue
        # остальные — до 100, одна страница (экономия)
        resp = lens_search(query, 0, 100, INCLUDE)
        calls += 1
        if resp:
            total = resp.get("total", 0)
            for p in resp.get("data", []) or []:
                rec = extract(p)
                if rec:
                    grouped[tag][rec["publication_number"]] = rec
            print(f"  {tag} ({desc}): {len(grouped[tag])} уник (total={total})", flush=True)
            if total > 100:
                print(f"    ⚠️ total {total} > 100 — страница 2", flush=True)
                resp2 = lens_search(query, 100, 100, INCLUDE)
                calls += 1
                if resp2:
                    for p in resp2.get("data", []) or []:
                        rec = extract(p)
                        if rec:
                            grouped[tag][rec["publication_number"]] = rec
                    print(f"    → {len(grouped[tag])} уник после стр.2", flush=True)
        time.sleep(3)

    # ---- сборка ----
    out_dir = PROJECT_ROOT / "data/raw/patents/cases"
    out_dir.mkdir(parents=True, exist_ok=True)
    # единый файл: тег → патенты
    all_map: dict[str, dict] = {}
    for tag in grouped:
        for pn, rec in grouped[tag].items():
            key = pn
            if key not in all_map:
                rec2 = dict(rec)
                rec2["tags"] = [tag]
                all_map[key] = rec2
            else:
                if tag not in all_map[key]["tags"]:
                    all_map[key]["tags"].append(tag)
    out = out_dir / "009_corc_grants.json"
    out.write_text(json.dumps({
        "query": "CORC патентная база по грантополучателям (грантовый поиск)",
        "downloaded": time.strftime("%Y-%m-%d"),
        "source": "lens.org",
        "note": "ACT/CERN/KIT/ВНИИКП/Курчатовский + география + импакт + legal_status",
        "n_patents": len(all_map),
        "patents": list(all_map.values()),
        "calls": calls,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n=== СВОДКА: всего {len(all_map)} уник. патентов, API-вызовов {calls} ===")
    for tag in grouped:
        print(f"  {tag}: {len(grouped[tag])}")

    # ---- паспорт ----
    passport = PROJECT_ROOT / "case_studies" / "009_corc_cables" / "signals" / "data_passports" / "corc_patents_grants.md"
    passport.parent.mkdir(parents=True, exist_ok=True)
    passport.write_text(
        "# Паспорт: CORC-патенты по грантополучателям (кейс 009)\n\n"
        f"- **Файл:** `data/raw/patents/cases/009_corc_grants.json` ({len(all_map)} патентов)\n"
        f"- **Скрипт:** `src/lens_corc_grants.py`\n"
        f"- **Запросы:** 13 (A1-A2 ядро, B1-B6 грантополучатели, C1-C3 география, D1-D2 импакт/legal)\n"
        f"- **Дата:** {time.strftime('%Y-%m-%d')}\n"
        f"- **API-вызовов:** {calls}\n"
        f"- **Поля:** publication_number, title, abstract, assignee, inventor, priority/filing/publication_date, cited_by_n, legal_status, tags, url\n"
        f"- **Ограничение:** Lens НЕ отдаёт government interest (номера грантов DE-SC...) — грантовые номера только из NSF/CORDIS/РНФ/PDF\n"
        f"- **Как восстановить:** `.venv/bin/python src/lens_corc_grants.py`\n",
        encoding="utf-8",
    )

    # ---- api_budget ----
    budget_log = PROJECT_ROOT / "results/runtime/api_budget.md"
    if budget_log.exists():
        log_text = budget_log.read_text(encoding="utf-8")
    else:
        log_text = "# API budget log\n"
    log_text += (f"\n| {time.strftime('%Y-%m-%d')} | Кейс 009 CORC гранты-патенты "
                 f"(lens_corc_grants.py, 13 лог. запросов) | ~{calls} | — | Да (команда «начинай грантовый поиск») |\n")
    budget_log.write_text(log_text, encoding="utf-8")
    print(f"\nСохранено: {out}")


if __name__ == "__main__":
    main()
