# -*- coding: utf-8 -*-
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\t380_single_node.txt"
lines=[]
def L(m):
    lines.append(str(m)); 
    try: unreal.log("T380SN: "+str(m))
    except Exception: print(m)
BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
bcls=unreal.EditorAssetLibrary.load_blueprint_class(BP)
L("bcls="+str(bcls))
cdo=unreal.get_default_object(bcls)
mesh=cdo.get_editor_property("mesh")
# Keep ABP created for later, but use Single Node so runtime play_animation drives idle/run/attack
try:
    mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    L("mode="+str(mesh.get_editor_property("animation_mode")))
except Exception as e:
    L("mode ERR "+str(e))
# Prefer Idle as default animation asset if property exists
idle=unreal.load_asset("/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Idle_Rig")
for prop in ("animation","Animation","animation_to_play"):
    try:
        mesh.set_editor_property(prop, idle)
        L("set %s ok"%prop)
    except Exception as e:
        L("%s ERR %s"%(prop,e))
try:
    mesh.play_animation(idle, True)
    L("CDO play idle ok")
except Exception as e:
    L("CDO play ERR "+str(e))
unreal.EditorAssetLibrary.save_asset(BP, only_if_is_dirty=False)
L("saved")
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
