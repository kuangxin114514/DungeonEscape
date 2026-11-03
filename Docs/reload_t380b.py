# -*- coding: utf-8 -*-
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_t380b.txt"
lines=[]
def L(m):
    lines.append(str(m))
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
import skeleton_engine_ai
importlib.reload(skeleton_engine_ai)
import shop_interact_runtime
importlib.reload(shop_interact_runtime)
shop_interact_runtime.bootstrap()
m=shop_interact_runtime
L("update_skeleton_ai=%s"%hasattr(m,"update_skeleton_ai"))
L("_clear_skeleton_ai=%s"%hasattr(m,"_clear_skeleton_ai"))
L("_damage_player=%s"%hasattr(m,"_damage_player"))
L("tick_wired=%s"%("tick_skeleton_engine_ai" in open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py",encoding="utf-8").read()))
L("AGGRO=%s SPEED=%s DMG=%s"%(skeleton_engine_ai.AGGRO_RANGE, skeleton_engine_ai.CHASE_SPEED, skeleton_engine_ai.ATTACK_DAMAGE))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
