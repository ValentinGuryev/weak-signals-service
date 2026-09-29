#!/usr/bin/env python3
"""НИНЬЗЯ-СКАЧКА Google Patents по 10 кейсам Lens-батча 2026-09-11 (ночная сессия).

Собирает патенты Google Patents (XHR, без ключа) по ТЕМ ЖЕ кейсам, что собраны
через Lens.org (data/raw/patents/cases/*.json), для кросс-проверки покрытия
источников Lens → Google Patents (у Lens остаток 7/1000 запросов, сброс 30.09).

ОТЛИЧИЯ от lens_*.py:
- Google-синтаксис запросов (кавычки, OR/AND), а не Lens-ES.
- 1 тема за запуск (ниндьзя), паузы 45-90 с между страницами, при 503/капче — выход.
- **ПОЛНЫЙ сбор**: пагинация до total_num_results (НЕ только 100; решение команды).
- Защитный кап TOTAL_CAP (по умолчанию 400) — на случай мега-широких запросов.
- Резюм досбора: если файл уже есть с downloaded < total — качаем недостающие страницы.
- Сохранение в data/raw/patents/gp_ninja/<case>.json (ОТДЕЛЬНО от Lens cases/,
  имя папки и source-поле явно помечают: данные Google Patents в ниньзя-режиме).
- НЕ перезаписываем завершённый файл (downloaded >= min(total, cap)).
- **Анти-бан-пауза**: счётчик подряд-503 (403/429/503), при N=CONSEC_LIMIT подряд → пауза PAUSE_MIN
  мин (pause-флаг в ninja_gp_state.json, скрипт выходит без единого запроса пока флаг активен).
  Решение команды.

Вызывается планировщиком ninja_gp_scheduler.py 1 раз в 15 минут.
"""
from __future__ import annotations

import json
import logging
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import PROJECT_ROOT, setup_logging

logger = setup_logging()

ND = "google_patents_ninja"  # метка источника: Google Patents, ниньзя-режим
TOTAL_CAP = int(os.environ.get("GP_TOTAL_CAP", "400"))  # защитный кап на число патентов (широкие запросы); дособор → env
PAGE_SIZE = 25              # страница 25 — исторически проверена (лимит GP ~8 запросов)

# Анти-бан-пауза (решение команды)
CONSEC_LIMIT = 2            # сколько ответов подряд 403/429/503 -> пауза (автор: «попыток оч много, исправь на 2»)
PAUSE_MIN = 60              # длительность паузы, минут
STATE_FILE = PROJECT_ROOT / "results" / "runtime" / "ninja_gp_state.json"

# Кейс -> GP-запрос. Порядок = приоритет скачки.
# Запросы — GP-синтаксис, переведены из Lens-планов (results/runtime/lens_plan_2026-09.md).
CASES: dict[str, str] = {
    # Этап 1 (собраны на Lens 2026-09-11)
    "sc_dc_cables": (
        '"superconducting DC cable" OR "DC HTS cable" OR "HVDC superconducting cable" '
        'OR "superconducting DC transmission"'),
    "sfcl": (
        '"superconducting fault current limiter" OR "SFCL" OR '
        '"HTS fault current limiter"'),
    "iron_based": (
        '"iron-based superconductor" OR "pnictide superconductor" OR "iron pnictide" '
        'OR "iron chalcogenide superconductor" OR "FeSe superconductor"'),
    "sc_induction_heaters": (
        '"superconducting induction heater" OR "superconducting induction heating" '
        'OR "HTS induction heating"'),
    # Этап 2
    "uhf_nmr": (
        '"superconducting NMR magnet" OR "HTS NMR insert" OR "superconducting NMR insert" '
        'OR "900 MHz NMR" OR "1.2 GHz NMR"'),
    "current_leads": (
        '"superconducting current lead" OR "HTS current lead" OR '
        '"superconducting current leads" OR "vapor cooled lead"'),
    "cryo_cmos": (
        '"cryogenic CMOS" OR "cryo-CMOS" OR "cryo CMOS"'),
    # тема дата-центров (находка сессии)
    "sc_datacenter": (
        '"superconducting datacenter" OR "superconducting data center" OR '
        '"cryogenic power distribution" OR "superconducting power distribution"'),
    # кейс #87: крио/СП-вычисления для ИИ-ЦОД (патентная разведка 2026-09-17)
    "cryo_sc_computing": (
        '"cryogenic computing" OR "cryogenic data center" OR "superconducting computer" '
        'OR "superconducting processor" OR "single flux quantum processor"'),
    # точечные
    "sc_magnetic_separation": (
        '"superconducting magnetic separation" OR "superconducting magnetic separator" '
        'OR "superconducting separator" OR "high gradient magnetic separation" superconducting'),
    "mkid": (
        '"microwave kinetic inductance detector" OR "kinetic inductance detector" '
        'OR "MKID" OR "MKIDs"'),
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://patents.google.com/",
}

