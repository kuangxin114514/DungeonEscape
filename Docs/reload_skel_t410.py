# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_skel_t410.txt"
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
import skeleton_engine_ai as s
importlib.reload(s)
s.clear_state()
src=open(s.__file__,encoding="utf-8").read()
msg="atk_reset=%s\n"%('st["flinch_left"] = 2  # attack done' in src)
open(OUT,"w",encoding="utf-8").write(msg); print(msg.strip())
