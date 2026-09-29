#!/usr/bin/env python3
"""Ночной монитор: перезапускает фоновые задачи, когда API отпускают.

- Патенты Google (капча 503): перезапуск каждые 2 часа, пока не будет всех тем.
- conference_mining (OpenAlex 429): перезапуск каждые 2 часа.
Логи в /tmp/*.log, отчёт в results/night_run_status.md
"""
import subprocess, time, json, os
from pathlib import Path
from datetime import datetime

ROOT = Path("/home/user/projects/Hackathon")
PATENT_SCRIPT = ROOT / "src" / "patents_by_topic.py"
CONF_SCRIPT = ROOT / "src" / "conference_mining.py"
VENV = ROOT / ".venv" / "bin" / "activate"

MY_PID = str(os.getpid())


def is_running(name: str) -> bool:
    """Точно: процесс с python <script> жив? (исключаем сам монитор)."""
    out = subprocess.run(["pgrep", "-f", f"python.*{name}"], capture_output=True, text=True)
    pids = [p for p in out.stdout.split() if p != MY_PID]
    return bool(pids)

def run_bg(cmd: str, log: str) -> None:
    subprocess.Popen(["bash", "-c", f"source {VENV}; {cmd} > {log} 2>&1"], start_new_session=True)
    print(f"[{datetime.now():%H:%M}] запущен: {cmd} -> {log}")

def patents_done() -> bool:
    """Все темы имеют >1KB файл (есть данные)."""
    d = ROOT / "experiment" / "runs" / "patents"
    files = list(d.glob("*.json"))
    if not files:
        return False
    return all(f.stat().st_size > 1000 for f in files)

def main() -> None:
    print(f"[{datetime.now():%H:%M}] Ночной монитор запущен")
    while True:
        now = datetime.now()
        # Патенты: перезапуск если не бежит и не все готовы
        if not patents_done() and not is_running("patents_by_topic"):
            run_bg(f"timeout 5400 python {PATENT_SCRIPT}", "/tmp/patents_night_auto.log")
        # Conference: перезапуск если не бежит
        if not is_running("conference_mining"):
            run_bg(f"timeout 5400 python -u {CONF_SCRIPT}", "/tmp/conference_night_auto.log")
        # Отчёт раз в час
        if now.minute == 0:
            pat = ROOT / "experiment" / "runs" / "patents"
            sizes = {f.name: f.stat().st_size for f in pat.glob("*.json")} if pat.exists() else {}
            conf = ROOT / "data" / "raw" / "conferences" / "conference_hits.json"
            conf_size = conf.stat().st_size if conf.exists() else 0
            (ROOT / "results" / "night_run_status.md").write_text(
                f"# Ночной статус ({now:%Y-%m-%d %H:%M})\n\n"
                f"## Патенты\n{sizes}\n\n## Conference\nconf size: {conf_size}\n",
                encoding="utf-8")
        time.sleep(300)  # 5 мин

if __name__ == "__main__":
    main()
