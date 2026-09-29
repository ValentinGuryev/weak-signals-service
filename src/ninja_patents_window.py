#!/usr/bin/env python3
"""НИНЗЯ-СКАЧКА патентов с ВРЕМЕННЫМ ОКНОМ (2006-2018) — для ретро-кейсов калибровки.

Зачем: ретро-кейсы = «стоило ли инвестировать в 2018». Нужны патенты, поданные
в окне 2006-2018 (до момента решения). Патенты после 2018 — не информативны.

Проблема: XHR Google Patents НЕ фильтрует по дате в query (все варианты синтаксиса
дают 0). Решение: качаем свежие страницы, фильтруем по priority_date ∈ [2006, 2018],
докачиваем страницы, пока не наберём N патентов в окне (или упрёмся в лимит страниц).

Отличия от ninja_patents.py (старый, без окна):
- ОДНА тема за запуск (планировщик 15 мин).
- Пауза 45-90 сек между страницами.
- Фильтр по priority_date; докачка до N в окне.
- Пишет в experiment/runs/patents_window/ (НЕ перезаписывает старые файлы!).
- Статус: results/runtime/ninja_status_window.md.

Запуск (одна тема): .venv/bin/python src/ninja_patents_window.py
"""
from __future__ import annotations

import json
import logging
import random
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import PROJECT_ROOT, setup_logging

# Прокси из env (задаётся планировщиком: PROXY_HOST/PROXY_PORT)
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from proxy_requests import enable_from_env
    enable_from_env()
except ImportError:
    pass

logger = setup_logging()

# ===== ВРЕМЕННОЕ ОКНО =====
WIN_FROM = 2006   # priority_date ≥ 2006-01-01
WIN_TO = 2018     # priority_date ≤ 2018-12-31

