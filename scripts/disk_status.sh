#!/bin/bash
# Правдивая картина дисков для планирования (см. docs/DISKS_20260925.md).
#
# ЛОВУШКА: df корня WSL (/home) показывает ВИРТУАЛЬНУЮ ёмкость ext4
# (десятки/сотни ГБ), но корень WSL — это sparse-vhdx на диске D:\.
# Реальный потолок новых записей = свободное на D:, а не «881G avail».
# Правило: большие файлы → ТОЛЬКО E:; в WSL не переносить ничего > 5 ГБ,
# пока не посмотрен этот скрипт.
set -u
warn() { printf '\033[1;33m%s\033[0m\n' "$*"; }

echo "== df корня WSL (ВИРТУАЛЬНО — НЕ лимит!) =="
df -h / | tail -1
echo
echo "== Реальные диски хоста =="
for m in /mnt/d /mnt/e /mnt/c; do
  [ -d "$m" ] && df -h "$m" | tail -1 || warn "$m не смонтирован"
done
echo
echo "== Фон: где лежит корень WSL =="
vhdx=$(find /mnt/d -maxdepth 4 -iname 'ext4.vhdx' -printf '%s %p\n' 2>/dev/null \
       | sort -rn | head -1 | cut -d' ' -f2-)
if [ -n "$vhdx" ]; then
  sz=$(stat -c '%s' "$vhdx" 2>/dev/null || echo 0)
  echo "vhdx: $vhdx  ($(numfmt --to=iec "$sz"))"
fi
avail_wsl_gb=0
dfree_kb=$(df -k /mnt/d 2>/dev/null | awk 'NR==2{print $4}')
if [ -n "${dfree_kb:-}" ]; then
  avail_wsl_gb=$((dfree_kb / 1024 / 1024))
fi
echo
warn "Запись в WSL (в /home, /root, tmp, спилл): максимум ~${avail_wsl_gb} ГБ (свободно на D:)."
warn "Большие данные — ТОЛЬКО /mnt/e. Прежде чем писать >5 ГБ в WSL — этот скрипт."
