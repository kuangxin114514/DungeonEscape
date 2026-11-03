# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\clear_bake_t435.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)

world=unreal.EditorLevelLibrary.get_editor_world()
L("world="+str(world.get_path_name() if world else None))

# 1) Force no precomputed lighting
try:
    ws=world.get_world_settings()
    ws.set_editor_property("force_no_precomputed_lighting", True)
    L("ForceNoPrecomputedLighting=True")
except Exception as e:
    L("ws ERR "+str(e))

# 2) Keep all point lights Movable so they never bake again
n=0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if not isinstance(a, unreal.PointLight):
        continue
    try:
        comp=a.light_component
        comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        # lift lights slightly off floor to avoid full-tile overbright
        loc=a.get_actor_location()
        if float(loc.z) < 80.0:
            a.set_actor_location(unreal.Vector(float(loc.x), float(loc.y), 180.0), False, False)
            L("lift %s z->180"%a.get_name())
        else:
            L("keep %s z=%.0f"%(a.get_name(), float(loc.z)))
        n+=1
    except Exception as e:
        L("light ERR "+str(e))
L("movable_count=%d"%n)

# 3) Invalidate / clear baked lighting data asset if present
built="/Game/Maps/Dungeon/Map_Dungeon1_BuiltData"
try:
    if unreal.EditorAssetLibrary.does_asset_exist(built):
        ok=unreal.EditorAssetLibrary.delete_asset(built)
        L("deleted BuiltData ok=%s"%ok)
    else:
        L("no BuiltData asset at "+built)
except Exception as e:
    L("BuiltData ERR "+str(e))

# also try map package sibling names
for p in [
    "/Game/Maps/Dungeon/Map_Dungeon1_BuiltData",
    "/Game/Maps/Map_Dungeon1_BuiltData",
]:
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            L("found extra "+p)
    except Exception:
        pass

# 4) Ask editor to rebuild lighting (with ForceNo this clears lightmaps)
try:
    # UE4.27: LightingBuildOptions via EditorLevelLibrary if available
    if hasattr(unreal.EditorLevelLibrary, "build_light_map"):
        unreal.EditorLevelLibrary.build_light_map()
        L("build_light_map called")
    elif hasattr(unreal, "EditorBuildingSubsystem"):
        bs=unreal.get_editor_subsystem(unreal.EditorBuildingSubsystem)
        bs.build(unreal.BuildOptions.LIGHTING)
        L("EditorBuildingSubsystem lighting")
    else:
        unreal.SystemLibrary.execute_console_command(world, "RebuildLighting")
        L("console RebuildLighting")
except Exception as e:
    L("rebuild ERR "+str(e))
    try:
        unreal.SystemLibrary.execute_console_command(world, "RebuildLighting")
        L("console RebuildLighting fallback")
    except Exception as e2:
        L("console ERR "+str(e2))

try:
    unreal.EditorLevelLibrary.save_current_level()
    L("saved")
except Exception as e:
    L("save ERR "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines))
