@echo off
set PY=C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe
set SCR=C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\run_wire_bp_remote.py
set OUT=C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\run_wire_stdout.txt
set ERR=C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\run_wire_stderr.txt
"%PY%" "%SCR%" > "%OUT%" 2> "%ERR%"
echo DONE>> "%OUT%"
