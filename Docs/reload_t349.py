# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t349.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T349RL: "+str(m))
    except Exception: print(m)
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
if "shop_interact_runtime" in sys.modules:
    m=importlib.reload(sys.modules["shop_interact_runtime"]); L("reloaded")
else:
    import shop_interact_runtime as m; L("imported")
try: m._SWORD_TMPL_CACHE.clear(); m._SWORD_TMPL_FAIL_LOGGED.clear()
except Exception: pass
L("SHIELD1_ITEM=%s" % m.SHIELD1_ITEM)
L("SHIELD1_MESH=%s" % m.SHIELD1_MESH)
mesh=unreal.load_asset(m.SHIELD1_MESH)
L("mesh=%s" % (mesh.get_name() if mesh else None))
tmpl=m._read_bp_shield_template("BP_KayKitKnight_Shield1")
if tmpl:
    sm,loc,rot,sc=tmpl
    L("tmpl mesh=%s scale=%s" % (sm.get_name() if sm else None, sc))
else:
    L("tmpl=None")
fn=getattr(m,"bootstrap",None)
if callable(fn): fn(); L("bootstrap ok")
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
