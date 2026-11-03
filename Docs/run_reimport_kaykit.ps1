$ErrorActionPreference = "Continue"
$root = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
$up = Join-Path $root "DungeonEscape.uproject"
$editor = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe"
# UE4 -ExecutePythonScript breaks on spaces; always run from C:\Temp copy
$srcPy = Join-Path $root "Docs\reimport_kaykit_scaled.py"
$py = "C:\Temp\DungeonEscape\reimport_kaykit_scaled.py"
$log = Join-Path $root "Docs\ue_kaykit_scaled.log"

$running = @(Get-Process UE4Editor,UE4Editor-Cmd -ErrorAction SilentlyContinue)
if ($running.Count -gt 0) {
    Write-Output "EDITOR_RUNNING ids=$($running.Id -join ',')"
    Write-Output "REFUSING to kill. Close editor (save first) then re-run."
    exit 2
}

New-Item -ItemType Directory -Force -Path "C:\Temp\DungeonEscape" | Out-Null
Copy-Item -Force $srcPy $py
if (Test-Path $log) { Remove-Item $log -Force }

$json = @'
{
	"FileVersion": 3,
	"EngineAssociation": "4.27",
	"Category": "",
	"Description": "Roguelite dungeon course project",
	"Plugins": [
		{ "Name": "PythonScriptPlugin", "Enabled": true },
		{ "Name": "EditorScriptingUtilities", "Enabled": true },
		{ "Name": "OculusVR", "Enabled": false },
		{ "Name": "OnlineSubsystemOculus", "Enabled": false },
		{ "Name": "OculusEditor", "Enabled": false }
	]
}
'@
Set-Content -Path $up -Value $json -Encoding ASCII

$argList = @(
  "`"$up`"",
  "-ExecutePythonScript=`"$($py -replace '\\','/')`"",
  "-stdout",
  "-unattended",
  "-nosplash",
  "-NullRHI",
  "-NoVerifyGC"
)
Write-Output "Running KayKit scaled reimport..."
Write-Output "Args: $($argList -join ' ')"
$p = Start-Process -FilePath $editor -ArgumentList $argList -Wait -PassThru -NoNewWindow -RedirectStandardOutput $log -RedirectStandardError "$log.err"
Write-Output "EXIT=$($p.ExitCode)"
Write-Output "=== Saved log matches ==="
$ueLog = Join-Path $root "Saved\Logs\DungeonEscape.log"
Select-String -Path $ueLog -Pattern "KAYKIT|BOUNDS|pass1|FALLBACK|placed |READY|destroyed|PlayerStart|UPRIGHT|SIDEWAYS" | Select-Object -Last 40 | ForEach-Object { $_.Line }
