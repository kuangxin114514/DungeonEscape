# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, traceback, sys, importlib
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t332_buy.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T332F: "+str(m))
    except Exception: print(m)
try:
    py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if py not in sys.path: sys.path.insert(0,py)
    m=importlib.reload(sys.modules["shop_interact_runtime"]) if "shop_interact_runtime" in sys.modules else __import__("shop_interact_runtime")
    try: m.bootstrap()
    except Exception as e: L("boot "+str(e))
    world=m._pie_world(); L("world=%s"%world)
    if not world:
        L("no pie"); 
    else:
        ok=m.buy_sword1(world); L("buy=%s meta=%s"%(ok,dict(m._PLAYER_META)))
        pc=unreal.GameplayStatics.get_player_controller(world,0)
        pawn=pc.get_controlled_pawn() if pc else None
        L("pawn=%s"%(pawn.get_class().get_path_name() if pawn else None))
        for c in (pawn.get_components_by_class(unreal.StaticMeshComponent.static_class()) if pawn else []) or []:
            sm=c.get_editor_property("static_mesh")
            L("SMC %s %s scale=%s"%(c.get_name(), sm.get_name() if sm else None, c.get_editor_property("relative_scale3d")))
except Exception as e:
    L("ERR "+str(e)); L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
