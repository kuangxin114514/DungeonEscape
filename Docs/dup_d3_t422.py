# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\dup_d3_t422.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)
src="/Game/Maps/Dungeon/Map_Dungeon2"
dst="/Game/Maps/Dungeon/Map_Dungeon3"
L("src exists=%s"%unreal.EditorAssetLibrary.does_asset_exist(src))
L("dst exists=%s"%unreal.EditorAssetLibrary.does_asset_exist(dst))
# try AssetTools duplicate
try:
    registry=unreal.AssetRegistryHelpers.get_asset_registry()
except Exception as e:
    L("registry "+str(e))
try:
    asset=unreal.EditorAssetLibrary.load_asset(src)
    L("loaded src type="+str(type(asset)))
except Exception as e:
    L("load ERR "+str(e)); asset=None
try:
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    # duplicate_asset(name, path, asset)
    dup=tools.duplicate_asset("Map_Dungeon3", "/Game/Maps/Dungeon", asset)
    L("AssetTools dup="+str(dup))
except Exception as e:
    L("AssetTools ERR "+str(e))
L("dst exists2=%s"%unreal.EditorAssetLibrary.does_asset_exist(dst))
if unreal.EditorAssetLibrary.does_asset_exist(dst):
    try:
        unreal.EditorLevelLibrary.load_level(dst)
        L("loaded D3")
        ps=None
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            try:
                if isinstance(a, unreal.PlayerStart) or ("PlayerStart" in (a.get_name() or "")):
                    ps=a; break
            except Exception:
                pass
        if ps is None:
            ps=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-1180.0,0.0,120.0), unreal.Rotator(0,0,0))
            L("spawned PS")
        if ps:
            ps.set_actor_label("Dungeon3_PlayerStart")
            try: ps.set_actor_location(unreal.Vector(-1180.0,0.0,120.0), False, False)
            except Exception: pass
            L("PS labeled")
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            try: lab=a.get_actor_label()
            except Exception: lab=""
            if lab=="HubReturn_D2Stairs":
                try: a.set_actor_label("D3_Stairs_Up")
                except Exception: pass
            if lab=="ToDungeon3_Stairs":
                try: a.set_actor_label("D3_Stairs_Down")
                except Exception: pass
        unreal.EditorLevelLibrary.save_current_level()
        L("saved D3")
        unreal.EditorLevelLibrary.load_level(src)
        L("back to D2")
    except Exception as e:
        L("D3 setup ERR "+str(e))
open(OUT,"w",encoding="utf-8").write("\n".join(lines))
