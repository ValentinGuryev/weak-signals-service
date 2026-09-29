#!/usr/bin/env python3
"""Планировщик ниндзя-скачки патентов С ВРЕМЕННЫМ ОКНОМ (2006-2018) + IBAD-технологии.

Приоритет (решение команды): докачка патентов по IBAD-семейству
(IBAD-MgO / IBAD-YSZ / RABiTS / ISD) — 1 технология за цикл через
ninja_ibad_technologies.py (с фильтром релевантности). Когда IBAD готово —
переходит к общему окну (ninja_patents_window.py).

Запускает скрипт 1 раз в 15 минут (одна тема/технология за цикл).
Останавливается, когда все темы скачаны в окне (флаг .ninja_window_done).

Использование:
    setsid nohup .venv/bin/python src/ninja_scheduler_window.py > results/runtime/ninja_scheduler_window.log 2>&1 &
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / ".venv" / "bin" / "python"
NINJA = ROOT / "src" / "ninja_patents_window.py"
NINJA_IBAD = ROOT / "src" / "ninja_ibad_technologies.py"
DONE = ROOT / "results" / ".ninja_window_done"
LOG = ROOT / "results" / "runtime" / "ninja_scheduler_window.log"

CYCLE_MIN = 20  # 20 мин между попытками (жесткий режим, Google отпустил прямой IP)


def log(msg: str) -> None:
    line = f"[{datetime.now():%H:%M:%S}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_ninja(script: Path, timeout: int = 3600) -> str:
    """Запуск нинзья-скрипта. Таймаут 1 час: 300 патентов = 20 стр × 45-90с = 25-30 мин
    + 503-перерывы. 30 мин не хватало → таймаут каждый цикл."""
    try:
        res = subprocess.run(
            [str(VENV), str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=str(ROOT))
        out = (res.stdout or "") + (res.stderr or "")
        return f"rc={res.returncode}\n" + "\n".join(out.splitlines()[-12:])
    except subprocess.TimeoutExpired:
        return "Таймаут — пропуск цикла"
    except Exception as e:
        return f"Ошибка запуска: {e}"


def ibad_pending() -> list[str]:
    """Технологии IBAD-семейства, которые ещё не докачаны (приоритет автора)."""
    try:
        sys.path.insert(0, str(ROOT / "src"))
        from ninja_ibad_technologies import TECHNOLOGIES, GIT_DIR, OUT_DIR
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
        return pending
    except Exception as e:
        log(f"Ошибка проверки IBAD-очереди: {e}")
        return []


def main() -> None:
    log("Ниндзя-планировщик (окно 2006-2018 + IBAD-технологии) запущен. Цикл: 15 мин.")
    while True:
        if DONE.exists():
            log("ВСЕ ТЕМЫ СКАЧАНЫ В ОКНЕ. Останавливаюсь.")
            break
        # Приоритет: IBAD-технологии (кейс 001_ibad_mgo) — 1 тема за цикл
        ibad = ibad_pending()
        if ibad:
            log(f"[IBAD-приоритет] докачка: {ibad[0]} (осталось: {ibad})")
            tail = run_ninja(NINJA_IBAD)
            log("IBAD завершено. Хвост:\n" + tail)
        else:
            log("[патенты-окно] запуск...")
            tail = run_ninja(NINJA)
            log("Завершено. Хвост:\n" + tail)
        log(f"Сплю {CYCLE_MIN} минут...")
        time.sleep(CYCLE_MIN * 60)


if __name__ == "__main__":
    main()
