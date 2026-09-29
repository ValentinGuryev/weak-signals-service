#!/bin/bash
# area_stage10.sh — конвейер ADDENDUM №10 (объявлен ДО запуска, ночь 27→28):
#   гибрид-окно K extras 200→400 (--top 400) + снятое win130-отсечение (--win-rank 99999).
#   Probe НЕ перезапускается (использует /tmp/S9_*_probe_ngi_full.json из №9).
#   Выход: results/stage10/. Идемпотентен, flock, один писатель.
set -u
cd "$(dirname "$0")/.."
LOG=results/runtime/area_stage10_20260928.log
exec 9>results/runtime/.stage10.lock
flock -n 9 || { echo "lock занят" >> "$LOG"; exit 0; }
echo "=== STAGE10 start $(date '+%H:%M:%S') ===" >> "$LOG"
mkdir -p results/stage10
for s in protect fintech industrial edge robots infra; do
  echo "--- $s $(date '+%H:%M:%S') ---" >> "$LOG"
  timeout 300 .venv/bin/python scripts/hybrid_window.py --run results/qa_areas9/$s.json \
    --probe /tmp/S9_${s}_probe_ngi_full.json --out /tmp/S10_${s}_hyb.json --top 400 >> "$LOG" 2>&1
  rc1=$?
  timeout 1200 .venv/bin/python scripts/rank_directions_ngi.py --run /tmp/S10_${s}_hyb.json \
    --relevance win --win-rank 99999 --garbage demote --prefix /tmp/S10_${s}_fin >> "$LOG" 2>&1
  rc2=$?
  echo "  hyb=$rc1 fin=$rc2" >> "$LOG"
  [ -f /tmp/S10_${s}_fin_ngi_full.json ] && cp /tmp/S10_${s}_fin_ngi_full.json results/stage10/${s}_fin_ngi_full.json
done
echo "=== STAGE10 ALL DONE $(date '+%H:%M:%S') ===" >> "$LOG"
