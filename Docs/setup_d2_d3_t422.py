# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\setup_d2_d3_t422.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)

world=unreal.EditorLevelLibrary.get_editor_world()
L("world="+str(world.get_path_name() if world else None))
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    try:
        n=a.get_name() or ""
        loc=a.get_actor_location()
    except Exception:
        continue
    nl=n.lower()
    if nl.startswith("sm_stairs2") or ("stairs2" in nl):
        try:
            a.set_actor_label("ToDungeon3_Stairs")
            L("label d3: %s (%.0f,%.0f,%.0f)"%(n,float(loc.x),float(loc.y),float(loc.z)))
        except Exception as e:
            L("d3 label ERR "+str(e))
    elif nl.startswith("sm_stairs"):
        try:
            a.set_actor_label("HubReturn_D2Stairs")
            L("label hub: %s (%.0f,%.0f,%.0f)"%(n,float(loc.x),float(loc.y),float(loc.z)))
        except Exception as e:
            L("hub label ERR "+str(e))

try:
    unreal.EditorLevelLibrary.save_current_level()
    L("saved Map_Dungeon2")
except Exception as e:
    L("save d2 ERR "+str(e))

src="/Game/Maps/Dungeon/Map_Dungeon2"
dst="/Game/Maps/Dungeon/Map_Dungeon3"
if unreal.EditorAssetLibrary.does_asset_exist(dst):
    L("Map_Dungeon3 already exists")
else:
    ok=unreal.EditorAssetLibrary.duplicate_asset(src, dst)
    L("duplicate -> %s ok=%s"%(dst, bool(ok)))

if unreal.EditorAssetLibrary.does_asset_exist(dst):
    try:
        unreal.EditorLevelLibrary.load_level(dst)
        L("loaded D3")
    except Exception as e:
        L("load D3 ERR "+str(e))
    ps=None
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            if isinstance(a, unreal.PlayerStart) or ("PlayerStart" in (a.get_name() or "")):
                ps=a
                break
        except Exception:
            pass
    if ps is None:
        try:
            ps=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-1180.0, 0.0, 120.0), unreal.Rotator(0,0,0))
            L("spawned PlayerStart")
        except Exception as e:
            L("spawn PS ERR "+str(e))
    if ps is not None:
        try:
            ps.set_actor_label("Dungeon3_PlayerStart")
            ps.set_actor_location(unreal.Vector(-1180.0, 0.0, 120.0), False, False)
            L("PS ok")
        except Exception as e:
            L("PS set ERR "+str(e))
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            lab=a.get_actor_label() if hasattr(a,"get_actor_label") else ""
        except Exception:
            lab=""
        if lab=="HubReturn_D2Stairs":
            try: a.set_actor_label("D3_Stairs_Up")
            except Exception: pass
        if lab=="ToDungeon3_Stairs":
            try: a.set_actor_label("D3_Stairs_Down")
            except Exception: pass
    try:
        unreal.EditorLevelLibrary.save_current_level()
        L("saved Map_Dungeon3")
    except Exception as e:
        L("save d3 ERR "+str(e))
    try:
        unreal.EditorLevelLibrary.load_level(src)
        L("reloaded Map_Dungeon2")
    except Exception as e:
        L("reload d2 ERR "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines))