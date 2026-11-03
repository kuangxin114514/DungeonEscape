# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_d1_skel_t395.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T395e: "+str(m))
    except Exception: print(m)

map_path="/Game/Maps/Dungeon/Map_Dungeon1"
try:
    unreal.EditorLoadingAndSavingUtils.load_map(map_path)
except Exception as e:
    L("load "+str(e))
world=unreal.EditorLevelLibrary.get_editor_world()
L("world=%s"%world)

for a in unreal.EditorLevelLibrary.get_all_level_actors():
    try:
        n=a.get_name(); cn=a.get_class().get_name(); pn=a.get_path_name()
    except Exception: continue
    if "Skeleton" not in n and "Skeleton" not in cn: continue
    L("ACTOR %s class=%s"%(n,cn))
    L("  path=%s"%pn)
    try:
        mov=a.get_editor_property("character_movement")
        before=mov.get_editor_property("rotation_rate")
        L("  before rate p=%.1f y=%.1f r=%.1f"%(float(before.pitch),float(before.yaw),float(before.roll)))
        mov.set_editor_property("rotation_rate", unreal.Rotator(pitch=0.0,yaw=720.0,roll=0.0))
        mov.set_editor_property("orient_rotation_to_movement", True)
        mov.set_editor_property("use_controller_desired_rotation", False)
        a.set_editor_property("use_controller_rotation_yaw", False)
        after=mov.get_editor_property("rotation_rate")
        L("  after rate p=%.1f y=%.1f r=%.1f ortm=%s"%(float(after.pitch),float(after.yaw),float(after.roll), mov.get_editor_property("orient_rotation_to_movement")))
        mesh=a.get_editor_property("mesh")
        mrr=mesh.get_editor_property("relative_rotation")
        L("  mesh rel (unchanged) p=%.1f y=%.1f r=%.1f"%(float(mrr.pitch),float(mrr.yaw),float(mrr.roll)))
        try:
            a.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD)
        except Exception as e:
            L("  possess "+str(e))
        # also try set on the archetype via modify
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(a)
        except Exception:
            pass
    except Exception as e:
        L("  ERR "+str(e))

# Fix CDO again
BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
cls=unreal.EditorAssetLibrary.load_blueprint_class(BP)
cdo=unreal.get_default_object(cls)
cm=cdo.get_editor_property("character_movement")
cm.set_editor_property("rotation_rate", unreal.Rotator(pitch=0.0,yaw=720.0,roll=0.0))
cm.set_editor_property("orient_rotation_to_movement", True)
rr=cm.get_editor_property("rotation_rate")
L("CDO rate p=%.1f y=%.1f"% (float(rr.pitch),float(rr.yaw)))
unreal.EditorAssetLibrary.save_asset(BP)

# Mark package dirty and save level
try:
    unreal.EditorLevelLibrary.save_current_level(); L("level saved")
except Exception as e:
    L("lvl "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("done")
