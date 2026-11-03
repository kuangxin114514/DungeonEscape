# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, traceback, sys, importlib
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_t332_buy.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T332: "+str(m))
    except Exception: print(m)
try:
    py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if py not in sys.path: sys.path.insert(0,py)
    m=importlib.reload(sys.modules["shop_interact_runtime"]) if "shop_interact_runtime" in sys.modules else __import__("shop_interact_runtime")
    L("meta=%s"%dict(m._PLAYER_META))
    L("open_widget=%s"%m._OPEN_WIDGET[0])
    L("btn=%s"%m._SHOP_BTN_SWORD1[0])
    L("wired=%s"%m._SHOP_WIRED_ID[0])
    world=m._pie_world(); L("world=%s"%world)
    if world:
        # try buy directly
        try:
            ok=m.buy_sword1(world); L("buy_direct=%s meta=%s"% (ok, dict(m._PLAYER_META)))
        except Exception as e:
            L("buy_direct ERR "+str(e)); L(traceback.format_exc())
        pc=unreal.GameplayStatics.get_player_controller(world,0)
        pawn=pc.get_controlled_pawn() if pc else None
        if pawn:
            L("pawn=%s"%pawn.get_class().get_path_name())
            for c in pawn.get_components_by_class(unreal.StaticMeshComponent.static_class()) or []:
                sm=c.get_editor_property("static_mesh")
                L("SMC %s %s"%(c.get_name(), sm.get_name() if sm else None))
    # syntax check force/deferred present
    L("has_force=%s"%hasattr(m,"_force_sword1_mesh_on_pawn"))
    L("has_ensure=%s"%hasattr(m,"ensure_equipped_pawn_class"))
except Exception as e:
    L("ERR "+str(e)); L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
