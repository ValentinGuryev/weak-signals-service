#!/usr/bin/env bash
# oa_dedup_years.sh — оркестратор v5: дедуп лет 2017..2026, ПО ОДНОМУ ГОДУ ЗА ПРОЦЕСС.
# Параметры --threads 2 --mem 3GB — единственные рабочие (см. get_to_context.md §6 OOM).
# Fail-fast: падение года => стоп (не продолжать, чтобы не терять данные молча).
# Запуск: setsid bash scripts/oa_dedup_years.sh >/dev/null 2>&1 &  (PID — в oa_dedup_years.pid)
set -u
cd /home/user/projects/Hackathon

FROM=${OA_FROM:-2017}
TO=${OA_TO:-2026}
LOG=results/runtime/oa_dedup_years.log
mkdir -p results/runtime
echo $$ > results/runtime/oa_dedup_years.pid

log() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }

log "START dedup years $FROM..$TO (threads=2 mem=${OA_MEM:-3GB}, v5)"

for y in $(seq "$FROM" "$TO"); do
  log "YEAR $y === begin ==="
  OA_YEAR_FROM=$y OA_YEAR_TO=$y OA_DEDUP_ONLY=1 \
    .venv/bin/python scripts/oa_run_ingest.py \
      --manifest /mnt/e/openalex-snapshot/data/jsonl/manifest.json \
      --works    /mnt/e/openalex-snapshot/data/jsonl/works \
      --local    data/openalex_derived \
      --e        /mnt/e/openalex_derived \
      --staging  /mnt/c/oa_tmp \
      --small    /mnt/c/oa_tmp/small \
      --post-only --threads 2 --mem "${OA_MEM:-3GB}" >> "$LOG" 2>&1
  rc=$?
  if [ $rc -ne 0 ]; then
    log "YEAR $y === FAILED rc=$rc — STOP (fail-fast) ==="
    exit $rc
  fi
  # быстрая верификация: year= каталог существует и непустой
  if [ -d "data/openalex_derived/T_stats/year=$y" ] && [ -n "$(ls -A "data/openalex_derived/T_stats/year=$y")" ]; then
    log "YEAR $y === OK (year= появился) ==="
  else
    log "YEAR $y === FAILED: year=$y не появился — STOP ==="
    exit 1
  fi
done

log "ALL DONE years $FROM..$TO"
