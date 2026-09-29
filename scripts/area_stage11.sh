#!/bin/bash
# area_stage11.sh — ADDENDUM №11: окно №10 (S10_*_hyb.json, top400/win99999) + childall-порядок.
set -u
cd "$(dirname "$0")/.."
LOG=results/runtime/area_stage11_20260928.log
exec 9>results/runtime/.stage11.lock
flock -n 9 || { echo "lock занят" >> "$LOG"; exit 0; }
echo "=== STAGE11 start $(date '+%H:%M:%S') ===" >> "$LOG"
mkdir -p results/stage11
for s in protect fintech industrial edge robots infra; do
  echo "--- $s $(date '+%H:%M:%S') ---" >> "$LOG"
  [ -f /tmp/S10_${s}_hyb.json ] || { echo "  НЕТ гибрид-окна $s" >> "$LOG"; continue; }
  timeout 1200 .venv/bin/python scripts/rank_directions_ngi.py --run /tmp/S10_${s}_hyb.json \
    --relevance childall --garbage demote --win-rank 99999 --prefix /tmp/S11_${s}_fin >> "$LOG" 2>&1
  rc=$?
  echo "  fin=$rc" >> "$LOG"
  [ -f /tmp/S11_${s}_fin_ngi_full.json ] && cp /tmp/S11_${s}_fin_ngi_full.json results/stage11/${s}_fin_ngi_full.json
done
echo "=== STAGE11 ALL DONE $(date '+%H:%M:%S') ===" >> "$LOG"
