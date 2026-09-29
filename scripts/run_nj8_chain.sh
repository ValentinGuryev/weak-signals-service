#!/bin/bash
# nj8 (materials): slice → mine → filter одной цепочкой (шаблон NJ-5/NJ-6)
set -uo pipefail
cd "$(dirname "$0")/.."
IDS=$(cat results/runtime/domain_materials_topics.txt)
export HF_HUB_OFFLINE=1
. scripts/lib_cap.sh  # фикс 26.09: кап памяти джоба (OOM → rc=137, НЕ teardown WSL)
{
  echo "=== nj8 materials chain start $(date) ==="
  echo "topics: $IDS"
  cap_run nj8-slice 4G .venv/bin/python scripts/termtech_sp_slice.py --topics "$IDS" \
    --out /mnt/e/openalex_derived/slices/materials --threads 2 --mem 2GB
  rc=$?; echo "[slice rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  cap_run nj8-mine 7G .venv/bin/python scripts/termtech_mine.py \
    --slice /mnt/e/openalex_derived/slices/materials \
    --out /mnt/e/openalex_derived/termtech_materials
  rc=$?; echo "[mine rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  cap_run nj8-filter 4G .venv/bin/python scripts/termtech_filter.py \
    --indir /mnt/e/openalex_derived/termtech_materials
  rc=$?; echo "[filter rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  echo "=== nj8 DONE $(date) ==="
} 2>&1
