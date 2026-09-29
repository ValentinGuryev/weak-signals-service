#!/bin/bash
# nj12 (ai_security): slice → mine → filter одной цепочкой (шаблон NJ-5/NJ-6)
set -uo pipefail
cd "$(dirname "$0")/.."
IDS=$(cat results/runtime/domain_ai_security_topics.txt)
export HF_HUB_OFFLINE=1
. scripts/lib_cap.sh  # фикс 26.09: кап памяти джоба (OOM → rc=137, НЕ teardown WSL)
{
  echo "=== nj12 ai_security chain start $(date) ==="
  echo "topics: $IDS"
  cap_run nj12-slice 4G .venv/bin/python scripts/termtech_sp_slice.py --topics "$IDS" \
    --out /mnt/e/openalex_derived/slices/ai_security --threads 2 --mem 2GB
  rc=$?; echo "[slice rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  cap_run nj12-mine 7G .venv/bin/python scripts/termtech_mine.py \
    --slice /mnt/e/openalex_derived/slices/ai_security \
    --out /mnt/e/openalex_derived/termtech_ai_security
  rc=$?; echo "[mine rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  cap_run nj12-filter 4G .venv/bin/python scripts/termtech_filter.py \
    --indir /mnt/e/openalex_derived/termtech_ai_security
  rc=$?; echo "[filter rc=$rc $(date)]"
  [ $rc -ne 0 ] && exit $rc
  echo "=== nj12 DONE $(date) ==="
} 2>&1
