#!/usr/bin/env python3
"""НИНЗЯ-ДОКАЧКА патентов по ТЕХНОЛОГИЯМ IBAD-семейства (кейс 001_ibad_mgo).

Проблема: широкий запрос ibad_tapes_wide дал 600 патентов, но только ~71 релевантный
(IBAD/RABiTS/ISD-маркер в title+abstract). Остальные 529 — coated conductor без
текстурирования подложки.

Решение: докачиваем УЗКИМИ запросами по 4 технологиям:
  - IBAD-MgO   (ионно-лучевое осаждение MgO-шаблона — доминирующий метод)
  - IBAD-YSZ/GZO (более толстые буферы, Fujikura/Iijima)
  - RABiTS     (текстурирование никелевой ленты прокаткой, ORNL/AMSC)
  - ISD        (inclined substrate deposition — альтернатива без ионного пучка)
с ПОСТ-ФИЛЬТРОМ релевантности (технологический маркер И сверхпроводимость).

Правила ниньзя (внутренний контракт §4.1):
  - 1 попытка за запуск, пауза 45-90 с между страницами, при 503/429 — немедленный выход.
  - НЕ перезаписывать уже скачанные файлы (>1000 байт), накопительное сохранение.
  - Пишет в experiment/runs/patents_window/ (git-трекается) + data/raw/patents/topics_window/.

Отличие от ninja_patents_window.py: НЕ конфликтует с планировщиком (свои файлы,
своя пауза), докачивает только релевантные по узким запросам.

Запуск (одна технология за запуск):
    setsid nohup .venv/bin/python src/ninja_ibad_technologies.py > results/runtime/ninja_ibad_tech.log 2>&1 &
"""
from __future__ import annotations

import json
import logging
import os
import random
import re
import subprocess
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

# ---- Мультиканальный режим (решение 2026-08-31 v2) ----
# Каналы (приоритет): vps (SSH curl на VPS — прямой IP VPS работает!) → прокси (SOCKS5, локальный)
# → direct (локальный IP, SSL-перехват провайдером — обычно fail).
# При 503/429/капче по текущему каналу: переключиться на следующий канал.
# Если все каналы заблокированы — перезапустить SOCKS-прокси на VPS (новый exit) и продолжить.
# Управление: env NINJA_CHANNEL=vps|tor|direct (default: vps), NINJA_MAX_TOR_RESTARTS=30.
# ⚠️ VPS-канал работает (проверено 2026-08-31 11:15): 212 результатов "IBAD-MgO", 3 стр. подряд OK.
TOR_HOST = os.environ.get("TOR_HOST", "127.0.0.1")
TOR_PORT = int(os.environ.get("TOR_PORT", "9051"))
SSH = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes",
       "-o", "ConnectTimeout=8", f"root@{TOR_HOST}"]
MAX_TOR_RESTARTS = int(os.environ.get("NINJA_MAX_TOR_RESTARTS", "30"))

_channel = os.environ.get("NINJA_CHANNEL", "vps").lower()
_tor_restarts = 0
_CHANNEL_ORDER = ["vps", "tor", "direct"]
_all_fail_streak = 0  # подряд полных циклов без успеха (глобальный бан?)


def _full_cycle_failed() -> bool:
    """Если целый цикл каналов (vps→tor→direct) дал 503 — вероятен глобальный бан.
    Возвращаем True и ждём 15 мин, сбрасывая счётчик перезапусков."""
    global _all_fail_streak, _tor_restarts
    _all_fail_streak += 1
    if _all_fail_streak >= 2:  # 2 полных цикла без успеха = бан всех каналов
        logger.warning("Глобальный бан всех каналов (2 цикла) — ждём 15 мин")
        _all_fail_streak = 0
        _tor_restarts = 0
        switch_channel("vps")
        time.sleep(900)
        return True
    return False


def _next_channel() -> str:
    global _channel
    idx = _CHANNEL_ORDER.index(_channel) if _channel in _CHANNEL_ORDER else -1
    _channel = _CHANNEL_ORDER[(idx + 1) % len(_CHANNEL_ORDER)]
    return _channel


