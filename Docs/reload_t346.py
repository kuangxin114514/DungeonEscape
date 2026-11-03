# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys, traceback
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t346.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T346RL: "+str(m))
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
    L("tag=%s" % ("T346_SHIELD1" in body))
    L("SHIELD1_ITEM=%s COST=%s" % (getattr(m,"SHIELD1_ITEM",None), getattr(m,"SHIELD1_COST",None)))
    try: m._SWORD_TMPL_CACHE.clear()
    except Exception: pass
    tmpl=m._read_bp_shield_template("BP_KayKitKnight_Shield1")
    if tmpl:
        sm,loc,rot,sc=tmpl
        L("shield1 mesh=%s scale=%s" % (sm.get_name() if sm else None, sc))
    else:
        L("shield1 tmpl=None")
    tmpl0=m._read_bp_shield_template("BP_KayKitKnight")
    if tmpl0:
        sm,loc,rot,sc=tmpl0
        L("default shield mesh=%s" % (sm.get_name() if sm else None))
    else:
        L("default shield tmpl=None")
    mesh=unreal.load_asset(m.SHIELD1_MESH)
    L("mesh_asset=%s" % (mesh.get_name() if mesh else None))
    abp=unreal.load_asset("/Game/UI/Shop/WBP_Shop_Armor")
    L("armor_wbp=%s" % (abp.get_name() if abp else None))
    fn=getattr(m,"bootstrap",None)
    if callable(fn):
        fn(); L("bootstrap ok")
except Exception as e:
    L("ERR "+str(e)); L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT)
