# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys, traceback
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t345.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T345RL: "+str(m))
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
    L("tag_T345=%s" % ("T345_LOAD_BP_TMPL" in body))
    L("has_force_load=%s" % hasattr(m, "_bp_asset_path_for_leaf"))
    # clear cache and try read sword1 template
    try:
        m._SWORD_TMPL_CACHE.clear()
    except Exception:
        pass
    tmpl = m._read_bp_sword_template("BP_KayKitKnight_Sword1", prefer_mesh_substr="Sword")
    if tmpl:
        sm, loc, rot, sc = tmpl
        L("sword1_tmpl mesh=%s loc=%s rot=%s scale=%s" % (sm.get_name() if sm else None, loc, rot, sc))
    else:
        L("sword1_tmpl=None")
    tmpl0 = m._read_bp_sword_template("BP_KayKitKnight", prefer_mesh_substr="SM_KayKitSword")
    if tmpl0:
        sm, loc, rot, sc = tmpl0
        L("default_tmpl mesh=%s" % (sm.get_name() if sm else None))
    else:
        L("default_tmpl=None")
    fn=getattr(m,"bootstrap",None)
    if callable(fn):
        fn(); L("bootstrap ok")
except Exception as e:
    L("ERR "+str(e))
    L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT)
