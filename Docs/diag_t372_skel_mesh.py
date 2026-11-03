# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_t372_skel_mesh.txt"
lines=[]
def L(m):
    lines.append(str(m)); 
    try: unreal.log("T372D: "+str(m))
    except Exception: print(m)
# load BP CDO / components
bp=unreal.load_asset("/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton")
L("bp=%s"%bp)
for o in unreal.ObjectIterator(unreal.SkeletalMeshComponent):
    try: pn=o.get_path_name()
    except Exception: continue
    if "BP_Enemy_Skeleton" not in pn: continue
    if "GEN_VARIABLE" not in pn and "Default__" not in pn: continue
    try:
        rel=o.get_editor_property("relative_rotation")
        L("mesh %s rel_rot=%s"%(o.get_name(), rel))
    except Exception as e: L("rel "+str(e))
    for prop in ("absolute_rotation","absolute_location","visibility_based_anim_tick_option"):
        try: L("  %s=%s"%(prop,o.get_editor_property(prop)))
        except Exception: pass
# also list anim asset rate scale if any
for p in [
"/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Running_A_Rig",
"/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Walking_A_Rig",
]:
    a=unreal.load_asset(p)
    L("anim %s = %s"%(p.split("/")[-1], a))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
