# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys, traceback
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t343.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T343RL: "+str(m))
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
    L("tag_T343=%s" % ("T343_KILL_GOLD" in body))
    L("KILL_GOLD_REWARD=%s" % getattr(m, "KILL_GOLD_REWARD", None))
    L("has_add_gold=%s" % hasattr(m, "add_gold"))
    fn=getattr(m,"bootstrap",None)
    if callable(fn):
        fn(); L("bootstrap ok")
except Exception as e:
    L("ERR "+str(e))
    L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT)
