$ErrorActionPreference = "Continue"
$root = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
$up = Join-Path $root "DungeonEscape.uproject"
$py = Join-Path $root "Docs\socket_kaykit_weapons.py"
$log = Join-Path $root "Docs\ue_socket_weapons_runner.log"
$editorCmd = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe"
$editorGui = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor.exe"

function Write-Log($m) {
  $line = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m
  Write-Output $line
  Add-Content -Path $log -Value $line -Encoding UTF8
}

Set-Content -Path $log -Value "begin runner" -Encoding UTF8

$running = @(Get-Process UE4Editor,UE4Editor-Cmd -ErrorAction SilentlyContinue)
if ($running.Count -gt 0) {
  Write-Log ("UE already running PIDs=" + (($running | ForEach-Object { $_.Id }) -join ","))
  Write-Log "WILL NOT kill editor. Trying remote execution / instructing in-editor run."
  # Try remote execution helper
  $remoteHelper = Join-Path $root "Docs\try_remote_exec_socket.py"
  $pyExe = $null
  foreach ($c in @(
    "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe",
    "C:\Users\86178\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Users\86178\AppData\Local\Programs\Python\Python310\python.exe",
    "python"
  )) {
    if ($c -eq "python") { $pyExe = "python"; break }
    if (Test-Path $c) { $pyExe = $c; break }
  }
  if ($pyExe) {
    Write-Log "remote via $pyExe"
    & $pyExe $remoteHelper 2>&1 | Tee-Object -FilePath (Join-Path $root "Docs\ue_socket_remote.log")
    Write-Log ("remote exit=" + $LASTEXITCODE)
    if (Test-Path (Join-Path $root "Docs\ue_socket_weapons.log")) {
      $tail = Get-Content (Join-Path $root "Docs\ue_socket_weapons.log") -Tail 30 -ErrorAction SilentlyContinue
      if ($tail -match "DONE") {
        Write-Log "SUCCESS via remote"
        exit 0
      }
    }
  }
  Write-Log "REMOTE_FAILED_OR_DISABLED"
  Write-Log "USER_ACTION: In UE editor: File -> Execute Python Script -> Docs\socket_kaykit_weapons.py"
  Write-Log "OR: Save All, close UE4Editor, re-run this runner."
  # Write a marker the parent can show
  Set-Content -Path (Join-Path $root "Docs\ue_socket_weapons_NEED_EDITOR.txt") -Value @"
Editor is open; runner refused to kill it.
Option A: In Unreal: File > Execute Python Script >
  C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\socket_kaykit_weapons.py
Option B: Ctrl+Shift+S save all, close editor, then run:
  powershell -File Docs\run_socket_kaykit_weapons.ps1
"@ -Encoding UTF8
  exit 2
}

# No editor: launch Cmd unattended (does not use Stop-Process)
Write-Log "No UE process; launching UE4Editor-Cmd"
$pyArg = "-ExecutePythonScript=" + ($py -replace '\\','/')
& $editorCmd "`"$up`"" $pyArg -stdout -unattended -nosplash -NullRHI -NoVerifyGC *> $log
Write-Log ("EXIT=" + $LASTEXITCODE)
if (Test-Path (Join-Path $root "Docs\ue_socket_weapons.log")) {
  Write-Log "=== script log ==="
  Get-Content (Join-Path $root "Docs\ue_socket_weapons.log") -Tail 80 | ForEach-Object { Write-Log $_ }
}
exit $LASTEXITCODE
