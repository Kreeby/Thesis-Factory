# Loads .env into the current PowerShell session without printing values (needed outside ./scripts/uv,
# e.g. before start_fetch.cmd). Usage: . .\scripts\windows\load_env.ps1
$envFile = Join-Path $PSScriptRoot "..\..\.env"
Get-Content $envFile | Where-Object { $_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$' } | ForEach-Object {
  $v = $Matches[2].Trim().Trim('"').Trim("'"); if ($v) { Set-Item "env:$($Matches[1])" $v }
}