OUT_DIR = PROJECT_ROOT / "data" / "raw" / "patents" / "gp_ninja"
ARC_DIR = OUT_DIR / "_capped"          # архив частичных/старых файлов
STATUS = PROJECT_ROOT / "results" / "runtime" / "ninja_gp_status.md"
DONE_FLAG = PROJECT_ROOT / "results" / ".ninja_gp_done"


# ---------- состояние (анти-бан: счётчик 503 + pause-флаг) ----------

def _load_state() -> dict:
    """Читаем ninja_gp_state.json (счётчик подряд-503 и время окончания паузы)."""
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"consecutive_503": 0, "pause_until": None, "total_retries": 0}


def _save_state(st: dict) -> None:
    STATE_FILE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


def is_paused() -> float:
    """Возвращает оставшиеся секунды паузы (0 — не пауза)."""
    st = _load_state()
    pu = st.get("pause_until")
    if not pu:
        return 0
    left = pu - time.time()
    return left if left > 0 else 0


def register_success() -> None:
    """Успешный ответ — сброс счётчика подряд-503 и (если пауза истекла) флага."""
    st = _load_state()
    st["consecutive_503"] = 0
    pu = st.get("pause_until")
    if pu and pu <= time.time():
        st["pause_until"] = None
    _save_state(st)


def register_fail() -> bool:
    """503/капча — инкремент счётчика; при лимите ставит pause-флаг. Возвращает True, если пауза поставлена."""
    st = _load_state()
    n = (st.get("consecutive_503") or 0) + 1
    st["consecutive_503"] = n
    st["total_retries"] = (st.get("total_retries") or 0) + 1
    if n >= CONSEC_LIMIT:
        st["pause_until"] = time.time() + PAUSE_MIN * 60
        st["consecutive_503"] = 0   # сброс счётчика — следующая пауза отсчитывается заново
        _save_state(st)
        logger.error("⚠️ %d подряд-503 — включаю паузу на %d мин (до %s)",
                     CONSEC_LIMIT, PAUSE_MIN, time.strftime('%H:%M', time.localtime(st["pause_until"])))
        return True
    _save_state(st)
    return False


def xhr_page(query: str, page: int, case: str) -> dict | None:
    """Один запрос XHR. При 503/капче — вернуть None (не ретраить долго).
    Обновляет счётчик подряд-503 / сбрасывает при успехе (anti-ban)."""
    url = "https://patents.google.com/xhr/query?url=" + urllib.parse.quote(
        f"q={query}&num={PAGE_SIZE}&page={page}", safe="")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=40) as r:
            data = json.loads(r.read().decode())
            register_success()
            return data
    except urllib.error.HTTPError as e:
        code = e.code
        if code in (403, 429, 503):
            logger.warning("[%s] HTTP %d (капча/лимит) — НЕ долбим, выходим", case, code)
            if register_fail():
                logger.info("  %s: достигнут лимит подряд-503 → пропускаю остаток кейса (пауза)", case)
        else:
            logger.warning("[%s] HTTP %d", case, code)
        return None
    except Exception as e:
        logger.warning("[%s] ошибка: %s", case, str(e)[:80])
        return None


def _patent_entry(p: dict, case: str) -> dict:
    return {
        "source": ND,
        "case": case,
        "publication_number": p.get("publication_number"),
        "title": (p.get("title") or "").strip(),
        "abstract": (p.get("snippet") or "")[:1500],
        "assignee": p.get("assignee"),
        "priority_date": p.get("priority_date"),
        "filing_date": p.get("filing_date"),
        "grant_date": p.get("grant_date"),
        "inventor": p.get("inventor"),
        "url": f"https://patents.google.com/patent/{p.get('publication_number')}",
    }


