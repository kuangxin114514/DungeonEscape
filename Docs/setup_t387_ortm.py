# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\setup_t387_ortm.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T387: "+str(m))
    except Exception: print(m)

BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
bp=unreal.load_asset(BP)
L("bp=%s"%bp)

# Stamp CharacterMovement on SCS / GEN / CDO-ish objects
n_ortm=0
for o in unreal.ObjectIterator(unreal.CharacterMovementComponent):
    try: pn=o.get_path_name()
    except Exception: continue
    if "BP_Enemy_Skeleton" not in pn: continue
    try:
        o.set_editor_property("orient_rotation_to_movement", True)
        o.set_editor_property("use_controller_desired_rotation", False)
        o.set_editor_property("max_walk_speed", 190.0)
        try:
            o.set_editor_property("rotation_rate", unreal.Rotator(0.0, 720.0, 0.0))
        except Exception:
            pass
        n_ortm+=1
        L("CMC OK %s"%pn.split(".")[-1])
    except Exception as e:
        L("CMC fail "+str(e))

for o in unreal.ObjectIterator(unreal.SkeletalMeshComponent):
    try: pn=o.get_path_name()
    except Exception: continue
    if "BP_Enemy_Skeleton" not in pn: continue
    if "GEN_VARIABLE" not in pn and "Default__" not in pn and "SCS" not in pn:
        # still try
        pass
    try:
        o.set_editor_property("anim_class", None)
    except Exception:
        pass
    try:
        o.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    except Exception:
        pass
    try:
        # Keep authored KayKit mesh yaw so ORTM faces correctly
        o.set_editor_property("relative_rotation", unreal.Rotator(0.0, 270.0, 0.0))
        L("mesh yaw 270 %s"%o.get_name())
    except Exception as e:
        L("mesh "+str(e))
    try:
        o.set_simulate_physics(False)
    except Exception:
        pass

# Character flags on default objects named BP_Enemy_Skeleton
for o in unreal.ObjectIterator(unreal.Character):
    try: pn=o.get_path_name()
    except Exception: continue
    if "BP_Enemy_Skeleton" not in pn: continue
    for prop,val in (
        ("use_controller_rotation_yaw", False),
        ("use_controller_rotation_pitch", False),
        ("use_controller_rotation_roll", False),
    ):
        try:
            o.set_editor_property(prop, val)
        except Exception:
            pass

try:
    unreal.EditorAssetLibrary.save_asset(BP); L("saved bp")
except Exception as e:
    L("save "+str(e))

# Reload python modules (no face hacks)
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0, py)
import skeleton_engine_ai as m
import shop_interact_runtime as sir
m=importlib.reload(m)
sir=importlib.reload(sir)
try: m.clear_state()
except Exception: pass
L("has_face=%s ortm_in_ensure=%s"%(hasattr(m,"_face_player"), "orient_rotation_to_movement" in open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\skeleton_engine_ai.py",encoding="utf-8").read()))
if callable(getattr(sir,"bootstrap",None)):
    sir.bootstrap(); L("bootstrap ok")
L("n_ortm=%d"%n_ortm)
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
