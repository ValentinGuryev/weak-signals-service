#!/usr/bin/env python3
"""Планировщик ночной ниндзя-скачки Google Patents по 10 кейсам Lens-батча.

1 попытка каждые 15 минут (правило §4.1: не словить капчу Google).
Останавливается, когда все кейсы скачаны (флаг results/.ninja_gp_done).

Запуск:
    setsid nohup .venv/bin/python src/ninja_gp_scheduler.py > results/runtime/ninja_gp_scheduler.log 2>&1 &
"""
from __future__ import annotations

import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / ".venv" / "bin" / "python"
NINJA_GP = ROOT / "src" / "ninja_gp_cases.py"
DONE = ROOT / "results" / ".ninja_gp_done"
LOG = ROOT / "results" / "runtime" / "ninja_gp_scheduler.log"

CYCLE_MIN = 15  # 1 запуск в 15 минут (безопасный интервал для Google)
START_DELAY_MIN = 15  # стартовая пауза перед ПЕРВЫМ циклом (правило: 1 попытка/15 мин)


def log(msg: str) -> None:
    line = f"[{datetime.now():%H:%M:%S}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_ninja(timeout: int = 1800) -> str:
    try:
        res = subprocess.run(
            [str(VENV), str(NINJA_GP)],
            capture_output=True, text=True, timeout=timeout, cwd=str(ROOT))
        out = (res.stdout or "") + (res.stderr or "")
        return f"rc={res.returncode}\n" + "\n".join(out.splitlines()[-12:])
    except subprocess.TimeoutExpired:
        return "Таймаут — пропуск цикла"
    except Exception as e:
        return f"Ошибка запуска: {e}"


def main() -> None:
    global first_iter
    first_iter = True
    log(f"Ниньзя-GP планировщик запущен. Цикл: {CYCLE_MIN} мин. Кейсы: data/raw/patents/gp_ninja/*.json")

    def stop(*_):
        log("SIGTERM — останавливаюсь.")
        sys.exit(0)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    while True:
        # Стартовая пауза: чтобы первый запрос был не раньше, чем через
        # START_DELAY_MIN после запуска планировщика (ниндзя-правило).
        if first_iter:
            log(f"Стартовая пауза {START_DELAY_MIN} мин перед первым циклом...")
            time.sleep(START_DELAY_MIN * 60)
            first_iter = False
        if DONE.exists():
            log("Все кейсы скачаны (флаг .ninja_gp_done) — останавливаюсь.")
            break
        log("[патенты GP] запуск...")
        tail = run_ninja()
        log(f"Завершено. Хвост:\n{tail}")
        if DONE.exists():
            log("После запуска обнаружен флаг готовности — останавливаюсь.")
            break
        log(f"Сплю {CYCLE_MIN} минут...")
        time.sleep(CYCLE_MIN * 60)


if __name__ == "__main__":
    main()