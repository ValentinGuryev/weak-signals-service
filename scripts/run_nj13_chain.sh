#!/bin/bash
# nj13 (pharma): slice → mine → filter одной цепочкой (шаблон NJ-5/NJ-6)
set -uo pipefail
cd "$(dirname "$0")/.."
IDS=$(cat results/runtime/domain_pharma_topics.txt)
export HF_HUB_OFFLINE=1
. scripts/lib_cap.sh  # фикс 26.09: кап памяти джоба (OOM → rc=137, НЕ teardown WSL)
{
  echo "=== nj13 pharma chain start $(date) ==="
  echo "topics: $IDS"
  cap_run nj13-slice 4G .venv/bin/python scripts/termtech_sp_slice.py --topics "$IDS" \
    --out /mnt/e/openalex_derived/slices/pharma --threads 2 --mem 2GB
  rc=$?; echo "[slice rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  cap_run nj13-mine 7G .venv/bin/python scripts/termtech_mine.py \
    --slice /mnt/e/openalex_derived/slices/pharma \
    --out /mnt/e/openalex_derived/termtech_pharma
  rc=$?; echo "[mine rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  cap_run nj13-filter 4G .venv/bin/python scripts/termtech_filter.py \
    --indir /mnt/e/openalex_derived/termtech_pharma
  rc=$?; echo "[filter rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  echo "=== nj13 DONE $(date) ==="
} 2>&1
