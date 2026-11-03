# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\check_skel_face_t392.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T392: "+str(m))
    except Exception: print(m)

BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
cls=unreal.EditorAssetLibrary.load_blueprint_class(BP)
cdo=unreal.get_default_object(cls) if cls else None
L("cdo=%s"%cdo)
if cdo:
    for prop in ["use_controller_rotation_yaw","use_controller_rotation_pitch","use_controller_rotation_roll"]:
        try: L("%s=%s"%(prop,cdo.get_editor_property(prop)))
        except Exception as e: L("%s err %s"%(prop,e))
    try:
        cm=cdo.get_editor_property("character_movement")
        L("cm=%s"%cm)
        for prop in ["orient_rotation_to_movement","use_controller_desired_rotation","rotation_rate","b_orient_rotation_to_movement"]:
            try: L("cm.%s=%s"%(prop,cm.get_editor_property(prop)))
            except Exception as e: L("cm.%s err %s"%(prop,e))
    except Exception as e:
        L("cm err "+str(e))
    try:
        mesh=cdo.get_editor_property("mesh")
        L("mesh=%s"%mesh)
        rr=mesh.get_editor_property("relative_rotation")
        L("mesh.rel_rot p=%.1f y=%.1f r=%.1f"%(float(rr.pitch),float(rr.yaw),float(rr.roll)))
        try:
            sm=mesh.get_editor_property("skeletal_mesh")
            L("skeletal_mesh=%s"%sm)
        except Exception as e:
            L("sm err "+str(e))
    except Exception as e:
        L("mesh err "+str(e))

# also sample placed actors + velocity facing if PIE
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    try: n=a.get_name()
    except Exception: continue
    if "BP_Enemy_Skeleton" not in n: continue
    try:
        r=a.get_actor_rotation()
        L("actor %s rot p=%.1f y=%.1f r=%.1f"%(n,float(r.pitch),float(r.yaw),float(r.roll)))
        mesh=a.get_component_by_class(unreal.SkeletalMeshComponent)
        if mesh:
            rr=mesh.get_editor_property("relative_rotation")
            L("  mesh rel p=%.1f y=%.1f r=%.1f"%(float(rr.pitch),float(rr.yaw),float(rr.roll)))
            try:
                fw=a.get_actor_forward_vector()
                L("  forward x=%.2f y=%.2f z=%.2f"%(float(fw.x),float(fw.y),float(fw.z)))
            except Exception: pass
    except Exception as e:
        L("%s err %s"%(n,e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("wrote",OUT)
