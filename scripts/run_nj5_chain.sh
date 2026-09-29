#!/bin/bash
# NJ-5 (quantum): slice → mine → filter одной цепочкой, лог+PID (NIGHT_PLAN E1..E6)
set -uo pipefail
cd "$(dirname "$0")/.."
IDS=$(cat results/runtime/domain_quantum_topics.txt)
export HF_HUB_OFFLINE=1
. scripts/lib_cap.sh  # фикс 26.09: кап памяти джоба (OOM → rc=137, НЕ teardown WSL)
{
  echo "=== NJ-5 quantum chain start $(date) ==="
  echo "topics: $IDS"
  cap_run nj5-slice 4G .venv/bin/python scripts/termtech_sp_slice.py --topics "$IDS" \
    --out /mnt/e/openalex_derived/slices/quantum --threads 2 --mem 2GB
  rc=$?; echo "[slice rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  cap_run nj5-mine 7G .venv/bin/python scripts/termtech_mine.py \
    --slice /mnt/e/openalex_derived/slices/quantum \
    --out /mnt/e/openalex_derived/termtech_quantum
  rc=$?; echo "[mine rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  cap_run nj5-filter 4G .venv/bin/python scripts/termtech_filter.py \
    --indir /mnt/e/openalex_derived/termtech_quantum
  rc=$?; echo "[filter rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  mkdir -p results/termtech_quantum
  cp /mnt/e/openalex_derived/termtech_quantum/filter_report.json results/termtech_quantum/ 2>/dev/null
  cp /mnt/e/openalex_derived/termtech_quantum/top_terms_clean.md results/termtech_quantum/ 2>/dev/null
  cp /mnt/e/openalex_derived/termtech_quantum/candidates_clean.parquet results/termtech_quantum/ 2>/dev/null
  echo "=== NJ-5 DONE $(date) ==="
} 2>&1
