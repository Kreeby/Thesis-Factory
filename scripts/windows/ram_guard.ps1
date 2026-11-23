# Stops deep reading and unloads Ollama if free RAM drops below the floor.
param([double]$FloorGB = 2.5, [int]$MaxTempC = 85,[string]$Log = (Join-Path $PSScriptRoot "..\..\.thesis-runs\logs\ram-guard.log"))
$hot = 0
while ($true) {
    $free = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB
    # keep the desktop responsive: model runner below normal priority
    Get-Process ollama*, llama* -ErrorAction SilentlyContinue | ForEach-Object { try { $_.PriorityClass = 'BelowNormal' } catch {} }
    $reader = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*read_papers.py*' }
    if (-not $reader) { "$(Get-Date -f s) reader gone, guard exits" | Add-Content $Log; break }
    # driver limits on this RTX 3060: target 83 C, max operating 93 C, slowdown 95 C
    $g = (nvidia-smi --query-gpu=temperature.gpu,clocks_event_reasons.hw_thermal_slowdown,clocks_event_reasons.sw_thermal_slowdown --format=csv,noheader,nounits) -split ',\s*'
    $temp = [int]$g[0]; $throttle = ($g[1] -eq 'Active') -or ($g[2] -eq 'Active')
    if ($temp -ge $MaxTempC) { $hot++ } else { $hot = 0 }
    $reason = $null
    if ($free -lt $FloorGB) { $reason = "free RAM {0:N1} GB < $FloorGB" -f $free }
    elseif ($hot -ge 3) { $reason = "GPU $temp C >= $MaxTempC C for 30 s" }
    elseif ($throttle) { $reason = "GPU thermal slowdown active at $temp C" }
    if ($reason) {
        "$(Get-Date -f s) $reason, stopping" | Add-Content $Log
        $reader | ForEach-Object { taskkill /T /F /PID $_.ProcessId | Out-Null }
        ollama stop qwen3:8b
        break
    }
    Start-Sleep 10
}
