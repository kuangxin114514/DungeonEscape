# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_skel_atk_t397.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T397: "+str(m))
    except Exception: print(m)
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
import skeleton_engine_ai as s
importlib.reload(s)
L("attack_until=%s anim_len=%s"%(hasattr(s,"_anim_length"), "attack_until" in open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py",encoding="utf-8").read()))
try:
    L("atk_len=%.2f"%s._anim_length(s.ANIM_ATK))
except Exception as e:
    L("len "+str(e))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("done")
