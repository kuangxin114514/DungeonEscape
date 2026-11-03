$ErrorActionPreference = "Continue"
$root = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
$up = Join-Path $root "DungeonEscape.uproject"

# Close running editors for this project if any
Get-Process UE4Editor,UE4Editor-Cmd -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

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

$editor = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe"
$py = Join-Path $root "Docs\create_gameflow_assets.py"
$log = Join-Path $root "Docs\ue_python_create.log"
if (Test-Path $log) { Remove-Item $log -Force }

# Use forward slashes for ExecutePythonScript path
$pyArg = "-ExecutePythonScript=" + ($py -replace '\\','/')
Write-Output "Running: $editor"
Write-Output "Script: $pyArg"

& $editor "`"$up`"" $pyArg -stdout -unattended -nosplash -NullRHI -NoVerifyGC *> $log
Write-Output "EXIT=$LASTEXITCODE"
Write-Output "=== LOG TAIL ==="
Get-Content $log -Tail 100
Write-Output "=== ASSETS ==="
Get-ChildItem (Join-Path $root "Content\Core\GameFlow") -Recurse | Format-Table Name, Length -AutoSize