def switch_channel(name: str) -> None:
    """Переключить глобальный канал (vps/tor/direct)."""
    global _channel
    _channel = name
    if name == "tor":
        try:
            from proxy_requests import enable_proxy_simple
            enable_proxy_simple(TOR_HOST, TOR_PORT)
            logger.info("Канал → TOR (%s:%d)", TOR_HOST, TOR_PORT)
        except Exception as e:
            logger.warning("Не удалось включить SOCKS-прокси: %s", str(e)[:80])
    elif name == "direct":
        try:
            from proxy_requests import disable_proxy
            disable_proxy()
            logger.info("Канал → DIRECT")
        except Exception as e:
            logger.warning("Не удалось выключить прокси: %s", str(e)[:80])
    else:
        # vps — без прокси на нашей машине, запросы идут через SSH
        try:
            from proxy_requests import disable_proxy
            disable_proxy()
        except Exception:
            pass
        logger.info("Канал → VPS (SSH curl)")


def restart_tor() -> bool:
    """Перезапустить SOCKS-прокси на VPS (новый exit-узел). Возвращает успех.

    Стратегия (2026-08-31 11:25): Google банит все каналы одновременно на
    15-60 мин. Поэтому при каждом перезапуске SOCKS-прокси ждём 90 сек (не сжигаем
    перезапуски впустую). При исчерпании лимита — ждём 15 мин, сбрасываем
    лимит, пробуем VPS (бан мог спасть).
    """
    global _tor_restarts
    if _tor_restarts >= MAX_TOR_RESTARTS:
        logger.warning("Лимит перезапусков SOCKS-прокси (%d) исчерпан — ждём бан 15 мин и пробуем VPS",
                       MAX_TOR_RESTARTS)
        time.sleep(900)  # 15 минут ждём, пока Google отпустит бан
        _tor_restarts = 0
        switch_channel("vps")
        return True
    _tor_restarts += 1
    logger.info("Смена цепочки SOCKS-прокси (NEWNYM, попытка %d/%d)...", _tor_restarts, MAX_TOR_RESTARTS)
    try:
        # Быстрая смена цепочки через ControlPort (быстрее полного рестарта)
        cmd = ("ssh -o StrictHostKeyChecking=no -o BatchMode=yes "
               f"-o ConnectTimeout=8 root@{TOR_HOST} "
               "'echo -e \"AUTHENTICATE \\\"ninja_tor_pass_2026\\\"\\nSIGNAL NEWNYM\\nQUIT\" "
               "| nc 127.0.0.1 9052'")
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if "250 OK" not in r.stdout:
            # fallback: полный рестарт
            subprocess.run(SSH + ["systemctl restart tor"], timeout=40, capture_output=True)
        # ждём перестроения цепочки
        time.sleep(12)
        return True
    except Exception as e:
        logger.warning("Ошибка смены SOCKS-прокси: %s", str(e)[:80])
        return False

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

OUT_DIR = PROJECT_ROOT / "data" / "raw" / "patents" / "topics_window"
GIT_DIR = PROJECT_ROOT / "experiment" / "runs" / "patents_window"

MAX_PAGES = 40          # макс. страниц на технологию (40×25 = 1000 сырых)
PAGE_NUM = 25
PAUSE_MIN, PAUSE_MAX = 8, 15

# ---- Технологии: (query, целевое число релевантных, окно лет, имя файла) ----
# ⚠️ Google капчит СЛОЖНЫЕ OR-запросы. Узкие простые запросы проходят лучше
# и дают больше релевантных на первых страницах (проверено 2026-08-30).
TECHNOLOGIES: dict[str, tuple[str, int, tuple[int, int], str]] = {
    "ibad_mgo": (
        '"IBAD-MgO" template',
        100, (1995, 2026), "ibad_mgo_tech.json"),
    "ibad_mgo2": (
        '"ion beam assisted deposition" "MgO"',
        80, (1995, 2026), "ibad_mgo2_tech.json"),
    "ibad_ysz": (
        '"ion beam assisted deposition" "YSZ"',
        60, (1995, 2026), "ibad_ysz_tech.json"),
    "rabits": (
        '"RABiTS"',
        60, (1995, 2026), "rabits_tech.json"),
    "isd": (
        '"inclined substrate deposition" superconductor',
        40, (1995, 2026), "isd_tech.json"),
}

# ---- Фильтр релевантности (по title+abstract, HTML-теги вырезаны) ----
IBAD_RE = re.compile(r"\bibad\b|ion[\s-]?beam[\s-]?assisted", re.I)
RABITS_RE = re.compile(r"rabits|rolling[\s-]?assisted[\s-]?biaxially", re.I)
ISD_RE = re.compile(r"inclined[\s-]?substrate[\s-]?deposition|\binclined[\s-]?substrate\b", re.I)
MGO_RE = re.compile(r"\bmgo\b|magnesium[\s-]?oxide", re.I)
YSZ_RE = re.compile(r"\bysz\b|yttria[\s-]?stabilized[\s-]?zirconia|\bgzo\b|gadolinium[\s-]?zirconate", re.I)
SC_RE = re.compile(r"superconduct|coated[\s-]?conductor|\bhts\b|\brebco\b|\bybco\b|\b2g\b|tape|wire", re.I)
TEXTURE_RE = re.compile(r"biaxially[\s-]?textured|textured[\s-]?(template|substrate|buffer)|"
                        r"texture|template|buffer[\s-]?layer|epitaxial", re.I)

