$ErrorActionPreference = "Continue"
$root = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
$log = Join-Path $root "Docs\ue_socket_wait_import.log"
$up = Join-Path $root "DungeonEscape.uproject"
$py = Join-Path $root "Docs\socket_kaykit_weapons.py"
$editorCmd = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe"
function W($m){ $l="[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m; Add-Content $log $l -Encoding UTF8; Write-Output $l }
Set-Content $log "begin wait" -Encoding UTF8
W "Waiting for UE4Editor to exit (will NOT kill it)..."
$deadline = (Get-Date).AddMinutes(20)
while ((Get-Date) -lt $deadline) {
  $p = Get-Process UE4Editor,UE4Editor-Cmd -ErrorAction SilentlyContinue
  if (-not $p) { W "Editor gone"; break }
  Start-Sleep -Seconds 5
}
if (Get-Process UE4Editor,UE4Editor-Cmd -ErrorAction SilentlyContinue) {
  W "TIMEOUT still running after 20m — abort"
  exit 3
}
Start-Sleep -Seconds 3
W "Launching UE4Editor-Cmd import"
$pyArg = "-ExecutePythonScript=" + ($py -replace '\\','/')
$outLog = Join-Path $root "Docs\ue_socket_weapons_cmd.log"
& $editorCmd "`"$up`"" $pyArg -stdout -unattended -nosplash -NullRHI -NoVerifyGC *> $outLog
W ("CMD_EXIT=" + $LASTEXITCODE)
if (Test-Path (Join-Path $root "Docs\ue_socket_weapons.log")) {
  W "=== script log ==="
  Get-Content (Join-Path $root "Docs\ue_socket_weapons.log") | ForEach-Object { W $_ }
}
# reopen editor for user
W "Reopening editor GUI"
Start-Process $editorCmd.Replace("UE4Editor-Cmd.exe","UE4Editor.exe") -ArgumentList "`"$up`""
W "DONE_PIPELINE"
