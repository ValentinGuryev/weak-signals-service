$ErrorActionPreference = 'Continue'
$dst = 'C:\oa_probe'
New-Item -ItemType Directory -Force -Path $dst | Out-Null
$root = 'E:\openalex-snapshot\data\jsonl'

# 1. manifest.json (top-level)
Copy-Item "$root\manifest.json" "$dst\manifest.json" -Force

# 2. small works part + a recent one
Copy-Item "$root\works\updated_date=2016-06-24\part_0000.gz" "$dst\works_old.gz" -Force
Copy-Item "$root\works\updated_date=2026-06-01\part_0000.gz" "$dst\works_recent.gz" -Force

# 3. topics / concepts / keywords / fields / subfields / domains (any part)
foreach ($ent in @('topics','concepts','keywords','fields','subfields','domains')) {
    $d = Get-ChildItem "$root\$ent" -Recurse -File -Filter *.gz | Select-Object -First 1
    if ($d) { Copy-Item $d.FullName "$dst\$ent.gz" -Force }
}

"COPIED:"
Get-ChildItem $dst | ForEach-Object { "$($_.Name)  $([math]::Round($_.Length/1KB,1)) KB" }