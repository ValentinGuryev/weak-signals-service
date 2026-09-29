$f = New-Object System.IO.FileStream('E:\openalex-snapshot\data\jsonl\works\updated_date=2025-10-10\part_0060.gz', 'r')
$buf = New-Object byte[] 16777216
$t0 = [DateTime]::Now
$read = 0
while ($true) {
    $n = $f.Read($buf, 0, 16777216)
    if ($n -le 0) { break }
    $read += $n
}
$f.Close()
$dt = [math]::Max(0.001, (([DateTime]::Now - $t0).TotalSeconds))
"NATIVE_READ_MB: " + [math]::Round($read/1MB,1)
"NATIVE_SPEED_MBs: " + [math]::Round($read/1MB/$dt,1)
$size = (Get-Item 'E:\openalex-snapshot\data\jsonl\works\updated_date=2025-10-10\part_0060.gz').Length
"FILE_MB: " + [math]::Round($size/1MB,1)