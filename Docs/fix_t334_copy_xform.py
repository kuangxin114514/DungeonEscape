# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, traceback
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t334_copy_xform.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T334X: "+str(m))
    except Exception: print(m)
try:
    src=None; dst=None
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        pn=o.get_path_name()
        if "GEN_VARIABLE" not in pn:
            continue
        if "BP_KayKitKnight_Sword1" in pn:
            if o.get_name().startswith("StaticMesh_GEN") and "StaticMesh1" not in o.get_name():
                dst=o
        elif "BP_KayKitKnight." in pn and "Sword1" not in pn:
            sm=o.get_editor_property("static_mesh")
            if sm and sm.get_name()=="SM_KayKitSword":
                src=o
    L("src=%s"%src); L("dst=%s"%dst)
    if not (src and dst):
        raise RuntimeError("missing comps")
    loc=src.get_editor_property("relative_location")
    rot=src.get_editor_property("relative_rotation")
    L("src loc=%s rot=%s"%(loc,rot))
    mesh=unreal.load_asset("/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword_2H")
    dst.set_editor_property("static_mesh", mesh)
    dst.set_editor_property("relative_location", loc)
    dst.set_editor_property("relative_rotation", rot)
    # 2H slightly smaller than 1H
    dst.set_editor_property("relative_scale3d", unreal.Vector(0.45,0.45,0.45))
    L("dst after mesh=%s loc=%s rot=%s scale=%s"%(
        dst.get_editor_property("static_mesh").get_name(),
        dst.get_editor_property("relative_location"),
        dst.get_editor_property("relative_rotation"),
        dst.get_editor_property("relative_scale3d")))
    # also update non-GEN templates if any named StaticMesh under Sword1 package
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        pn=o.get_path_name()
        if "BP_KayKitKnight_Sword1" not in pn: continue
        if "StaticMesh1" in o.get_name(): continue
        sm=o.get_editor_property("static_mesh")
        if sm and "Sword" in sm.get_name():
            o.set_editor_property("static_mesh", mesh)
            o.set_editor_property("relative_location", loc)
            o.set_editor_property("relative_rotation", rot)
            o.set_editor_property("relative_scale3d", unreal.Vector(0.45,0.45,0.45))
            L("updated %s"%o.get_path_name())
    bp=unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1")
    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    try: unreal.EditorAssetLibrary.save_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight_Sword1")
    except Exception as e: L("save "+str(e))
    L("DONE")
except Exception as e:
    L("ERR "+str(e)); L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
