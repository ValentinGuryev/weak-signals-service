#!/usr/bin/env bash
# Watchdog для ротационного планировщика патентов.
# Если ротатор умер — перезапускает. Логирует в results/runtime/ninja_watchdog.log.
# Запуск: setsid nohup bash scripts/patent_watchdog.sh > results/runtime/ninja_watchdog.log 2>&1 &

ROOT=/home/user/projects/Hackathon
VENV=$ROOT/.venv/bin/python
ROTATE=$ROOT/src/ninja_scheduler_tor.py
LOG=$ROOT/results/runtime/ninja_watchdog.log

log() {
    echo "[$(date +%H:%M:%S)] $1" >> "$LOG"
}

log "Watchdog запущен. Проверка каждые 5 мин."

while true; do
    # ротатор жив?
    if ! pgrep -f "ninja_scheduler_rotate.py" > /dev/null; then
        log "Ротатор НЕ найден — перезапускаю"
        cd "$ROOT"
        setsid nohup "$VENV" "$ROTATE" > "$ROOT/results/runtime/ninja_rotate.log" 2>&1 &
        log "Перезапущен (PID $!)"
    fi
    sleep 300  # 5 мин
done
