#!/bin/bash
# night_orchestrator4.sh — NJ-13b (pharma v2, 38 тем с таргетом под реальные
# токены сигналов) → артефакты+E7 → фарма-замер --domain pharma2 → рестарт
# супервизора (чекпоинты NJ-6/NJ-12/NJ-13? нет — NJ-7 energy идёт первым из
# незавершённых; NJ-13b в список супервизора НЕ входит, выполняется здесь).
set -uo pipefail
cd "$(dirname "$0")/.."
LOG=results/runtime/night_orchestrator4.log
log(){ echo "[$(date '+%H:%M:%S')] $*" >> "$LOG"; }

log "orchestrator4 start; старт NJ-13b"
setsid nohup bash scripts/run_nj13b_chain.sh >> results/runtime/night_NJ-13b_20260927.log 2>&1 &
echo $! > results/runtime/nj13b_chain.pid
log "NJ-13b pid $(cat results/runtime/nj13b_chain.pid)"
while kill -0 "$(cat results/runtime/nj13b_chain.pid)" 2>/dev/null; do sleep 30; done

if [ -s /mnt/e/openalex_derived/termtech_pharma2/filter_report.json ]; then
  log "NJ-13b DONE"
  mkdir -p results/termtech_pharma2
  cp /mnt/e/openalex_derived/termtech_pharma2/{filter_report.json,top_terms_clean.md,candidates_clean.parquet} \
     results/termtech_pharma2/ 2>/dev/null && log "артефакты скопированы"
  .venv/bin/python -u scripts/retro_coverage.py \
    --domain "pharma2=/mnt/e/openalex_derived/termtech_pharma2" >> "$LOG" 2>&1
  log "E7 retro rc=$?"
  .venv/bin/python -u scripts/pharma_coverage_check.py --domain pharma2 >> "$LOG" 2>&1
  log "ФАРМА-ЗАМЕР pharma2 rc=$? (≥13/16 = PASS; ⚠ потолок при джунк-сигналах = 12)"
else
  log "⚠ NJ-13b не дал filter_report"
fi

log "рестарт супервизора (чекпоинт-skip готовых → NJ-7 energy → NJ-9 → NJ-8 → NJ-10)"
bash scripts/run_night_rest.sh >> results/runtime/night_rest_orchestrated4.log 2>&1
log "супервизор завершился rc=$?"
