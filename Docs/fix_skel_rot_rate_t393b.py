# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_skel_rot_rate_t393b.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T393b: "+str(m))
    except Exception: print(m)

# probe constructor order
for label,r in [
 ("pos(0,720,0)", unreal.Rotator(0.0,720.0,0.0)),
 ("pos(0,0,720)", unreal.Rotator(0.0,0.0,720.0)),
 ("kw yaw720", unreal.Rotator(pitch=0.0,yaw=720.0,roll=0.0)),
]:
    L("%s -> p=%.1f y=%.1f r=%.1f"%(label,float(r.pitch),float(r.yaw),float(r.roll)))

rr=unreal.Rotator(pitch=0.0, yaw=720.0, roll=0.0)
BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
cls=unreal.EditorAssetLibrary.load_blueprint_class(BP)
cdo=unreal.get_default_object(cls)
cm=cdo.get_editor_property("character_movement")
before=cm.get_editor_property("rotation_rate")
L("cdo before p=%.1f y=%.1f r=%.1f"%(float(before.pitch),float(before.yaw),float(before.roll)))
cm.set_editor_property("rotation_rate", rr)
cm.set_editor_property("orient_rotation_to_movement", True)
cm.set_editor_property("use_controller_desired_rotation", False)
cdo.set_editor_property("use_controller_rotation_yaw", False)
after=cm.get_editor_property("rotation_rate")
L("cdo after p=%.1f y=%.1f r=%.1f"%(float(after.pitch),float(after.yaw),float(after.roll)))

for o in unreal.ObjectIterator(unreal.CharacterMovementComponent):
    try: pn=o.get_path_name()
    except Exception: continue
    if "BP_Enemy_Skeleton" not in pn and "Skeleton" not in pn: continue
    if "Enemy_Skeleton" not in pn and "BP_Enemy_Skeleton" not in pn: continue
    try:
        o.set_editor_property("rotation_rate", rr)
        o.set_editor_property("orient_rotation_to_movement", True)
        o.set_editor_property("use_controller_desired_rotation", False)
        a=o.get_editor_property("rotation_rate")
        L("set %s -> p=%.1f y=%.1f r=%.1f"%(pn.split("/")[-1][:70], float(a.pitch),float(a.yaw),float(a.roll)))
    except Exception as e:
        L("err "+str(e))

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
