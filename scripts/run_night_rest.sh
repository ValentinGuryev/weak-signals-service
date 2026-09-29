#!/bin/bash
# run_night_rest.sh — WATCHDOG-RELАУНЧ 27.09 v2 (переключён на stage9 по согласованию; бэкапы run_night_rest_20260926.bak).
# Безопасное продолжение: только доделка addendum №9 (stage9-конвейер) + оценка stage9.
# НИКАКИХ новых addendum/параметров автоматически (антиподгонка — см. CONTINUE_20260927.md).
set -uo pipefail
cd "$(dirname "$0")/.."
export HF_HUB_OFFLINE=1
LOG=results/runtime/watchdog_resume_20260927.log
echo "=== WATCHDOG RESUME $(date) ===" >> "$LOG"

# preflight
if ! ls /mnt/e/openalex_derived >/dev/null 2>&1; then
  echo "⛔ нет E: — выходим" >> "$LOG"; exit 1
fi
AVAIL_KB=$(awk '/^MemAvailable:/{print $2}' /proc/meminfo)
if [ "$AVAIL_KB" -lt 3145728 ]; then
  echo "⛔ MemAvailable=$((AVAIL_KB/1024))M < 3G — выходим" >> "$LOG"; exit 1
fi

# один писатель: flock (инцидент 27.09 14:26 — два конвейера вперемешку)
exec 9>results/runtime/.stage9.lock
if ! flock -n 9; then
  echo "⏳ lock занят (другой процесс работает) — выходим" >> "$LOG"; exit 0
fi

# Примечание (аудит 27.09, SHOULD-FIX lock): watchdog вызывает этот скрипт ТОЛЬКО после
# холодного рестарта WSL (watchdog.bat: wsl --shutdown → relaunch) — в этот момент любая
# pi-сессия уже мертва, поэтому «лестница сессии параллельно stage9» физически невозможна.
# От параллельных ручных запусков защищает flock ниже. Ночной план: NIGHT_PLAN_20260927.md.

# конвейер №9 доехал? (STAGE9 start vs STAGE9 ALL DONE — каждый запуск добавляет пару)
S9LOG=results/runtime/area_stage9_20260927.log
starts=$(grep -c 'STAGE9 start' "$S9LOG" 2>/dev/null || echo 0)
dones=$(grep -c 'STAGE9 ALL DONE' "$S9LOG" 2>/dev/null || echo 0)
if [ "$starts" -gt "$dones" ]; then
  echo "⏳ stage9 не доехал — запускаем area_stage9.sh" >> "$LOG"
  bash scripts/area_stage9.sh >> "$LOG" 2>&1
else
  echo "✅ stage9 завершён (start=$starts done=$dones)" >> "$LOG"
fi

# оценка (всегда, безопасно)
.venv/bin/python scripts/eval_stage9.py >> "$LOG" 2>&1
echo "=== RESUME DONE $(date) ===" >> "$LOG"
echo "Подробности: results/runtime/CONTINUE_20260927.md" >> "$LOG"
