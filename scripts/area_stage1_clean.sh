#!/bin/bash
# area_stage1_clean.sh — ЧИСТЫЙ проход addendum №7 (27.09): все 6 областей после
# прогрева birth-кэша (контаминация 429 устраняется: no_birth → 0).
set -u
cd "$(dirname "$0")/.."
LOG=results/runtime/area_stage1_20260927.log
while kill -0 462715 2>/dev/null; do sleep 10; done   # ждём fixup
echo "=== CLEAN start $(date '+%H:%M:%S') ===" >> "$LOG"
for s in protect industrial infra robots fintech edge; do
  echo "--- clean $s $(date '+%H:%M:%S') ---" >> "$LOG"
  timeout 1800 .venv/bin/python scripts/rank_directions_ngi.py --run results/qa_areas/$s.json \
    --relevance childall --garbage none --prefix /tmp/CL_${s}_probe >> "$LOG" 2>&1
  echo "  probe rc=$?" >> "$LOG"
  timeout 120 .venv/bin/python scripts/hybrid_window.py --run results/qa_areas/$s.json \
    --probe /tmp/CL_${s}_probe_ngi_full.json --out /tmp/CL_${s}_hyb.json >> "$LOG" 2>&1
  rc2=$?
  timeout 900 .venv/bin/python scripts/rank_directions_ngi.py --run /tmp/CL_${s}_hyb.json \
    --relevance win --win-rank 130 --garbage demote --prefix /tmp/CL_${s}_fin >> "$LOG" 2>&1
  rc3=$?
  echo "  hyb=$rc2 fin=$rc3" >> "$LOG"
  [ -f /tmp/CL_${s}_fin_ngi_full.json ] && cp /tmp/CL_${s}_fin_ngi_full.json results/stage1/${s}_fin_ngi_full.json
  echo "  copied=$?" >> "$LOG"
done
echo "=== CLEAN ALL DONE $(date '+%H:%M:%S') ===" >> "$LOG"
