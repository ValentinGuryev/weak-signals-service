#!/bin/bash
# NJ-6 (biomed): slice → mine → filter одной цепочкой (NIGHT_PLAN E1..E6)
set -uo pipefail
cd "$(dirname "$0")/.."
IDS=$(cat results/runtime/domain_biomed_topics.txt)
export HF_HUB_OFFLINE=1
. scripts/lib_cap.sh  # фикс 26.09: кап памяти джоба (OOM → rc=137, НЕ teardown WSL)
{
  echo "=== NJ-6 biomed chain start $(date) ==="
  echo "topics: $IDS"
  cap_run nj6-slice 4G .venv/bin/python scripts/termtech_sp_slice.py --topics "$IDS" \
    --out /mnt/e/openalex_derived/slices/biomed --threads 2 --mem 2GB
  rc=$?; echo "[slice rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  cap_run nj6-mine 7G .venv/bin/python scripts/termtech_mine.py \
    --slice /mnt/e/openalex_derived/slices/biomed \
    --out /mnt/e/openalex_derived/termtech_biomed
  rc=$?; echo "[mine rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  cap_run nj6-filter 4G .venv/bin/python scripts/termtech_filter.py \
    --indir /mnt/e/openalex_derived/termtech_biomed
  rc=$?; echo "[filter rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  mkdir -p results/termtech_biomed
  cp /mnt/e/openalex_derived/termtech_biomed/{filter_report.json,top_terms_clean.md,candidates_clean.parquet} results/termtech_biomed/ 2>/dev/null
  echo "=== NJ-6 DONE $(date) ==="
} 2>&1
