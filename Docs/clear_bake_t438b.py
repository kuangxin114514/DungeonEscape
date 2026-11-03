# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\clear_bake_t438b.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)

# Switch away so BuiltData can be deleted
try:
    unreal.EditorLevelLibrary.load_level("/Game/Maps/Dungeon/Map_Dungeon1")
    L("switched to Dungeon1")
except Exception as e:
    L("switch ERR "+str(e))

built="/Game/Maps/Dungeon/Map_Dungeon2_BuiltData"
try:
    exists=unreal.EditorAssetLibrary.does_asset_exist(built)
    L("exists=%s"%exists)
    if exists:
        ok=unreal.EditorAssetLibrary.delete_asset(built)
        L("delete_asset ok=%s"%ok)
except Exception as e:
    L("del ERR "+str(e))

# reload dungeon2
try:
    unreal.EditorLevelLibrary.load_level("/Game/Maps/Dungeon/Map_Dungeon2")
    world=unreal.EditorLevelLibrary.get_editor_world()
    L("reloaded "+str(world.get_path_name() if world else None))
    ws=world.get_world_settings()
    ws.set_editor_property("force_no_precomputed_lighting", True)
    L("ForceNo=True")
    unreal.EditorLevelLibrary.save_current_level()
    L("saved")
except Exception as e:
    L("reload ERR "+str(e))

# confirm built gone
try:
    L("BuiltData still exists=%s"%unreal.EditorAssetLibrary.does_asset_exist(built))
except Exception as e:
    L("check ERR "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines))
