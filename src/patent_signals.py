#!/usr/bin/env python3
"""Анализ патентов как СИГНАЛА ТРЕНДА (не коллекции).

Для каждой темы строит:
1. **Динамику по годам** — сколько патентов по priority_date (год подачи).
   Всплеск после научных статей (лаг 2-4 года) = зарождающийся тренд.
2. **Типы заявителей** — крупный игрок (корпорация) vs университет/институт vs однодневка.
   Крупный игрок входит рано = тренд реальный; однодневки = шум.
3. **Релевантность** — доля патентов, где ключевые слова темы реально в title/abstract
   (а не случайно совпали). Очистка от мусора.

Вход: data/raw/patents/topics/*.json (или topics_window/*.json)
Выход: results/patent_signals/<topic>_signal.md + JSON
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "results" / "patent_signals"
OUT.mkdir(parents=True, exist_ok=True)

# Крупные игроки по сверхпроводимости (для классификации)
MAJOR_PLAYERS = {
    # Япония
    "toshiba": "Toshiba",
    "東芝": "Toshiba",
    "sumitomo": "Sumitomo",
    "住友": "Sumitomo",
    "fujikura": "Fujikura",
    "古河": "Furukawa",
    "hitachi": "Hitachi",
    "日立": "Hitachi",
    "mitsubishi": "Mitsubishi",
    "三菱": "Mitsubishi",
    "seiko": "Seiko",
    "kyocera": "Kyocera",
    "nec": "NEC",
    "sharp": "Sharp",
    "canon": "Canon",
    "panasonic": "Panasonic",
    "sony": "Sony",
    # США/Европа
    "american superconductor": "AMSC",
    "general electric": "GE",
    "ge company": "GE",
    "ibm": "IBM",
    "intel": "Intel",
    "qualcomm": "Qualcomm",
    "google": "Google",
    "microsoft": "Microsoft",
    "hypres": "Hypres",
    "seeqc": "SeeQC",
    "psi quantum": "PsiQuantum",
    "rigetti": "Rigetti",
    "ibm research": "IBM",
    "siemens": "Siemens",
    "bosch": "Bosch",
    "philips": "Philips",
    "abb": "ABB",
    "nkt": "NKT",
    "bruker": "Bruker",
    "varian": "Varian",
    "lockheed": "Lockheed",
    "northrop": "Northrop",
    "raytheon": "Raytheon",
    "boeing": "Boeing",
    "spacex": "SpaceX",
    "tesla": "Tesla",
    "tokamak energy": "Tokamak Energy",
    "commonwealth fusion": "CFS",
    "iter": "ITER",
    "cern": "CERN",
    "nfri": "NFRI",
    "korea electric": "KEPCO",
    "lg": "LG",
    "samsung": "Samsung",
    "hyundai": "Hyundai",
    "kawasaki": "Kawasaki",
    "川崎": "Kawasaki",
    "三井": "Mitsui",
    "jfe": "JFE",
    "nssmc": "Nippon Steel",
    "新日鉄": "Nippon Steel",
    # Китай
    "中科院": "CAS (Китай)",
    "中国科学院": "CAS (Китай)",
    "中国电力": "State Grid",
    "国家电网": "State Grid",
    "深圳供电": "Shenzhen Power",
    "华为": "Huawei",
    "中国华能": "Huaneng",
    "国网": "State Grid",
}


def classify_assignee(assignee: str) -> tuple[str, str]:
    """Вернуть (тип, имя-нормализованное). Тип: major / university / institute / other."""
    if not assignee or assignee == "None":
        return ("none", "")
    a = assignee.lower()
    # крупный игрок?
    for key, name in MAJOR_PLAYERS.items():
        if key in a:
            return ("major", name)
    # университет
    if any(k in a for k in ["university", "université", "universitat", "universita", "大学", "学院"]):
        return ("university", assignee)
    # институт/лаборатория/НИИ
    if any(k in a for k in ["institute", "laborator", "research", "研究院", "研究所", "实验室"]):
        return ("institute", assignee)
    # китайские символы = вероятно компания/университет Китая
    if re.search(r"[\u4e00-\u9fff]", assignee):
        return ("other_cn", assignee)
    return ("other", assignee)


def relevance_check(title: str, abstract: str, keywords: list[str]) -> bool:
    """Патент релевантен, если ключевые слова темы реально в title/abstract."""
    text = (title + " " + abstract).lower()
    return any(k.lower() in text for k in keywords)


def analyze_topic(topic: str, file: Path, keywords: list[str]) -> dict:
    d = json.load(open(file))
    patents = d.get("patents", [])
    result = {
        "topic": topic,
        "query": d.get("query", ""),
        "total": len(patents),
        "years": Counter(),          # priority_date год → число
        "assignee_types": Counter(), # тип заявителя → число
        "top_assignees": Counter(),  # assignee → число
        "relevant": 0,
        "irrelevant": 0,
        "year_hist": {},             # год → {type: n} для сигнала
        "patents": [],
    }
    for p in patents:
        year = (p.get("priority_date") or "")[:4]
        if year:
            result["years"][year] += 1
        a = p.get("assignee") or ""
        atype, aname = classify_assignee(a)
        result["assignee_types"][atype] += 1
        if aname:
            result["top_assignees"][aname] += 1
        if keywords:
            rel = relevance_check(p.get("title", ""), p.get("abstract", ""), keywords)
            if rel:
                result["relevant"] += 1
            else:
                result["irrelevant"] += 1
        else:
            rel = True
        # для year_hist
        if year:
            result["year_hist"].setdefault(year, Counter())[atype] += 1
        result["patents"].append({
            "n": p.get("publication_number"),
            "year": year,
            "assignee": a,
            "type": atype,
            "relevant": rel,
            "title": re.sub(r"<[^>]+>", "", p.get("title", "")).strip(),
        })
    return result


def write_report(r: dict, keywords: list[str]) -> Path:
    """Markdown-отчёт: динамика + игроки + релевантность."""
    topic = r["topic"]
    lines = [f"# Патентный сигнал: {topic}", ""]
    lines.append(f"- Запрос: `{r['query']}`")
    lines.append(f"- Патентов: {r['total']}")
    if keywords:
        lines.append(f"- Релевантных: {r['relevant']} ({100*r['relevant']//max(r['total'],1)}%), нерелевантных: {r['irrelevant']}")
    lines.append("")
    lines.append("## Динамика по годам (priority_date)")
    lines.append("")
    lines.append("| Год | Патенты | Крупные игроки | Университеты/НИИ | Прочие |")
    lines.append("|---|---|---|---|---|")
    for year in sorted(r["years"]):
        yh = r["year_hist"].get(year, Counter())
        lines.append(f"| {year} | {r['years'][year]} | {yh.get('major',0)} | {yh.get('university',0)+yh.get('institute',0)} | {yh.get('other',0)+yh.get('other_cn',0)+yh.get('none',0)} |")
    lines.append("")
    lines.append("## Заявители")
    lines.append("")
    lines.append(f"- Крупные игроки: **{r['assignee_types'].get('major',0)}**")
    lines.append(f"- Университеты: {r['assignee_types'].get('university',0)}")
    lines.append(f"- Институты/НИИ: {r['assignee_types'].get('institute',0)}")
    lines.append(f"- Прочие (вкл. китайские): {r['assignee_types'].get('other',0)+r['assignee_types'].get('other_cn',0)+r['assignee_types'].get('none',0)}")
    lines.append("")
    lines.append("### ТОП-10 заявителей")
    lines.append("")
    lines.append("| Заявитель | Патентов |")
    lines.append("|---|---|")
    for name, c in r["top_assignees"].most_common(10):
        lines.append(f"| {name} | {c} |")
    lines.append("")
    # Первые патенты по годам (для примера)
    lines.append("## Примеры патентов по годам")
    lines.append("")
    seen_years = set()
    for p in r["patents"]:
        if p["year"] and p["year"] not in seen_years:
            seen_years.add(p["year"])
            mark = "✅" if p["relevant"] else "⚠️"
            lines.append(f"- **{p['year']}** {mark} {p['n']} — {p['title'][:70]} ({p['assignee'][:30]})")
    path = OUT / f"{topic}_signal.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    # Темы: имя → (файл, ключевые слова для релевантности)
    src_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT_ROOT / "data" / "raw" / "patents" / "topics"
    topics = {
        "sc_motors": (["superconducting motor", "superconducting machine", "superconducting propulsion", "aircraft motor"]),
        "smes": (["superconducting magnetic energy storage", "smes"]),
        "hts_cables": (["hts cable", "high temperature superconducting cable", "superconducting power cable"]),
        "ac_cables": (["superconducting cable", "superconducting power transmission"]),
        "corc_cables": (["corc", "conductor on round core"]),
        "ibad_tapes": (["ibad", "ion beam assisted", "mgo template", "ysz"]),
        "no_insulation_coils": (["no-insulation", "no insulation", "non-insulated", "insulation-free"]),
        "flux_pump": (["flux pump", "flux-pump"]),
    }
    all_reports = []
    for topic, keywords in topics.items():
        f = src_dir / f"{topic}.json"
        if not f.exists():
            print(f"  {topic}: файл {f.name} НЕТ — пропуск")
            continue
        r = analyze_topic(topic, f, keywords)
        path = write_report(r, keywords)
        all_reports.append((topic, r))
        print(f"  {topic}: {r['total']} патентов, релевантных {r['relevant']}, крупных игроков {r['assignee_types'].get('major',0)} → {path.name}")
    print(f"\nГотово: {len(all_reports)} тем. Отчёты в {OUT}/")


if __name__ == "__main__":
    main()
