# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal,importlib,sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t424.txt"
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0,py)
import shop_interact_runtime as sir
importlib.reload(sir)
msg="EXIT_RANGE=%s\n"%getattr(sir,"EXIT_RANGE","?")
open(OUT,"w",encoding="utf-8").write(msg); print(msg.strip())