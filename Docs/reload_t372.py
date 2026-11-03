# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t372.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T372RL: "+str(m))
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
L("YAW_OFF=%s MESH_YAW=%s WINDUP=%s SPEED=%s AGGRO=%s" % (
    m.SKELETON_FACE_YAW_OFFSET, m.SKELETON_MESH_REL_YAW, m.SKELETON_ATTACK_WINDUP,
    m.SKELETON_CHASE_SPEED, m.SKELETON_AGGRO_RANGE))
run=m._load_skeleton_anim("run"); L("run=%s"%(run.get_name() if run else None))
fn=getattr(m,"bootstrap",None)
if callable(fn): fn(); L("bootstrap ok")
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
