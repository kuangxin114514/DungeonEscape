# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_skel_t405.txt"
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
import skeleton_engine_ai as s
import shop_interact_runtime as sir
importlib.reload(s)
importlib.reload(sir)
s.clear_state()
ok = hasattr(s, "notify_hit") and "notify_hit" in open(sir.__file__, encoding="utf-8").read()
msg = "hit_react ok notify=%s hook=%s ANIM_HIT=%s\n" % (hasattr(s,"notify_hit"), ok, getattr(s,"ANIM_HIT","?"))
open(OUT,"w",encoding="utf-8").write(msg)
print(msg.strip())
