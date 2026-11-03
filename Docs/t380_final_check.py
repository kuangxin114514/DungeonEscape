# -*- coding: utf-8 -*-
import unreal, importlib
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\t380_final_check.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T380F: "+str(m))
    except Exception: print(m)
# reload runtime
import sys
for n in list(sys.modules.keys()):
    if n in ("shop_interact_runtime","skeleton_engine_ai") or n.endswith("shop_interact_runtime") or n.endswith("skeleton_engine_ai"):
        del sys.modules[n]
import shop_interact_runtime as s
import skeleton_engine_ai as e
importlib.reload(e); importlib.reload(s)
L("has_update_skeleton_ai="+str(hasattr(s,"update_skeleton_ai")))
L("has_clear="+str(hasattr(s,"_clear_skeleton_ai")))
L("has_damage="+str(hasattr(s,"_damage_player")))
L("tick_wired="+str("skeleton_engine_ai" in open(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py",encoding="utf-8").read()))
L("AGGRO=%s SPEED=%s DMG=%s CD=%s WINDUP=%s"%(e.AGGRO_RANGE,e.CHASE_SPEED,e.ATTACK_DAMAGE,e.ATTACK_COOLDOWN,e.ATTACK_WINDUP))
# BP
bp="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
bcls=unreal.EditorAssetLibrary.load_blueprint_class(bp)
cdo=unreal.get_default_object(bcls)
cm=cdo.get_editor_property("character_movement")
L("ortm="+str(cm.get_editor_property("orient_rotation_to_movement")))
L("max_walk="+str(cm.get_editor_property("max_walk_speed")))
mesh=cdo.get_editor_property("mesh")
L("anim_mode="+str(mesh.get_editor_property("animation_mode")))
try: L("rel_rot="+str(mesh.get_editor_property("relative_rotation")))
except Exception as ex: L("rel_rot ERR "+str(ex))
# nav volumes on current map
world=unreal.EditorLevelLibrary.get_editor_world()
L("world="+str(world.get_name() if world else None))
cnt=0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if a.get_class().get_name().startswith("NavMeshBoundsVolume"):
        cnt+=1
L("nav_volumes_current="+str(cnt))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
