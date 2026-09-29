#!/bin/bash
# night_orchestrator2.sh — автопродолжение после остановки супервизора (27.09 01:3x):
# NJ-12 (бежит сиротой) → артефакты+E7 → NJ-13 pharma (правило автора: замер 3/16)
# → фарма-замер по NJ-13 → рестарт супервизора (NJ-6/NJ-12 skip по чекпоинту →
# NJ-7 energy → NJ-9 → NJ-8 → NJ-10).
set -uo pipefail
cd "$(dirname "$0")/.."
LOG=results/runtime/night_orchestrator2.log
log(){ echo "[$(date '+%H:%M:%S')] $*" >> "$LOG"; }

finish_job() {  # $1=slug $2=имя NJ $3=лог
  local slug=$1 nj=$2 lg=$3
  mkdir -p "results/termtech_${slug}"
  cp "/mnt/e/openalex_derived/termtech_${slug}/filter_report.json" \
     "/mnt/e/openalex_derived/termtech_${slug}/top_terms_clean.md" \
     "/mnt/e/openalex_derived/termtech_${slug}/candidates_clean.parquet" \
     "results/termtech_${slug}/" 2>/dev/null && log "$nj артефакты скопированы"
  .venv/bin/python -u scripts/retro_coverage.py \
    --domain "${slug}=/mnt/e/openalex_derived/termtech_${slug}" \
    --years 2018,2020,2024,2026 >> "$LOG" 2>&1
  log "$nj E7 rc=$?"
}

log "orchestrator2 start; жду NJ-12 chain"
while pgrep -f 'run_nj12_chain[.]sh' >/dev/null; do sleep 30; done
if [ -s /mnt/e/openalex_derived/termtech_ai_security/filter_report.json ]; then
  log "NJ-12 DONE"
  finish_job ai_security NJ-12 night_NJ-12_20260926.log
else
  log "⚠ NJ-12 filter_report НЕТ (упал?) — NJ-13 всё равно запускаю, NJ-12 доделаем утром"
fi

log "NJ-13 pharma chain start"
bash scripts/run_nj13_chain.sh >> results/runtime/night_NJ-13_20260927.log 2>&1
rc=$?
log "NJ-13 rc=$rc"
if [ -s /mnt/e/openalex_derived/termtech_pharma/filter_report.json ]; then
  finish_job pharma NJ-13 night_NJ-13_20260927.log
  # честный повторный замер фармы по НОВЫМ кандидатам NJ-13
  .venv/bin/python -u scripts/retro_coverage.py \
    --domain "pharma=/mnt/e/openalex_derived/termtech_pharma" \
    >> "$LOG" 2>&1
  .venv/bin/python -u scripts/pharma_coverage_check.py --domain pharma >> "$LOG" 2>&1
  log "фарма-замер по NJ-13 rc=$? (0=PASS ≥13/16)"
else
  log "⚠ NJ-13 не дал filter_report"
fi

log "рестарт супервизора run_night_rest.sh (NJ-6/NJ-12 skip)"
bash scripts/run_night_rest.sh >> results/runtime/night_rest_orchestrated2.log 2>&1
log "супервизор завершился rc=$?"