# ===== ТЕМЫ =====
# Все темы (кейсы): уже скачанные старые (перекачиваем с окном!) + новые кейсы без патентов.
# name -> (query, сколько патентов в окне нужно)
TOPICS: dict[str, tuple[str, int]] = {
    # === КЕЙСЫ АВТОРА (приоритет 1): зарождающиеся тренды — ВЫСОКАЯ ДЕТАЛИЗАЦИЯ ===
    # 300 патентов в окне — для гладкой динамики по годам + ручной разбор автора.
    "corc_cables": ('"CORC" OR "conductor on round core"', 300),
    # ibad_wide: расширенное окно 1995-2026, только релевантные (IBAD/текстура-подложки).
    # Целевой файл ibad_tapes_wide.json (не затирает ibad_tapes.json с окном 1990-2018).
    "ibad_tapes_wide": ('("IBAD" OR "ion beam assisted deposition" OR "ion-beam assisted deposition" OR "ion beam assisted" OR "biaxially textured MgO template" OR "MgO template" OR "RABiTS" OR "rolling assisted biaxially textured" OR "biaxially textured substrate") ("coated conductor" OR "coated superconductor" OR "HTS tape" OR "HTS-2" OR "2G HTS" OR "second generation HTS" OR "second generation tape" OR "2G tape" OR "REBCO" OR "REBCO tape" OR "YBCO" OR "YBCO tape" OR "superconducting tape" OR "superconducting wire" OR "buffer layer" OR "template" OR "substrate")', 600, (1995, 2026)),
    "no_insulation_coils": ('"no-insulation coil" OR "no insulation coil" OR "non-insulated superconducting coil" OR "NI REBCO"', 100),
    "flux_pump": ('"flux pump" superconducting OR "superconducting flux pump"', 100),
    "sc_aircraft_motors": ('"superconducting aircraft motor" OR "superconducting aviation propulsion"', 100),
    "smes": ('"superconducting magnetic energy storage"', 100),
    "sc_motors": ('"superconducting motor"', 300),
    "hts_cables": ('"HTS cable" OR "high temperature superconducting cable"', 300),

    # === Остальные темы ===
    "ac_cables": ('"superconducting cable"', 100),
    "chiral_phonon": ('"chiral phonon"', 50),
    "current_leads": ('"superconducting current lead" OR "HTS current lead"', 100),
    "fluxonics": ('"single flux quantum logic"', 100),
    "fusion_magnets": ('"fusion magnet" OR "tokamak magnet"', 100),
    "hts_tapes": ('"coated conductor" OR "HTS tape" OR "REBCO tape"', 100),
    "maglev": ('"superconducting maglev" OR "magnetic levitation train"', 100),
    "mgb2_mri": ('"MgB2 MRI" OR "magnesium diboride MRI"', 100),
    "nb3sn": ('"Nb3Sn" OR "niobium tin"', 100),
    "qec": ('"quantum error correction"', 100),
    "sc_transformers": ('"superconducting transformer"', 100),
    "sde": ('"superconducting diode"', 100),
    "sfcl": ('"superconducting fault current limiter" OR "SFCL"', 100),
    "bi2223_tapes": ('"Bi-2223" OR "BSCCO tape" OR "bismuth strontium calcium copper oxide tape"', 100),
    "cryo_cmos": ('"cryo-CMOS" OR "cryogenic CMOS"', 100),
    "cryocoolers": ('"cryocooler" OR "pulse tube refrigerator" OR "GM cryocooler"', 100),
    "cryogen_free_mri": ('"cryogen-free MRI" OR "dry magnet MRI" OR "conduction-cooled MRI"', 100),
    "detector_magnets": ('"detector magnet" OR "solenoid magnet" accelerator', 100),
    "high_field_facilities": ('"high field magnet" OR "32 tesla" OR "hybrid magnet"', 100),
    "hts_filters": ('"HTS filter" OR "superconducting filter" OR "high temperature superconducting filter"', 100),
    "hydrides": ('"room temperature superconductor" OR "superhydride" OR "carbonaceous sulfur hydride"', 100),
    "iron_chalcogenides": ('"iron chalcogenide" OR "FeSe superconductor"', 100),
    "iron_pnictides": ('"iron pnictide" OR "FeAs superconductor" OR "iron-based superconductor"', 100),
    "josephson_qec": ('"Josephson junction" OR "transmon qubit" OR "flux qubit"', 100),
    "magnetron_deposition": ('"magnetron sputtering" superconductor coating', 100),
    "nb3al": ('"Nb3Al" OR "niobium aluminide"', 100),
    "proton_therapy": ('"proton therapy" superconducting cyclotron OR gantry', 100),
    "pulsed_magnets": ('"pulsed magnet" OR "multi-pulse magnet" OR "non-destructive magnet"', 100),
    "sc_bearings": ('"superconducting bearing" OR "HTS bearing" OR "magnetic levitation bearing"', 100),
    "sc_induction_heaters": ('"superconducting induction heater" OR "HTS induction heating"', 100),
    "sc_magnetic_refrigeration": ('"magnetic refrigeration" OR "magnetocaloric refrigerator" superconductor', 100),
    "sc_magnetic_separation": ('"magnetic separation" superconducting OR "high gradient magnetic separation"', 100),
    "sc_qubits": ('"superconducting qubit" OR "transmon"', 100),
    "sc_undulators": ('"superconducting undulator" OR "superconducting wiggler"', 100),
    "sc_wind_generators": ('"superconducting wind generator" OR "superconducting wind turbine"', 100),
    "snspd": ('"SNSPD" OR "superconducting nanowire single photon detector"', 100),
    "srf_cavities": ('"superconducting RF cavity" OR "SRF cavity" OR "niobium cavity"', 100),
    "superconducting_diode": ('"superconducting diode"', 100),
    "tes_detectors": ('"transition edge sensor" OR "TES detector" OR "superconducting bolometer"', 100),
    "test_facilities": ('"test facility" superconducting cable OR magnet OR "SULTAN" OR "EDIPO"', 100),
    "topological_qubits": ('"topological qubit" OR "Majorana qubit" OR "Majorana zero mode"', 100),
    "twisted_graphene": ('"twisted bilayer graphene" OR "magic angle graphene"', 100),
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

OUT_DIR = PROJECT_ROOT / "data" / "raw" / "patents" / "topics_window"
GIT_DIR = PROJECT_ROOT / "experiment" / "runs" / "patents_window"
STATUS = PROJECT_ROOT / "results" / "runtime" / "ninja_status_window.md"
DONE_FLAG = PROJECT_ROOT / "results" / ".ninja_window_done"

MAX_PAGES = 30  # макс. страниц на тему (30×25 = 750 патентов сырых, хватит для ~100 в окне)


def xhr_page(query: str, num: int, page: int, topic: str) -> dict | None:
    """Один запрос XHR. При 503/капче — вернуть None (не ретраить)."""
    url = "https://patents.google.com/xhr/query?url=" + urllib.parse.quote(
        f"q={query}&num={num}&page={page}", safe="")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        code = e.code
        if code in (403, 429, 503):
            logger.warning("[%s] HTTP %d (капча/лимит) — НЕ долбим, выходим", topic, code)
        else:
            logger.warning("[%s] HTTP %d", topic, code)
        return None
    except Exception as e:
        logger.warning("[%s] ошибка: %s", topic, str(e)[:80])
        return None


def in_window(p: dict, win: tuple[int, int] | None = None) -> bool:
    """priority_date в окне [from, to]. win=None → глобальное (WIN_FROM, WIN_TO)."""
    wf, wt = win if win else (WIN_FROM, WIN_TO)
    pd = p.get("priority_date") or ""
    if not pd or len(pd) < 4 or not pd[:4].isdigit():
        return False
    year = int(pd[:4])
    return wf <= year <= wt


def save_progress(name: str, query: str, win: tuple[int, int] | None, uniq: list[dict],
                  with_abs: int, scanned: int, out_name: str, target: int) -> None:
    """Накопительное сохранение патентов в файл (out_name) с защитой от перезаписи.

    Пишется после КАЖДОЙ страницы, чтобы прогресс не терялся при 503/таймауте.
    Если файл уже содержит >= target патентов — не трогаем.
    """
    win_str = f"{win[0]}-{win[1]}" if win else f"{WIN_FROM}-{WIN_TO}"
    result = {"query": query, "window": win_str,
              "downloaded": len(uniq), "with_abstract": with_abs,
              "scanned_raw": scanned, "patents": uniq}
    for d in (OUT_DIR, GIT_DIR):
        d.mkdir(parents=True, exist_ok=True)
        f = d / out_name
        if f.exists() and f.stat().st_size > 1000:
            try:
                existing = json.loads(f.read_text(encoding="utf-8"))
                if len(existing.get("patents", [])) >= target:
                    logger.info("  %s: файл уже содержит %d патентов (цель %d) — пропуск",
                                name, len(existing.get("patents", [])), target)
                    continue
            except Exception:
                pass  # битый файл — перезапишем
        if len(uniq) == 0:
            logger.warning("  %s: 0 патентов в окне — НЕ перезаписываю", name)
            continue
        f.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_topic(name: str, query: str, n: int, win: tuple[int, int] | None = None) -> int:
    """Скачать n патентов В ОКНЕ. Возвращает число с абстрактом.

    win — пер-темное окно (from, to); None → глобальное (WIN_FROM, WIN_TO).
    Resume: если файл уже содержит K<n патентов, продолжаем со страницы K//25
    (не начинаем заново — экономим лимит XHR при 503).
    """
    all_pats: list[dict] = []
    seen: set[str] = set()
    with_abs = 0

    # целевой файл: для широкого запроса — отдельный (не затираем ibad_tapes.json)
    out_name = "ibad_tapes_wide.json" if name == "ibad_tapes_wide" else f"{name}.json"

    # resume: стартуем со страницы, где остановились (если файл частичный)
    start_page = 0
    for d in (OUT_DIR, GIT_DIR):
        f = d / out_name
        if f.exists() and f.stat().st_size > 1000:
            try:
                existing = json.loads(f.read_text(encoding="utf-8"))
                k = len(existing.get("patents", []))
                if 0 < k < n:
                    start_page = k // 25
                    all_pats = existing.get("patents", [])
                    seen = {p.get("publication_number") for p in all_pats}
                    with_abs = sum(1 for p in all_pats if p.get("abstract"))
                    logger.info("  %s: resume с %d патентов, старт со стр.%d (цель %d)",
                                name, k, start_page, n)
            except Exception:
                pass
            break

    for page in range(start_page, MAX_PAGES):
        data = xhr_page(query, 25, page, name)
        if not data:
            break  # капча/лимит — стоп

        new_on_page = 0
        for cluster in data.get("results", {}).get("cluster", []):
            for r in cluster.get("result", []):
                p = r.get("patent", {})
                if not p:
                    continue
                pub = p.get("publication_number")
                if not pub or pub in seen:
                    continue
                seen.add(pub)
                new_on_page += 1
                # только патент в окне!
                if not in_window(p, win):
                    continue
                abstract = (p.get("snippet") or "")[:1500]
                if abstract:
                    with_abs += 1
                all_pats.append({
                    "publication_number": pub,
                    "title": p.get("title"),
                    "abstract": abstract,
                    "assignee": p.get("assignee"),
                    "priority_date": p.get("priority_date"),
                    "filing_date": p.get("filing_date"),
                    "inventor": p.get("inventor"),
                    "snippet": (p.get("snippet") or "")[:800],
                    "url": f"https://patents.google.com/patent/{pub}",
                })

        logger.info("  %s: стр.%d → %d в окне (всего %d), сырых на стр. %d",
                    name, page, len(all_pats), len(all_pats), new_on_page)

        # накопительное сохранение после каждой страницы (защита от 503/таймаута)
        save_progress(name, query, win, all_pats[:n], with_abs, len(seen), out_name, n)

        if len(all_pats) >= n:
            break
        # ниньзя-пауза
        if page < MAX_PAGES - 1:
            pause = random.randint(45, 90)
            logger.info("  %s: ниньзя-пауза %ds", name, pause)
            time.sleep(pause)

    uniq = all_pats[:n]
    save_progress(name, query, win, uniq, with_abs, len(seen), out_name, n)
    logger.info("  %s: сохранено %d в окне %d-%d (абстрактов %d, просканировано сырых %d)",
                name, len(uniq), WIN_FROM, WIN_TO, with_abs, len(seen))
    return with_abs


def pending_topics() -> list[str]:
    """Темы, которые ещё не скачаны В ОКНЕ (файл отсутствует или содержит < n патентов)."""
    pending = []
    for name in TOPICS:
        g = GIT_DIR / f"{name}.json"
        if g.exists() and g.stat().st_size > 1000:
            try:
                existing = json.loads(g.read_text(encoding="utf-8"))
                if len(existing.get("patents", [])) >= TOPICS[name][1]:
                    continue  # уже достаточно
            except Exception:
                pass
        pending.append(name)
    return pending


def write_status(msg: str) -> None:
    sizes = {f.name: f.stat().st_size for f in sorted(GIT_DIR.glob("*.json"))} if GIT_DIR.exists() else {}
    done = [n for n in TOPICS if (GIT_DIR / f"{n}.json").exists() and (GIT_DIR / f"{n}.json").stat().st_size > 1000]
    pending = [n for n in TOPICS if n not in done]
    STATUS.write_text(
        f"# Ниньзя-статус (окно {WIN_FROM}-{WIN_TO}) — {time.strftime('%Y-%m-%d %H:%M')}\n\n"
        f"{msg}\n\n"
        f"## Скачано ({len(done)}/{len(TOPICS)})\n{done}\n\n"
        f"## Осталось ({len(pending)})\n{pending}\n\n"
        f"## Размеры файлов\n{json.dumps(sizes, indent=1)}\n",
        encoding="utf-8")


def main() -> None:
    pending = pending_topics()
    if not pending:
        write_status(f"ВСЕ ТЕМЫ СКАЧАНЫ (окно {WIN_FROM}-{WIN_TO}) 🎉")
        DONE_FLAG.write_text("done\n", encoding="utf-8")
        logger.info("Все темы скачаны в окне. Выход.")
        return

    name = pending[0]  # ОДНА тема за запуск
    spec = TOPICS[name]
    query, n = spec[0], spec[1]
    win = spec[2] if len(spec) > 2 else None
    wstr = f"{win[0]}-{win[1]}" if win else f"{WIN_FROM}-{WIN_TO}"
    logger.info("=== Ниньзя (окно %s): тема %s (%d патентов) — осталось %d тем ===",
                wstr, name, n, len(pending))
    n_abs = fetch_topic(name, query, n, win)
    write_status(f"Тема {name}: сохранено {n_abs} абстрактов в окне {wstr}.")
    logger.info("Готово: %s (%d абстрактов). Осталось: %s", name, n_abs, pending_topics())


if __name__ == "__main__":
    main()
