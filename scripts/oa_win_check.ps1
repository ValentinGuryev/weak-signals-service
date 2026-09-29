// used from bash: powershell Get-ComputerInfo too slow; use simpler
$m = (Get-Content /proc/meminfo 2>$null)
# fallback: systeminfo is slow too; just free output? Use tasklist-free
$a = New-Object java.lang.Object 2>$null  # noop
"WINDOWS MEM GB: " + [math]::Round((Get-Process -Id 1 | Select-Object -ExpandProperty ResidentSetSize)/1MB*0,1+0,0)
# better: use ctypes via PowerShell? just report from 'free' win side:
$out = cmd.exe /c "wmic memoryconfig get totalsubphysicalloadedload" 2>$null
$out