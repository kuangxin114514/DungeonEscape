# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys, os
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\apply_skel_focus_t395.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T395f: "+str(m))
    except Exception: print(m)
try:
    BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
    cls=unreal.EditorAssetLibrary.load_blueprint_class(BP)
    cdo=unreal.get_default_object(cls)
    cm=cdo.get_editor_property("character_movement")
    cm.set_editor_property("orient_rotation_to_movement", False)
    cm.set_editor_property("use_controller_desired_rotation", True)
    cm.set_editor_property("rotation_rate", unreal.Rotator(pitch=0.0,yaw=720.0,roll=0.0))
    cdo.set_editor_property("use_controller_rotation_yaw", False)
    L("CDO ortm=%s ucdr=%s rate_y=%.1f"%(cm.get_editor_property("orient_rotation_to_movement"), cm.get_editor_property("use_controller_desired_rotation"), float(cm.get_editor_property("rotation_rate").yaw)))
    mrr=cdo.get_editor_property("mesh").get_editor_property("relative_rotation")
    L("mesh rel unchanged y=%.1f"%float(mrr.yaw))
    unreal.EditorAssetLibrary.save_asset(BP); L("bp saved")
    for o in unreal.ObjectIterator(unreal.CharacterMovementComponent):
        try: pn=o.get_path_name()
        except Exception: continue
        if "Enemy_Skeleton" not in pn and "Preview_Skeleton" not in pn: continue
        try:
            o.set_editor_property("orient_rotation_to_movement", False)
            o.set_editor_property("use_controller_desired_rotation", True)
            o.set_editor_property("rotation_rate", unreal.Rotator(pitch=0.0,yaw=720.0,roll=0.0))
            L("cm ok")
        except Exception as e:
            L("cm err "+str(e))
    py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if py not in sys.path: sys.path.insert(0, py)
    if "skeleton_engine_ai" in sys.modules:
        importlib.reload(sys.modules["skeleton_engine_ai"]); L("reloaded skai")
    else:
        import skeleton_engine_ai; L("imported skai")
except Exception as e:
    import traceback
    L("FAIL "+str(e))
    L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("wrote")
