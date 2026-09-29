#!/usr/bin/env bash
# run_mine_domains.sh — последовательный mine 9 доменных слайсов → _yeardf
# (годовые ряды термов) для подключения доменных сторов к tech_ngi.
# решение команды: («проект сдавать вот-вот»); слайсы: /mnt/e/openalex_derived/slices/<d>
# (read-only!), выход: results/termtech_<d>/{_yeardf,all_terms,candidates,...}.
# Порядок — приоритет демо-областям жюри (protect → robots → industrial/infra → quantum → …).
# Запуск: setsid nohup bash scripts/run_mine_domains.sh >/dev/null 2>&1 &
set -u
cd /home/user/projects/Hackathon
STAMP="$(date +%Y%m%d_%H%M)"
LOG="results/runtime/mine_domains_${STAMP}.log"
echo "$LOG" > results/runtime/mine_domains_latest.logpath
ORDER="ai_security robotics energy materials quantum space biomed pharma pharma2"

{
  echo "=== mine доменных слайсов, старт $(date '+%F %T')"
  FAIL=""
  for d in $ORDER; do
    slice="/mnt/e/openalex_derived/slices/$d"
    out="results/termtech_$d"
    echo "=== [$(date +%H:%M:%S)] $d: start"
    if .venv/bin/python scripts/termtech_mine.py --slice "$slice" --out "$out"; then
      echo "=== [$(date +%H:%M:%S)] $d: DONE"
    else
      echo "=== [$(date +%H:%M:%S)] $d: FAIL (продолжаем)"
      FAIL="$FAIL $d"
    fi
  done
  echo "=== ALL_DONE $(date '+%F %T') | failed:${FAIL:- нет}"
} >> "$LOG" 2>&1
