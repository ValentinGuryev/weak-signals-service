#!/bin/bash
# area_stage9.sh — конвейер addendum №9/9а: probe → hybrid(K=200) → fin → stage9/
# Запуск: bash scripts/area_stage9.sh  (идемпотентен, один писатель, лог рядом)
set -u
cd "$(dirname "$0")/.."
LOG=results/runtime/area_stage9_20260927.log
exec 9>results/runtime/.stage9.lock
flock -n 9 || { echo "lock занят" >> "$LOG"; exit 0; }
echo "=== STAGE9 start $(date '+%H:%M:%S') ===" >> "$LOG"
mkdir -p results/stage9
for s in protect industrial infra robots fintech edge; do
  echo "--- $s $(date '+%H:%M:%S') ---" >> "$LOG"
  timeout 2400 .venv/bin/python scripts/rank_directions_ngi.py --run results/qa_areas9/$s.json \
    --relevance childall --garbage none --prefix /tmp/S9_${s}_probe >> "$LOG" 2>&1
  echo "  probe rc=$?" >> "$LOG"
  timeout 120 .venv/bin/python scripts/hybrid_window.py --run results/qa_areas9/$s.json \
    --probe /tmp/S9_${s}_probe_ngi_full.json --out /tmp/S9_${s}_hyb.json --top 200 >> "$LOG" 2>&1
  rc2=$?
  timeout 1200 .venv/bin/python scripts/rank_directions_ngi.py --run /tmp/S9_${s}_hyb.json \
    --relevance win --win-rank 130 --garbage demote --prefix /tmp/S9_${s}_fin >> "$LOG" 2>&1
  rc3=$?
  echo "  hyb=$rc2 fin=$rc3" >> "$LOG"
  [ -f /tmp/S9_${s}_fin_ngi_full.json ] && cp /tmp/S9_${s}_fin_ngi_full.json results/stage9/${s}_fin_ngi_full.json
done
echo "=== STAGE9 ALL DONE $(date '+%H:%M:%S') ===" >> "$LOG"
# оценка (eval_stage9: копия eval с results/stage9/ — если файла нет, см. CONTINUE §3)
