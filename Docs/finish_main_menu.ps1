Copy-Item 'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\create_menu_map_only.py' 'C:\Temp\create_menu_map_only.py' -Force
Get-Process UE4Editor,UE4Editor-Cmd -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep 3
$e = 'C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe'
$u = 'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\DungeonEscape.uproject'
& $e $u '-ExecutePythonScript=C:/Temp/create_menu_map_only.py' -stdout -unattended -nosplash -NullRHI *> 'C:\Temp\ue_mm.log'
Write-Output "EXIT=$LASTEXITCODE"
Select-String 'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Saved\Logs\DungeonEscape.log' -Pattern 'MENU MAP ONLY|LogPython: Error' | Select-Object -Last 10 | ForEach-Object { $_.Line }

$ini = 'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Config\DefaultInput.ini'
$txt = ''
if (Test-Path $ini) { $txt = Get-Content $ini -Raw }
if ($txt -notmatch 'open Map_Hub') {
  if ($txt -notmatch '\[/Script/Engine\.PlayerInput\]') {
    $txt += "`r`n[/Script/Engine.PlayerInput]`r`n"
  }
  $txt += "+DebugExecBindings=(Key=Enter,Command=`"open Map_Hub`",bIgnoreShift=True)`r`n"
  $txt += "+DebugExecBindings=(Key=SpaceBar,Command=`"open Map_Hub`",bIgnoreShift=True)`r`n"
  $txt += "+DebugExecBindings=(Key=Escape,Command=`"quit`",bIgnoreShift=True)`r`n"
  Set-Content -Path $ini -Value $txt -Encoding UTF8
  Write-Output 'INPUT_BINDS_ADDED'
} else {
  Write-Output 'INPUT_BINDS_EXIST'
}

Select-String 'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Config\DefaultEngine.ini' -Pattern 'StartupMap|DefaultMap' | ForEach-Object { $_.Line }
Write-Output ("MAP_EXISTS=" + (Test-Path 'C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Maps\MainMenu\Map_MainMenu.umap'))
$gui = $e -replace 'UE4Editor-Cmd','UE4Editor'
Start-Process $gui -ArgumentList @("`"($u)`"", '/Game/Maps/MainMenu/Map_MainMenu', '-nosplash')
# fix Start-Process args
Start-Process $gui -ArgumentList "`"$u`"","/Game/Maps/MainMenu/Map_MainMenu","-nosplash"
Write-Output 'EDITOR_LAUNCHED'
