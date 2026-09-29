"""Зарубежные грантовые базы: NSF + NIH RePORTER (6-я база данных).

Мульти-базовый подход (внутренний контракт, docs/KNOWHOW.md):
тренд = пересечение сигналов (наука ∩ патенты ∩ гранты ∩ инвестиции ∩ код).
РНФ — российские гранты; NSF (США, наука) + NIH RePORTER (США, биомед) —
зарубежный аналог, доступны БЕЗ ключа (проверено 2026-08-17/18).

Эндпоинты (проверены):
- NSF:   GET https://api.nsf.gov/services/v1/awards.json?keyword=...&printFields=...&rpp=25
         (параметр rpp вместо size; keyword матчит title+abstract)
- NIH:   POST https://api.reporter.nih.gov/v2/projects/search
         criteria.advanced_text_search = {operator: and, search_field: projecttitle, search_text: "..."}
         (search_text без кавычек даёт шум: 2.9M; с фразой в кавычках — точное совпадение)

Результат: data/raw/grants_foreign/{nsf,nih}_results.json
Формат записи: {source, query, id, title, org, pi, amount, year, url, abstract?}
"""
from __future__ import annotations

import argparse
import json
import logging
import time
import urllib.parse
import urllib.request
from pathlib import Path

from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

NSF_URL = "https://api.nsf.gov/services/v1/awards.json"
NIH_URL = "https://api.reporter.nih.gov/v2/projects/search"

# Ключевые направления сверхпроводимости (пилотная область).
# Список выровнен по label патентного слоя (data/raw/patents/patents_results.json),
# чтобы пересечение баз (гранты ∩ патенты ∩ arXiv) работало по label.
KEYWORDS = [
    "superconducting diode",          # диодный эффект (РНФ: Фоминов, Водолазов)
    "fluxonium",                      # флаксоника / fluxonium кубиты
    "no-insulation coil",             # NI-катушки (70k патентов, 0 грантов РНФ)
    "flux pinning",                   # пиннинг ВТСП-2G
    "fluxonics",                      # флаксонная логика
    "force-free coil",                # квазибессиловые обмотки ВТСП
    "superconducting magnet",         # ВТСП-магниты (термояд: CFS $1 млрд)
    "mgb2",                           # MgB2 провода
    "superconducting qubit",          # сверхпроводящие кубиты
    "josephson junction",             # джозефсоновские переходы
]

NSF_FIELDS = "id,title,abstractText,awardeeName,piFirstName,piLastName,fundsObligatedAmt,startDate,expDate,fundProgramName,awardeeCity,awardeeStateCode"


def _http_get(url: str, timeout: int = 40, retries: int = 3) -> dict | None:
    """GET с ретраями; возвращает распарсенный JSON или None."""
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001 — логируем и ретраим
            logger.warning("retry %d: %s", attempt + 1, str(e)[:120])
            time.sleep(3 * (attempt + 1))
    return None


def _http_post(url: str, payload: dict, timeout: int = 40, retries: int = 3) -> dict | None:
    """POST JSON с ретраями."""
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "trends-pipeline/1.0"}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            logger.warning("retry %d: %s", attempt + 1, str(e)[:120])
            time.sleep(3 * (attempt + 1))
    return None


# ---------- NSF ----------