def fetch_case(name: str, query: str) -> dict:
    """Полный сбор по кейсу: пагинация до total (cap TOTAL_CAP), досбор существующего."""
    f = OUT_DIR / f"{name}.json"
    # 1) резюм: уже собранные номера/страницы из файла (если не завершён)
    existing: list[dict] = []
    if f.exists() and f.stat().st_size > 1000:
        try:
            prev = json.loads(f.read_text(encoding="utf-8"))
            existing = prev.get("patents", [])
            logger.info("  %s: найден существующий файл (%d патентов) — досбор", name, len(existing))
        except Exception:
            existing = []
    seen = {p.get("publication_number") for p in existing}

    all_pats = list(existing)
    total = TOTAL_CAP        # пока unknown — кап
    start_page = len(existing) // PAGE_SIZE
    page = start_page
    interrupted = False
    empty_page = 0
    while len(all_pats) < TOTAL_CAP:
        data = xhr_page(query, page, name)
        if not data:
            interrupted = True
            break
        results = data.get("results", {})
        total_here = results.get("total_num_results", 0) or 0
        if total_here:
            total = total_here   # фиксируем только при успешной выдаче
        page_total = min(total, TOTAL_CAP)
        got_page = 0
        for cluster in results.get("cluster", []) or []:
            for r in cluster.get("result", []) or []:
                p = r.get("patent", {})
                if not p:
                    continue
                got_page += 1
                pn = p.get("publication_number")
                if pn in seen:
                    continue
                seen.add(pn)
                all_pats.append(_patent_entry(p, name))
        logger.info("  %s: страница %d → +%d (всего %d из total=%d)",
                    name, page, got_page, len(all_pats), page_total)
        if len(all_pats) >= page_total:
            break
        if got_page == 0:
            empty_page += 1
            if empty_page >= 2:
                logger.info("  %s: две пустые страницы подряд — исчерпано (total=%d)", name, total)
                break
        if page < (page_total - 1) // PAGE_SIZE:
            pause = random.randint(45, 90)
            logger.info("  %s: ниньзя-пауза %ds перед страницей %d", name, pause, page + 2)
            time.sleep(pause)
        page += 1

    # завершён ли счёт: total известен и мы дошли до конца / капа
    fetched_all = (not interrupted) and (len(all_pats) >= min(total, TOTAL_CAP))
    capped = total > TOTAL_CAP
    result = {"query": query, "source": ND, "downloaded": len(all_pats),
              "total": total, "capped": capped, "complete": fetched_all,
              "with_abstract": sum(1 for p in all_pats if p.get("abstract")),
              "patents": all_pats}

    if len(all_pats) == 0:
        logger.warning("  %s: 0 патентов — НЕ перезаписываю", name)
        return result

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if f.exists() and f.stat().st_size > 1000:
        try:
            prev = json.loads(f.read_text(encoding="utf-8"))
            if prev.get("complete") and prev.get("downloaded", 0) >= min(prev.get("total", 0) or 0, TOTAL_CAP):
                logger.info("  %s: файл уже завершён (%d) — пропуск", name, prev.get("downloaded"))
                return prev
        except Exception:
            pass
    f.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("  %s: сохранено %d из total=%d (полнота %s) → %s",
                name, len(all_pats), total, "✅" if fetched_all else f"⚠️ неполно {'' if not interrupted else '(503)'}", f)
    return result


def pending_cases() -> list[str]:
    """Кейсы, которые нужно качать (нет файла ИЛИ файл не завершён)."""
    if not OUT_DIR.exists():
        return list(CASES)
    pending = []
    for name in CASES:
        f = OUT_DIR / f"{name}.json"
        if not (f.exists() and f.stat().st_size > 1000):
            pending.append(name)
            continue
        try:
            prev = json.loads(f.read_text(encoding="utf-8"))
            if not prev.get("complete"):
                pending.append(name)   # досбор
        except Exception:
            pending.append(name)
    return pending


def write_status(msg: str) -> None:
    sizes = {f.name: f.stat().st_size for f in sorted(OUT_DIR.glob("*.json"))} if OUT_DIR.exists() else {}
    details = {}
    for name in CASES:
        f = OUT_DIR / f"{name}.json"
        if f.exists() and f.stat().st_size > 1000:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                details[name] = f"{d.get('downloaded')}/{d.get('total')} {'✅' if d.get('complete') else '⚠️'}"
            except Exception:
                details[name] = "? файл битый"
    pending = pending_cases()
    STATUS.write_text(
        f"# Ниньзя-GP статус ({time.strftime('%Y-%m-%d %H:%M')})\n\n"
        f"{msg}\n\n"
        f"## Детали по кейсам\n{json.dumps(details, indent=1, ensure_ascii=False)}\n\n"
        f"## Осталось ({len(pending)})\n{pending}\n\n"
        f"## Размеры файлов\n{json.dumps(sizes, indent=1)}\n",
        encoding="utf-8")


def main() -> None:
    # 0) анти-бан: если пауза активна — выйти СРАЗУ, без единого запроса
    left = is_paused()
    if left > 0:
        mins = int(left // 60)
        logger.info("⏸ Анти-бан пауза: сплю ещё %d мин (до %s) — выхожу без запросов",
                    mins, time.strftime('%H:%M', time.localtime(time.time() + left)))
        write_status(f"⏸ Анти-бан пауза: %d мин до {time.strftime('%H:%M', time.localtime(time.time() + left))} — скачка остановлена")
        return

    pending = pending_cases()
    if not pending:
        write_status("ВСЕ КЕЙСЫ СОБРАНЫ ПОЛНОСТЬЮ 🎉")
        DONE_FLAG.write_text("done\n", encoding="utf-8")
        logger.info("Все кейсы собраны. Выход.")
        return

    st = _load_state()
    if st.get("total_retries"):
        logger.info("(всего накоплено 503-retries: %d)", st["total_retries"])

    name = pending[0]  # только ОДИН кейс за запуск
    if st.get("consecutive_503"):
        logger.info("  счётчик подряд-503: %d → при %d включается пауза %d мин",
                    st["consecutive_503"], CONSEC_LIMIT, PAUSE_MIN)
    query = CASES[name]
    logger.info("=== Ниньзя-GP: кейс %s — осталось %d ===", name, len(pending))
    res = fetch_case(name, query)
    write_status(f"Кейс {name}: {res.get('downloaded')}/{res.get('total')} ({'complete' if res.get('complete') else 'неполно'}).")
    logger.info("Готово: %s (%d/%d). Осталось: %s", name, res.get("downloaded"), res.get("total"), pending_cases())


if __name__ == "__main__":
    main()