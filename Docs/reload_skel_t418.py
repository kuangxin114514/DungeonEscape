# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal,importlib,sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_skel_t418.txt"
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0,py)
import skeleton_engine_ai as s
importlib.reload(s); s.clear_state()
open(OUT,"w",encoding="utf-8").write("WINDUP=%.2f\n"%s.ATTACK_WINDUP)
print("WINDUP",s.ATTACK_WINDUP)
