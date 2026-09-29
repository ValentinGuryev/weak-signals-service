#!/bin/bash
# Watcher: каждые 20 мин снимок прогресса + авто-перезапуск цепочки, если умерла.
BASE=/home/user/projects/Hackathon
LOG=$BASE/results/runtime/oa_post.log
W=$BASE/results/runtime/oa_watchdog.log
: > "$W"
echo "$(date '+%F %T') watchdog started" >> "$W"
while true; do
  sleep 1200
  if ! pgrep -f "scripts/oa_post_full.sh" >/dev/null; then
    if grep -q "CHAIN DONE" "$LOG" 2>/dev/null; then
      echo "$(date '+%T') COMPLETED (CHAIN DONE в логе)" >> "$W"; exit 0
    fi
    echo "$(date '+%T') CHAIN DIED — перезапуск oa_post_full.sh" >> "$W"
    nohup bash "$BASE/scripts/oa_post_full.sh" > /dev/null 2>&1 &
  fi
  cur=$(ls -d "$BASE/data/openalex_derived/T_stats"/year_tmp=* 2>/dev/null | sed 's/.*year_tmp=//' | tr '\n' ' ')
  fin=$(ls -d "$BASE/data/openalex_derived/T_stats"/year=* 2>/dev/null | sed 's/.*year=//' | sort -n | tr '\n' ' ')
  tbl=$(ls -d "$BASE/data/openalex_derived/T_stats"/batch=* 2>/dev/null | wc -l)
  echo "$(date '+%T') SNAP tmp=[$cur] finals=[$fin] batches_left=$tbl" >> "$W"
done