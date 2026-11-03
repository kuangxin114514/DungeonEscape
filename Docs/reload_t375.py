# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t375.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T375RL: "+str(m))
    except Exception: print(m)
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
if "shop_interact_runtime" in sys.modules:
    m=importlib.reload(sys.modules["shop_interact_runtime"]); L("reloaded")
else:
    import shop_interact_runtime as m; L("imported")
try: m._clear_skeleton_ai()
except Exception: pass
try: m._SKELETON_ANIM_CACHE.clear()
except Exception: pass
L("face=%s phys=%s" % (hasattr(m,"_skeleton_face_target"), hasattr(m,"_skeleton_disable_physics_flip")))
fn=getattr(m,"bootstrap",None)
if callable(fn): fn(); L("bootstrap ok")
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
