#!/usr/bin/env python3
"""Lens: патентная база JTWPA / quantum-limited усилителей (кейс 007).

План: case_studies/007_jtwpa/lens_strategy.md (11 логических запросов, ~25 API-вызовов).
Слои:
  Слой 1 (ядро JTWPA/KIT): traveling wave parametric amplifier, +Josephson, +qubit, kinetic inductance
  Слой 2 (широкий QL/СП-усилители): quantum-limited amplifier, superconducting microwave amplifier,
         Josephson amplifier, qubit readout amplifier
  Слой 3 (контроль/assignee): гиганты (IBM/Google/MIT-Lincoln/D-Wave), коммерческие
         (QuantWare/Silent Waves/Imec/SeeQC/Hypres), KIT-родоначальники (NIST/JPL/Caltech)

Окно: 2000-2026 (вся история). Выход:
  data/raw/patents/cases/007_jtwpa.json    — ядро JTWPA (слои 1+2 после дедупа)
  data/raw/patents/cases/007_kitwpa.json   — KITWPA-конкуренты (J4+контроль)
  + паспорт, api_budget-лог.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
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


# ---------- построение запросов ----------
def mp(field: str, phrase: str) -> dict:
    return {"match_phrase": {field: phrase}}


def m(field: str, term: str) -> dict:
    return {"match": {field: term}}


def q_title(phrase: str) -> dict:
    return {"bool": {"must": [mp("title", phrase)]}}


def q_title_any(phrases: list[str]) -> dict:
    return {"bool": {"should": [mp("title", p) for p in phrases]}}


def q_title_and_title(t1: str, t2: str) -> dict:
    return {"bool": {"must": [mp("title", t1), mp("title", t2)]}}


def q_title_abs(t1: str) -> dict:
    """И title, И abstract содержат фразу (снимает title-only шум для широких)."""
    return {"bool": {"must": [mp("title", t1), mp("abstract", t1)]}}


def q_assignee_and(assignee: str, concept: str) -> dict:
    """assignee (в applicants) + концепт в title/abstract."""
    return {"bool": {"must": [
        {"match": {"applicants": assignee}},
        {"bool": {"should": [
            {"match_phrase": {"title": concept}},
            {"match_phrase": {"abstract": concept}},
        ]}},
    ]}}


# (tag, query, target, group)  group: JTWPA / KITWPA / JPA / QUANTUM
QUERIES = [
    # Слой 1 — ядро JTWPA/KIT
    ("twpa_title", q_title("traveling wave parametric amplifier"), 80, "JTWPA"),
    ("twpa_josephson", q_title_abs("Josephson traveling wave parametric amplifier"), 60, "JTWPA"),
    ("param_amp_qubit", {"bool": {"must": [mp("abstract", "parametric amplifier"), mp("abstract", "Josephson"), mp("abstract", "qubit")]}}, 80, "JTWPA"),
    ("kit_title", q_title("kinetic inductance amplifier"), 60, "KITWPA"),
    # Слой 2 — широкий
    ("ql_amplifier", q_title_any(["quantum-limited amplifier", "quantum limited amplifier"]), 60, "QUANTUM"),
    ("sc_mw_amplifier", q_title_any(["superconducting microwave amplifier", "superconducting amplifier"]), 60, "QUANTUM"),
    ("josephson_amp", q_title("Josephson amplifier"), 60, "JPA"),
    ("qubit_readout_amp", {"bool": {"must": [mp("abstract", "qubit readout"), mp("abstract", "amplifier")]}}, 60, "QUANTUM"),
    # Слой 3 — assignee контроль
    ("giants", {"bool": {"must": [
        {"bool": {"should": [{"match": {"applicants": "IBM"}}, {"match": {"applicants": "Google"}},
                             {"match": {"applicants": "Lincoln"}}, {"match": {"applicants": "D-Wave"}}]}},
        {"bool": {"should": [
            {"match_phrase": {"abstract": "Josephson"}},
            {"match_phrase": {"abstract": "parametric amplifier"}},
            {"match_phrase": {"abstract": "superconducting amplifier"}},
        ]}},
    ]}}, 50, "QUANTUM"),
    ("commercial", {"bool": {"must": [
        {"bool": {"should": [{"match": {"applicants": "QuantWare"}}, {"match": {"applicants": "Silent Waves"}},
                             {"match": {"applicants": "Imec"}}, {"match": {"applicants": "SeeQC"}},
                             {"match": {"applicants": "Hypres"}}]}},
        {"bool": {"should": [
            {"match_phrase": {"abstract": "Josephson"}},
            {"match_phrase": {"abstract": "amplifier"}},
        ]}},
    ]}}, 40, "QUANTUM"),
    ("kit_roots", {"bool": {"must": [
        {"bool": {"should": [{"match": {"applicants": "NIST"}}, {"match": {"applicants": "California Institute"}},
                             {"match": {"applicants": "JPL"}}]}},
        {"bool": {"should": [
            {"match_phrase": {"title": "kinetic inductance"}},
            {"match_phrase": {"abstract": "kinetic inductance amplifier"}},
        ]}},
    ]}}, 30, "KITWPA"),
]

DATE_RANGE = {"gte": "2000-01-01", "lte": "2026-12-31"}


def lens_search(query: dict, offset: int, size: int = 50) -> dict | None:
    payload = {
        "query": query, "size": size, "offset": offset,
        "date_filter": {"field": "publication_date", "from": DATE_RANGE["gte"], "to": DATE_RANGE["lte"]},
        "include": ["biblio.publication_reference", "biblio.application_reference",
                    "biblio.priority_claims", "biblio.invention_title", "biblio.parties", "abstract"],
    }
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


def extract(p: dict) -> dict | None:
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
    return {
        "publication_number": doc_key,
        "title": title,
        "abstract": abstract[:1500],
        "assignee": ", ".join(applicants[:3]) if applicants else "",
        "priority_date": (biblio.get("priority_claims", {}).get("earliest_claim", {}).get("date") or "")[:10],
        "filing_date": (biblio.get("application_reference", {}).get("date") or "")[:10],
        "publication_date": pdate[:10],
        "url": f"https://www.lens.org/lens/patent/{lens_id}" if lens_id else "",
        "topic": "",
    }


def in_window(rec: dict) -> bool:
    for f in ("publication_date", "priority_date", "filing_date"):
        y = (rec.get(f) or "")[:4]
        if y and 2000 <= int(y) <= 2026:
            return True
    return False


def main() -> None:
    grouped = defaultdict(dict)
    calls = 0
    print("=== Lens: JTWPA/QL-усилители (кейс 007) ===", flush=True)
    for tag, query, target, group in QUERIES:
        print(f"\n=== {tag} (group={group}, до {target}) ===", flush=True)
        got, offset, pages = 0, 0, 0
        while got < target and offset < 400 and pages < 6:
            resp = lens_search(query, offset)
            calls += 1
            if not resp:
                break
            results = resp.get("data", []) or []
            total = resp.get("total", 0)
            if not results:
                break
            for p in results:
                rec = extract(p)
                if not rec:
                    continue
                if not in_window(rec):
                    continue
                rec["topic"] = tag
                grouped[group][rec["publication_number"]] = rec
            pages += 1
            offset += len(results)
            got = sum(1 for v in grouped[group].values() if v["topic"] == tag)
            print(f"  offset {offset}: обработано {len(results)} (total={total}, {tag}-уник={got})", flush=True)
            time.sleep(3)
        print(f"  Итог {tag}: {got} уникальных", flush=True)

    # ---- сборка по группам ----
    out_dir = PROJECT_ROOT / "data/raw/patents/cases"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 007_jtwpa.json = JTWPA + QUANTUM (ядро+широкий), дедуп
    core = {}
    for g in ("JTWPA", "QUANTUM", "JPA"):
        core.update(grouped[g])
    jtwpa_list = list(core.values())
    f1 = out_dir / "007_jtwpa.json"
    f1.write_text(json.dumps({
        "query": "JTWPA/quantum-limited amplifiers (Lens, план 007)",
        "downloaded": time.strftime("%Y-%m-%d"),
        "window": "2000-2026",
        "source": "lens.org",
        "note": "ядро JTWPA + широкие QL/СП-усилители + JPA, дедуп по publication_number",
        "patents": jtwpa_list,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    # 007_kitwpa.json = KITWPA
    kit_list = list(grouped["KITWPA"].values())
    f2 = out_dir / "007_kitwpa.json"
    f2.write_text(json.dumps({
        "query": "KITWPA (kinetic inductance amplifier) Lens",
        "downloaded": time.strftime("%Y-%m-%d"),
        "window": "2000-2026",
        "source": "lens.org",
        "note": "kinetic inductance traveling wave amplifiers (конкурент JTWPA)",
        "patents": kit_list,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- паспорт ----
    passport = (PROJECT_ROOT / "case_studies" / "007_jtwpa" / "signals" / "data_passports" / "patents_jtwpa.md")
    passport.parent.mkdir(parents=True, exist_ok=True)
    passport.write_text(
        "# Паспорт: патентные базы JTWPA (кейс 007)\n\n"
        f"- **Файлы:** `data/raw/patents/cases/007_jtwpa.json` ({len(jtwpa_list)}), "
        f"`007_kitwpa.json` ({len(kit_list)})\n"
        f"- **Скрипт:** `src/lens_jtwpa.py`\n"
        f"- **Запросы:** {len(QUERIES)} логических (слои ядро/широкий/контроль), окно 2000-2026\n"
        f"- **Дата:** {time.strftime('%Y-%m-%d')}\n"
        f"- **API-вызовов:** {calls}\n"
        f"- **Поля:** publication_number, title, abstract, assignee, priority/filing/publication_date, url\n"
        f"- **Бюджет:** Lens, остаток до ~529 (лог: results/runtime/api_budget.md)\n",
        encoding="utf-8",
    )

    # ---- api_budget лог ----
    budget_log = PROJECT_ROOT / "results/runtime/api_budget.md"
    if budget_log.exists():
        log_text = budget_log.read_text(encoding="utf-8")
    else:
        log_text = "# API budget log\n"
    log_text += (f"\n| {time.strftime('%Y-%m-%d')} | Кейс 007 JTWPA патенты "
                 f"(lens_jtwpa.py, {len(QUERIES)} лог. запросов) | ~{calls} | — | Да (команда «Выполни Lens по плану 007») |\n")
    budget_log.write_text(log_text, encoding="utf-8")

    # ---- сводка ----
    print("\n=== СВОДКА ===")
    print(f"JTWPA+QUANTUM (ядро): {len(jtwpa_list)}")
    print(f"KITWPA: {len(kit_list)}")
    print(f"API-вызовов: {calls}")
    # годы
    from collections import Counter
    yr = Counter()
    for r in jtwpa_list:
        y = (r.get("publication_date") or "")[:4]
        if y:
            yr[y] += 1
    print("JTWPA-ядро по годам:", dict(sorted(yr.items())))
    print(f"Сохранено: {f1}, {f2}")


if __name__ == "__main__":
    main()
