# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\verify_gate_actors.txt"
lines = []

def L(m):
    lines.append(str(m))
    try:
        unreal.log("VerifyGate: " + str(m))
    except Exception:
        pass

world = unreal.EditorLevelLibrary.get_editor_world()
L("world=" + world.get_path_name())
found = []
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    lab = a.get_actor_label() or ""
    tags = []
    try:
        tags = [str(t) for t in list(a.get_editor_property("tags"))]
    except Exception:
        try:
            tags = [str(t) for t in list(a.tags)]
        except Exception:
            tags = []
    hit = ("HubGate" in lab) or ("GateTrigger" in lab) or ("DungeonEntrance" in lab) or ("GateInteract" in tags) or ("DungeonGate" in tags)
    if hit:
        loc = a.get_actor_location()
        found.append("%s tags=%s loc=(%.0f,%.0f,%.0f)" % (lab, tags, loc.x, loc.y, loc.z))
L("gate_count=" + str(len(found)))
for f in found:
    L(f)
L("Map_Dungeon=" + str(unreal.EditorAssetLibrary.does_asset_exist("/Game/Maps/Dungeon/Map_Dungeon")))
try:
    import shop_interact_runtime as m
    L("enter_dungeon=" + str(hasattr(m, "enter_dungeon")))
    L("DUNGEON_LEVEL=" + str(getattr(m, "DUNGEON_LEVEL", None)))
except Exception as e:
    L("runtime_err=" + str(e))
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
