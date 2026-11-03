# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_d2_stairs_t422.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)
world=unreal.EditorLevelLibrary.get_editor_world()
L("world="+str(world.get_path_name() if world else None))
# list actors with stair/Stairs/ramp in name, and PlayerStarts
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    try:
        n=a.get_name() or ""
        lab=a.get_actor_label() if hasattr(a,"get_actor_label") else n
    except Exception:
        continue
    low=(n+" "+str(lab)).lower()
    if ("stair" in low) or ("stairs" in low) or ("playerstart" in low) or ("dungeonexit" in low) or ("hubreturn" in low) or ("todungeon" in low):
        loc=a.get_actor_location()
        L("%s | %s | (%.0f,%.0f,%.0f)"%(n,lab,float(loc.x),float(loc.y),float(loc.z)))
# also dump actors near expected stair area ~ look at all SM near x 0-2000 y 500-2000 with Z span
L("--- nearby static meshes with large Z or stairs mesh path ---")
count=0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    try:
        loc=a.get_actor_location()
        if not (400<=float(loc.x)<=1400 and 700<=float(loc.y)<=1600):
            continue
        n=a.get_name()
        cls=a.get_class().get_name() if a.get_class() else ""
        path=""
        try:
            if isinstance(a, unreal.StaticMeshActor):
                sm=a.static_mesh_component.static_mesh
                path=sm.get_path_name() if sm else ""
        except Exception:
            pass
        if ("stair" in (n+path).lower()) or ("Stairs" in path) or ("step" in (n+path).lower()):
            L("NEAR %s %s (%.0f,%.0f,%.0f) %s"%(cls,n,float(loc.x),float(loc.y),float(loc.z),path))
            count+=1
    except Exception:
        pass
L("near_count=%d"%count)
open(OUT,"w",encoding="utf-8").write("\n".join(lines))
