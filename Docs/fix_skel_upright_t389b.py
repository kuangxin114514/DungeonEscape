# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_skel_upright_t389b.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T389b: "+str(m))
    except Exception: print(m)

BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
# verify a few
for o in unreal.ObjectIterator(unreal.SkeletalMeshComponent):
    try: pn=o.get_path_name()
    except Exception: continue
    if "BP_Enemy_Skeleton" not in pn: continue
    if "CharacterMesh0" not in pn: continue
    try:
        rr=o.get_editor_property("relative_rotation")
        L("%s -> p=%.1f y=%.1f r=%.1f"%(pn.split("PersistentLevel.")[-1][:60], float(rr.pitch), float(rr.yaw), float(rr.roll)))
    except Exception as e:
        L(str(e))
try:
    unreal.EditorAssetLibrary.save_asset(BP); L("bp saved")
except Exception as e:
    L("bp save "+str(e))
try:
    unreal.EditorLevelLibrary.save_current_level(); L("level saved")
except Exception as e:
    L("lvl "+str(e))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("done")
