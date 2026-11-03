# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\reload_skel_t400.txt"
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
import skeleton_engine_ai as s
importlib.reload(s)
s.clear_state()
src = open(s.__file__, encoding="utf-8").read()
checks = [
  "ANIM_ATK" in src and "_play_anim(enemy, ANIM_ATK" in src,
  "drop aggro" in src,
  "def _trace_clear" in src,
]
msg = "atk_back=%s wall_los=%s trace=%s HIT=%.2f\n" % (checks[0], checks[1], checks[2], s.ATTACK_HIT_DELAY)
open(OUT,"w",encoding="utf-8").write(msg)
print(msg.strip())