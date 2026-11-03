# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_skel_rot_rate_t393.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T393: "+str(m))
    except Exception: print(m)

BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
cls=unreal.EditorAssetLibrary.load_blueprint_class(BP)
cdo=unreal.get_default_object(cls)
cm=cdo.get_editor_property("character_movement")
before=cm.get_editor_property("rotation_rate")
L("before p=%.1f y=%.1f r=%.1f"%(float(before.pitch),float(before.yaw),float(before.roll)))
# Rotator(pitch, yaw, roll) — yaw must be the turn speed
rr=unreal.Rotator(0.0, 720.0, 0.0)
cm.set_editor_property("rotation_rate", rr)
cm.set_editor_property("orient_rotation_to_movement", True)
cm.set_editor_property("use_controller_desired_rotation", False)
cdo.set_editor_property("use_controller_rotation_yaw", False)
after=cm.get_editor_property("rotation_rate")
L("after p=%.1f y=%.1f r=%.1f"%(float(after.pitch),float(after.yaw),float(after.roll)))
L("ortm=%s"%cm.get_editor_property("orient_rotation_to_movement"))

# fix placed / live instances too
n=0
for a in unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(), unreal.Character):
    try:
        if "Skeleton" not in a.get_class().get_name(): continue
    except Exception: continue
    try:
        mov=a.get_editor_property("character_movement")
        mov.set_editor_property("rotation_rate", unreal.Rotator(0.0, 720.0, 0.0))
        mov.set_editor_property("orient_rotation_to_movement", True)
        mov.set_editor_property("use_controller_desired_rotation", False)
        a.set_editor_property("use_controller_rotation_yaw", False)
        n+=1
        L("fixed actor "+a.get_name())
    except Exception as e:
        L("actor err "+str(e))
L("actors_fixed=%d"%n)

# also patch via ObjectIterator on CharacterMovement belonging to skeletons
for o in unreal.ObjectIterator(unreal.CharacterMovementComponent):
    try: pn=o.get_path_name()
    except Exception: continue
    if "BP_Enemy_Skeleton" not in pn: continue
    try:
        o.set_editor_property("rotation_rate", unreal.Rotator(0.0, 720.0, 0.0))
        o.set_editor_property("orient_rotation_to_movement", True)
        o.set_editor_property("use_controller_desired_rotation", False)
        L("cm path ok "+pn.split("PersistentLevel.")[-1][:80])
    except Exception as e:
        L("cm path err "+str(e))

try:
    unreal.BlueprintEditorLibrary.compile_blueprint(unreal.EditorAssetLibrary.load_asset(BP))
    L("compiled")
except Exception as e:
    L("compile "+str(e))
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
