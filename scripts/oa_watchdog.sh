#!/bin/bash
# Сторожевой процесс пост-пассов OpenAlex (dedup → topic_index → digest).
# Каждые 20 мин: процесс жив? → лог прогресса; упал → перезапуск (OOM → mem ниже),
# до 3 быстрых падений подряд, затем остановка с докладом. Завершение: "Пост-пассы OK".

BASE=/home/user/projects/Hackathon
LOG=$BASE/results/runtime/oa_post.log
WLOG=$BASE/results/runtime/oa_watchdog.log
STATS=$BASE/data/openalex_derived/T_stats
INTERVAL=${OA_WATCH_INTERVAL:-1200}   # 20 минут

declare -a RUN_ARGS=(--manifest /mnt/e/openalex-snapshot/data/jsonl/manifest.json
  --works /mnt/e/openalex-snapshot/data/jsonl/works
  --local $BASE/data/openalex_derived
  --e /mnt/e/openalex_derived
  --staging /mnt/c/oa_tmp --small /mnt/c/oa_tmp/small
  --post-only --threads 6 --mem 4GB)

log() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$WLOG"; }

alive() {
  # настоящий python-процесс (не bash-обёртка)
  for p in $(pgrep -f "oa_run_ingest"); do
    [ "$(ps -o comm= -p "$p" 2>/dev/null)" = "python3" ] && return 0
  done
  return 1
}

finish_check() {  # 0 = смоук-финиш найден в логе
  grep -q "Пост-пассы OK" "$LOG" 2>/dev/null
}

launch() {
  local mem="${1:-4GB}"
  nohup bash -c "cd $BASE && .venv/bin/python scripts/oa_run_ingest.py ${RUN_ARGS[*]//--mem 4GB/} --threads 6 --mem $mem >> $LOG 2>&1" >/dev/null 2>&1 &
  log "RESTART mem=$mem pid=$!"
}

snapshot() {
  local tmp=$(ls -d $STATS/year_tmp=* 2>/dev/null | sed 's/.*year_tmp=//' | tr '\n' ' ')
  local fin=$(ls -d $STATS/year=* 2>/dev/null | sed 's/.*year=//' | sort -n | tr '\n' ' ')
  local bat=$(ls -d $STATS/batch=* 2>/dev/null | wc -l)
  log "OK in-process year_tmp=[$tmp] finals=[$fin] batches_left=$bat"
}

# ---- старт
log "WATCHDOG started interval=${INTERVAL}s (ждём текущий процесс)"
FAILS=0
while true; do
  sleep "$INTERVAL"
  if alive; then
    FAILS=0
    snapshot
    continue
  fi
  # процесс не жив
  if finish_check; then
    log "COMPLETED: 'Пост-пассы OK' найден в логе — все пост-пассы готовы"
    exit 0
  fi
  FAILS=$((FAILS+1))
  log "DEAD (fail#$FAILS текущий год_tmp= сворачиваю): tail лога:"
  tail -6 "$LOG" | sed 's/^/    | /' >> "$WLOG"
  if [ "$FAILS" -gt 3 ]; then
    log "GIVING UP после $FAILS быстрых падений — жду автора (нужен фикс кода)"
    exit 1
  fi
  # адаптация по типу ошибки
  if tail -6 "$LOG" | grep -q "Cannot allocate memory"; then
    launch 3GB
  else
    launch 4GB
  fi
  log "ожидание 2 мин перед след. проверкой (дать питону стартовать)"
  sleep 120
done