# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, os
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\clear_bake_t438c.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)

# leave dungeon2 so file unlock
try:
    unreal.EditorLevelLibrary.load_level("/Game/Maps/Dungeon/Map_Dungeon1")
    L("on Dungeon1")
except Exception as e:
    L("switch ERR "+str(e))

built="/Game/Maps/Dungeon/Map_Dungeon2_BuiltData"
disk=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Maps\Dungeon\Map_Dungeon2_BuiltData.uasset"

# try delete_loaded_asset
try:
    asset=unreal.EditorAssetLibrary.load_asset(built)
    L("loaded asset="+str(asset))
    if asset:
        ok=unreal.EditorAssetLibrary.delete_loaded_asset(asset)
        L("delete_loaded_asset ok=%s"%ok)
except Exception as e:
    L("loaded del ERR "+str(e))

# also try ObjectTools if available
try:
    if unreal.EditorAssetLibrary.does_asset_exist(built):
        # force unload registry then disk delete signal via console
        unreal.SystemLibrary.execute_console_command(None, 'obj garbage')
        L("gc")
except Exception as e:
    L("gc ERR "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines))
