# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal,importlib,sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t422.txt"
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0,py)
import shop_interact_runtime as sir
importlib.reload(sir)
msg="D3=%s enter3=%s\n"%(getattr(sir,"DUNGEON3_LEVEL","?"), hasattr(sir,"enter_dungeon3"))
open(OUT,"w",encoding="utf-8").write(msg); print(msg.strip())
