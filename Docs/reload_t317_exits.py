# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys, traceback
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t317_exits.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T317RL: "+str(m))
    except Exception: print(m)
try:
    # verify markers still ok on current map
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try: lab=a.get_actor_label() or ""
        except Exception: continue
        if "DungeonExit" in lab or "HubReturn" in lab or "ToDungeon2" in lab:
            loc=a.get_actor_location()
            tags=[str(t) for t in list(a.get_editor_property("tags") or [])]
            L("marker %s tags=%s @ (%.0f,%.0f,%.0f)" % (lab, tags, loc.x, loc.y, loc.z))
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
    L("Stairs->d2=%s" % m._is_dungeon2_exit_marker("DungeonExit_HubReturn_Stairs", ["HubReturn","DungeonExit"]))
    L("ToDungeon2->d2=%s" % m._is_dungeon2_exit_marker("DungeonExit_ToDungeon2", ["ToDungeon2","DungeonExit"]))
    L("Wide hub=%s" % m._is_hub_return_marker("DungeonExit_HubReturn_Wide", ["HubReturn","DungeonExit"]))
    fn=getattr(m,"bootstrap",None)
    if callable(fn):
        fn(); L("bootstrap ok")
except Exception as e:
    L("ERR "+str(e))
    L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT)