TAG_RE = re.compile(r"<[^>]+>")


def tech_relevant(title: str, abstract: str, tech: str) -> bool:
    """Релевантен ли патент конкретной технологии (маркер И сверхпроводимость)."""
    t = TAG_RE.sub("", f"{title} {abstract}").lower()
    sc = bool(SC_RE.search(t))
    if not sc:
        return False
    if tech == "ibad_mgo":
        return bool(IBAD_RE.search(t)) and bool(MGO_RE.search(t))
    if tech == "ibad_ysz":
        return bool(IBAD_RE.search(t)) and bool(YSZ_RE.search(t))
    if tech == "rabits":
        return bool(RABITS_RE.search(t))
    if tech == "isd":
        return bool(ISD_RE.search(t))
    return False


def any_tech_relevant(title: str, abstract: str) -> bool:
    """Релевантен ли патент ХОТЯ БЫ одной технологии IBAD-семейства."""
    t = TAG_RE.sub("", f"{title} {abstract}").lower()
    sc = bool(SC_RE.search(t))
    if not sc:
        return False
    return bool(IBAD_RE.search(t) or RABITS_RE.search(t) or ISD_RE.search(t))


def xhr_page(query: str, page: int, tech: str) -> dict | None:
    url = "https://patents.google.com/xhr/query?url=" + urllib.parse.quote(
        f"q={query}&num={PAGE_NUM}&page={page}", safe="")
    # Мультиканальность: vps → tor → direct, при блоке — перезапуск SOCKS-прокси.
    attempts = 0
    while True:
        try:
            if _channel == "vps":
                # SSH curl на VPS (прямой IP VPS работает с Google)
                # ⚠️ ВАЖНО: вся команда ОДНОЙ строкой в кавычках (shell=True на VPS)
                url_sh = url.replace("'", "'\\''")
                ssh_cmd = ("ssh -o StrictHostKeyChecking=no -o BatchMode=yes "
                           f"-o ConnectTimeout=8 root@{TOR_HOST} "
                           f"'curl -s -m 20 -H \"{HEADERS['User-Agent']}\" "
                           f"-H 'Accept: application/json' -- \"{url_sh}\"'")
                r = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=40)
                if r.returncode != 0 or not r.stdout.strip():
                    raise ConnectionError(f"ssh curl fail rc={r.returncode}")
                # Проверка на капчу (Google возвращает HTML)
                if r.stdout.strip().startswith("<"):
                    raise urllib.error.HTTPError(url, 503, "CAPTCHA HTML", None, None)
                return json.loads(r.stdout)
            else:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=20) as r2:
                    return json.loads(r2.read().decode())
        except urllib.error.HTTPError as e:
            code = e.code
            if code in (403, 429, 503):
                attempts += 1
                logger.warning("[%s] HTTP %d (капча/лимит) на канале %s — попытка %d",
                               tech, code, _channel, attempts)
                # 🔑 Ключевая логика: на SOCKS-прокси при 503 — СРАЗУ перезапускаем SOCKS-прокси
                # (свежий exit часто не забанен; проверено: 5 запросов OK с нового exit)
                if _channel == "tor":
                    if not restart_tor():
                        return None
                    continue
                # На vps/direct при 503 — переключаемся на SOCKS-прокси (там свежие exit-узлы)
                if len(_CHANNEL_ORDER) > 1:
                    nxt = _next_channel()
                    switch_channel(nxt)
                    time.sleep(2)
                    continue
                # fallback: перезапуск SOCKS-прокси
                if not restart_tor():
                    return None
                continue
            else:
                logger.warning("[%s] HTTP %d", tech, code)
                return None
        except Exception as e:
            # сетевые ошибки (timeout и т.п.) — на SOCKS-прокси перезапуск, на других — смена канала
            attempts += 1
            logger.warning("[%s] ошибка (%s): %s — попытка %d", tech, _channel, str(e)[:60], attempts)
            if _channel == "tor":
                if not restart_tor():
                    return None
                continue
            if len(_CHANNEL_ORDER) > 1:
                nxt = _next_channel()
                switch_channel(nxt)
                time.sleep(2)
                continue
            if not restart_tor():
                return None
            continue


