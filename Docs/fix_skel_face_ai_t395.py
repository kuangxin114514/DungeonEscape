# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_skel_face_ai_t395.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T395d: "+str(m))
    except Exception: print(m)

# Load dungeon maps and inspect/fix instance movement on skeletons
for map_path in ["/Game/Maps/Dungeon/Map_Dungeon1","/Game/Maps/Dungeon/Map_Dungeon2"]:
    try:
        unreal.EditorLoadingAndSavingUtils.load_map(map_path)
        L("loaded "+map_path)
    except Exception as e:
        try:
            unreal.EditorLevelLibrary.load_level(map_path)
            L("load_level "+map_path)
        except Exception as e2:
            L("load fail %s %s %s"%(map_path,e,e2)); continue
    world=unreal.EditorLevelLibrary.get_editor_world()
    L("world=%s"%world)
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try: n=a.get_name(); cn=a.get_class().get_name()
        except Exception: continue
        if "Skeleton" not in cn and "Skeleton" not in n: continue
        try:
            mov=a.get_editor_property("character_movement")
            rr=mov.get_editor_property("rotation_rate")
            ortm=mov.get_editor_property("orient_rotation_to_movement")
            ucry=a.get_editor_property("use_controller_rotation_yaw")
            mesh=a.get_editor_property("mesh")
            mrr=mesh.get_editor_property("relative_rotation")
            L("%s rate p=%.1f y=%.1f ortm=%s ucry=%s meshY=%.1f"%(n,float(rr.pitch),float(rr.yaw),ortm,ucry,float(mrr.yaw)))
            # ensure rate without touching mesh
            mov.set_editor_property("rotation_rate", unreal.Rotator(pitch=0.0,yaw=720.0,roll=0.0))
            mov.set_editor_property("orient_rotation_to_movement", True)
            mov.set_editor_property("use_controller_desired_rotation", False)
            a.set_editor_property("use_controller_rotation_yaw", False)
            # Auto possess AI placed in world
            try:
                a.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD)
                L("  auto_possess set")
            except Exception as e:
                L("  auto_possess "+str(e))
        except Exception as e:
            L("%s ERR %s"%(n,e))
    try:
        unreal.EditorLevelLibrary.save_current_level(); L("saved "+map_path)
    except Exception as e:
        L("save err "+str(e))

# Also set AI focus-friendly defaults on BP CDO (still no mesh change)
BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
cls=unreal.EditorAssetLibrary.load_blueprint_class(BP)
cdo=unreal.get_default_object(cls)
cm=cdo.get_editor_property("character_movement")
cm.set_editor_property("rotation_rate", unreal.Rotator(pitch=0.0,yaw=720.0,roll=0.0))
cm.set_editor_property("orient_rotation_to_movement", True)
cm.set_editor_property("use_controller_desired_rotation", False)
cdo.set_editor_property("use_controller_rotation_yaw", False)
try:
    cdo.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD)
    L("cdo auto_possess ok")
except Exception as e:
    L("cdo auto_possess "+str(e))
# AIController class?
try:
    L("ai_controller_class=%s"%cdo.get_editor_property("ai_controller_class"))
except Exception as e:
    L("aiclass "+str(e))
unreal.EditorAssetLibrary.save_asset(BP); L("bp saved")

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("done")
