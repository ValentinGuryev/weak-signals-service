#!/bin/bash
# night_orchestrator3.sh — NJ-13 pharma (исправленные ID, запущен вручную 01:55)
# → артефакты+E7 → честный повторный фарма-замер (порог ≥13/16) → рестарт
# супервизора (чекпоинт-skip NJ-6/NJ-12 → NJ-7 energy → NJ-9 → NJ-8 → NJ-10).
set -uo pipefail
cd "$(dirname "$0")/.."
LOG=results/runtime/night_orchestrator3.log
log(){ echo "[$(date '+%H:%M:%S')] $*" >> "$LOG"; }

log "orchestrator3 start; жду NJ-13 (pid $(cat results/runtime/nj13_chain.pid))"
while kill -0 "$(cat results/runtime/nj13_chain.pid)" 2>/dev/null; do sleep 30; done

if [ -s /mnt/e/openalex_derived/termtech_pharma/filter_report.json ]; then
  log "NJ-13 DONE"
  mkdir -p results/termtech_pharma
  cp /mnt/e/openalex_derived/termtech_pharma/{filter_report.json,top_terms_clean.md,candidates_clean.parquet} \
     results/termtech_pharma/ 2>/dev/null && log "NJ-13 артефакты скопированы"
  .venv/bin/python -u scripts/retro_coverage.py \
    --domain "pharma=/mnt/e/openalex_derived/termtech_pharma" >> "$LOG" 2>&1
  log "E7 retro (все годы) rc=$?"
  .venv/bin/python -u scripts/pharma_coverage_check.py --domain pharma >> "$LOG" 2>&1
  log "ФАРМА-ЗАМЕР по NJ-13 rc=$? (0 = PASS ≥13/16, 1 = FAIL)"
else
  log "⚠ NJ-13 не дал filter_report — фарма-замер пропущен"
fi

log "рестарт супервизора (NJ-6/NJ-12 skip по чекпоинту → NJ-7…NJ-10)"
bash scripts/run_night_rest.sh >> results/runtime/night_rest_orchestrated3.log 2>&1
log "супервизор завершился rc=$?"
