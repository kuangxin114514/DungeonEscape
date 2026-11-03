# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal,importlib,sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t425.txt"
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0,py)
import shop_interact_runtime as sir
importlib.reload(sir)
msg=[]
msg.append("PREV_default_check gen reload")
msg.append("has_hub=%s"%hasattr(sir,"_world_is_hub"))
# inspect source of reset
import inspect
src=inspect.getsource(sir._reset_ui_after_travel)
msg.append("prev_e_true=%s"%("_PREV_E[0] = True" in src))
worlds=unreal.EditorLevelLibrary.get_pie_worlds(False)
if worlds:
  pw=worlds[0]
  msg.append("level=%s"%unreal.GameplayStatics.get_current_level_name(pw,True))
  msg.append("is_hub=%s is_d=%s is_d2=%s"%(sir._world_is_hub(pw), sir._world_is_dungeon(pw), sir._world_is_dungeon2(pw)))
open(OUT,"w",encoding="utf-8").write("\n".join(msg))
print("\n".join(msg))