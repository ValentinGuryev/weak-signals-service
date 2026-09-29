#!/usr/bin/env python3
"""Lens: патентная база кейса 010 (EcoSwing / СП-ветрогенераторы).

План (~8 логических запросов, разрешён командой, остаток ~430/1000):
  A1  title|abstract "superconducting wind turbine"
  A2  title|abstract "superconducting wind generator" | "wind power superconducting"
  A3  title|abstract "high temperature superconducting wind" | "HTS wind"
  A4  ядро-контекст: superconducting generator + wind (включить wind-фильтр, счёт)
  B1  "superconducting electrical machine" | "superconducting machine"
  B2  "superconducting generator" (класс, для счёта + игроков)
  C1  верификация: EcoSwing | SUPRAPOWER в title/abstract (патентуют ли)
  C2  assignee-подобная проверка через термины ядра (KEPCO/Changwon/AMSC/Envision)
       — УРОК 008: assignee-фильтры Lens НЕ работают → проверка через термины.

Дедуп: уровень 1 = publication_number, уровень 2 = (assignee + нормализованный title)
(урок 006: US/WO семейства раздувают счёт в ~3 раза).
Выход: data/raw/patents/cases/010_sc_wind.json + паспорт.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
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


def mp(field: str, phrase: str) -> dict:
    return {"match_phrase": {field: phrase}}


def m(field: str, term: str) -> dict:
    return {"match": {field: term}}


def query(es_query: dict, size: int = 40) -> dict:
    body = {
        "query": es_query,
        "include": INCLUDE,
        "size": size,
    }
    req = urllib.request.Request(LENS_API, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {TOKEN}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def _text(x):
    """Развернуть структуру {'text': ...} или [{'text': ...}] или строку в текст."""
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return " ".join(_text(i) for i in x)
    if isinstance(x, dict):
        return _text(x.get("text") or x.get("value") or "")
    return str(x)


def _pubnum(pat: dict) -> str:
    """Номер патента = {jurisdiction}_{doc_number} (схема Lens: application_reference).
    Напр. CN_201821436853; для US: US_... (проверять priority_claims при отсутствии app).
    """
    app = pat.get("biblio", {}).get("application_reference", {})
    if isinstance(app, list):
        app = app[0] if app else {}
    if isinstance(app, dict) and app.get("doc_number"):
        return f"{app.get('jurisdiction','')}_{app.get('doc_number')}"
    pc = pat.get("biblio", {}).get("priority_claims", {})
    if isinstance(pc, dict):
        for c in pc.get("claims", []) or []:
            if isinstance(c, dict) and c.get("doc_number"):
                return f"{c.get('jurisdiction','')}_{c.get('doc_number')}"
    pub = pat.get("biblio", {}).get("publication_reference", [])
    if isinstance(pub, dict):
        pub = [pub]
    for p in pub or []:
        if isinstance(p, dict) and p.get("publication_number"):
            return str(p["publication_number"])
    return ""


def _year(pat: dict) -> int | None:
    pc = pat.get("biblio", {}).get("priority_claims", {})
    if isinstance(pc, dict):
        ec = pc.get("earliest_claim", {}) or {}
        dt = ec.get("date") if isinstance(ec, dict) else None
        if not dt:
            for c in pc.get("claims", []) or []:
                if isinstance(c, dict) and c.get("date"):
                    dt = c["date"]; break
        if dt and isinstance(dt, str):
            return int(dt[:4])
    app = pat.get("biblio", {}).get("application_reference", {})
    if isinstance(app, dict) and isinstance(app.get("date"), str) and app["date"][:4].isdigit():
        return int(app["date"][:4])
    return None


def rec(pat: dict, q: str) -> dict:
    parties = pat.get("biblio", {}).get("parties", {})
    applicants = parties.get("applicants", []) or []
    inv = parties.get("inventors", []) or []
    owners = parties.get("owners_all", []) or []
    applicants_n = "; ".join(_text(a.get("extracted_name", {}).get("value")) for a in applicants[:4])
    inventors = "; ".join(_text(i.get("extracted_name", {}).get("value")) for i in inv[:4])
    owners_n = "; ".join(_text(o.get("extracted_name", {}).get("value")) for o in owners[:2])
    num = _pubnum(pat)
    return {
        "source": "lens", "query": q,
        "publication_number": num,
        "title": _text(pat.get("biblio", {}).get("invention_title")),
        "abstract": _text(pat.get("abstract")),
        "assignee": applicants_n,
        "inventors": inventors,
        "owners": owners_n,
        "cited_by": (pat.get("biblio", {}).get("cited_by", {}) or {}).get("count"),
        "year": _year(pat),
        "url": f"https://www.lens.org/lens/patent/{num}" if num else "",
    }


def run(label: str, es_query: dict, tag: str) -> list[dict]:
    print(f"--- {label} ---")
    try:
        data = query(es_query)
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read()[:200]}")
        return []
    total = data.get("total", 0)
    results = data.get("data", []) or data.get("results", [])
    print(f"  total={total}, получено={len(results)}")
    out = [rec(p, tag) for p in results]
    # пагинация, если нужно (мало вероятно для узкой темы, но на всякий случай)
    n = len(results)
    while n < min(total, 60) and n < 60:
        body = {"query": es_query, "include": INCLUDE, "size": 40,
                "offset": n}
        req = urllib.request.Request(LENS_API, data=json.dumps(body).encode(),
                                     headers={"Authorization": f"Bearer {TOKEN}",
                                              "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                d2 = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            print(f"  HTTP {e.code}")
            break
        results = d2.get("data", []) or d2.get("results", [])
        if not results:
            break
        out.extend(rec(p, tag) for p in results)
        n += len(results)
        time.sleep(1.2)
    return out


def norm_title(t) -> str:
    if isinstance(t, list):
        t = " ".join(str(x) for x in t)
    return " ".join(str(t).lower().split())[:80]


WIND_RE = re.compile(r"\b(wind|turbine|offshore|\u0432\u0435\u0442\u0440|\u2440\u5918|\u98a8\u529b|\u98ce\u529b)\b", re.I)
SC_RE = re.compile(r"(superconduct|hts|rebco|\u8d85\u5bfc|\ucca0\uc804\ub3c4|nadprzewodnik|supraleit)", re.I)
# ГАЗОВЫЕ/паровые турбины — НЕ ветер (патенты «coupled to a turbine» = газовая турбина)
GAS_TURBINE_RE = re.compile(r"(gas turbine|steam turbine|\bturbine engine\b|exhaust|combustion|\bturbine 1\b|turning device|\bturbine 7\b|inlet valve)\b", re.I)
# 80-90е: японские LTS-генераторы New Sunshine — ВНЕ кейса (не ветро-HTS)
LTS_ERA = 2000


def relevant(p: dict) -> bool:
    """Ветро-специфичность: тема СП-генератора/машины В ВЕТРОВОМ контексте.
    Правила:
      - год < 2000 → False (LTS-эпоха: New Sunshine, общие СП-генераторы; кейс = ВТСП-ветро, с ~2000-х)
      - нужен СП-термин И ветро-термин (wind/turbine/offshore/…);
      - «turbine» в контексте ГАЗОВОЙ/паровой турбины (gas/steam/exhaust/…) → НЕ ветер.
    """
    if not p.get("year") or p.get("year") < LTS_ERA:
        return False
    t = f"{p.get('title','')} {p.get('abstract','')}"
    if not SC_RE.search(t):
        return False
    if not WIND_RE.search(t):
        return False
    if GAS_TURBINE_RE.search(t):
        return False
    return True


MNC_RE = re.compile(r"(llc|inc\b|corp|co ltd|ltd|co\b|gmbh|ag\b|s\.a\.|holdings?|industr|energy|power|electric|renewables|heavy|engineering|corp|group|works)\b", re.I, )
GOV_RE = re.compile(r"(ministr|office|department of|academy|university|institute|research|national lab|foundation|fgbun|federalnoe|gosudarstvennoe)\b", re.I)

def player_type(name: str) -> str:
    """Тип игрока по заявителю. Приоритет: НИИ/вуз → гос. структуры → компания (ТНК) → лицо.
    Корейские/японские НИИ-фонды ('academic cooperation foundation') → research_institute."""
    n = (name or "").lower()
    if not n.strip():
        return "unknown"
    if any(k in n for k in ["univ", "institute", "academy", "laborator", "research", "politech", "foundation jeju", "academic cooperation", "ind academy", "univ ", "university"]):
        return "research_institute"
    if any(k in n for k in ["ministr", "department of", "national", "state", "bureau", "commiss", "fgbun", "federalnoe", "gosudarstvennoe", "fnau", "ran"]):
        return "government"
    if len(name.split()) <= 2 and MNC_RE.search(n):
        return "company"
    if MNC_RE.search(n):
        return "company"
    if len(name.split()) <= 2:
        return "individual"
    return "other"


def main() -> None:
    queries = {
        "A1_sc_wind_turbine": {"bool": {"should": [
            mp("title", "superconducting wind turbine"),
            mp("abstract", "superconducting wind turbine")]}},
        "A2_sc_wind_gen": {"bool": {"should": [
            mp("title", "superconducting wind generator"),
            mp("abstract", "superconducting wind generator"),
            mp("title", "wind power superconducting"),
            mp("abstract", "wind power superconducting")]}},
        "A3_hts_wind": {"bool": {"should": [
            mp("title", "high temperature superconducting wind"),
            mp("abstract", "high temperature superconducting wind"),
            mp("title", "HTS wind generator"),
            mp("abstract", "HTS wind generator")]}},
        "A4_sc_gen_wind_ctx": {"bool": {"must": [
            {"bool": {"should": [
                mp("title", "superconducting generator"),
                mp("abstract", "superconducting generator")]}},
            {"bool": {"should": [
                mp("title", "wind"),
                mp("title", "turbine"),
                mp("title", "offshore")],
             "minimum_should_match": 1}}]}},
        "B1_sc_machine": {"bool": {"should": [
            mp("title", "superconducting electrical machine"),
            mp("abstract", "superconducting electrical machine"),
            mp("title", "superconducting machine"),
            mp("abstract", "superconducting machine")]}},
        "B2_sc_generator": {"bool": {"should": [
            mp("title", "superconducting generator"),
            mp("abstract", "superconducting generator")]}},
        "C1_ecoswing_projects": {"bool": {"should": [
            mp("title", "EcoSwing"),
            mp("abstract", "EcoSwing"),
            mp("title", "SUPRAPOWER"),
            mp("abstract", "SUPRAPOWER")]}},
        "C2_players_terms": {"bool": {"should": [
            mp("abstract", "KEPCO superconducting"),
            mp("abstract", "floating offshore superconducting"),
            mp("abstract", "Changwon superconducting"),
            mp("abstract", "AMSC wind turbine superconducting"),
            mp("abstract", "Envision superconducting")]}},
    }

    all_rows: list[dict] = []
    for tag, esq in queries.items():
        rows = run(tag, esq, tag)
        all_rows.extend(rows)
        time.sleep(1.0)

    # Уровень 1: дедуп по публикации (jurisdiction_doc_number; fallback title+assignee)
    seen1: set[str] = set()
    u1: list[dict] = []
    for r in all_rows:
        key = r["publication_number"] or f"T:{norm_title(r['title'])}|{r['assignee'].lower()}"
        if key in seen1:
            continue
        seen1.add(key)
        u1.append(r)

    # Уровень 2: дедуп по (assignee + норм. title) — семейства US/WO
    # только когда assignee непустой; иначе оставляем запись (изд. без чёткого заявителя)
    seen2: set[str] = set()
    u2: list[dict] = []
    for r in u1:
        k = (r["assignee"].lower(), norm_title(r["title"]))
        if k in seen2 and r["assignee"]:
            continue
        seen2.add(k)
        u2.append(r)

    print(f"\nИТОГ: raw={len(all_rows)}, по публикациям={len(u1)}, по изобретениям={len(u2)}")

    # Поля релевантности и типа игрока (для анализа)
    for r in u2:
        r["relevant"] = relevant(r)
        r["player_type"] = player_type(r["assignee"])

    n_rel = sum(1 for r in u2 if r["relevant"])
    print(f"релевантных: {n_rel} / {len(u2)}")

    result = {
        "case": "010_ecoswing_sc_wind",
        "query_plan": list(queries.keys()),
        "downloaded": "2026-09-11",
        "raw_count": len(all_rows),
        "publication_count": len(u1),
        "invention_count": len(u2),
        "relevant_count": n_rel,
        "patents": u2,
    }
    out = PROJECT_ROOT / "data/raw/patents/cases/010_sc_wind.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved:", out)

    # ---- api_budget ----
    budget = PROJECT_ROOT / "results/runtime/api_budget.md"
    with budget.open("a") as f:
        f.write(f"\n| 2026-09-11 | Кейс 010 EcoSwing: Lens патенты (lens_ecoswing.py, "
                f"{len(queries)} логич. запросов; {len(all_rows)} raw / {len(u1)} публ. / "
                f"{len(u2)} изобретений) | Lens.org | ~{len(queries)+6} | Да (команда «Запускай сбор патентов через Lens» 2026-09-11) |\n")
    print("api_budget обновлён")


if __name__ == "__main__":
    main()