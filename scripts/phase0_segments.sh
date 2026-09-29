#!/bin/bash
# phase0_segments.sh — Фаза 0: сегментация ВСЕХ доменов последовательно (один
# тяжёлый процесс за раз, mem-guard внутри segment_topics.py). Уже готовы: biomed,
# ai_security. Остальные 7.
set -uo pipefail
cd "$(dirname "$0")/.."
LOG=results/runtime/phase0_segments.log
log(){ echo "[$(date '+%H:%M:%S')] $*" >> "$LOG"; }
for d in quantum energy robotics materials space pharma pharma2; do
  if [ -s "/mnt/e/openalex_derived/termtech_$d/segments/child_topics.parquet" ]; then
    log "$d: уже сегментирован — skip"; continue
  fi
  log "$d: старт"
  .venv/bin/python -u scripts/segment_topics.py \
    --cand "/mnt/e/openalex_derived/termtech_$d/candidates_clean.parquet" \
    --out  "/mnt/e/openalex_derived/termtech_$d/segments" \
    --name "$d" --top 40000 >> "$LOG" 2>&1
  log "$d: rc=$?"
done
log "ФАЗА 0 ГОТОВА"
