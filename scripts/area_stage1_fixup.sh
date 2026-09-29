#!/bin/bash
# area_stage1_fixup.sh — добивка addendum №7 после аномалии chain (27.09).
set -u
cd "$(dirname "$0")/.."
LOG=results/runtime/area_stage1_20260927.log
CHAIN=455912
# ждём конца основной цепочки (edge)
while kill -0 $CHAIN 2>/dev/null; do sleep 10; done
echo "=== FIXUP start $(date '+%H:%M:%S') (chain завершён) ===" >> "$LOG"
for s in industrial infra fintech edge; do
  if [ ! -f /tmp/A7_${s}_probe_ngi_full.json ]; then
    echo "=== fixup probe $s $(date '+%H:%M:%S') ===" >> "$LOG"
    timeout 1800 .venv/bin/python scripts/rank_directions_ngi.py --run results/qa_areas/$s.json \
      --relevance childall --garbage none --prefix /tmp/A7_${s}_probe >> "$LOG" 2>&1
    echo "  probe rc=$?" >> "$LOG"
  fi
  if [ -f /tmp/A7_${s}_probe_ngi_full.json ] && [ ! -f /tmp/A7_${s}_fin_ngi_full.json ]; then
    timeout 120 .venv/bin/python scripts/hybrid_window.py --run results/qa_areas/$s.json \
      --probe /tmp/A7_${s}_probe_ngi_full.json --out /tmp/A7_${s}_hyb.json >> "$LOG" 2>&1
    rc2=$?
    timeout 900 .venv/bin/python scripts/rank_directions_ngi.py --run /tmp/A7_${s}_hyb.json \
      --relevance win --win-rank 130 --garbage demote --prefix /tmp/A7_${s}_fin >> "$LOG" 2>&1
    rc3=$?
    echo "  fixup $s hyb=$rc2 fin=$rc3 $(date '+%H:%M:%S')" >> "$LOG"
  fi
done
echo "=== FIXUP ALL DONE $(date '+%H:%M:%S') ===" >> "$LOG"