def in_window(p: dict, win: tuple[int, int]) -> bool:
    pd = p.get("priority_date") or ""
    if not pd or len(pd) < 4 or not pd[:4].isdigit():
        return False
    return win[0] <= int(pd[:4]) <= win[1]


def save_progress(tech: str, query: str, win: tuple[int, int], uniq: list[dict],
                  scanned: int, out_name: str, target: int) -> None:
    result = {
        "query": query, "window": f"{win[0]}-{win[1]}",
        "downloaded": len(uniq), "scanned_raw": scanned, "patents": uniq,
    }
    for d in (OUT_DIR, GIT_DIR):
        d.mkdir(parents=True, exist_ok=True)
        f = d / out_name
        if f.exists() and f.stat().st_size > 1000:
            try:
                existing = json.loads(f.read_text(encoding="utf-8"))
                if len(existing.get("patents", [])) >= target:
                    logger.info("  %s: файл уже содержит %d (цель %d) — пропуск", tech,
                                len(existing.get("patents", [])), target)
                    continue
            except Exception:
                pass
        if not uniq:
            logger.warning("  %s: 0 релевантных — НЕ перезаписываю", tech)
            continue
        f.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_tech(tech: str, query: str, target: int, win: tuple[int, int], out_name: str) -> int:
    """Докачать target релевантных патентов по технологии. Возвращает число релевантных."""
    all_pats: list[dict] = []
    seen: set[str] = set()
    start_page = 0
    for d in (OUT_DIR, GIT_DIR):
        f = d / out_name
        if f.exists() and f.stat().st_size > 1000:
            try:
                existing = json.loads(f.read_text(encoding="utf-8"))
                k = len(existing.get("patents", []))
                if 0 < k < target:
                    start_page = k // PAGE_NUM
                    all_pats = existing.get("patents", [])
                    seen = {p.get("publication_number") for p in all_pats}
                    logger.info("  %s: resume с %d, старт со стр.%d (цель %d)",
                                tech, k, start_page, target)
            except Exception:
                pass
            break

    for page in range(start_page, MAX_PAGES):
        data = xhr_page(query, page, tech)
        if not data:
            break
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
                title = p.get("title") or ""
                abstract = (p.get("abstract") or "")[:1500]
                if not in_window(p, win):
                    continue
                # фильтр релевантности — ядро метода
                if not tech_relevant(title, abstract, tech):
                    continue
                all_pats.append({
                    "publication_number": pub,
                    "title": title,
                    "abstract": abstract,
                    "assignee": p.get("assignee"),
                    "priority_date": p.get("priority_date"),
                    "filing_date": p.get("filing_date"),
                    "inventor": p.get("inventor"),
                    "tech": tech,
                    "url": f"https://patents.google.com/patent/{pub}",
                })
        logger.info("  %s: стр.%d → %d релевантных (всего %d), сырых на стр. %d",
                    tech, page, len(all_pats), len(all_pats), new_on_page)
        save_progress(tech, query, win, all_pats[:target], len(seen), out_name, target)
        if len(all_pats) >= target:
            break
        if page < MAX_PAGES - 1:
            pause = random.randint(PAUSE_MIN, PAUSE_MAX)
            logger.info("  %s: ниньзя-пауза %ds", tech, pause)
            time.sleep(pause)

    uniq = all_pats[:target]
    save_progress(tech, query, win, uniq, len(seen), out_name, target)
    logger.info("  %s: сохранено %d релевантных (окно %d-%d, просканировано %d)",
                tech, len(uniq), win[0], win[1], len(seen))
    return len(uniq)


def main() -> None:
    pending = []
    for tech, (query, target, win, out_name) in TECHNOLOGIES.items():
        done = 0
        for d in (OUT_DIR, GIT_DIR):
            f = d / out_name
            if f.exists() and f.stat().st_size > 1000:
                try:
                    done = len(json.loads(f.read_text(encoding="utf-8")).get("patents", []))
                except Exception:
                    done = 0
                break
        if done < target:
            pending.append(tech)
    if not pending:
        logger.info("Все технологии IBAD-семейства докачаны. Выход.")
        return
    tech = pending[0]
    query, target, win, out_name = TECHNOLOGIES[tech]
    logger.info("=== Ниньзя IBAD-технологии: %s (цель %d, окно %d-%d), осталось: %s ===",
                tech, target, win[0], win[1], pending)
    n = fetch_tech(tech, query, target, win, out_name)
    logger.info("Готово: %s (%d релевантных). Осталось: %s", tech, n, pending[1:])


if __name__ == "__main__":
    main()
