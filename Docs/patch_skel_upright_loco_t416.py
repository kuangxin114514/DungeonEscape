# -*- coding: utf-8 -*-
from __future__ import print_function
import io
p = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py"
raw = io.open(p, "r", encoding="utf-8").read()
old = 'ANIM_RUN = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Running_A_Rig"'
new = 'ANIM_RUN = "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Walking_A_Rig"  # upright loco (no lean run)'
if old not in raw:
    print("MISSING", "Running" in raw)
else:
    raw = raw.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(raw)
    print("switched_to_walk")
compile(io.open(p,encoding="utf-8").read(), p, "exec")
print("syntax_ok")
