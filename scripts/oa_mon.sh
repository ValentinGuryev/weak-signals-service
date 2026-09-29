#!/usr/bin/env bash
# oa_mon.sh — мониторинг оркестратора дедупа: ждёт следующую 10-мин метку от START, печатает статус.
set -u
cd /home/user/projects/Hackathon
LOG=results/runtime/oa_dedup_years.log
ts=$(grep 'START dedup years 2024' "$LOG" | tail -1 | sed -E 's/^\[([^]]+)\].*/\1/')
start=$(date -d "$ts" +%s)
now=$(date +%s)
next=$(( start + ( (now - start) / 600 + 1) * 600 ))
PID=$(cat results/runtime/oa_dedup_years.pid 2>/dev/null || echo 0)
while [ "$(date +%s)" -lt "$next" ]; do
  kill -0 "$PID" 2>/dev/null || break
  grep -q 'ALL DONE years 2024..2026' "$LOG" && break
  sleep 15
done
echo "TIME     : $(date '+%F %T')  (+$(( ($(date +%s)-start)/60 )) мин от START)"
if kill -0 "$PID" 2>/dev/null; then echo "ORCH     : ALIVE (pid $PID)"; else echo "ORCH     : EXITED (pid $PID)"; fi
PYPID=$(pgrep -f 'python scripts/oa_run_ingest.py' | head -1 || true)
if [ -n "${PYPID:-}" ]; then ps -o pid=,pcpu=,pmem=,etime= -p "$PYPID" | sed 's/^/PYTHON   : /'; else echo "PYTHON   : not running"; fi
echo "--- log:"
grep -E 'START dedup years|YEAR [0-9]+ ===|ALL DONE|FAILED|ОСТАНОВЛЕНО' "$LOG" | tail -8 | sed 's/^/  /'
echo "--- progress:"
du -sh data/openalex_derived/T_stats/year_tmp=2024 2>/dev/null | sed 's/^/  stats tmp: /'
du -sh /mnt/e/openalex_derived/T_text/year_tmp=2024 2>/dev/null | sed 's/^/  text tmp : /'
du -sh data/openalex_derived/T_stats/year=2024 2>/dev/null | sed 's/^/  year=24 : /'
echo "--- errors since START:"
awk '/START dedup years 2024/{f=1;next} f' "$LOG" | grep -cE 'OutOfMemory|Out of Memory|Traceback|FAILED' | sed 's/^/  count: /'
free -h | sed -n 2p | sed 's/^/  RAM    : /'
