# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\apply_skel_focus_t395b.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T395g: "+str(m))
    except Exception: print(m)

BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
asset=None
try:
    asset=unreal.EditorAssetLibrary.load_asset(BP)
    L("asset=%s"%asset)
except Exception as e:
    L("load_asset "+str(e))
cls=None
try:
    cls=unreal.EditorAssetLibrary.load_blueprint_class(BP)
    L("cls=%s"%cls)
except Exception as e:
    L("load_bp_class "+str(e))
cdo=None
if cls:
    try: cdo=unreal.get_default_object(cls); L("cdo=%s"%cdo)
    except Exception as e: L("cdo "+str(e))
if cdo is None and asset is not None:
    try:
        # Generated class
        gc=asset.generated_class()
        L("generated=%s"%gc)
        cdo=unreal.get_default_object(gc)
        L("cdo2=%s"%cdo)
    except Exception as e:
        L("gen "+str(e))

if cdo is not None:
    try:
        cm=cdo.get_editor_property("character_movement")
        L("cm=%s"%cm)
        if cm:
            cm.set_editor_property("orient_rotation_to_movement", False)
            cm.set_editor_property("use_controller_desired_rotation", True)
            cm.set_editor_property("rotation_rate", unreal.Rotator(pitch=0.0,yaw=720.0,roll=0.0))
            L("ortm=%s ucdr=%s y=%.1f"%(cm.get_editor_property("orient_rotation_to_movement"), cm.get_editor_property("use_controller_desired_rotation"), float(cm.get_editor_property("rotation_rate").yaw)))
        cdo.set_editor_property("use_controller_rotation_yaw", False)
    except Exception as e:
        L("set cdo "+str(e))
    try:
        unreal.EditorAssetLibrary.save_asset(BP); L("bp saved")
    except Exception as e:
        L("save "+str(e))
else:
    L("NO_CDO")

n=0
for o in unreal.ObjectIterator(unreal.CharacterMovementComponent):
    try: pn=o.get_path_name()
    except Exception: continue
    if "Skeleton" not in pn: continue
    if "Enemy_Skeleton" not in pn and "Preview_Skeleton" not in pn: continue
    try:
        o.set_editor_property("orient_rotation_to_movement", False)
        o.set_editor_property("use_controller_desired_rotation", True)
        o.set_editor_property("rotation_rate", unreal.Rotator(pitch=0.0,yaw=720.0,roll=0.0))
        n+=1
    except Exception as e:
        L("cm "+str(e))
L("instances=%d"%n)

py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
try:
    if "skeleton_engine_ai" in sys.modules:
        importlib.reload(sys.modules["skeleton_engine_ai"]); L("reloaded")
    else:
        import skeleton_engine_ai as s; L("imported focus=%s"%hasattr(s,"_set_focus_player"))
except Exception as e:
    L("py "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("done")
