# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t384.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T384RL: "+str(m))
    except Exception: print(m)
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
for name in ("skeleton_engine_ai","shop_interact_runtime"):
    if name in sys.modules:
        importlib.reload(sys.modules[name]); L("reloaded "+name)
    else:
        __import__(name); L("imported "+name)
m=sys.modules["skeleton_engine_ai"]
try: m.clear_state()
except Exception: pass
L("FACE=%s has_face=%s"%(getattr(m,"FACE_YAW_OFFSET",None), hasattr(m,"_face_player")))
sir=sys.modules.get("shop_interact_runtime")
if sir and callable(getattr(sir,"bootstrap",None)):
    sir.bootstrap(); L("bootstrap ok")
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
