#!/bin/bash
# lib_cap.sh — кап памяти джобов (фикс 26.09 после падений WSL; журнал 20:55).
#
# Зачем: OOM python в init.scope валял systemd → teardown VM WSL целиком
# (03:43 и 19:47 26.09) + crash-loop. Кап через systemd-run --user --scope:
#   MemoryMax=<лимит> + MemorySwapMax=0
# → при исчерпании лимита cgroup OOM убивает ТОЛЬКО процесс джоба (rc=137),
# система жива, супервизор видит 137 и останавливает очередь (без ретраев).
#
# Проверено смоуком 26.09: scope поднимается, rc прокидывается (42→42,
# alloc 300M при MemoryMax=64M → rc=137, host жив).
#
# Доступность капа определяется ОДНОКРАТНО пробным запуском (cap-probe):
# при отказе systemd-run выполняется fallback БЕЗ капа (с предупреждением).
CAP_OK=-1

cap_run() {  # cap_run <unit-suffix> <MemoryMax> <cmd...>
  local unit="$1" mem="$2"; shift 2
  if [ "$CAP_OK" = -1 ]; then
    if command -v systemd-run >/dev/null 2>&1 && \
       systemd-run --user --quiet --scope --collect \
         --unit="cap-probe-$$-$RANDOM" -- /bin/true 2>/dev/null; then
      CAP_OK=1
      echo "[cap] капы памяти доступны (systemd-run --user scope)"
    else
      CAP_OK=0
      echo "[cap] ⚠ КАПЫ НЕДОСТУПНЫ — джоба запускается БЕЗ лимита памяти!" >&2
    fi
  fi
  if [ "$CAP_OK" = 1 ]; then
    systemd-run --user --quiet --scope --collect \
      --unit="${unit}-$$" -p "MemoryMax=$mem" -p MemorySwapMax=0 -- "$@"
    return $?
  fi
  "$@"
}