def fetch_nsf(keyword: str, max_pages: int = 4) -> list[dict]:
    """Скачать все страницы выдачи NSF по ключевому слову (rpp=25)."""
    rows: list[dict] = []
    for offset in range(0, max_pages * 25, 25):
        params = urllib.parse.urlencode({
            "keyword": keyword,
            "printFields": NSF_FIELDS,
            "rpp": 25,
            "offset": offset,
        })
        data = _http_get(f"{NSF_URL}?{params}")
        if not data or "award" not in data.get("response", {}):
            break
        awards = data["response"]["award"]
        if not awards:
            break
        for a in awards:
            pi = " ".join(filter(None, [a.get("piFirstName"), a.get("piLastName")])) or None
            start = a.get("startDate") or ""
            rows.append({
                "source": "nsf",
                "query": keyword,
                "id": a.get("id"),
                "title": a.get("title"),
                "org": a.get("awardeeName"),
                "city": a.get("awardeeCity"),
                "state": a.get("awardeeStateCode"),
                "pi": pi,
                "amount": a.get("fundsObligatedAmt"),
                "year": start[-4:] if len(start) >= 4 else start,  # MM/DD/YYYY → YYYY
                "program": a.get("fundProgramName"),
                "abstract": (a.get("abstractText") or "")[:2000],
                "url": f"https://www.nsf.gov/awardsearch/showAward?AWD_ID={a.get('id')}",
            })
        logger.info("  NSF '%s' offset=%d → %d строк", keyword, offset, len(rows))
        time.sleep(1.0)  # вежливая пауза
    return rows


# ---------- NIH ----------

def fetch_nih(keyword: str, limit: int = 200) -> list[dict]:
    """NIH RePORTER: точное совпадение фразы в названии проекта."""
    payload = {
        "criteria": {
            "advanced_text_search": {
                "operator": "and",
                "search_field": "projecttitle",
                "search_text": f'"{keyword}"',
            }
        },
        "include_fields": [
            "ProjectTitle", "Organization", "FiscalYear", "AwardAmount",
            "ProjectNum", "PrincipalInvestigators", "AbstractText",
        ],
        "limit": limit,
        "offset": 0,
    }
    data = _http_post(NIH_URL, payload)
    if not data:
        return []
    rows = []
    for r in data.get("results", []):
        org = (r.get("organization") or {}).get("org_name")
        pis = [pi.get("full_name") for pi in (r.get("principal_investigators") or []) if pi.get("full_name")]
        rows.append({
            "source": "nih",
            "query": keyword,
            "id": r.get("project_num"),
            "title": r.get("project_title"),
            "org": org,
            "pi": ", ".join(pis) or None,
            "amount": r.get("award_amount"),
            "year": r.get("fiscal_year"),
            "url": f"https://reporter.nih.gov/project-details/{r.get('appl_id', '')}",
            "abstract": (r.get("abstract_text") or "")[:2000],
        })
    logger.info("  NIH '%s' → %d строк", keyword, len(rows))
    return rows


# ---------- main ----------

def main() -> None:
    ap = argparse.ArgumentParser(description="Скачивание NSF + NIH RePORTER грантов")
    ap.add_argument("--outdir", default="data/raw/grants_foreign")
    ap.add_argument("--sources", default="nsf,nih", help="какие базы качать")
    ap.add_argument("--limit", type=int, default=200, help="лимит NIH на ключевое слово")
    args = ap.parse_args()

    outdir = PROJECT_ROOT / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    sources = [s.strip() for s in args.sources.split(",")]

    db: dict = {"method": "nsf_api + nih_reporter_api (без ключа)", "fetched": None, "grants": []}
    for kw in KEYWORDS:
        for src in sources:
            if src == "nsf":
                rows = fetch_nsf(kw)
            elif src == "nih":
                rows = fetch_nih(kw, limit=args.limit)
            else:
                logger.error("Неизвестный источник: %s", src)
                continue
            db["grants"].extend(rows)
            time.sleep(0.7)

    # дедупликация по (source, id)
    seen: set[tuple[str, str]] = set()
    uniq: list[dict] = []
    for g in db["grants"]:
        key = (g["source"], str(g.get("id") or g.get("title")))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(g)
    db["grants"] = uniq
    db["fetched"] = {"nsf": sum(1 for g in uniq if g["source"] == "nsf"),
                     "nih": sum(1 for g in uniq if g["source"] == "nih")}

    for src in sources:
        path = outdir / f"{src}_results.json"
        sub = [g for g in uniq if g["source"] == src]
        path.write_text(json.dumps({"method": f"{src} API без ключа", "count": len(sub), "grants": sub},
                                   ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Сохранено: %s (%d грантов)", path, len(sub))
    logger.info("Итого уникальных грантов: %d", len(uniq))


if __name__ == "__main__":
    main()
