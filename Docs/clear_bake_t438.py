# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\clear_bake_t438.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)

world=unreal.EditorLevelLibrary.get_editor_world()
L("world="+str(world.get_path_name() if world else None))

# Ensure Map_Dungeon2 is loaded
want="/Game/Maps/Dungeon/Map_Dungeon2"
try:
    cur=world.get_path_name() if world else ""
    if "Map_Dungeon2" not in cur:
        unreal.EditorLevelLibrary.load_level(want)
        world=unreal.EditorLevelLibrary.get_editor_world()
        L("loaded Map_Dungeon2 -> "+str(world.get_path_name() if world else None))
except Exception as e:
    L("load ERR "+str(e))

try:
    ws=world.get_world_settings()
    ws.set_editor_property("force_no_precomputed_lighting", True)
    L("ForceNoPrecomputedLighting=True")
except Exception as e:
    L("ws ERR "+str(e))

# Point lights movable if any remain
n=0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if isinstance(a, unreal.PointLight) or isinstance(a, unreal.SpotLight) or isinstance(a, unreal.DirectionalLight):
        try:
            comp=a.light_component
            comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
            L("movable "+a.get_name())
            n+=1
        except Exception as e:
            L("light ERR "+str(e))
L("lights_touched=%d"%n)

for p in [
    "/Game/Maps/Dungeon/Map_Dungeon2_BuiltData",
    "/Game/Maps/Map_Dungeon2_BuiltData",
]:
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            ok=unreal.EditorAssetLibrary.delete_asset(p)
            L("deleted %s ok=%s"%(p, ok))
        else:
            L("missing "+p)
    except Exception as e:
        L("del ERR %s %s"%(p,e))

try:
    unreal.SystemLibrary.execute_console_command(world, "RebuildLighting")
    L("RebuildLighting")
except Exception as e:
    L("rebuild ERR "+str(e))

try:
    unreal.EditorLevelLibrary.save_current_level()
    L("saved")
except Exception as e:
    L("save ERR "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines))
