#!/usr/bin/env python3
"""Планировщик ниндзя-скачки: чередует патенты и конференции, 1 запуск/15 мин.

Стратегия (согласовано с пользователем):
- 1 попытка каждые 15 минут — чтобы не словить блокировку (Google Patents, OpenAlex).
- Чередование: патент (1 тема) → конференции (1 пара источник+ключевое слово) → ...
- Днём работает тоже (1 запрос/15 мин безопасно).
- Останавливается, когда обе очереди пусты (флаги .ninja_done + .ninja_conf_done).

Использование:
    setsid nohup .venv/bin/python src/ninja_scheduler.py > results/ninja_scheduler.log 2>&1 &
"""
from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / ".venv" / "bin" / "python"
NINJA_PAT = ROOT / "src" / "ninja_patents.py"
NINJA_CONF = ROOT / "src" / "ninja_conferences.py"
DONE_PAT = ROOT / "results" / ".ninja_done"
DONE_CONF = ROOT / "results" / ".ninja_conf_done"
LOG = ROOT / "results" / "runtime" / "ninja_scheduler.log"

CYCLE_MIN = 15  # 1 запуск в 15 минут


def log(msg: str) -> None:
    line = f"[{datetime.now():%H:%M:%S}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:  # append, не overwrite — хранить всю историю
        f.write(line + "\n")


def run_script(script: Path, timeout: int = 1200) -> str:
    try:
        res = subprocess.run(
            [str(VENV), str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=str(ROOT))
        out = (res.stdout or "") + (res.stderr or "")
        return f"rc={res.returncode}\n" + "\n".join(out.splitlines()[-8:])
    except subprocess.TimeoutExpired:
        return "Таймаут — пропуск цикла"
    except Exception as e:
        return f"Ошибка запуска: {e}"


def main() -> None:
    log(f"Ниндзя-планировщик запущен. Цикл: {CYCLE_MIN} мин. Чередуем: патенты/конференции.")
    tick = 0
    while True:
        pat_done = DONE_PAT.exists()
        conf_done = DONE_CONF.exists()
        if pat_done and conf_done:
            log("Обе очереди пусты — ВСЁ СКАЧАНО. Останавливаюсь.")
            break

        tick += 1
        if not pat_done and (tick % 2 == 1 or conf_done):
            log("[патенты] запуск...")
            tail = run_script(NINJA_PAT)
        else:
            log("[конференции] запуск...")
            tail = run_script(NINJA_CONF)
        log(f"Завершено. Хвост:\n{tail}")

        log(f"Сплю {CYCLE_MIN} минут...")
        time.sleep(CYCLE_MIN * 60)


if __name__ == "__main__":
    main()
