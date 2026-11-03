# -*- coding: utf-8 -*-
"""T368 setup/verify: skeleton AI constants + anim assets (no Map_Hub edits)."""
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\setup_t368_skeleton_ai.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T368SETUP: "+str(m))
    except Exception: print(m)

ANIMS=[
 ("idle","/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Idle_Rig"),
 ("run","/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Running_A_Rig"),
 ("attack","/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_1H_Melee_Attack_Chop_Rig"),
]
BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
L("BP exists=%s" % unreal.EditorAssetLibrary.does_asset_exist(BP))
for kind,p in ANIMS:
    ok=unreal.EditorAssetLibrary.does_asset_exist(p)
    L("anim %s exists=%s path=%s" % (kind, ok, p))
L("Design: AGGRO=1000 LOS required (Visibility line_trace), ATTACK=180 dmg=5 cd=1.6")
L("No Map_Hub building edits.")
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
