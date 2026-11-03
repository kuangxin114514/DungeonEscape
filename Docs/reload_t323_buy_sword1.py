# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys, traceback
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t323_buy_sword1.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T323RL: "+str(m))
    except Exception: print(m)
try:
    py = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if py not in sys.path: sys.path.insert(0, py)
    if "shop_interact_runtime" in sys.modules:
        m = importlib.reload(sys.modules["shop_interact_runtime"])
        L("reloaded")
    else:
        import shop_interact_runtime as m
        L("imported")
    body=open(m.__file__, encoding="utf-8").read()
    L("tag_T323=%s" % ("T323_BUY_SWORD1" in body))
    L("SWORD1_COST=%s" % getattr(m, "SWORD1_COST", None))
    L("SWORD1_ITEM=%s" % getattr(m, "SWORD1_ITEM", None))
    L("has_buy=%s" % hasattr(m, "buy_sword1"))
    L("has_wire=%s" % hasattr(m, "wire_weapon_shop_buttons") or hasattr(m, "_wire_weapon_shop_buttons"))
    L("has_apply=%s" % hasattr(m, "apply_equipped_sword_to_pawn"))
    mesh = unreal.load_asset(m.SWORD1_MESH)
    L("mesh_load=%s" % (mesh.get_name() if mesh else None))
    fn=getattr(m,"bootstrap",None)
    if callable(fn):
        fn(); L("bootstrap ok")
except Exception as e:
    L("ERR "+str(e))
    L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT)
