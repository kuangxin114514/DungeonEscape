# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys, os
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\apply_t317_exits.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T317: "+str(m))
    except Exception: print(m)

# 1) Retag stairs exit on Map_Dungeon1
MAP="/Game/Maps/Dungeon/Map_Dungeon1"
unreal.EditorLoadingAndSavingUtils.load_map(MAP)
found=False
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    try: lab=a.get_actor_label() or ""
    except Exception: continue
    if lab == "DungeonExit_HubReturn_Stairs" or ("Stairs" in lab and "DungeonExit" in lab):
        try:
            a.set_actor_label("DungeonExit_ToDungeon2")
        except Exception as e:
            L("label fail "+str(e))
        try:
            a.set_editor_property("tags", ["ToDungeon2", "DungeonExit"])
        except Exception as e:
            L("tags fail "+str(e))
        loc=a.get_actor_location()
        L("retagged %s -> DungeonExit_ToDungeon2 @ (%.0f,%.0f,%.0f)" % (lab, loc.x, loc.y, loc.z))
        found=True
    elif "DungeonExit" in lab or "HubReturn" in lab:
        loc=a.get_actor_location()
        tags=list(a.get_editor_property("tags") or [])
        L("keep %s tags=%s @ (%.0f,%.0f,%.0f)" % (lab, [str(t) for t in tags], loc.x, loc.y, loc.z))
if not found:
    L("WARN stairs marker not found")
unreal.EditorLevelLibrary.save_current_level()
try: unreal.EditorAssetLibrary.save_asset(MAP)
except Exception as e: L("save "+str(e))

# 2) Hot reload runtime
py = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
if "shop_interact_runtime" in sys.modules:
    m = importlib.reload(sys.modules["shop_interact_runtime"])
    L("reloaded")
else:
    import shop_interact_runtime as m
    L("imported")
body=open(m.__file__, encoding="utf-8").read()
L("tag_T317=%s" % ("T317_SPLIT_EXITS" in body))
L("has_is_d2=%s" % hasattr(m, "_is_dungeon2_exit_marker"))
L("has_is_hub=%s" % hasattr(m, "_is_hub_return_marker"))
# quick unit of helpers
L("Stairs->d2=%s" % m._is_dungeon2_exit_marker("DungeonExit_HubReturn_Stairs", ["HubReturn","DungeonExit"]))
L("ToDungeon2->d2=%s" % m._is_dungeon2_exit_marker("DungeonExit_ToDungeon2", ["ToDungeon2","DungeonExit"]))
L("Wide->hub=%s hubmark=%s" % (
    (not m._is_dungeon2_exit_marker("DungeonExit_HubReturn_Wide", ["HubReturn","DungeonExit"])),
    m._is_hub_return_marker("DungeonExit_HubReturn_Wide", ["HubReturn","DungeonExit"]),
))
fn=getattr(m,"bootstrap",None)
if callable(fn):
    try: fn(); L("bootstrap ok")
    except Exception as e: L("bootstrap "+str(e))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT)
