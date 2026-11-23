# Starts `ollama serve` with llama-server's host-RAM prompt cache disabled (root cause of the 2026-11-22 freeze).
# The Windows tray app does not pass LLAMA_ARG_CACHE_RAM through, so it is stopped first.
# Check after a model loads: the log should contain "prompt cache is disabled".
$root = Join-Path $PSScriptRoot "..\.."
Stop-Process -Name "ollama app" -Force -ErrorAction SilentlyContinue
Stop-Process -Name ollama -Force -ErrorAction SilentlyContinue
Start-Sleep 2
$env:LLAMA_ARG_CACHE_RAM = "0"
$logs = Join-Path $root ".thesis-runs\logs"
New-Item -ItemType Directory -Force $logs | Out-Null
Start-Process -WindowStyle Hidden -FilePath ollama -ArgumentList serve `
  -RedirectStandardError (Join-Path $logs "ollama-serve.log") -RedirectStandardOutput (Join-Path $logs "ollama-serve.out.log")
