#!/bin/bash
# area_stage1_chain.sh — addendum №7: probe → hybrid → fin для областей,
# не прошедших из-за 429 (27.09). Один тяжёлый шаг за раз, щедрые таймауты.
set -u
cd "$(dirname "$0")/.."
LOG=results/runtime/area_stage1_20260927.log
for s in industrial infra fintech edge; do
  echo "=== $s $(date '+%H:%M:%S') ===" >> "$LOG"
  timeout 3000 .venv/bin/python scripts/rank_directions_ngi.py --run results/qa_areas/$s.json \
    --relevance childall --garbage none --prefix /tmp/A7_${s}_probe >> "$LOG" 2>&1
  rc1=$?
  timeout 120 .venv/bin/python scripts/hybrid_window.py --run results/qa_areas/$s.json \
    --probe /tmp/A7_${s}_probe_ngi_full.json --out /tmp/A7_${s}_hyb.json >> "$LOG" 2>&1
  rc2=$?
  timeout 900 .venv/bin/python scripts/rank_directions_ngi.py --run /tmp/A7_${s}_hyb.json \
    --relevance win --win-rank 130 --garbage demote --prefix /tmp/A7_${s}_fin >> "$LOG" 2>&1
  rc3=$?
  echo "=== $s DONE probe=$rc1 hyb=$rc2 fin=$rc3 $(date '+%H:%M:%S') ===" >> "$LOG"
done
echo "=== CHAIN ALL DONE $(date '+%H:%M:%S') ===" >> "$LOG"
