#!/usr/bin/env python3
"""Ночной планировщик по стратегии «Ночное окно» (согласовано с пользователем).

Правила:
1. ДО 3:00 — ПОЛНОЕ бездействие (не запускать ничего).
2. С 3:00 до ~8:00 — медленная скачка: 1 запрос каждые 10-15 мин.
3. Источник НЕ меняем: Google Patents (патенты) + OpenAlex (конференции).
4. Патенты: 16 тем (10 базовых + 6 новых: Nb3Sn, SFCL, трансформаторы, маглевы, токовводы, HTS-кабели).
5. Конференции: OpenAlex по ключевым словам провала/успеха (IEEE TAS + EuCAS JPCS).

Реализация: каждый цикл (10-15 мин) делает ОДИН запрос.
- Сначала конференции (OpenAlex), потом патенты (Google) — чередуем.
- Пишет прогресс в results/night_run_status.md
"""
import subprocess
import time
import json
import os
import sys
from pathlib import Path
from datetime import datetime, time as dtime

ROOT = Path("/home/user/projects/Hackathon")
PATENT_SCRIPT = ROOT / "src" / "patents_by_topic.py"
CONF_SCRIPT = ROOT / "src" / "conference_mining.py"
VENV = ROOT / ".venv" / "bin" / "activate"
STATUS = ROOT / "results" / "night_run_status.md"

START_HOUR = 3   # 3:00
END_HOUR = 9     # до 9:00
CYCLE_MIN = 12   # 1 запрос / 12 мин (10-15 мин)


def log(msg: str) -> None:
    print(f"[{datetime.now():%H:%M}] {msg}", flush=True)


def now_hour() -> int:
    return datetime.now().hour


def patents_files() -> dict:
    """Размеры файлов патентов: {имя: размер}."""
    d = ROOT / "experiment" / "runs" / "patents"
    return {f.name: f.stat().st_size for f in d.glob("*.json")} if d.exists() else {}


def write_status(msg: str = "") -> None:
    sizes = patents_files()
    conf = ROOT / "data" / "raw" / "conferences" / "conference_hits.json"
    conf_size = conf.stat().st_size if conf.exists() else 0
    (STATUS).write_text(
        f"# Ночной статус ({datetime.now():%Y-%m-%d %H:%M})\n\n"
        f"{msg}\n\n"
        f"## Патенты (размеры файлов, >1000 = скачано)\n{json.dumps(sizes, indent=1)}\n\n"
        f"## Конференции\nconf size: {conf_size} байт\n",
        encoding="utf-8")


def one_patent_batch() -> None:
    """Один запуск патентной скачки (все темы, но с большими паузами)."""
    log("Запуск патентной скачки (одна порция)")
    subprocess.Popen(
        ["bash", "-c", f"source {VENV}; timeout 1500 python {PATENT_SCRIPT}"],
        start_new_session=True)


def one_conf_batch() -> None:
    """Один запуск конференционной скачки."""
    log("Запуск конференционной скачки (одна порция)")
    subprocess.Popen(
        ["bash", "-c", f"source {VENV}; timeout 1500 python -u {CONF_SCRIPT}"],
        start_new_session=True)


def main() -> None:
    log(f"Планировщик запущен. Окно: {START_HOUR}:00-{END_HOUR}:00, цикл {CYCLE_MIN} мин. До {START_HOUR}:00 — бездействие.")
    write_status("Планировщик запущен, ожидание окна.")

    # Парный счётчик: чередуем патенты/конференции
    tick = 0
    while True:
        h = now_hour()
        if h < START_HOUR or h >= END_HOUR:
            log(f"Вне окна ({h}:00). Спим до {START_HOUR}:00...")
            write_status(f"Вне окна ({h}:00). Спим до {START_HOUR}:00.")
            # Спим до начала окна (или максимум 30 мин для проверки)
            sleep_s = min(1800, ((START_HOUR - h + 24) % 24) * 3600)
            time.sleep(sleep_s)
            continue

        # В окне: делаем ОДИН запрос
        tick += 1
        if tick % 2 == 1:
            one_conf_batch()
        else:
            one_patent_batch()
        write_status(f"Цикл {tick}: {'конференции' if tick % 2 else 'патенты'} запущены.")
        log(f"Цикл {tick}: {'конференции' if tick % 2 else 'патенты'} запущены. Спим {CYCLE_MIN} мин.")
        time.sleep(CYCLE_MIN * 60)


if __name__ == "__main__":
    main()
