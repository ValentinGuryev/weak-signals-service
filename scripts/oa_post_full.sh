#!/bin/bash
# Полный прогон пост-пассов OpenAlex в ГОДОВОМ режиме:
#  - dedup по одному году за процесс (пик памяти = один год; до 3 попыток, при OOM → mem 5GB)
#  - после всех лет: финал (topic_index + digest)
BASE=/home/user/projects/Hackathon
LOG=$BASE/results/runtime/oa_post.log
: > "$LOG"
run_year() {
  local y=$1 mem=${2:-4GB}
  OA_YEAR_FROM=$y OA_YEAR_TO=$y OA_DEDUP_ONLY=1 \
  "$BASE/.venv/bin/python" "$BASE/scripts/oa_run_ingest.py" \
    --manifest /mnt/e/openalex-snapshot/data/jsonl/manifest.json \
    --works /mnt/e/openalex-snapshot/data/jsonl/works \
    --local "$BASE/data/openalex_derived" \
    --e /mnt/e/openalex_derived \
    --staging /mnt/c/oa_tmp --small /mnt/c/oa_tmp/small \
    --post-only --threads 6 --mem "$mem" >> "$LOG" 2>&1
}
echo "$(date '+%F %T') FULL-REAL post-passes: годовой dedup + финал" >> "$LOG"
FAILED=""
for y in 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026; do
  ok=0
  for attempt in 1 2 3; do
    mem=4GB
    [ $attempt -gt 1 ] && mem=5GB
    run_year $y $mem
    if [ $? -eq 0 ]; then echo "$(date '+%T') year $y OK (attempt $attempt, $mem)" >> "$LOG"; ok=1; break; fi
    echo "$(date '+%T') year $y FAIL attempt $attempt ($mem)" >> "$LOG"
  done
  [ $ok -eq 0 ] && { echo "year $y GAVE UP" >> "$LOG"; FAILED="$FAILED $y"; break; }
done
if [ -z "$FAILED" ]; then
  OA_SKIP_DEDUP=1 \
  "$BASE/.venv/bin/python" "$BASE/scripts/oa_run_ingest.py" \
    --manifest /mnt/e/openalex-snapshot/data/jsonl/manifest.json \
    --works /mnt/e/openalex-snapshot/data/jsonl/works \
    --local "$BASE/data/openalex_derived" \
    --e /mnt/e/openalex_derived \
    --staging /mnt/c/oa_tmp --small /mnt/c/oa_tmp/small \
    --post-only --threads 6 --mem 4GB >> "$LOG" 2>&1 \
  && echo "$(date '+%T') FINAL topic_index+digest OK" >> "$LOG"
else
  echo "SKIPPED final, годы упали:$FAILED" >> "$LOG"
fi
echo "$(date '+%T') CHAIN DONE$FAILED" >> "$LOG"